import os
import gc
import json
import asyncio
import traceback
import numpy as np
import google.generativeai as genai
from typing import List, Dict, Any
from dotenv import load_dotenv

from app.services.document_processor import DocumentProcessor
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService, INDEX_DIR
from app.services.rag_service import RAGService

# Load environment variables
load_dotenv()

# Configure Gemini for summary and quiz fallback if needed
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def index_document_file(document_id: str, file_path: str) -> bool:
    """
    Page-aware structured indexing:
    1. Extract text page-by-page preserving page numbers via PyMuPDF.
    2. Chunk pages into sentence-aware sliding window chunks with metadata.
    3. Generate normalized vector embeddings.
    4. Save FAISS index and metadata mapping to indices/.
    5. Save combined text file for summaries and quizzes.
    """
    try:
        print(f"[RAG Facade] Indexing document file {file_path} for ID: {document_id}")

        # 1. Page-aware PDF extraction
        pages = DocumentProcessor.extract_pages_from_pdf(file_path)
        if not pages:
            pages = [{"page": 1, "text": "This document has no readable text content."}]

        # Save combined text file for summarizer / quiz generator
        full_text = DocumentProcessor.get_full_text(pages)
        txt_path = os.path.join(INDEX_DIR, f"{document_id}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        del full_text  # Release full text string

        # 2. Chunk text with page metadata
        chunks_metadata = ChunkingService.chunk_pages(pages=pages, document_id=document_id)
        del pages  # Release pages list
        if not chunks_metadata:
            chunks_metadata = [{
                "chunk_id": 0,
                "document_id": document_id,
                "page": 1,
                "text": "This document has no readable text content.",
                "preview": "This document has no readable text content."
            }]

        # 3. Generate embeddings
        chunk_texts = [c["text"] for c in chunks_metadata]
        embeddings = EmbeddingService.generate_embeddings(chunk_texts)
        del chunk_texts  # Release chunk text list

        # 4. Build and save FAISS index & metadata
        success = VectorStoreService.build_and_save_index(
            document_id=document_id,
            embeddings=embeddings,
            chunks_metadata=chunks_metadata
        )
        del embeddings  # Release embeddings array
        gc.collect()

        print(f"[RAG Facade] Structured indexing completed for doc {document_id}. Chunks: {len(chunks_metadata)}")
        return success
    except Exception as e:
        print(f"[RAG Facade] Error indexing document file {document_id}: {e}")
        traceback.print_exc()
        gc.collect()
        return False

def index_document_text(document_id: str, text: str) -> bool:
    """
    Fallback indexing from raw text string. Converts raw text to single-page structured object.
    """
    try:
        pages = [{"page": 1, "text": text}]
        
        # Save full text
        txt_path = os.path.join(INDEX_DIR, f"{document_id}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        chunks_metadata = ChunkingService.chunk_pages(pages=pages, document_id=document_id)
        del pages
        chunk_texts = [c["text"] for c in chunks_metadata]
        embeddings = EmbeddingService.generate_embeddings(chunk_texts)
        del chunk_texts

        success = VectorStoreService.build_and_save_index(
            document_id=document_id,
            embeddings=embeddings,
            chunks_metadata=chunks_metadata
        )
        del embeddings
        gc.collect()
        return success
    except Exception as e:
        print(f"[RAG Facade] Error indexing text for doc {document_id}: {e}")
        traceback.print_exc()
        gc.collect()
        return False

def query_rag_engine(document_id: str, question: str, document_name: str = "Uploaded Document", debug: bool = False) -> Dict[str, Any]:
    """
    Delegates to async RAGService two-stage pipeline.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already running inside async FastAPI event loop
            task = RAGService.process_query(document_id, question, document_name=document_name, debug_mode=debug)
            return loop.create_task(task)
        else:
            return asyncio.run(RAGService.process_query(document_id, question, document_name=document_name, debug_mode=debug))
    except Exception:
        return asyncio.run(RAGService.process_query(document_id, question, document_name=document_name, debug_mode=debug))

async def async_query_rag_engine(document_id: str, question: str, document_name: str = "Uploaded Document", debug: bool = False) -> Dict[str, Any]:
    """
    Async helper for FastAPI routes.
    """
    return await RAGService.process_query(document_id, question, document_name=document_name, debug_mode=debug)

def generate_with_gemini_fallback(prompt: str, is_json: bool = True) -> str:
    """
    Tries preferred Gemini models in sequence and returns text response.
    """
    models_to_try = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-2.5-pro"]
    config = {"response_mime_type": "application/json"} if is_json else {}
    
    last_err = None
    for model_name in models_to_try:
        try:
            print(f"[RAG Engine] Trying Gemini model '{model_name}'...")
            m = genai.GenerativeModel(model_name)
            res = m.generate_content(prompt, generation_config=config)
            if res and res.text:
                return res.text.strip()
        except Exception as e:
            last_err = e
            print(f"[RAG Engine] Model '{model_name}' returned error: {e}")
            continue
            
    raise RuntimeError(f"All Gemini models failed. Last error: {last_err}")

def generate_notes_summary(document_id: str, filename: str) -> Dict[str, Any]:
    """
    Generate student-friendly simplified notes and summary using Gemini API.
    """
    print(f"[RAG Facade] Generating summary for document ID: {document_id}")
    txt_path = os.path.join(INDEX_DIR, f"{document_id}.txt")
    if not os.path.exists(txt_path):
        return {
            "document_id": document_id,
            "summary": "This document was uploaded before the summarization system was set up. Please re-upload.",
            "notes": ["Please re-upload this document to generate study notes."]
        }
        
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            full_text = f.read()
            
        if not full_text.strip():
            return {
                "document_id": document_id,
                "summary": "The document contains no readable text.",
                "notes": []
            }
            
        words = full_text.split()
        max_words = 12000
        if len(words) > max_words:
            full_text = " ".join(words[:max_words]) + "\n... [truncated] ..."
            
        prompt = f"""You are an expert academic tutor. Summarize the research paper "{filename}" for a student.
Please generate:
1. A beginner-friendly, concise executive summary of the paper.
2. A list of 4 to 6 clear, structured study notes explaining core concepts, methodology, key findings, and practical takeaways.

Return response as JSON matching schema:
{{
    "summary": "string - a simplified, educational executive summary",
    "notes": [
        "Core Concept: ...",
        "Methodology: ...",
        "Key Findings: ...",
        "Practical Takeaways: ..."
    ]
}}

Content:
{full_text}
"""
        response_text = generate_with_gemini_fallback(prompt, is_json=True)
        result = json.loads(response_text)
        return {
            "document_id": document_id,
            "summary": result.get("summary", "Summary not generated."),
            "notes": result.get("notes", [])
        }
    except Exception as e:
        print(f"[RAG Facade] Error generating notes summary: {e}")
        return {
            "document_id": document_id,
            "summary": f"An error occurred while generating summary: {str(e)}",
            "notes": []
        }

def generate_quiz_questions(document_id: str) -> List[Dict[str, Any]]:
    """
    Generate multiple-choice quiz questions categorized into 3 distinct quiz sessions based on paper content.
    """
    txt_path = os.path.join(INDEX_DIR, f"{document_id}.txt")
    if not os.path.exists(txt_path):
        return []
        
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            full_text = f.read()
            
        if not full_text.strip():
            return []
            
        words = full_text.split()
        max_words = 12000
        if len(words) > max_words:
            full_text = " ".join(words[:max_words]) + "\n... [truncated] ..."
            
        prompt = f"""You are an expert educator creating study materials for learners.
Based on the research paper below, generate 6 to 9 high-quality multiple choice quiz questions divided across 3 distinct learning sessions:
- Session 1: Fundamentals & Core Concepts
- Session 2: Methodology & Analysis
- Session 3: Key Findings & Applications

Each question must have:
- "session": Exact session title string ("Session 1: Fundamentals & Core Concepts", "Session 2: Methodology & Analysis", or "Session 3: Key Findings & Applications")
- "question": Question text
- "options": Array of 4 unique answer choice strings
- "correct_option_index": Integer (0, 1, 2, or 3) indicating the correct answer option index
- "explanation": Brief educational explanation of why the correct option is right.

Return response as a JSON array of objects:
[
    {{
        "session": "Session 1: Fundamentals & Core Concepts",
        "question": "string",
        "options": ["string", "string", "string", "string"],
        "correct_option_index": 0,
        "explanation": "string"
    }}
]

Content:
{full_text}
"""
        response_text = generate_with_gemini_fallback(prompt, is_json=True)
        return json.loads(response_text)
    except Exception as e:
        print(f"[RAG Facade] Error generating quiz questions: {e}")
        return []


from datetime import datetime
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status

from app.config import documents_collection, chat_history_collection
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService

class ChatService:
    """
    RAG service coordinating context retrieval from FAISS indices
    and generating targeted responses using Google's Gemini LLM.
    """

    @staticmethod
    async def ask_question(document_id: str, question: str, current_user: dict) -> dict:
        """
        Executes end-to-end RAG pipeline:
        1. Fetches paper metadata from MongoDB.
        2. Embeds user query.
        3. Retrieves relevant context chunks via FAISS.
        4. Queries Gemini for plain-English answers.
        5. Saves chat history.
        """
        # Validate MongoDB document ID structure
        try:
            doc_obj_id = ObjectId(document_id)
        except (InvalidId, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Document ID format provided."
            )

        # Lookup document in database
        doc = await documents_collection.find_one({"_id": doc_obj_id})
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target research document not found."
            )

        # Verify that FAISS index exists on disk
        faiss_path = doc.get("faiss_path")
        if not faiss_path or not os.path.exists(faiss_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vector search database index file is missing for this document. Please re-upload."
            )

        # Retrieve text chunks mapping from DB
        chunks = doc.get("chunks", [])
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Extracted text chunks are missing for this document."
            )

        # 1. Embed user query using Phase 8 service
        try:
            query_vector = EmbeddingService.generate_embeddings([question])[0]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate query vector embeddings: {str(e)}"
            )

        # 2. Run similarity search to get matching chunk indices using Phase 9 service
        try:
            matched_indices = VectorService.similarity_search(faiss_path, query_vector, k=4)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Vector search execution failed: {str(e)}"
            )

        # 3. Compile matched chunks into context
        sources = []
        for idx in matched_indices:
            if idx < len(chunks):
                sources.append(chunks[idx])

        context_block = "\n\n".join(sources)

        # 4. Formulate System Prompt instructions
        prompt = f"""You are a helpful academic study mentor. Answer the student's question clearly, explaining complex math, equations, or concepts in simple, easy-to-understand terms.
Use ONLY the provided research paper context blocks below to answer. If the answer cannot be found in the context, say: "I cannot find the answer based on the provided research context." Do not make up information.

=== Context Blocks ===
{context_block}

=== Student Question ===
{question}

Provide your detailed, study-friendly answer:
"""

        # 5. Get generative answer from Gemini API
        print(f"[Chat Service] Querying LLM for answer...")
        answer = LLMService.generate_response(prompt)

        # 6. Save query-response interaction to MongoDB
        chat_record = {
            "user_id": str(current_user["_id"]),
            "document_id": document_id,
            "question": question,
            "answer": answer,
            "sources": sources,
            "created_at": datetime.utcnow()
        }

        try:
            result = await chat_history_collection.insert_one(chat_record)
            chat_record["id"] = str(result.inserted_id)
        except Exception as e:
            print(f"[Chat Service Warning] Failed to log chat to database: {e}")
            chat_record["id"] = "local_only_id"

        return chat_record

    @staticmethod
    async def get_chat_history(current_user: dict) -> List[dict]:
        """
        Retrieves all query logs belonging to the active user sorted by date.
        """
        cursor = chat_history_collection.find({"user_id": str(current_user["_id"])}).sort("created_at", -1)
        history = []
        async for chat in cursor:
            history.append({
                "id": str(chat["_id"]),
                "user_id": chat["user_id"],
                "document_id": chat["document_id"],
                "question": chat["question"],
                "answer": chat["answer"],
                "sources": chat.get("sources", []),
                "created_at": chat["created_at"]
            })
        return history
import os

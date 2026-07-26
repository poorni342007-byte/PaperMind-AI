import os
import shutil
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
from app.config import settings, documents_collection
from app.utils.pdf_extractor import extract_text_from_pdf
from app.utils.text_chunker import chunk_text
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService

# Define file storage root directory
UPLOAD_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
    settings.UPLOAD_DIR
)
os.makedirs(UPLOAD_ROOT, exist_ok=True)

class PDFService:
    """
    Business service layer managing local research PDF file writes 
    and indexing metadata fields inside MongoDB collections.
    """

    @staticmethod
    async def save_and_initialize_document(file: UploadFile, current_user: dict) -> dict:
        """
        Validates file formats, writes binaries to disk, and indexes records.
        """
        # Validate file extension
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF research documents are supported."
            )

        # Generate unique, collision-free filename using timestamp and owner ID prefix
        safe_filename = f"{str(current_user['_id'])}_ts{int(datetime.utcnow().timestamp())}_{file.filename}"
        file_path = os.path.join(UPLOAD_ROOT, safe_filename)

        # Save uploaded file binary payload to server local storage path
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to write file to local disk: {str(e)}"
            )

        # Extract actual text from PDF using PyMuPDF (fitz)
        try:
            extracted_text = extract_text_from_pdf(file_path)
        except Exception as err:
            # Clean up file on disk if extraction fails
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to process PDF content structure: {str(err)}"
            )

        # Generate 500 characters preview length
        preview_len = min(len(extracted_text), 500)
        preview = extracted_text[:preview_len]

        # Segment parsed text content into semantic chunks (sliding window)
        chunks = chunk_text(extracted_text, chunk_size=800, chunk_overlap=150)
        print(f"[PDF Service] Text chunking complete. Created {len(chunks)} overlapping chunks.")

        # Generate vector embeddings for text chunks using local Hugging Face transformer
        print(f"[PDF Service] Generating vector embeddings for {len(chunks)} chunks...")
        embeddings = EmbeddingService.generate_embeddings(chunks)

        # Save local FAISS index binary file on server filesystem path
        print("[PDF Service] Indexing vectors using FAISS...")
        faiss_path = VectorService.create_and_save_index(file_path, embeddings)

        # Assemble MongoDB index document
        doc_record = {
            "user_id": str(current_user["_id"]),
            "filename": file.filename,
            "file_path": file_path,
            "faiss_path": faiss_path,
            "uploaded_at": datetime.utcnow(),
            "extracted_text_preview": preview,
            "extracted_text": extracted_text,  # store full text
            "chunks": chunks  # store parsed chunks
        }

        # Write metadata to DB
        result = await documents_collection.insert_one(doc_record)
        
        # Return serialized metadata dictionary
        return {
            "id": str(result.inserted_id),
            "user_id": doc_record["user_id"],
            "filename": doc_record["filename"],
            "file_path": doc_record["file_path"],
            "uploaded_at": doc_record["uploaded_at"],
            "extracted_text_preview": doc_record["extracted_text_preview"]
        }

    @staticmethod
    async def list_user_documents(current_user: dict) -> list:
        """
        Queries all indexed files belonging to the currently active session user.
        """
        cursor = documents_collection.find({"user_id": str(current_user["_id"])})
        docs_list = []
        async for doc in cursor:
            docs_list.append({
                "id": str(doc["_id"]),
                "user_id": doc["user_id"],
                "filename": doc["filename"],
                "file_path": doc["file_path"],
                "uploaded_at": doc["uploaded_at"],
                "extracted_text_preview": doc["extracted_text_preview"]
            })
        return docs_list

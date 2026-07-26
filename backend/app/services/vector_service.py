import os
from typing import List
import numpy as np
import faiss

class VectorService:
    """
    Service layer wrapping Facebook AI Similarity Search (FAISS).
    Creates vector files on disk and retrieves nearest neighbor indexes.
    """

    @staticmethod
    def create_and_save_index(pdf_path: str, embeddings: List[List[float]]) -> str:
        """
        Creates an IndexFlatL2 index for the document and writes it to a .faiss file.
        Returns the path where the index file was written.
        """
        if not embeddings:
            raise ValueError("[Vector Service Error] Embeddings list cannot be empty.")

        # Convert embeddings list into a float32 numpy array matrix
        xb = np.array(embeddings).astype('float32')
        dimension = xb.shape[1]  # Dimensional size, should be 384 for all-MiniLM-L6-v2

        print(f"[Vector Service] Creating FAISS L2 index with dimension {dimension} for {len(embeddings)} vectors...")
        
        # Initialize standard IndexFlatL2 (Euclidean distance search space)
        index = faiss.IndexFlatL2(dimension)
        index.add(xb)

        # Build FAISS output path using source PDF file path as base
        faiss_path = pdf_path.replace(".pdf", ".faiss")
        
        try:
            # Write compiled binary index to disk
            faiss.write_index(index, faiss_path)
            print(f"[Vector Service] Saved FAISS index successfully to: {faiss_path}")
        except Exception as e:
            print(f"[Vector Service Error] Failed to write index to disk: {e}")
            raise RuntimeError(f"FAISS save error: {str(e)}")

        return faiss_path

    @staticmethod
    def similarity_search(faiss_path: str, query_vector: List[float], k: int = 4) -> List[int]:
        """
        Loads the .faiss index file from disk and searches for the top k nearest vector neighbors.
        Returns a list of integer indices mapping back to the source text chunks.
        """
        if not os.path.exists(faiss_path):
            raise FileNotFoundError(f"[Vector Service Error] FAISS index file not found at: {faiss_path}")

        try:
            # Load the binary FAISS index from disk
            index = faiss.read_index(faiss_path)
        except Exception as e:
            print(f"[Vector Service Error] Failed to read FAISS index: {e}")
            raise RuntimeError(f"FAISS index read error: {str(e)}")

        # Format query vector to a float32 numpy matrix of shape (1, dimension)
        xq = np.array([query_vector]).astype('float32')
        
        # Execute index search
        # D: distances (floats), I: indices (integers)
        distances, indices = index.search(xq, k)
        
        # Convert index array to a standard Python integer list
        matched_indices = indices[0].tolist()
        
        # Filter out negative index padding if FAISS returns fewer than k matches
        valid_indices = [idx for idx in matched_indices if idx != -1]
        
        print(f"[Vector Service] Similarity search complete. Found nearest indices: {valid_indices}")
        return valid_indices

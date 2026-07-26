import os
import json
import faiss
import numpy as np
from typing import List, Dict, Any, Tuple

# Index directory path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INDEX_DIR = os.path.join(BASE_DIR, "indices")
os.makedirs(INDEX_DIR, exist_ok=True)

class VectorStoreService:
    """
    Service for building, saving, loading, and searching FAISS vector indexes
    with associated chunk metadata mapping. Strictly isolated by document_id.
    """

    @staticmethod
    def get_index_paths(document_id: str) -> Tuple[str, str]:
        """
        Returns file paths for FAISS index and chunk metadata JSON for a document.
        """
        # Escape document_id to prevent path traversal
        safe_id = "".join([c for c in str(document_id) if c.isalnum() or c in ("-", "_")])
        index_path = os.path.join(INDEX_DIR, f"{safe_id}.index")
        metadata_path = os.path.join(INDEX_DIR, f"{safe_id}_metadata.json")
        return index_path, metadata_path

    @staticmethod
    def build_and_save_index(
        document_id: str,
        embeddings: np.ndarray,
        chunks_metadata: List[Dict[str, Any]]
    ) -> bool:
        """
        Creates a FAISS IndexFlatL2 (or IndexFlatIP for normalized vectors) index,
        populates it with chunk embeddings, and persists both index and metadata mapping to disk.
        """
        try:
            if embeddings.size == 0 or len(chunks_metadata) == 0:
                print(f"[VectorStoreService] Warning: empty embeddings or metadata for doc {document_id}")
                return False

            dimension = embeddings.shape[1]
            index_path, metadata_path = VectorStoreService.get_index_paths(document_id)

            # Using IndexFlatIP for normalized vectors (equivalent to cosine similarity)
            # or IndexFlatL2 for L2 distance. IndexFlatIP gives higher values for higher similarity.
            index = faiss.IndexFlatIP(dimension)
            index.add(embeddings.astype('float32'))

            faiss.write_index(index, index_path)
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(chunks_metadata, f, ensure_ascii=False, indent=2)

            print(f"[VectorStoreService] Index saved for doc {document_id} with {len(chunks_metadata)} vectors.")
            return True
        except Exception as e:
            print(f"[VectorStoreService] Error saving index for doc {document_id}: {e}")
            raise RuntimeError(f"FAISS index creation failed: {str(e)}")

    @staticmethod
    def retrieve_candidates(
        document_id: str,
        query_vector: np.ndarray,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Loads FAISS index and chunk metadata for the specified document_id,
        and retrieves the top_k closest candidate chunks.
        
        Enforces strict document boundary isolation.
        """
        index_path, metadata_path = VectorStoreService.get_index_paths(document_id)

        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            print(f"[VectorStoreService] Warning: index files missing for doc {document_id}")
            return []

        try:
            index = faiss.read_index(index_path)
            with open(metadata_path, "r", encoding="utf-8") as f:
                chunks_metadata = json.load(f)

            if not chunks_metadata:
                return []

            k = min(top_k, len(chunks_metadata))
            query_vector_f32 = query_vector.astype('float32')

            # Search FAISS index
            scores, indices = index.search(query_vector_f32, k)

            candidates = []
            for idx, vec_idx in enumerate(indices[0]):
                if vec_idx != -1 and vec_idx < len(chunks_metadata):
                    meta = dict(chunks_metadata[vec_idx])
                    # Strictly verify document_id match
                    if str(meta.get("document_id")) == str(document_id):
                        meta["retrieval_score"] = float(scores[0][idx])
                        candidates.append(meta)

            print(f"[VectorStoreService] Retrieved {len(candidates)} candidate chunks for doc {document_id}")
            return candidates

        except Exception as e:
            print(f"[VectorStoreService] Error querying index for doc {document_id}: {e}")
            return []

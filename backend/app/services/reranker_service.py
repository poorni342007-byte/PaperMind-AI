import traceback
from typing import List, Dict, Any

RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

class RerankerService:
    """
    Singleton service loading cross-encoder/ms-marco-MiniLM-L-6-v2 model once.
    Reranking (query, candidate_chunk) text pairs using CrossEncoder scoring.
    """
    _model = None
    _load_attempted = False

    @classmethod
    def get_model(cls):
        """
        Lazy-loads the CrossEncoder model on demand and caches it.
        """
        if cls._model is None and not cls._load_attempted:
            cls._load_attempted = True
            print(f"[RerankerService] Loading CrossEncoder model '{RERANKER_MODEL_NAME}'...")
            try:
                import torch
                torch.set_num_threads(1)
                from sentence_transformers import CrossEncoder
                cls._model = CrossEncoder(RERANKER_MODEL_NAME)
                print(f"[RerankerService] Model '{RERANKER_MODEL_NAME}' loaded successfully!")
            except Exception as e:
                print(f"[RerankerService] Error loading CrossEncoder model: {e}")
                traceback.print_exc()
                print("[RerankerService] Will fall back to vector retrieval scoring.")
                cls._model = None
        return cls._model

    @classmethod
    def rerank_candidates(
        cls,
        question: str,
        candidates: List[Dict[str, Any]],
        final_top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Scores (question, candidate_text) pairs with the CrossEncoder model,
        sorts candidates in descending order of reranker score, and returns the top final_top_k items.
        
        Args:
            question: User search query string
            candidates: List of candidate chunk dictionaries from vector retrieval
            final_top_k: Maximum number of reranked chunks to return (default 4)
            
        Returns:
            List of reranked chunk metadata dictionaries with 'reranker_score' populated.
        """
        if not candidates:
            return []

        model = cls.get_model()
        if model is None:
            print("[RerankerService] Model unavailable; falling back to top candidates by retrieval score.")
            for cand in candidates:
                if "reranker_score" not in cand:
                    cand["reranker_score"] = float(cand.get("retrieval_score", 0.0))
            return candidates[:final_top_k]

        try:
            # Construct text pairs: (query, chunk_text)
            pairs = [[question, cand.get("text", "")] for cand in candidates]
            
            # Predict logit scores using CrossEncoder
            scores = model.predict(pairs)

            # Attach scores to candidates
            for idx, cand in enumerate(candidates):
                cand["reranker_score"] = float(scores[idx])

            # Sort by reranker_score descending
            reranked = sorted(candidates, key=lambda x: x.get("reranker_score", -999.0), reverse=True)
            
            # Keep top final_top_k
            selected = reranked[:final_top_k]
            print(f"[RerankerService] Reranked {len(candidates)} candidates down to {len(selected)} top chunks.")
            return selected

        except Exception as e:
            print(f"[RerankerService] Error during reranking: {e}")
            for cand in candidates:
                if "reranker_score" not in cand:
                    cand["reranker_score"] = float(cand.get("retrieval_score", 0.0))
            return candidates[:final_top_k]


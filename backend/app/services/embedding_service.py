import os
import numpy as np
from typing import List
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GEMINI_EMBEDDING_MODEL = "models/gemini-embedding-001"

class EmbeddingService:
    """
    Singleton embedding service.
    First attempts local SentenceTransformer ('sentence-transformers/all-MiniLM-L6-v2').
    If PyTorch/SentenceTransformer is blocked by Windows Application Control policy (WinError 4551) or fails to load,
    falls back gracefully to Google Gemini API embeddings ('models/gemini-embedding-001').
    """
    _model = None
    _use_gemini_fallback = False

    @classmethod
    def _init_model(cls):
        if cls._model is None and not cls._use_gemini_fallback:
            try:
                print(f"[EmbeddingService] Attempting to load local model '{MODEL_NAME}'...")
                from sentence_transformers import SentenceTransformer
                cls._model = SentenceTransformer(MODEL_NAME)
                print(f"[EmbeddingService] Local model '{MODEL_NAME}' loaded successfully!")
            except Exception as e:
                print(f"[EmbeddingService] Could not load SentenceTransformer ({e}).")
                print(f"[EmbeddingService] Falling back to Gemini API embeddings ('{GEMINI_EMBEDDING_MODEL}').")
                cls._use_gemini_fallback = True

    @classmethod
    def _generate_gemini_embeddings(cls, texts: List[str]) -> np.ndarray:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)

        vectors = []
        for text in texts:
            clean_text = text.strip() if text else " "
            try:
                res = genai.embed_content(
                    model=GEMINI_EMBEDDING_MODEL,
                    content=clean_text
                )
                vec = np.array(res['embedding'], dtype=np.float32)
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
                vectors.append(vec)
            except Exception as e:
                print(f"[EmbeddingService] Gemini embed_content error: {e}")
                vectors.append(np.zeros(3072, dtype=np.float32))
        return np.array(vectors, dtype=np.float32)

    @classmethod
    def generate_embeddings(cls, texts: List[str]) -> np.ndarray:
        """
        Encodes a list of strings into normalized float32 numpy vector array.
        """
        cls._init_model()

        if not texts:
            dim = 3072 if cls._use_gemini_fallback else 384
            return np.empty((0, dim), dtype=np.float32)

        if cls._use_gemini_fallback:
            return cls._generate_gemini_embeddings(texts)

        try:
            embeddings = cls._model.encode(
                texts,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            print(f"[EmbeddingService] Error generating local embeddings: {e}. Switching to Gemini fallback.")
            cls._use_gemini_fallback = True
            return cls._generate_gemini_embeddings(texts)

    @classmethod
    def generate_query_embedding(cls, query: str) -> np.ndarray:
        """
        Encodes a single user search question into a normalized float32 numpy vector array.
        """
        return cls.generate_embeddings([query])


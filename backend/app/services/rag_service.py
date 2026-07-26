import os
from typing import Dict, Any, List
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.services.reranker_service import RerankerService
from app.services.llm_service import LLMService

GROUNDING_SYSTEM_PROMPT = """You are PaperMind AI, a research-document assistant.

Answer only from the supplied document context.

Rules:
1. Never use outside knowledge.
2. Never invent a person, date, number, result or conclusion.
3. If the context does not contain enough information, respond exactly:
   'I could not find this information in the uploaded document.'
4. Ignore context that is unrelated to the question.
5. Give a clear beginner-friendly answer.
6. Cite the supporting page numbers.
7. Do not claim that a source supports something unless it actually does.
8. Format your answer cleanly and naturally. Avoid raw markdown header hashes (like ###) or redundant divider symbols."""

FALLBACK_NO_INFO_ANSWER = "I could not find this information in the uploaded document."

class RAGService:
    """
    Coordinator service for two-stage RAG:
    1. FAISS retrieval (Top K candidate chunks)
    2. Cross-Encoder reranking (Top K final chunks)
    3. Relevance threshold validation
    4. Grounded Gemini LLM answer generation
    """

    @classmethod
    async def process_query(
        cls,
        document_id: str,
        question: str,
        document_name: str = "Uploaded Document",
        debug_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Executes end-to-end grounded RAG pipeline for a given user question and document_id.
        """
        # Read parameters from environment
        retrieval_top_k = int(os.getenv("RAG_RETRIEVAL_TOP_K", "10"))
        final_top_k = int(os.getenv("RAG_FINAL_TOP_K", "4"))
        min_relevance_score = float(os.getenv("RAG_MIN_RELEVANCE_SCORE", "-2.0"))
        env_debug = os.getenv("RAG_DEBUG", "false").lower() in ("true", "1", "yes")
        is_debug = debug_mode or env_debug

        # Input validation & sanitization
        question_clean = question.strip()
        if len(question_clean) > 500:
            question_clean = question_clean[:500]

        print(f"[RAGService] Processing query for doc {document_id}: '{question_clean}'")

        # Step 1: Embed user question
        try:
            query_vector = EmbeddingService.generate_query_embedding(question_clean)
        except Exception as e:
            print(f"[RAGService] Query embedding error: {e}")
            return {
                "answer": FALLBACK_NO_INFO_ANSWER,
                "sources": [],
                "grounded": False
            }

        # Step 2: Retrieve Top K candidate chunks from FAISS
        raw_candidates = VectorStoreService.retrieve_candidates(
            document_id=document_id,
            query_vector=query_vector,
            top_k=retrieval_top_k
        )

        if not raw_candidates:
            print(f"[RAGService] No vector store candidates found for doc {document_id}")
            return {
                "answer": FALLBACK_NO_INFO_ANSWER,
                "sources": [],
                "grounded": False
            }

        # Step 3: Rerank candidates with Cross-Encoder
        reranked_chunks = RerankerService.rerank_candidates(
            question=question_clean,
            candidates=raw_candidates,
            final_top_k=final_top_k
        )

        # Step 4: Relevance score threshold validation
        first_chunk = reranked_chunks[0] if reranked_chunks else {}
        best_score = first_chunk.get("reranker_score", first_chunk.get("retrieval_score", -999.0))
        print(f"[RAGService] Best score: {best_score:.4f} (threshold: {min_relevance_score})")

        if not reranked_chunks or (best_score < min_relevance_score and best_score != -999.0 and min_relevance_score > -10.0):
            print(f"[RAGService] Retrieval rejected: Best score {best_score:.4f} < {min_relevance_score}")
            response_payload = {
                "answer": FALLBACK_NO_INFO_ANSWER,
                "sources": [],
                "grounded": False
            }
            if is_debug:
                response_payload["debug"] = {
                    "raw_candidates_count": len(raw_candidates),
                    "best_score": float(best_score),
                    "min_relevance_score": min_relevance_score,
                    "rejection_reason": "Reranker score below relevance threshold"
                }
            return response_payload

        # Deduplicate final chunks by text while preserving rank order
        seen_texts = set()
        final_chunks = []
        for chunk in reranked_chunks:
            text_snippet = chunk.get("text", "").strip()
            if text_snippet and text_snippet not in seen_texts:
                seen_texts.add(text_snippet)
                final_chunks.append(chunk)

        # Step 5: Build Grounded Context Block
        context_lines = []
        sources_list = []

        for chunk in final_chunks:
            page_num = chunk.get("page", 1)
            chunk_id = chunk.get("chunk_id", 0)
            text_content = chunk.get("text", "")
            preview_str = chunk.get("preview", text_content[:120])

            context_lines.append(f"[Page {page_num}, Chunk {chunk_id}]\n{text_content}")

            sources_list.append({
                "page": page_num,
                "chunk_id": chunk_id,
                "preview": preview_str,
                "retrieval_score": round(float(chunk.get("retrieval_score", 0.0)), 4),
                "reranker_score": round(float(chunk.get("reranker_score", 0.0)), 4)
            })

        formatted_context = "\n\n".join(context_lines)

        user_prompt = f"""Document: {document_name}

Supplied Context:
---
{formatted_context}
---

Question: {question_clean}

Answer:"""

        # Step 6: Query Google Gemini API via LLMService
        llm_result = await LLMService.generate_response(
            system_prompt=GROUNDING_SYSTEM_PROMPT,
            user_message=user_prompt
        )

        if not llm_result["success"]:
            answer_text = llm_result["answer"]
            grounded_flag = False
        else:
            answer_text = llm_result["answer"]
            if FALLBACK_NO_INFO_ANSWER.lower() in answer_text.lower():
                answer_text = FALLBACK_NO_INFO_ANSWER
                sources_list = []
                grounded_flag = False
            else:
                grounded_flag = True

        response_payload = {
            "answer": answer_text,
            "sources": sources_list,
            "grounded": grounded_flag
        }

        # Step 7: Optional Debug Mode Info
        if is_debug:
            response_payload["debug"] = {
                "document_id": document_id,
                "raw_faiss_candidates_count": len(raw_candidates),
                "raw_candidates": [
                    {
                        "chunk_id": c.get("chunk_id"),
                        "page": c.get("page"),
                        "retrieval_score": round(float(c.get("retrieval_score", 0.0)), 4)
                    } for c in raw_candidates
                ],
                "reranked_chunks": [
                    {
                        "chunk_id": c.get("chunk_id"),
                        "page": c.get("page"),
                        "reranker_score": round(float(c.get("reranker_score", 0.0)), 4)
                    } for c in final_chunks
                ],
                "llm_model_used": llm_result.get("model_used"),
                "context_supplied": formatted_context
            }

        return response_payload

import os
import sys
import asyncio

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from rag_engine import index_document_file
from app.services.rag_service import RAGService

TEST_DOC_ID = "test_b2g_doc"
TEST_PDF_PATH = os.path.join(backend_dir, "uploads", "6a5cc2e020a9ebe3ef55b846_1784444336.70895_Build2Gether_Instructions (1).pdf")

async def run_b2g_test():
    print("Indexing Build2Gether Instructions PDF...")
    index_document_file(document_id=TEST_DOC_ID, file_path=TEST_PDF_PATH)

    questions = [
        "what is the main rule to be followed throughput this event",
        "totally how many innovations to be evaluated in round 1"
    ]

    for q in questions:
        print("\n" + "="*70)
        print(f"QUESTION: {q}")
        print("="*70)
        res = await RAGService.process_query(
            document_id=TEST_DOC_ID,
            question=q,
            document_name="Build2Gether Instructions",
            debug_mode=True
        )
        print("ANSWER:\n", res["answer"])
        print("\nSOURCES:")
        for s in res.get("sources", []):
            print(f"  - Page {s['page']} (Reranker: {s['reranker_score']}): {s['preview']}")

if __name__ == "__main__":
    asyncio.run(run_b2g_test())

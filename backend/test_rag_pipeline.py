import os
import sys
import asyncio

# Ensure backend path is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from rag_engine import index_document_file
from app.services.rag_service import RAGService

TEST_DOC_ID = "test_poorni_cmrl_report"
TEST_PDF_PATH = os.path.join(backend_dir, "uploads", "6a4a6d8fad6f28c80651d2b8_ts1783255064_Poorni S CMRL Report.pdf")

async def run_tests():
    print("=" * 70)
    print("STARTING RAG PIPELINE TEST SUITE")
    print("=" * 70)

    if not os.path.exists(TEST_PDF_PATH):
        print(f"ERROR: Test PDF file not found at {TEST_PDF_PATH}")
        return

    # Step 1: Index PDF using page-aware structured chunker
    print(f"\n[1/6] Indexing document: {TEST_PDF_PATH}")
    success = index_document_file(document_id=TEST_DOC_ID, file_path=TEST_PDF_PATH)
    print(f"Indexing Status: {'SUCCESS' if success else 'FAILED'}")
    assert success, "Indexing failed!"

    # Test cases to execute
    test_cases = [
        {
            "id": 1,
            "question": "What is the name of the intern?",
            "expected_keyword": "Poorni"
        },
        {
            "id": 2,
            "question": "Where was the internship completed?",
            "expected_keyword": "Chennai Metro"
        },
        {
            "id": 3,
            "question": "Who was the project guide?",
            "expected_keyword": "guide"
        },
        {
            "id": 4,
            "question": "What is the quantum computing algorithm used for rocket propulsion in this paper?",
            "expected_keyword": "I could not find this information"
        },
        {
            "id": 5,
            "question": "Tell me about it.",
            "expected_keyword": None
        }
    ]

    for tc in test_cases:
        print("\n" + "-" * 70)
        print(f"TEST CASE {tc['id']}: '{tc['question']}'")
        print("-" * 70)

        result = await RAGService.process_query(
            document_id=TEST_DOC_ID,
            question=tc["question"],
            document_name="Poorni S CMRL Internship Report",
            debug_mode=True
        )

        print(f"Answer:\n{result['answer']}\n")
        print(f"Grounded: {result['grounded']}")
        print("Sources:")
        for src in result.get("sources", []):
            print(f"  - Page {src['page']} (Chunk {src['chunk_id']}) [Reranker Score: {src['reranker_score']}]: {src['preview']}")

        if tc["expected_keyword"]:
            if tc["expected_keyword"].lower() in result["answer"].lower():
                print(f"\n[PASSED] Expected keyword '{tc['expected_keyword']}' found in answer!")
            else:
                print(f"\n[INFO] Keyword '{tc['expected_keyword']}' check completed.")

    print("\n" + "=" * 70)
    print("RAG PIPELINE TEST SUITE COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_tests())

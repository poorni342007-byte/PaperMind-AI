import re
from typing import List, Dict, Any

class ChunkingService:
    """
    Service responsible for sentence-aware sliding window text chunking.
    Preserves page numbers, chunk index, document ID, and preview text.
    """

    @staticmethod
    def chunk_pages(
        pages: List[Dict[str, Any]],
        document_id: str,
        target_chunk_size: int = 800,
        chunk_overlap: int = 150
    ) -> List[Dict[str, Any]]:
        """
        Chunks page-structured document data into sliding window chunks while maintaining sentence boundaries.
        
        Args:
            pages: List of {"page": int, "text": str}
            document_id: Unique document identifier string
            target_chunk_size: Target characters per chunk (default 800)
            chunk_overlap: Overlap characters between consecutive chunks (default 150)
            
        Returns:
            List of chunk dictionaries:
            [
                {
                    "chunk_id": 0,
                    "document_id": "...",
                    "page": 1,
                    "text": "Chunk text content...",
                    "preview": "First 100 chars..."
                },
                ...
            ]
        """
        all_chunks = []
        global_chunk_id = 0

        for page_obj in pages:
            page_num = page_obj.get("page", 1)
            page_text = page_obj.get("text", "").strip()

            if not page_text:
                continue

            # Split page text into sentences (handles '.', '!', '?', newlines)
            sentences = ChunkingService._split_into_sentences(page_text)
            
            current_chunk_sentences = []
            current_length = 0

            for sentence in sentences:
                sentence_len = len(sentence)
                
                # If adding this sentence exceeds target size and current_chunk is not empty
                if current_length + sentence_len > target_chunk_size and current_chunk_sentences:
                    chunk_text = " ".join(current_chunk_sentences).strip()
                    if chunk_text:
                        all_chunks.append({
                            "chunk_id": global_chunk_id,
                            "document_id": document_id,
                            "page": page_num,
                            "text": chunk_text,
                            "preview": chunk_text[:120].strip() + ("..." if len(chunk_text) > 120 else "")
                        })
                        global_chunk_id += 1

                    # Slide window backwards to create overlap
                    overlap_sentences = []
                    overlap_len = 0
                    for prev_sent in reversed(current_chunk_sentences):
                        if overlap_len + len(prev_sent) <= chunk_overlap:
                            overlap_sentences.insert(0, prev_sent)
                            overlap_len += len(prev_sent)
                        else:
                            break

                    current_chunk_sentences = overlap_sentences
                    current_length = overlap_len

                current_chunk_sentences.append(sentence)
                current_length += sentence_len

            # Add remaining sentences for the page
            if current_chunk_sentences:
                chunk_text = " ".join(current_chunk_sentences).strip()
                if chunk_text:
                    all_chunks.append({
                        "chunk_id": global_chunk_id,
                        "document_id": document_id,
                        "page": page_num,
                        "text": chunk_text,
                        "preview": chunk_text[:120].strip() + ("..." if len(chunk_text) > 120 else "")
                    })
                    global_chunk_id += 1

        print(f"[ChunkingService] Created {len(all_chunks)} chunks for document {document_id}")
        return all_chunks

    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        """
        Splits text into sentences while respecting common punctuation and line breaks.
        """
        # Split on standard sentence delimiters or double newlines
        raw_sentences = re.split(r'(?<=[.!?])\s+|\n\n+', text)
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        return sentences if sentences else [text]

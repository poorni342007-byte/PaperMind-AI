def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> list[str]:
    """
    Splits a raw text string into segments of roughly `chunk_size` characters,
    overlapping adjacent chunks by `chunk_overlap` characters.
    Adjusts boundaries to split on whitespace to avoid cutting words in half.
    """
    chunks = []
    if not text:
        return chunks

    text_length = len(text)
    start = 0

    while start < text_length:
        # If the remaining text is smaller than the target chunk size, consume the rest
        if start + chunk_size >= text_length:
            chunks.append(text[start:].strip())
            break

        # Calculate initial target boundary
        end = start + chunk_size

        # Search backwards up to 120 characters to find a suitable separator
        search_limit = max(start, end - 120)
        split_point = end
        
        for idx in range(end - 1, search_limit, -1):
            if text[idx] in (' ', '\n', '\t', '.', ',', ';', '?'):
                # Found a boundary space or punctuation to split cleanly
                split_point = idx + 1
                break

        # Slice text content
        chunk = text[start:split_point]
        chunks.append(chunk.strip())

        # Slide starting position forward, subtracting overlap length
        start = split_point - chunk_overlap
        
        # Guard condition: ensure we always make progress to prevent infinite loops
        if start <= 0 or start >= split_point:
            start = split_point

    # Clean up empty chunks if any were generated
    return [c for c in chunks if len(c) > 0]

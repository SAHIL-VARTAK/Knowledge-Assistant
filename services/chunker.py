def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Prefer splitting at a newline
        if end < len(text):
            last_newline = text.rfind("\n", start, end)

            if last_newline != -1:
                end = last_newline

        chunks.append(text[start:end].strip())

        start = max(end - overlap, start + 1)

    return chunks

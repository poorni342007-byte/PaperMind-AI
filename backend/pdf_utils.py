import fitz

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from a PDF file using PyMuPDF (fitz).
    """
    print(f"[PDF Utils] Extracting text from: {file_path}")
    text_content = []
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content.append(page.get_text())
        doc.close()
    except Exception as e:
        print(f"Error during PDF text extraction: {e}")
    return "\n".join(text_content)

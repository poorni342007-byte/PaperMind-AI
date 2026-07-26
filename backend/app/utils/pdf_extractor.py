import fitz  # PyMuPDF library for advanced PDF processing

def extract_text_from_pdf(file_path: str) -> str:
    """
    Opens a PDF document and extracts plain text page by page.
    Combines text blocks and cleans basic spacing irregularities.
    """
    print(f"[PDF Extractor] Processing file at: {file_path}")
    extracted_text = ""
    
    try:
        # Open PDF file using PyMuPDF (fitz)
        doc = fitz.open(file_path)
        
        # Loop through pages index-by-index
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")  # Retrieve layout-preserved text blocks
            if page_text:
                extracted_text += f"\n--- Page {page_num + 1} ---\n"
                extracted_text += page_text
                
        doc.close()
    except Exception as e:
        print(f"[PDF Extractor Error] Failed to extract text from PDF: {e}")
        # Raise an exception to let the caller handle it gracefully
        raise RuntimeError(f"Failed to parse PDF document contents: {str(e)}")
        
    return extracted_text.strip()

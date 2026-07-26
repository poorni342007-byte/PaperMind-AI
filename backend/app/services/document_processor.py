import os
import re
import fitz
import google.generativeai as genai
from typing import List, Dict, Any

class DocumentProcessor:
    """
    Service responsible for extracting text page-by-page from PDF documents,
    preserving page numbers, cleaning extra whitespace, filtering empty content,
    and running Gemini Vision OCR fallback for image-based/scanned PDFs.
    """

    @staticmethod
    def extract_pages_from_pdf(file_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from PDF page by page using PyMuPDF (fitz).
        If a page has no text layer (scanned/image PDF), uses Gemini Vision OCR fallback.
        
        Returns a list of dictionaries with page numbers (1-indexed) and cleaned text.
        """
        print(f"[DocumentProcessor] Extracting structured page text from: {file_path}")
        pages = []

        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            print(f"[DocumentProcessor] PDF has {total_pages} total page(s)")

            for page_idx in range(total_pages):
                page = doc.load_page(page_idx)
                raw_text = page.get_text()

                # Clean text: replace multiple tabs/spaces with a single space
                cleaned_text = re.sub(r'[ \t]+', ' ', raw_text)
                cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text).strip()

                # If direct text extraction returned empty/negligible text, try OCR fallback
                if len(cleaned_text) < 15:
                    print(f"[DocumentProcessor] Page {page_idx+1} has little/no text layer. Attempting OCR fallback...")
                    ocr_text = DocumentProcessor._ocr_page_with_gemini(page)
                    if ocr_text:
                        cleaned_text = re.sub(r'[ \t]+', ' ', ocr_text)
                        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text).strip()
                        print(f"[DocumentProcessor] Page {page_idx+1} OCR succeeded! Extracted {len(cleaned_text)} chars.")

                if cleaned_text:
                    pages.append({
                        "page": page_idx + 1,  # 1-indexed page number
                        "text": cleaned_text
                    })

            doc.close()
            print(f"[DocumentProcessor] Extracted {len(pages)} non-empty page(s) out of {total_pages}")
        except Exception as e:
            print(f"[DocumentProcessor] Error extracting text from PDF {file_path}: {e}")
            raise RuntimeError(f"PDF extraction failed: {str(e)}")

        return pages

    @staticmethod
    def _ocr_page_with_gemini(page: fitz.Page) -> str:
        """
        Renders a PDF page to image and uses Gemini 2.5 Flash multimodal vision API
        to extract text from scanned/image-based PDF pages.
        """
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            print("[DocumentProcessor OCR] GEMINI_API_KEY not set; skipping OCR.")
            return ""

        try:
            genai.configure(api_key=api_key)
            # Render page to PNG pixmap
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")

            # Query Gemini Vision model
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content([
                {"mime_type": "image/png", "data": img_bytes},
                "Extract all text, headers, numbers, and instructions from this image page verbatim."
            ])

            return response.text.strip() if response and response.text else ""
        except Exception as err:
            print(f"[DocumentProcessor OCR Error] Failed to OCR page with Gemini: {err}")
            return ""

    @staticmethod
    def get_full_text(pages: List[Dict[str, Any]]) -> str:
        """
        Combines structured page objects back into full document text if needed.
        """
        return "\n\n".join([f"--- Page {p['page']} ---\n{p['text']}" for p in pages])

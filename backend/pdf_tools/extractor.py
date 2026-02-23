import pdfplumber
import pytesseract

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None
import os

def extract_text(pdf_path):
    """
    Extracts text from a PDF file.
    Uses pdfplumber for text-based PDFs and OCR for scanned PDFs.
    
    Args:
        pdf_path (str): Path to the PDF file.
        
    Returns:
        str: Extracted text.
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    # If text is too short, it might be scanned
    if len(text.strip()) < 50:
        print("Text too short, attempting OCR...")
        try:
            if convert_from_path:
                images = convert_from_path(pdf_path)
                for img in images:
                    text += pytesseract.image_to_string(img) + "\n"
            else:
                print("pdf2image not installed, skipping OCR")
        except Exception as e:
            print(f"OCR failed: {e}")
            
    return text

def split_text_into_chunks(text, max_chars_per_page=1500):
    """
    Splits text into chunks suitable for pages.
    """
    # Simple splitting for now
    # TODO: Respect paragraphs
    chunks = []
    current_chunk = ""
    
    for line in text.split('\n'):
        if len(current_chunk) + len(line) > max_chars_per_page:
            chunks.append(current_chunk)
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"
            
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

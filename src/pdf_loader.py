"""
PDF Loader Module
Handles PDF text extraction with scan detection and rejection.
"""

import pdfplumber
from typing import Tuple, Optional
import io


def extract_text_from_pdf(uploaded_file) -> Tuple[bool, str, Optional[str]]:
    """
    Extract text from a PDF file using pdfplumber.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Tuple of (success: bool, message: str, extracted_text: Optional[str])
        - If successful: (True, success_message, extracted_text)
        - If failed: (False, error_message, None)
    """
    try:
        # Read the file into a bytes buffer
        pdf_bytes = io.BytesIO(uploaded_file.read())
        
        with pdfplumber.open(pdf_bytes) as pdf:
            # Check if PDF has pages
            if len(pdf.pages) == 0:
                return (False, "❌ The PDF file appears to be empty.", None)
            
            extracted_text = []
            total_chars = 0
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                
                if page_text:
                    extracted_text.append(page_text)
                    total_chars += len(page_text.strip())
            
            # Join all extracted text
            full_text = "\n\n".join(extracted_text)
            
            # Scan Detection: Check if we extracted meaningful text
            # A scanned PDF typically yields very little or no text
            min_expected_chars = 100  # Minimum characters expected for a valid resume
            
            if total_chars < min_expected_chars:
                return (
                    False,
                    f"❌ **Scanned PDF Detected**\n\n"
                    f"This PDF appears to be a scanned image with minimal extractable text "
                    f"(only {total_chars} characters found).\n\n"
                    f"**Please upload a text-based PDF** that was created digitally "
                    f"(e.g., exported from Word, Google Docs, or a PDF editor).\n\n"
                    f"💡 *Tip: If you only have a scanned copy, use an OCR tool to convert it first.*",
                    None
                )
            
            # Success
            return (
                True,
                f"✅ Successfully extracted {total_chars:,} characters from {len(pdf.pages)} page(s).",
                full_text
            )
            
    except pdfplumber.pdfminer.pdfparser.PDFSyntaxError:
        return (
            False,
            "❌ **Invalid PDF Format**\n\nThe uploaded file is not a valid PDF or is corrupted.",
            None
        )
    except Exception as e:
        return (
            False,
            f"❌ **Error Processing PDF**\n\nAn unexpected error occurred: {str(e)}",
            None
        )


def get_pdf_info(uploaded_file) -> dict:
    """
    Get basic information about the PDF file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Dictionary with file information
    """
    try:
        pdf_bytes = io.BytesIO(uploaded_file.read())
        uploaded_file.seek(0)  # Reset file pointer
        
        with pdfplumber.open(pdf_bytes) as pdf:
            return {
                "filename": uploaded_file.name,
                "size_kb": round(len(uploaded_file.getvalue()) / 1024, 2),
                "pages": len(pdf.pages),
                "valid": True
            }
    except Exception:
        return {
            "filename": uploaded_file.name,
            "size_kb": round(len(uploaded_file.getvalue()) / 1024, 2),
            "pages": 0,
            "valid": False
        }

##File name: pdf_extraction.py

from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
import pytesseract

import logging_utils
from ocr_utils import perform_ocr_on_image
import logging

# Suppress lower-level logging messages from pytesseract
logging.getLogger('pytesseract').setLevel(logging.ERROR)

# If Tesseract is not in your system PATH, you can explicitly provide the path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# logger = logging_utils.setup_logger(f'logs/{__name__}.log')
logger = logging_utils.setup_logger(f'logs/main_log.log')

class PDFExtractionError(Exception):
    """Custom exception for handling PDF extraction errors."""
    pass

def extract_text_from_pdf(file_path):
    try:
        text = extract_text(file_path)
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}")
        raise PDFExtractionError(f"Error extracting text from PDF {file_path}")

def extract_text_from_pdf_with_ocr(file_path):
    try:
        # Explicitly provide the path to the Poppler binaries
        poppler_path = r"C:/Program Files/poppler-24.07.0/Library/bin"  # Update to your actual Poppler path
        #print(poppler_path) # debugging
        pages = convert_from_path(file_path, poppler_path=poppler_path)
        text = ""
        for page in pages:
            text += perform_ocr_on_image(page)  # Assuming perform_ocr_on_image uses Tesseract
        return text
    except Exception as e:
        logger.error(f"Error performing OCR on PDF {file_path}: {e}")
        raise PDFExtractionError(f"Error performing OCR on PDF {file_path}")

def get_text_from_pdf(file_path):
    try:
        text = extract_text_from_pdf(file_path)
        if not text.strip():
            # raise PDFExtractionError(f"No text found in PDF {file_path}, attempting Pure OCR...")
            logger.info(f"No text found in PDF {file_path}, attempting OCR...")
        ocr_text = extract_text_from_pdf_with_ocr(file_path)
        combined_text = text + "\n" + "OCR TEXT:" + "\n" + ocr_text
        return combined_text
    except Exception as e:
        logger.error(f"Error getting text from PDF {file_path}: {e}")
        raise PDFExtractionError(f"Error getting text from PDF {file_path}")
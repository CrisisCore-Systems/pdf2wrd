from typing import Optional, Callable, List, Dict
from dataclasses import dataclass, field
from pathlib import Path
import pytesseract
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from .exceptions import OCRError, FileAccessError
import tempfile
import shutil
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@dataclass
class ConversionProgress:
    """Represents conversion progress information."""
    current_page: int
    total_pages: int
    status: str

    @property
    def percentage(self) -> float:
        return (self.current_page / self.total_pages) * 100

class PDFConverter:
    """Handles PDF text extraction and OCR operations.
    
    Attributes:
        config: Application configuration for paths and settings
        
    Methods:
        extract_text: Primary method for text extraction with OCR fallback
        batch_convert: Process multiple PDF files in sequence
        _extract_text_direct: Direct text extraction from PDF
        _extract_text_ocr: OCR-based text extraction using Tesseract
    """
    
    def __init__(self, config: 'AppConfig'):
        self.config = config
        pytesseract.pytesseract.tesseract_cmd = config.get_tesseract_path()
        
    def batch_convert(self, pdf_files: List[Path]) -> Dict[Path, str]:
        """Convert multiple PDFs concurrently.
        
        Args:
            pdf_files: List of PDF file paths
            
        Returns:
            Dictionary mapping file paths to extracted text
        """
        results = {}
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.extract_text, pdf_file): pdf_file 
                for pdf_file in pdf_files
            }
            for future in futures:
                pdf_file = futures[future]
                try:
                    results[pdf_file] = future.result()
                except Exception as e:
                    logger.error(f"Failed to convert {pdf_file}: {e}")
                    results[pdf_file] = str(e)
        return results

    def extract_text(self, pdf_path: Path, callback: Optional[Callable[[ConversionProgress], None]] = None) -> str:
        """
        Extract text from PDF, falling back to OCR if needed.
        
        Args:
            pdf_path: Path to PDF file
            callback: Optional progress callback function
            
        Returns:
            Extracted text as string
        """
        logger.info(f"Starting text extraction for {pdf_path}")
        if not pdf_path.exists():
            raise FileAccessError(f"PDF file not found: {pdf_path}")
            
        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                text = self._extract_text_direct(reader, callback)
                
                if not text.strip():
                    text = self._extract_text_ocr(pdf_path, callback)
                    
                logger.info("Text extraction completed successfully")
                return text
                
        except Exception as e:
            logger.error(f"Text extraction failed: {e}", exc_info=True)
            raise OCRError(f"Failed to convert PDF: {str(e)}")

    def _extract_text_direct(self, reader: PdfReader, callback: Optional[Callable[[ConversionProgress], None]]) -> str:
        """Extract text directly from PDF."""
        text = ""
        total_pages = len(reader.pages)
        for i, page in enumerate(reader.pages):
            text += page.extract_text() or ""
            if callback:
                progress = ConversionProgress(current_page=i + 1, total_pages=total_pages, status="Extracting text")
                callback(progress)
        return text

    def _extract_text_ocr(self, pdf_path: Path, callback: Optional[Callable[[ConversionProgress], None]]) -> str:
        """OCR text extraction with memory optimization."""
        text = []
        with tempfile.TemporaryDirectory() as temp_dir:
            images = convert_from_path(
                pdf_path,
                output_folder=temp_dir,
                fmt='jpeg',
                thread_count=2
            )
            for i, image in enumerate(images):
                text.append(pytesseract.image_to_string(image))
                image.close()  # Release memory
                if callback:
                    callback(ConversionProgress(i + 1, len(images), "OCR Processing"))
        return "\n".join(text)

import pytest
from pathlib import Path
from src.converter import PDFConverter
from src.config import AppConfig
from src.exceptions import OCRError, FileAccessError

@pytest.fixture
def sample_pdf():
    return Path("tests/samples/sample.pdf")

@pytest.fixture
def scanned_pdf():
    return Path("tests/samples/scanned.pdf")
    
@pytest.fixture
def converter():
    config = AppConfig()
    return PDFConverter(config)

def test_pdf_text_extraction(converter, sample_pdf):
    text = converter.extract_text(sample_pdf)
    assert text is not None
    assert len(text) > 0
    
def test_invalid_pdf_path(converter):
    with pytest.raises(FileNotFoundError):
        converter.extract_text(Path("nonexistent.pdf"))

def test_ocr_conversion(converter, scanned_pdf):
    text = converter.extract_text_ocr(scanned_pdf)
    assert text is not None

def test_progress_callback(converter, sample_pdf):
    progress_called = False
    def callback(progress):
        nonlocal progress_called
        progress_called = True
    converter.extract_text(sample_pdf, callback=callback)
    assert progress_called

def test_invalid_pdf_raises_error(converter):
    with pytest.raises(FileAccessError):
        converter.extract_text(Path("nonexistent.pdf"))

def test_ocr_failure_raises_error(converter, sample_pdf):
    converter.config.tesseract_paths['nt'] = 'invalid'
    with pytest.raises(OCRError):
        converter.extract_text(sample_pdf)

def test_batch_conversion(converter, sample_pdf, scanned_pdf):
    results = converter.batch_convert([sample_pdf, scanned_pdf])
    assert len(results) == 2
    assert all(isinstance(r, str) for r in results)

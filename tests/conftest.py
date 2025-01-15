
import pytest
from pathlib import Path
from src.config import AppConfig
from src.converter import PDFConverter

@pytest.fixture
def config():
    return AppConfig()

@pytest.fixture
def converter(config):
    return PDFConverter(config)

@pytest.fixture
def sample_pdf():
    return Path('tests/samples/sample.pdf')
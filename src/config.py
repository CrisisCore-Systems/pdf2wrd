from dataclasses import dataclass
from pathlib import Path
import os
import json
from typing import Dict, Optional
from .exceptions import ConfigurationError

@dataclass
class AppConfig:
    """Application configuration settings."""
    tesseract_paths: Dict[str, str]
    temp_dir: Path
    
    def __init__(self):
        self.tesseract_paths = {
            'nt': os.getenv('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe'),
            'posix': '/usr/bin/tesseract'
        }
        self.temp_dir = Path(os.getenv('TEMP_DIR', 'temp'))
        self.validate()
    
    def get_tesseract_path(self) -> Optional[str]:
        return self.tesseract_paths.get(os.name)

    @classmethod
    def load_from_file(cls, config_path: Path) -> 'AppConfig':
        """Load configuration from JSON file."""
        with open(config_path) as f:
            config_data = json.load(f)
        return cls(**config_data)

    def save_to_file(self, config_path: Path) -> None:
        """Save current configuration to JSON file."""
        config_data = {
            'tesseract_paths': self.tesseract_paths,
            'temp_dir': str(self.temp_dir)
        }
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)

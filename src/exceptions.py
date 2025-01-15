class PDFConverterError(Exception):
    """Base exception for PDF converter errors"""
    pass

class OCRError(PDFConverterError):
    """Raised when OCR processing fails"""
    pass

class FileAccessError(PDFConverterError):
    """Raised when file operations fail"""
    pass

class ConfigurationError(PDFConverterError):
    """Raised when configuration is invalid"""
    pass

class OCRConfigError(ConfigurationError):
    """Raised when OCR configuration is invalid"""
    pass

class ConversionCancelledError(PDFConverterError):
    """Raised when conversion is cancelled by user"""
    pass

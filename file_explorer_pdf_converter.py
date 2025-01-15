import os
import tkinter as tk
from tkinter import ttk, messagebox
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

class Config:
    def __init__(self):
        self.tesseract_path = {
            'nt': r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            'posix': '/usr/bin/tesseract'
        }
    
    def get_tesseract_path(self):
        return self.tesseract_path.get(os.name)

class PDFConverterApp:
    """
    A GUI application for converting PDF files to text.
    Supports both text extraction and OCR capabilities.
    
    Attributes:
        root: The main tkinter window
        main_frame: The primary container frame
        text_area: Text widget for displaying converted content
    """
    def __init__(self, root):
        self.root = root
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.text_area = tk.Text(self.main_frame, wrap='word', height=20, width=80)
        self.text_area.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_frame, 
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

        config = Config()
        pytesseract.pytesseract.tesseract_cmd = config.get_tesseract_path()

    def convert_pdf_to_text(self, file_path):
        try:
            self.text_area.delete(1.0, tk.END)
            
            # First try normal PDF text extraction
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text = ""
                has_text = False
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text.strip():
                        has_text = True
                        text += f"\n=== Page {page_num + 1} ===\n\n"
                        text += page_text
                
                # If no text found, use OCR
                if not has_text:
                    self.text_area.insert(tk.END, "No embedded text found. Starting OCR process...\n")
                    self.root.update()
                    
                    # Convert PDF to images
                    images = convert_from_path(file_path)
                    text = ""
                    
                    for i, image in enumerate(images):
                        self.text_area.insert(tk.END, f"Processing page {i+1}...\n")
                        self.root.update()
                        
                        # Perform OCR
                        page_text = pytesseract.image_to_string(image)
                        text += f"\n=== Page {i + 1} ===\n\n"
                        text += page_text
                        self.progress_var.set((i + 1) / len(images) * 100)
                        self.root.update_idletasks()
                
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, text)
                    
        except FileNotFoundError:
            messagebox.showerror("Error", "PDF file not found")
        except PermissionError:
            messagebox.showerror("Error", "Permission denied accessing the PDF file")
        except ImportError as e:
            messagebox.showerror("Error", "Missing required library: " + str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")

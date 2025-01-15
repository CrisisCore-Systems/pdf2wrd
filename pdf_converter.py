import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from threading import Thread
import queue

class PDFConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced PDF Converter")
        self.root.geometry("1024x768")
        self.setup_ui()
        self.processing_queue = queue.Queue()
        
    def setup_ui(self):
        # Create main container with improved styling
        self.style = ttk.Style()
        self.style.configure('Custom.TFrame', background='#f0f0f0')
        self.main_frame = ttk.Frame(self.root, padding="10", style='Custom.TFrame')
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Toolbar frame
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Enhanced buttons
        self.browse_button = ttk.Button(self.toolbar, text="Open PDF", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = ttk.Button(self.toolbar, text="Save Text", command=self.save_text)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.ocr_var = tk.BooleanVar(value=True)
        self.ocr_check = ttk.Checkbutton(self.toolbar, text="Enable OCR", variable=self.ocr_var)
        self.ocr_check.pack(side=tk.LEFT, padx=5)
        
        # Progress indicators
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.main_frame, variable=self.progress_var, mode='determinate')
        self.progress.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Enhanced text display
        self.text_frame = ttk.Frame(self.main_frame)
        self.text_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.text_area = tk.Text(self.text_frame, wrap=tk.WORD, width=80, height=30,
                                font=('Segoe UI', 10))
        self.scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL, 
                                     command=self.text_area.yview)
        
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.text_area['yscrollcommand'] = self.scrollbar.set
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.rowconfigure(0, weight=1)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Select a PDF file"
        )
        if file_path:
            self.process_pdf(file_path)
    
    def process_pdf(self, file_path):
        def worker():
            try:
                self.status_var.set("Processing PDF...")
                self.progress_var.set(0)
                self.text_area.delete(1.0, tk.END)
                
                with open(file_path, 'rb') as file:
                    pdf_reader = PdfReader(file)
                    total_pages = len(pdf_reader.pages)
                    text = ""
                    has_text = False
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text().strip()
                        if page_text:
                            has_text = True
                            text += f"\n=== Page {page_num + 1} ===\n\n{page_text}\n"
                        self.progress_var.set((page_num + 1) / total_pages * 100)
                    
                    if not has_text and self.ocr_var.get():
                        self.status_var.set("Running OCR...")
                        images = convert_from_path(file_path)
                        text = ""
                        for i, image in enumerate(images):
                            page_text = pytesseract.image_to_string(image)
                            text += f"\n=== Page {i + 1} ===\n\n{page_text}\n"
                            self.progress_var.set((i + 1) / len(images) * 100)
                
                self.text_area.insert(tk.END, text)
                self.status_var.set("Conversion complete")
                
            except Exception as e:
                self.status_var.set(f"Error: {str(e)}")
                messagebox.showerror("Error", str(e))
            finally:
                self.progress_var.set(0)
        
        Thread(target=worker, daemon=True).start()
    
    def save_text(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save converted text"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.text_area.get(1.0, tk.END))
                self.status_var.set("Text saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFConverterApp(root)
    root.mainloop()

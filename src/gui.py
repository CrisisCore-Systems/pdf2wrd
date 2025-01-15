import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from src.converter import PDFConverter, ConversionProgress
from threading import Thread

class ConverterGUI:
    def __init__(self, converter: PDFConverter):
        self.root = tk.Tk()
        self.converter = converter
        self.cancel_flag = False
        self.setup_ui()
        
    def setup_ui(self):
        # Create modern styled UI
        style = ttk.Style()
        style.configure('Modern.TFrame', background='#f0f0f0')
        
        self.main_frame = ttk.Frame(self.root, padding="10", style='Modern.TFrame')
        self.main_frame.grid(sticky='nsew')
        
        # Add progress bar and status
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.main_frame, variable=self.progress_var)
        self.progress.grid(sticky='ew')
        
        self.cancel_button = ttk.Button(
            self.main_frame, 
            text="Cancel",
            command=self.cancel_conversion,
            state=tk.DISABLED
        )
        self.cancel_button.grid(sticky='ew')
        
        self.setup_export_menu()

    def create_widgets(self):
        self.file_label = tk.Label(self.root, text="Select PDF file:")
        self.file_label.pack()
        self.file_button = tk.Button(self.root, text="Browse", command=self.browse_file)
        self.file_button.pack()
        self.convert_button = tk.Button(self.root, text="Convert", command=self.convert_file)
        self.convert_button.pack()
        self.progress_label = tk.Label(self.root, text="")
        self.progress_label.pack()

    def browse_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.file_path:
            self.file_label.config(text=f"Selected file: {self.file_path}")

    def convert_file(self):
        self.cancel_flag = False
        self.cancel_button['state'] = tk.NORMAL
        try:
            def callback(progress):
                if self.cancel_flag:
                    raise InterruptedError("Conversion cancelled")
                self.update_progress(progress)
                
            Thread(target=lambda: self.converter.extract_text(
                self.file_path, callback
            )).start()
        finally:
            self.cancel_button['state'] = tk.DISABLED
            
    def cancel_conversion(self):
        self.cancel_flag = True

    def setup_export_menu(self):
        self.export_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.export_menu.add_command(label="Text File", command=self.export_text)
        self.export_menu.add_command(label="Word Document", command=self.export_word)

    def export_text(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.result_text.get(1.0, tk.END))

    def update_progress(self, progress: ConversionProgress):
        self.progress_label.config(text=f"Progress: {progress.percentage:.2f}% - {progress.status}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()

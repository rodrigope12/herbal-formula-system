import sys
import os

try:
    from pypdf import PdfReader
    print("Using pypdf")
except ImportError:
    try:
        import PyPDF2
        from PyPDF2 import PdfReader
        print("Using PyPDF2")
    except ImportError:
        print("No PDF library found. Please install pypdf or PyPDF2.")
        sys.exit(1)

def extract_text(pdf_path):
    print(f"--- Extracting from: {pdf_path} ---")
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

pdf_files = ["Project_Overview.pdf"]

with open("pdf_extracted.txt", "w", encoding="utf-8") as f:
    f.write("Using PyPDF2\n\n")
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            content = extract_text(pdf_file)
            f.write(content + "\n\n")
        else:
            print(f"File not found: {pdf_file}")

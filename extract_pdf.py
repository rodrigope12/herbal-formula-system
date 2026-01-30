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
    print(f"\n--- Extracting from: {os.path.basename(pdf_path)} ---")
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        print(text)
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")

files = [
    "/Users/rodrigoperezcordero/Documents/TRABAJO/RELATIVE DOSING LIMITS.pdf",
    "/Users/rodrigoperezcordero/Documents/TRABAJO/phase 2.pdf",
    "/Users/rodrigoperezcordero/Documents/TRABAJO/PLANT SCORING SYSTEM (1–10) - SROCK + PLANT SCORING SYSTEM (1–10) (1).pdf"
]

for f in files:
    if os.path.exists(f):
        extract_text(f)
    else:
        print(f"File not found: {f}")

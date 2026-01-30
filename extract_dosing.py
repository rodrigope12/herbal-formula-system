from pypdf import PdfReader
import sys

try:
    reader = PdfReader("/Users/rodrigoperezcordero/Documents/TRABAJO/RELATIVE DOSING LIMITS.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    print(text)
except Exception as e:
    print(e)

from pypdf import PdfReader

def load_pdf(file):
    reader = PdfReader(file)
    text = ""
    
    for i, page in enumerate(reader.pages):
        content = page.extract_text()
        if content:
            text += content
    
    return text
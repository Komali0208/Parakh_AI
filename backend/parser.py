import io
from fastapi import UploadFile, File, HTTPException, APIRouter
from docx import Document
import pdfplumber
from nltk.tokenize import sent_tokenize
import analyzer

router = APIRouter()

def extract_text_from_txt(file_bytes):
    return file_bytes.decode("utf-8", errors="ignore")

def extract_text_from_pdf(file_bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text

def extract_text_from_docx(file_bytes):
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename.lower()

    if filename.endswith(".txt"):
        raw_text = extract_text_from_txt(contents)
    elif filename.endswith(".pdf"):
        raw_text = extract_text_from_pdf(contents)
    elif filename.endswith(".docx"):
        raw_text = extract_text_from_docx(contents)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX, or TXT.")

    # Split into sentences
    sentences = sent_tokenize(raw_text)
    # Remove extremely short sentences
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    if not sentences:
        raise HTTPException(status_code=400, detail="No readable text found in file.")

    # Call internal analysis logic
    analysis_result = analyzer.analyze_sentences(sentences)

    return {"sentences": analysis_result}

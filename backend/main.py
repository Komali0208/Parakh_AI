from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import joblib
import numpy as np
import io
from datetime import datetime
import pdfplumber
from docx import Document
from nltk.tokenize import sent_tokenize

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    model = joblib.load('model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
except FileNotFoundError:
    raise RuntimeError("Run train.py first.")


class AnalyzeRequest(BaseModel):
    sentences: List[str]


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    results = []
    if not request.sentences:
        return results
    X_vec = vectorizer.transform(request.sentences)
    predictions = model.predict(X_vec)
    probabilities = model.predict_proba(X_vec)
    feature_names = vectorizer.get_feature_names_out()
    for i, sentence in enumerate(request.sentences):
        label = predictions[i]
        class_index = list(model.classes_).index(label)
        confidence = round(probabilities[i][class_index] * 100, 1)
        sent_vec = X_vec[i].toarray()[0]
        non_zero_indices = np.nonzero(sent_vec)[0]
        if len(non_zero_indices) == 0:
            keywords = []
        else:
            top_indices = non_zero_indices[np.argsort(sent_vec[non_zero_indices])][::-1]
            top_3_indices = top_indices[:3]
            keywords = [feature_names[idx] for idx in top_3_indices]
        results.append({
            "sentence": sentence,
            "label": str(label),
            "confidence": float(confidence),
            "keywords": keywords
        })
    return results


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename.lower()

    if filename.endswith(".txt"):
        raw_text = contents.decode("utf-8", errors="ignore")
    elif filename.endswith(".pdf"):
        raw_text = ""
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    raw_text += t + "\n"
    elif filename.endswith(".docx"):
        doc_obj = Document(io.BytesIO(contents))
        raw_text = "\n".join([p.text for p in doc_obj.paragraphs])
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Unsupported format. Use PDF, DOCX, or TXT.")

    sentences = sent_tokenize(raw_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if not sentences:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No readable text found.")

    results = []
    X_vec = vectorizer.transform(sentences)
    predictions = model.predict(X_vec)
    probabilities = model.predict_proba(X_vec)
    feature_names = vectorizer.get_feature_names_out()
    for i, sentence in enumerate(sentences):
        label = predictions[i]
        class_index = list(model.classes_).index(label)
        confidence = round(probabilities[i][class_index] * 100, 1)
        sent_vec = X_vec[i].toarray()[0]
        non_zero_indices = np.nonzero(sent_vec)[0]
        if len(non_zero_indices) == 0:
            keywords = []
        else:
            top_indices = non_zero_indices[np.argsort(sent_vec[non_zero_indices])][::-1]
            top_3_indices = top_indices[:3]
            keywords = [feature_names[idx] for idx in top_3_indices]
        results.append({
            "sentence": sentence,
            "label": str(label),
            "confidence": float(confidence),
            "keywords": keywords
        })
    return {"sentences": results}


class ReportRequest(BaseModel):
    results: List[dict]
    filename: str = "document"


@app.post("/report")
def generate_report(req: ReportRequest):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import cm

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('title', parent=styles['Title'], fontSize=20,
        textColor=colors.HexColor('#78350f'), spaceAfter=6)
    story.append(Paragraph("Parakh AI - Detection Report", title_style))
    story.append(Paragraph(
        f"File: {req.filename} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.5*cm))

    total = len(req.results)
    ai_count = sum(1 for r in req.results if r['label'] == 'AI')
    human_count = total - ai_count
    ai_pct = round((ai_count / total) * 100, 1) if total > 0 else 0

    summary_data = [
        ['Total Sentences', 'AI Generated', 'Human Written', 'AI Percentage'],
        [str(total), str(ai_count), str(human_count), f"{ai_pct}%"]
    ]
    summary_table = Table(summary_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#78350f')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#fef3c7'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d6d3d1')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5*cm))

    h2_style = ParagraphStyle('h2', parent=styles['Heading2'],
        textColor=colors.HexColor('#78350f'))
    story.append(Paragraph("Sentence-by-Sentence Breakdown", h2_style))
    story.append(Spacer(1, 0.3*cm))

    for i, r in enumerate(req.results):
        is_ai = r['label'] == 'AI'
        bg = colors.HexColor('#fee2e2') if is_ai else colors.HexColor('#dcfce7')
        sentence_text = r['sentence'][:200] + '...' if len(r['sentence']) > 200 else r['sentence']
        keywords_text = ', '.join(r.get('keywords', [])) or 'none'
        label_color = 'red' if is_ai else 'green'
        row_data = [[
            Paragraph(f"<b>#{i+1}</b>", styles['Normal']),
            Paragraph(sentence_text, styles['Normal']),
            Paragraph(f"<font color='{label_color}'><b>{r['label']}</b></font>", styles['Normal']),
            Paragraph(f"{r['confidence']}%", styles['Normal']),
            Paragraph(keywords_text, styles['Normal'])
        ]]
        t = Table(row_data, colWidths=[1*cm, 8*cm, 2*cm, 2*cm, 4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.15*cm))

    story.append(Spacer(1, 0.5*cm))
    disclaimer_style = ParagraphStyle('disclaimer', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#78716c'))
    story.append(Paragraph(
        "* Parakh AI uses TF-IDF + Logistic Regression. Results are indicative and not final judgment.",
        disclaimer_style
    ))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Parakh_Report.pdf"}
    )


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

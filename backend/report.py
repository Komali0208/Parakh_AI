import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

router = APIRouter()

class ReportItem(BaseModel):
    sentence: str
    label: str
    confidence: float
    keywords: List[str]

class ReportRequest(BaseModel):
    results: List[ReportItem]

@router.post("/generate-report")
def generate_report(req: ReportRequest):
    if not req.results:
        raise HTTPException(status_code=400, detail="No results provided")

    total_sentences = len(req.results)
    ai_sentences = sum(1 for r in req.results if r.label == "AI")
    overall_score = (ai_sentences / total_sentences * 100) if total_sentences > 0 else 0

    pdf_path = "report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Parakh - AI Content Analysis Report")

    c.setFont("Helvetica", 14)
    c.drawString(50, height - 90, f"Overall AI Score: {overall_score:.2f}%")

    if overall_score > 50:
        recommendation = "Recommendation: This document shows significant AI involvement."
        c.setFillColor(colors.red)
    else:
        recommendation = "Recommendation: This document appears to be mostly Human-written."
        c.setFillColor(colors.green)

    c.drawString(50, height - 120, recommendation)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 160, "Sentence Breakdown:")

    # Top Keywords
    all_keywords = []
    for r in req.results:
        if r.label == "AI":
            all_keywords.extend(r.keywords)
    top_keywords = list(set(all_keywords))[:10]

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 190, f"Top AI Keywords Detected: {', '.join(top_keywords)}")

    y_pos = height - 230
    c.setFont("Helvetica", 10)
    for res in req.results:
        if y_pos < 50:
            c.showPage()
            y_pos = height - 50
            c.setFont("Helvetica", 10)

        color_str = "RED" if res.label == "AI" else "GREEN"
        text = f"[{color_str} {res.confidence}%] {res.sentence[:80]}..."
        c.drawString(50, y_pos, text)
        y_pos -= 20

    c.save()

    return FileResponse(path=pdf_path, filename="AI_Analysis_Report.pdf", media_type="application/pdf")

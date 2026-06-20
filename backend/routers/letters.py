import os
from io import BytesIO
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, Any

from explainability.reason_codes import generate_reason_codes
from explainability.letter_generator import generate_letter

router = APIRouter(prefix="/letters", tags=["Decision Letters"])

class LetterRequest(BaseModel):
    applicant_name: str
    decision: str
    final_score: int
    shap_values: Dict[str, float]
    feature_values: Dict[str, Any]

@router.post("/generate")
async def generate_letter_endpoint(req: LetterRequest):
    """
    Generates a human-readable decision letter based on SHAP values.
    """
    try:
        reason_codes = generate_reason_codes(req.shap_values, req.feature_values, req.decision)
        letter = generate_letter(
            applicant_name=req.applicant_name,
            decision=req.decision,
            final_score=req.final_score,
            reason_codes=reason_codes,
            application_date=datetime.now().strftime("%B %d, %Y")
        )
        return letter
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate letter: {str(e)}")

@router.post("/generate-pdf")
async def generate_pdf_endpoint(req: LetterRequest):
    """
    Generates a decision letter and returns it as a PDF.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        # Get letter text
        reason_codes = generate_reason_codes(req.shap_values, req.feature_values, req.decision)
        letter_data = generate_letter(
            applicant_name=req.applicant_name,
            decision=req.decision,
            final_score=req.final_score,
            reason_codes=reason_codes,
            application_date=datetime.now().strftime("%B %d, %Y")
        )
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(name='CustomNormal', parent=styles['Normal'], fontSize=11, spaceAfter=12))
        
        flowables = []
        
        # Header text
        flowables.append(Paragraph("<b>ScoreSeva — Decision Notice</b>", styles['Heading2']))
        
        # Split text into paragraphs
        paragraphs = letter_data["letter_text"].split("\n")
        
        for p in paragraphs:
            # Skip the plain text header since we added a styled one
            if "ScoreSeva — Decision Notice" in p:
                continue
            if not p.strip():
                continue
            
            flowables.append(Paragraph(p.replace("\n", "<br />"), styles['CustomNormal']))
            
        # Optional: Add technical appendix to PDF? 
        # The prompt says: "(the raw data, separate from the customer-facing letter)"
        # So we won't add it to the main PDF flow, or maybe as an appendix page if needed.
            
        doc.build(flowables)
        
        buffer.seek(0)
        return Response(content=buffer.getvalue(), media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename=ScoreSeva_Notice_{req.applicant_name.replace(' ', '_')}.pdf"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

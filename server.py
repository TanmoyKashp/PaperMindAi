"""FastAPI Application Server for PaperMind AI.

Exposes RESTful endpoints connecting the React frontend to the core NLP modules:
- PDF upload, validation & text extraction (PyMuPDF)
- NLP linguistic statistics (NLTK)
- Structured AI research analysis (Gemini API & Pydantic)
- Document-grounded conversational Q&A
- Markdown report generation & download
"""

import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, File, HTTPException, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from modules.pdf_processor import PDFProcessor, PDFProcessingResult
from modules.text_preprocessor import TextPreprocessor, TextStatistics
from modules.gemini_client import (
    GeminiClient,
    GeminiAPIError,
    GeminiAPIKeyError,
    GeminiQuotaError,
)
from modules.paper_analyzer import PaperAnalyzer, PaperAnalysisResult
from modules.qa_engine import QAEngine
from modules.report_generator import ReportGenerator
from utils.helpers import get_api_key, load_config

# Initialize FastAPI
app = FastAPI(
    title="PaperMind AI API",
    description="Backend API powering PaperMind AI Research Intelligence Assistant",
    version="1.0.0",
)

# Enable CORS for local Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration and service singletons
config = load_config()
app_cfg = config.get("app", {})
model_cfg = config.get("model", {})
max_file_mb = app_cfg.get("max_file_size_mb", 20)

preprocessor = TextPreprocessor()
pdf_processor = PDFProcessor(
    min_text_chars=config.get("nlp", {}).get("min_extracted_text_chars", 100),
    max_size_mb=max_file_mb,
)

gemini_client = GeminiClient(api_key=get_api_key(), model_name=model_cfg.get("name", "gemini-2.5-flash"))
analyzer = PaperAnalyzer(gemini_client=gemini_client)
qa_engine = QAEngine(gemini_client=gemini_client, text_preprocessor=preprocessor)

# In-memory document storage for active user sessions
DOCUMENTS: Dict[str, Dict[str, Any]] = {}
ACTIVE_DOC_ID: Optional[str] = None


# Request Models
class APIKeyRequest(BaseModel):
    api_key: str


class AnalyzeRequest(BaseModel):
    doc_id: str


class ChatRequest(BaseModel):
    doc_id: str
    question: str


# Endpoints
@app.get("/api/config")
def get_configuration():
    """Return system configuration and current API key status."""
    return {
        "app_name": app_cfg.get("name", "PaperMind AI"),
        "version": app_cfg.get("version", "1.0.0"),
        "model_name": gemini_client.model_name,
        "max_file_size_mb": max_file_mb,
        "is_api_configured": gemini_client.is_configured(),
        "has_active_doc": bool(ACTIVE_DOC_ID and ACTIVE_DOC_ID in DOCUMENTS),
        "active_doc_id": ACTIVE_DOC_ID,
    }


@app.post("/api/config/api-key")
def update_api_key(req: APIKeyRequest):
    """Update active Gemini API key in-memory."""
    key = req.api_key.strip()
    gemini_client.update_api_key(key)
    ok, msg = gemini_client.test_connection()
    return {
        "success": ok,
        "message": msg,
        "is_configured": gemini_client.is_configured(),
    }


@app.post("/api/config/test-connection")
def test_connection():
    """Verify Gemini API connection."""
    ok, msg = gemini_client.test_connection()
    return {"success": ok, "message": msg}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process academic PDF document."""
    global ACTIVE_DOC_ID

    contents = await file.read()
    filename = file.filename or "uploaded_paper.pdf"

    # Process PDF
    res: PDFProcessingResult = pdf_processor.extract_from_bytes(contents, filename=filename)

    if not res.success:
        raise HTTPException(
            status_code=400,
            detail={
                "message": res.error_message or "Failed to extract text from PDF.",
                "is_scanned": res.is_scanned_or_empty,
            },
        )

    # Calculate NLP statistics
    stats: TextStatistics = preprocessor.compute_statistics(res.full_text)

    # Store in session state
    doc_id = str(uuid.uuid4())
    doc_data = {
        "doc_id": doc_id,
        "filename": filename,
        "page_count": res.page_count,
        "full_text": res.full_text,
        "total_words": res.total_words,
        "total_characters": res.total_characters,
        "stats": {
            "character_count": stats.character_count,
            "character_count_no_spaces": stats.character_count_no_spaces,
            "word_count": stats.word_count,
            "sentence_count": stats.sentence_count,
            "paragraph_count": stats.paragraph_count,
            "vocabulary_size": stats.vocabulary_size,
            "avg_word_length": stats.avg_word_length,
            "avg_sentence_length_words": stats.avg_sentence_length_words,
            "estimated_reading_time_minutes": stats.estimated_reading_time_minutes,
        },
        "raw_stats_obj": stats,
        "analysis": None,
        "chat_history": [],
    }

    DOCUMENTS[doc_id] = doc_data
    ACTIVE_DOC_ID = doc_id

    return {
        "success": True,
        "doc_id": doc_id,
        "filename": filename,
        "page_count": res.page_count,
        "total_words": res.total_words,
        "stats": doc_data["stats"],
    }


@app.get("/api/document/{doc_id}")
def get_document(doc_id: str):
    """Retrieve metadata, current analysis, and chat history for a document."""
    if doc_id not in DOCUMENTS:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc = DOCUMENTS[doc_id]
    return {
        "doc_id": doc["doc_id"],
        "filename": doc["filename"],
        "page_count": doc["page_count"],
        "total_words": doc["total_words"],
        "stats": doc["stats"],
        "analysis": doc["analysis"].model_dump() if doc["analysis"] else None,
        "chat_history": doc["chat_history"],
    }


@app.post("/api/analyze")
def analyze_document(req: AnalyzeRequest):
    """Perform structured academic paper analysis via Gemini API."""
    if req.doc_id not in DOCUMENTS:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc = DOCUMENTS[req.doc_id]

    if not gemini_client.is_configured():
        raise HTTPException(
            status_code=400,
            detail="Gemini API key is not configured. Please add it to .env or settings.",
        )

    try:
        analysis: PaperAnalysisResult = analyzer.analyze_paper(doc["full_text"])
        doc["analysis"] = analysis
        return {"success": True, "analysis": analysis.model_dump()}
    except GeminiAPIKeyError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except GeminiQuotaError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/chat")
def chat_with_document(req: ChatRequest):
    """Ask a question grounded in the current uploaded research paper."""
    if req.doc_id not in DOCUMENTS:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc = DOCUMENTS[req.doc_id]

    if not gemini_client.is_configured():
        raise HTTPException(
            status_code=400,
            detail="Gemini API key is not configured. Please add it to .env or settings.",
        )

    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # User message
        doc["chat_history"].append({"role": "user", "content": question})

        # Answer question
        answer = qa_engine.answer_question(
            question=question,
            full_document_text=doc["full_text"],
            chat_history=doc["chat_history"][:-1],
        )

        doc["chat_history"].append({"role": "assistant", "content": answer})

        return {
            "success": True,
            "answer": answer,
            "chat_history": doc["chat_history"],
        }
    except GeminiAPIKeyError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except GeminiQuotaError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Q&A failed: {str(e)}")


@app.post("/api/chat/clear")
def clear_chat(req: AnalyzeRequest):
    """Clear conversation history for a document."""
    if req.doc_id in DOCUMENTS:
        DOCUMENTS[req.doc_id]["chat_history"] = []
    return {"success": True}


@app.get("/api/report/download")
def download_report(doc_id: str = Query(...)):
    """Generate and download Markdown report."""
    if doc_id not in DOCUMENTS:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc = DOCUMENTS[doc_id]
    if not doc["analysis"]:
        raise HTTPException(
            status_code=400,
            detail="Document has not been analyzed yet. Run analysis first.",
        )

    report_md = ReportGenerator.generate_markdown_report(
        analysis=doc["analysis"],
        filename=doc["filename"],
        stats=doc.get("raw_stats_obj"),
        page_count=doc["page_count"],
    )

    base_name = os.path.splitext(doc["filename"])[0]
    download_filename = f"{base_name}_papermind_report.md"

    return Response(
        content=report_md,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{download_filename}"'
        },
    )


@app.post("/api/reset")
def reset_workspace():
    """Reset current workspace state."""
    global ACTIVE_DOC_ID
    ACTIVE_DOC_ID = None
    DOCUMENTS.clear()
    return {"success": True}


# Mount built frontend if available
dist_path = Path(__file__).parent / "frontend" / "dist"
if dist_path.exists():
    app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

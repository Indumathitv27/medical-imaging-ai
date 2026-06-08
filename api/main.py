import os
import sys
import uuid
import shutil
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.ingest import ingest_scan
from cv_model.predict import run_inference
from agent.report_agent import generate_report
from project_config import RAW_DATA_DIR, LOGS_DIR

# ── Logging setup ──────────────────────────────────────────
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "api.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ── FastAPI app ────────────────────────────────────────────
app = FastAPI(
    title="Medical Imaging AI API",
    description="Chest X-ray analysis with AI anomaly detection and report generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ── Health check endpoint ──────────────────────────────────
@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": "Medical Imaging AI",
        "version": "1.0.0"
    }


# ── Main analyze endpoint ──────────────────────────────────
@app.post("/analyze")
async def analyze_scan(file: UploadFile = File(...)):
    """
    Accepts a chest X-ray image, runs the full pipeline:
    1. Ingestion — validate and store
    2. CV model — detect anomalies
    3. LLM agent — generate report
    Returns structured findings and radiology report.
    """
    logger.info(f"Received upload: {file.filename}")

    # Step 1 — save uploaded file temporarily
    temp_path = os.path.join(RAW_DATA_DIR, f"temp_{uuid.uuid4()}{os.path.splitext(file.filename)[1]}")
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

    # Step 2 — ingest
    ingest_result = ingest_scan(temp_path, file.filename)
    if ingest_result["status"] == "rejected":
        os.remove(temp_path)
        raise HTTPException(status_code=400, detail=ingest_result["reason"])

    scan_id = ingest_result["scan_id"]
    stored_path = ingest_result["stored_path"]

    # remove temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)

    # Step 3 — run CV model inference
    inference_result = run_inference(stored_path)
    if inference_result["status"] == "error":
        raise HTTPException(status_code=500, detail=inference_result["reason"])

    # Step 4 — generate LLM report
    report_result = generate_report(scan_id, inference_result)

    # Step 5 — return full result
    logger.info(f"Pipeline complete for scan_id={scan_id}")

    return {
        "scan_id": scan_id,
        "filename": file.filename,
        "ingested_at": ingest_result["ingested_at"],
        "total_findings": inference_result["total_findings"],
        "critical_findings": inference_result["critical_findings"],
        "top_findings": inference_result["all_findings"][:10],
        "report": report_result["report"],
        "report_status": report_result["status"],
        "model_used": report_result.get("model_used", "llama-3.3-70b-versatile")
    }
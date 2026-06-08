import os
import uuid
import shutil
import logging
from datetime import datetime
from pathlib import Path
from PIL import Image

from project_config import RAW_DATA_DIR, LOGS_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB

# ── Logging setup ──────────────────────────────────────────
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "ingestion.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


# ── Helper functions ───────────────────────────────────────
def validate_extension(filename: str) -> bool:
    """Check if file extension is allowed."""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def validate_file_size(file_path: str) -> bool:
    """Check if file size is within limit."""
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    return size_mb <= MAX_FILE_SIZE_MB


def validate_image(file_path: str) -> bool:
    """Check if file is a valid readable image."""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False


# ── Main ingestion function ────────────────────────────────
def ingest_scan(source_path: str, original_filename: str) -> dict:
    """
    Validates and stores an incoming scan.
    Returns a result dict with scan_id and status.
    """
    # Step 1 — validate extension
    if not validate_extension(original_filename):
        logger.warning(f"Rejected {original_filename} — invalid extension")
        return {
            "status": "rejected",
            "reason": f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}",
            "scan_id": None
        }

    # Step 2 — validate file size
    if not validate_file_size(source_path):
        logger.warning(f"Rejected {original_filename} — exceeds size limit")
        return {
            "status": "rejected",
            "reason": f"File exceeds {MAX_FILE_SIZE_MB}MB limit",
            "scan_id": None
        }

    # Step 3 — validate image integrity
    if not validate_image(source_path):
        logger.warning(f"Rejected {original_filename} — corrupt or unreadable image")
        return {
            "status": "rejected",
            "reason": "File is corrupt or not a valid image",
            "scan_id": None
        }

    # Step 4 — generate unique scan ID
    scan_id = str(uuid.uuid4())
    ext = Path(original_filename).suffix.lower()
    stored_filename = f"{scan_id}{ext}"

    # Step 5 — store in raw data directory
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    destination = os.path.join(RAW_DATA_DIR, stored_filename)
    shutil.copy2(source_path, destination)

    # Step 6 — log the successful ingestion
    logger.info(f"Ingested | scan_id={scan_id} | original={original_filename} | stored={stored_filename}")

    return {
        "status": "success",
        "scan_id": scan_id,
        "stored_path": destination,
        "original_filename": original_filename,
        "ingested_at": datetime.utcnow().isoformat()
    }
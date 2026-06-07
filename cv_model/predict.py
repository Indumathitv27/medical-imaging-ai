import os
import numpy as np
import torch
import torchxrayvision as xrv
import skimage.io
import skimage.transform
import logging

from project_config import RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR

# ── Logging setup ──────────────────────────────────────────
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "model.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ── Load model once at startup ─────────────────────────────
print("Loading chest X-ray model...")
model = xrv.models.DenseNet(weights="densenet121-res224-all")
model.eval()
print("Model loaded successfully.")


# ── Image preprocessing ────────────────────────────────────
def preprocess_image(image_path: str) -> torch.Tensor:
    """
    Loads and preprocesses a chest X-ray image for model inference.
    - Converts to grayscale
    - Resizes to 224x224
    - Normalizes pixel values
    """
    # Load image
    img = skimage.io.imread(image_path)

    # Convert to grayscale if RGB
    if len(img.shape) == 3:
        img = img.mean(axis=2)

    # Resize to 224x224
    img = skimage.transform.resize(img, (224, 224))

    # Normalize to [-1024, 1024] range expected by TorchXRayVision
    img = xrv.datasets.normalize(img, maxval=255, reshape=True)

    # Convert to tensor and add batch dimension
    img_tensor = torch.from_numpy(img).unsqueeze(0).float()

    return img_tensor


# ── Run inference ──────────────────────────────────────────
def run_inference(image_path: str) -> dict:
    """
    Runs the chest X-ray model on a given image.
    Returns structured findings with confidence scores.
    """
    logger.info(f"Running inference on: {image_path}")

    # Step 1 — preprocess
    try:
        img_tensor = preprocess_image(image_path)
    except Exception as e:
        logger.error(f"Preprocessing failed for {image_path}: {e}")
        return {"status": "error", "reason": str(e), "findings": []}

    # Step 2 — run model
    with torch.no_grad():
        outputs = model(img_tensor)

    # Step 3 — map scores to pathology names
    scores = outputs[0].detach().numpy()
    pathologies = model.pathologies

    # Step 4 — build findings list
    findings = []
    for pathology, score in zip(pathologies, scores):
        findings.append({
            "pathology": pathology,
            "confidence": round(float(score), 4)
        })

    # Step 5 — sort by confidence descending
    findings = sorted(findings, key=lambda x: x["confidence"], reverse=True)

    # Step 6 — flag critical findings (confidence > 0.5)
    critical = [f for f in findings if f["confidence"] > 0.5]

    logger.info(f"Inference complete | findings={len(findings)} | critical={len(critical)}")

    return {
        "status": "success",
        "image_path": image_path,
        "total_findings": len(findings),
        "critical_findings": critical,
        "all_findings": findings
    }
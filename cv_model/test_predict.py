import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cv_model.predict import run_inference
from project_config import RAW_DATA_DIR

# ── Find the test image we ingested in Stage 2 ────────────
print("=" * 50)
print("TEST: Running chest X-ray inference")
print("=" * 50)

# Get the first image in data/raw/
images = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith((".jpg", ".jpeg", ".png"))]

if not images:
    print("⚠️  No images found in data/raw/")
    print("Please make sure Stage 2 ran successfully")
else:
    test_image = os.path.join(RAW_DATA_DIR, images[0])
    print(f"Using image: {images[0]}")
    print()

    result = run_inference(test_image)

    print(f"Status          : {result['status']}")
    print(f"Total findings  : {result['total_findings']}")
    print()

    print("Critical findings (confidence > 0.5):")
    if result['critical_findings']:
        for f in result['critical_findings']:
            print(f"  {f['pathology']:<30} {f['confidence']:.4f}")
    else:
        print("  None above 0.5 threshold")

    print()
    print("Top 5 findings:")
    for f in result['all_findings'][:5]:
        print(f"  {f['pathology']:<30} {f['confidence']:.4f}")
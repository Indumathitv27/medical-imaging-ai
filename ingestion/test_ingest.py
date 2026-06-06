import sys
import os

# Make sure Python can find config.py in the root folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.ingest import ingest_scan

# ── Test 1: Valid image ────────────────────────────────────
print("=" * 50)
print("TEST 1: Valid image")
print("=" * 50)

# We need a real image to test with
# Download any chest xray image and put it in data/raw temporarily
# OR use any .jpg image you have on your machine for now

test_image_path = "data/raw/test_sample.jpg"  # change this to any image path on your machine

if not os.path.exists(test_image_path):
    print(f"⚠️  No test image found at {test_image_path}")
    print("Please add any .jpg image at that path and run again")
else:
    result = ingest_scan(test_image_path, "test_sample.jpg")
    print(f"Status  : {result['status']}")
    print(f"Scan ID : {result['scan_id']}")
    print(f"Stored  : {result.get('stored_path')}")
    print(f"Time    : {result.get('ingested_at')}")

# ── Test 2: Invalid extension ──────────────────────────────
print()
print("=" * 50)
print("TEST 2: Invalid extension (.pdf)")
print("=" * 50)

result2 = ingest_scan("some_file.pdf", "some_file.pdf")
print(f"Status : {result2['status']}")
print(f"Reason : {result2['reason']}")
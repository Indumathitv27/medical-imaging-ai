import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.report_agent import generate_report

# ── Simulate inference result from Stage 3 ─────────────────
print("=" * 50)
print("TEST: Generating radiology report")
print("=" * 50)

# Simulated findings — same structure Stage 3 returns
mock_inference_result = {
    "status": "success",
    "total_findings": 18,
    "critical_findings": [
        {"pathology": "Edema", "confidence": 0.7591},
        {"pathology": "Lung Opacity", "confidence": 0.7336},
        {"pathology": "Effusion", "confidence": 0.7265},
        {"pathology": "Atelectasis", "confidence": 0.7135},
        {"pathology": "Consolidation", "confidence": 0.6455},
        {"pathology": "Cardiomegaly", "confidence": 0.6370},
        {"pathology": "Pneumonia", "confidence": 0.6084},
    ],
    "all_findings": [
        {"pathology": "Edema", "confidence": 0.7591},
        {"pathology": "Lung Opacity", "confidence": 0.7336},
        {"pathology": "Effusion", "confidence": 0.7265},
        {"pathology": "Atelectasis", "confidence": 0.7135},
        {"pathology": "Consolidation", "confidence": 0.6455},
        {"pathology": "Cardiomegaly", "confidence": 0.6370},
        {"pathology": "Pneumonia", "confidence": 0.6084},
        {"pathology": "Enlarged Cardiomediastinum", "confidence": 0.5797},
        {"pathology": "Fracture", "confidence": 0.5622},
        {"pathology": "Emphysema", "confidence": 0.5354},
    ]
}

mock_scan_id = "0fca5f0b-c489-43b8-b327-0aa0a4424e5c"

# ── Run report generation ──────────────────────────────────
result = generate_report(mock_scan_id, mock_inference_result)

print(f"Status  : {result['status']}")
print(f"Scan ID : {result['scan_id']}")

if result['status'] == 'error':
    print(f"Error   : {result['reason']}")
else:
    print(f"Model   : {result['model_used']}")
    print()
    print("=" * 50)
    print("GENERATED RADIOLOGY REPORT")
    print("=" * 50)
    print(result["report"])
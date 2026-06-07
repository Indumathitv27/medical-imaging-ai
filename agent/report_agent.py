import os
import logging
from groq import Groq
from dotenv import load_dotenv

from project_config import LOGS_DIR

# ── Load environment variables ─────────────────────────────
load_dotenv()

# ── Logging setup ──────────────────────────────────────────
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "agent.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ── Groq client ────────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ── Format findings for the prompt ────────────────────────
def format_findings(findings: list) -> str:
    """
    Converts the findings list into a readable string
    for the LLM prompt.
    """
    lines = []
    for f in findings:
        confidence_pct = round(f["confidence"] * 100, 1)
        lines.append(f"  - {f['pathology']}: {confidence_pct}% confidence")
    return "\n".join(lines)


# ── Build the prompt ───────────────────────────────────────
def build_prompt(scan_id: str, findings: list, critical_findings: list) -> str:
    """
    Builds the clinical prompt sent to the LLM agent.
    """
    all_findings_text = format_findings(findings[:10])  # top 10
    critical_text = format_findings(critical_findings) if critical_findings else "  None"

    prompt = f"""You are an expert radiologist AI assistant. 
A chest X-ray scan has been analyzed by a computer vision model.
Your job is to draft a structured radiology report based on the findings.

SCAN ID: {scan_id}

CRITICAL FINDINGS (confidence > 50%):
{critical_text}

TOP 10 MODEL FINDINGS:
{all_findings_text}

Write a structured radiology report with the following sections:
1. CLINICAL INDICATION
2. TECHNIQUE
3. FINDINGS
4. IMPRESSION
5. RECOMMENDATIONS

Important rules:
- Only include findings with meaningful confidence scores
- Use professional radiology language
- Be specific about severity based on confidence levels
- High confidence (>70%) = highly suspicious
- Medium confidence (50-70%) = moderate suspicion, correlate clinically
- Always end with a note that this is an AI-generated draft pending radiologist review
- Keep the report concise and clinically actionable"""

    return prompt


# ── Main report generation function ───────────────────────
def generate_report(scan_id: str, inference_result: dict) -> dict:
    """
    Takes inference results from Stage 3 and generates
    a structured radiology report using the LLM agent.
    """
    logger.info(f"Generating report for scan_id={scan_id}")

    findings = inference_result.get("all_findings", [])
    critical_findings = inference_result.get("critical_findings", [])

    # Step 1 — build prompt
    prompt = build_prompt(scan_id, findings, critical_findings)

    # Step 2 — call Groq LLM
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert radiologist AI assistant that drafts structured radiology reports. Always be precise, clinical, and professional."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )

        report_text = response.choices[0].message.content

        logger.info(f"Report generated successfully for scan_id={scan_id}")

        return {
            "status": "success",
            "scan_id": scan_id,
            "report": report_text,
            "model_used": "llama-3.3-70b-versatile",
            "critical_findings_count": len(critical_findings)
        }

    except Exception as e:
        logger.error(f"Report generation failed for scan_id={scan_id}: {e}")
        return {
            "status": "error",
            "scan_id": scan_id,
            "report": None,
            "reason": str(e)
        }
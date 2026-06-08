import streamlit as st
import requests
import os

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="Medical Imaging AI",
    page_icon="🏥",
    layout="wide"
)

# ── Header ─────────────────────────────────────────────────
st.title("🏥 Medical Imaging AI System")
st.markdown("Upload a chest X-ray to receive AI-powered anomaly detection and a radiology report draft.")
st.divider()

# ── API URL ────────────────────────────────────────────────
API_URL = "http://localhost:8000"

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This system analyzes chest X-rays using:
    - **DenseNet121** pretrained CV model
    - **Llama 3.3 70B** LLM for report generation
    - Detects **18 pathologies**
    """)
    st.divider()
    st.markdown("⚠️ For research use only. Not for clinical diagnosis.")

# ── File upload ────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Upload Scan")
    uploaded_file = st.file_uploader(
        "Choose a chest X-ray image",
        type=["jpg", "jpeg", "png"],
        help="Upload a chest X-ray in JPG or PNG format"
    )

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Scan", width=400)

    analyze_btn = st.button(
        "🔍 Analyze Scan",
        disabled=uploaded_file is None,
        type="primary",
        use_container_width=True
    )

# ── Results ────────────────────────────────────────────────
with col2:
    st.subheader("Results")

    if analyze_btn and uploaded_file:
        with st.spinner("Running AI analysis... this may take 30-60 seconds"):
            try:
                # Call FastAPI backend
                response = requests.post(
                    f"{API_URL}/analyze",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "image/jpeg")}
                )

                if response.status_code == 200:
                    result = response.json()

                    # Scan ID
                    st.success(f"✅ Analysis complete")
                    st.caption(f"Scan ID: `{result['scan_id']}`")

                    # Critical findings
                    st.markdown("### 🚨 Critical Findings")
                    if result["critical_findings"]:
                        for f in result["critical_findings"]:
                            confidence_pct = round(f["confidence"] * 100, 1)
                            color = "🔴" if f["confidence"] > 0.7 else "🟡"
                            st.markdown(f"{color} **{f['pathology']}** — {confidence_pct}% confidence")
                    else:
                        st.success("No critical findings detected")

                    st.divider()

                    # Top findings table
                    st.markdown("### 📊 All Findings")
                    findings_data = {
                        "Pathology": [f["pathology"] for f in result["top_findings"]],
                        "Confidence": [f"{round(f['confidence']*100, 1)}%" for f in result["top_findings"]]
                    }
                    st.table(findings_data)

                    st.divider()

                    # Radiology report
                    st.markdown("### 📋 AI Draft Radiology Report")
                    st.info("⚠️ AI-generated draft — pending radiologist review")
                    st.markdown(result["report"])

                else:
                    st.error(f"Analysis failed: {response.json().get('detail', 'Unknown error')}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Make sure the FastAPI server is running.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
    else:
        st.info("Upload a chest X-ray and click Analyze to see results here.")
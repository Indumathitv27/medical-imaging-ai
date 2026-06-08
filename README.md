---
title: Medical Imaging AI
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🏥 Medical Imaging AI System
![Dashboard](screenshot.png)

A production-grade AI system that analyzes chest X-rays, detects pulmonary 
abnormalities using computer vision, and generates structured radiology 
report drafts using a large language model agent.

---

## 🧠 What it does

1. **Ingests** a chest X-ray image (JPG/PNG/DICOM)
2. **Validates** the file — format, size, integrity
3. **Detects** 18 pathologies using a pretrained DenseNet121 CV model
4. **Generates** a structured radiology report draft using Llama 3.3 70B
5. **Displays** findings and report on a live dashboard

---

## 🏗️ ArchitectureUser Upload
↓
FastAPI Backend (/analyze)
↓
Ingestion Layer → validates, assigns UUID, stores scan
↓
CV Model Layer → DenseNet121 inference, 18 pathology scores
↓
LLM Agent Layer → Groq Llama 3.3 70B, structured report draft
↓
Streamlit Dashboard → live findings + report display

### AWS Production Mapping
| Local Component | AWS Equivalent |
|---|---|
| Local filesystem | S3 |
| FastAPI + uvicorn | API Gateway + Lambda |
| DenseNet121 model | SageMaker real-time endpoint |
| Groq Llama 3.3 70B | Amazon Bedrock |
| Streamlit | CloudFront + React |
| logs/ | CloudWatch |

---

## 🛠️ Tech Stack

- **Computer Vision** — TorchXRayVision, DenseNet121, PyTorch
- **Agentic AI** — Groq API, Llama 3.3 70B, LangChain
- **Backend** — FastAPI, Uvicorn, Python
- **Frontend** — Streamlit
- **Data** — NIH ChestX-ray14 dataset (112,000+ chest X-rays)
- **Cloud** — Designed for AWS (S3, SageMaker, Bedrock)

---

## 📋 Detected Pathologies

The model detects 18 chest pathologies including:
Atelectasis, Cardiomegaly, Consolidation, Edema, Effusion,
Emphysema, Fibrosis, Fracture, Hernia, Infiltration,
Lung Lesion, Lung Opacity, Mass, Nodule, Pleural Thickening,
Pneumonia, Pneumothorax, Enlarged Cardiomediastinum

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- Conda
- Groq API key (free at console.groq.com)

### Installation

```bash
# Clone the repo
git clone https://github.com/Indumathitv27/medical-imaging-ai.git
cd medical-imaging-ai

# Create conda environment
conda create -n medical-imaging python=3.10
conda activate medical-imaging

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root folder:
GROQ_API_KEY=your_groq_api_key_here

### Run the application

Terminal 1 — Start the API:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 — Start the dashboard:
```bash
streamlit run dashboard/app.py
```

Open your browser at `http://localhost:8501`

---

## 📁 Project Structure
medical-imaging-ai/
├── ingestion/          # Image validation and storage pipeline
├── cv_model/           # DenseNet121 inference module
├── agent/              # LLM report generation agent
├── api/                # FastAPI backend
├── dashboard/          # Streamlit frontend
├── data/
│   ├── raw/            # Uploaded scans (gitignored)
│   └── processed/      # Model outputs
├── logs/               # Audit logs (gitignored)
├── project_config.py   # Centralized configuration
├── requirements.txt    # Dependencies
└── .env                # API keys (gitignored)

---

## ⚠️ Disclaimer

This system is for research and educational purposes only.
It is not intended for clinical diagnosis or medical decision-making.
All reports are AI-generated drafts and must be reviewed by a 
qualified radiologist before any clinical use.

---

## 👩‍💻 Author

**Indumathi Tamil Selvi Varadharajan**  
M.S. Data Science, University at Buffalo  
[LinkedIn](https://linkedin.com/in/indumathitv2702/) | 
[GitHub](https://github.com/Indumathitv27/)
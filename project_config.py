import os
from dotenv import load_dotenv

load_dotenv()

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Ingestion settings
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".dcm"}
MAX_FILE_SIZE_MB = 50

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000
STREAMLIT_PORT = 7860
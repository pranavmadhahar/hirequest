# backend/config.py
from pathlib import Path
import os

VECTORSTORES_DIR = Path(os.getenv("VECTORSTORES_DIR", "/app/vectorstores"))

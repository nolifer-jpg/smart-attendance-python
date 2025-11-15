# This file centralizes all configuration and paths for the project.

import os
from pathlib import Path
from dotenv import load_dotenv

# --- Base Directory ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Load Environment Variables ---
load_dotenv(BASE_DIR / ".env")

# --- Email Settings (from .env file) ---
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# --- Data Folders ---
DATA_DIR = BASE_DIR / "data"
KNOWN_FACES_DIR = DATA_DIR / "known_faces"
UNKNOWN_FACES_DIR = DATA_DIR / "unknowns"  # <-- CHANGED from "unknown_faces"
MODELS_DIR = DATA_DIR / "models"  # <-- NEW folder for your .pkl file

# --- Database File ---
DB_PATH = DATA_DIR / "students.db"

# --- Data Files ---
ENCODINGS_PATH = MODELS_DIR / "encodings.pkl"  # <-- CHANGED to use MODELS_DIR
ATTENDANCE_CSV_PATH = DATA_DIR / "attendance.csv"

# --- Cooldown Setting ---
ATTENDANCE_COOLDOWN_SECONDS = 10 * 60  # 10 minutes

# --- Note on config.yaml ---
# I see you also have a config.yaml.
# For this simple project, we are loading settings directly from this Python file.
# In a more advanced project, you could use this config.py file
# to load and parse the config.yaml file.

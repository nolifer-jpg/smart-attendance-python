# This file centralizes all configuration and paths for the project.
# It makes it easy to change file locations without hunting through all the code.

import os
from pathlib import Path  # pathlib is a modern way to handle file paths
from dotenv import load_dotenv

# --- Base Directory ---
# This finds the root directory of your project (the one with requirements.txt)
# We go up two levels because this file is in 'config/' which is in 'src/'
# Note: This is a bit fragile. A more common way is to base it on this file's location.
# Let's use a simpler, more robust way.
# __file__ is the path to this current file (config.py)
# .parent gives the folder it's in (config/)
# .parent.parent gives the folder *that* folder is in (the project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Load Environment Variables ---
# This loads the .env file (containing secrets like email passwords)
# into the environment so os.getenv() can read them.
load_dotenv(BASE_DIR / ".env")

# --- Email Settings (from .env file) ---
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# --- Data Folders ---
# We use the BASE_DIR to build absolute paths to our data folders.
# This ensures the script works regardless of where you run it from.
DATA_DIR = BASE_DIR / "data"
KNOWN_FACES_DIR = DATA_DIR / "known_faces"
UNKNOWN_FACES_DIR = DATA_DIR / "unknown_faces"

# --- Database File ---
DB_PATH = DATA_DIR / "students.db"

# --- Data Files ---
ENCODINGS_PATH = DATA_DIR / "encodings.pkl"
ATTENDANCE_CSV_PATH = DATA_DIR / "attendance.csv"

# --- Cooldown Setting ---
# The number of seconds before a student can be marked present again.
ATTENDANCE_COOLDOWN_SECONDS = 10 * 60  # 10 minutes

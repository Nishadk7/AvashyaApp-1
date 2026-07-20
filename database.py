import os
import sys

# Redirect root imports directly to backend/database.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from backend.database import Base, engine, get_db, SessionLocal

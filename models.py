import os
import sys

# Redirect root imports directly to backend/models.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from backend.models import User, Item, ItemTag, ALLOWED_TYPES

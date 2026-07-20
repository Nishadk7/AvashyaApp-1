import os
import sys

# Redirect root imports directly to backend/storage.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from backend.storage import get_storage_service, S3StorageService

import os
import sys
import importlib.util

_backend_storage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "storage.py")
_spec = importlib.util.spec_from_file_location("_backend_storage", _backend_storage_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

get_storage_service = _mod.get_storage_service
S3StorageService = _mod.S3StorageService

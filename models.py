import os
import sys
import importlib.util

_backend_models_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "models.py")
_spec = importlib.util.spec_from_file_location("_backend_models", _backend_models_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

User = _mod.User
Item = _mod.Item
ItemTag = _mod.ItemTag
ALLOWED_TYPES = _mod.ALLOWED_TYPES

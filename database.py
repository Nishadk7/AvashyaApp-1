import os
import sys
import importlib.util

_backend_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "database.py")
_spec = importlib.util.spec_from_file_location("_backend_db", _backend_db_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

Base = _mod.Base
engine = _mod.engine
get_db = _mod.get_db
SessionLocal = _mod.SessionLocal

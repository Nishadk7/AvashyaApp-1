import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from database import SessionLocal
from models import Item, ItemTag

def clear_all_items():
    db = SessionLocal()
    try:
        tag_count = db.query(ItemTag).delete()
        item_count = db.query(Item).delete()
        db.commit()
        print(f"✅ Successfully cleared {item_count} items and {tag_count} metadata tags from the database.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error clearing items: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_items()

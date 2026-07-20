import os
import sys
import datetime
from typing import List, Optional

# Add root directory and backend directory to sys.path for robust imports
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI, Depends, HTTPException, status, Form, UploadFile, File, Request, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
import jwt
from passlib.context import CryptContext

from database import Base, engine, get_db
from models import User, Item, ItemTag, ALLOWED_TYPES
from storage import get_storage_service, S3StorageService

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = "avashya-drop-secret-key-for-local-demo"
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None

def seed_default_users():
    from database import SessionLocal
    db = SessionLocal()
    try:
        users_to_seed = [
            {"username": "nishad", "email": "nishad@avashya.com", "password": "nishad"},
            {"username": "supreeth", "email": "supreeth@avashya.com", "password": "supreeth"},
            {"username": "varun", "email": "varun@avashya.com", "password": "varun"},
        ]
        for u_data in users_to_seed:
            existing = db.query(User).filter(User.username == u_data["username"]).first()
            if not existing:
                user = User(
                    username=u_data["username"],
                    email=u_data["email"],
                    hashed_password=hash_password(u_data["password"])
                )
                db.add(user)
        db.commit()
    finally:
        db.close()

seed_default_users()

# Initialize FastAPI REST API App
app = FastAPI(title="Avashya Drop REST API (Port 8000)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        return None

    username = payload.get("sub")
    if not username:
        return None

    user = db.query(User).filter(User.username == username).first()
    return user


def require_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided or are invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@app.post("/api/auth/register")
def register(data: dict, db: Session = Depends(get_db)):
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="Username, email, and password are required")

    existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "email": user.email}
    }


@app.post("/api/auth/login")
def login(data: dict, db: Session = Depends(get_db)):
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "email": user.email}
    }


@app.get("/api/auth/me")
def get_me(user: User = Depends(require_current_user)):
    return {"id": user.id, "username": user.username, "email": user.email}


@app.get("/api/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.username.asc()).all()
    return [{"id": u.id, "username": u.username, "email": u.email} for u in users]


@app.get("/api/items")
def list_items(
    q: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    uploader: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    storage: S3StorageService = Depends(get_storage_service)
):
    query = db.query(Item)

    if q and q.strip():
        search_pattern = f"%{q.strip()}%"
        query = query.outerjoin(ItemTag).filter(
            or_(
                Item.item_name.ilike(search_pattern),
                ItemTag.key.ilike(search_pattern),
                ItemTag.value.ilike(search_pattern)
            )
        ).distinct()

    if type and type in ALLOWED_TYPES:
        query = query.filter(Item.type == type)

    if uploader and uploader.strip():
        query = query.join(User).filter(User.username == uploader.strip())

    if start_date:
        try:
            s_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Item.upload_date >= s_dt)
        except ValueError:
            pass

    if end_date:
        try:
            e_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(days=1)
            query = query.filter(Item.upload_date < e_dt)
        except ValueError:
            pass

    items = query.order_by(Item.upload_date.desc()).all()

    result = []
    for item in items:
        result.append({
            "id": item.id,
            "item_name": item.item_name,
            "type": item.type,
            "upload_date": item.upload_date.isoformat(),
            "file_reference": item.file_reference,
            "file_url": storage.get_file_url(item.file_reference),
            "user_id": item.user_id,
            "owner": {"username": item.owner.username} if item.owner else None,
            "tags": [{"key": t.key, "value": t.value} for t in item.tags]
        })

    return result


@app.post("/api/items/upload")
async def upload_item(
    request: Request,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
    storage: S3StorageService = Depends(get_storage_service)
):
    form = await request.form()
    item_name = str(form.get("item_name", "")).strip()
    type = str(form.get("type", "")).strip()
    file_obj = form.get("file")

    if not item_name or not type or not file_obj:
        raise HTTPException(status_code=400, detail="Item Name, Type, and File are required")

    if type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid type. Must be one of: {ALLOWED_TYPES}")

    file_bytes = await file_obj.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    filename = getattr(file_obj, "filename", "upload.bin") or "upload.bin"
    file_ref = storage.save_file(file_bytes, filename)

    new_item = Item(
        item_name=item_name,
        type=type,
        file_reference=file_ref,
        user_id=user.id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    tag_keys = form.getlist("tag_keys[]") + form.getlist("tag_keys")
    tag_values = form.getlist("tag_values[]") + form.getlist("tag_values")

    for key, val in zip(tag_keys, tag_values):
        k = str(key).strip()
        v = str(val).strip()
        if k and v:
            tag = ItemTag(item_id=new_item.id, key=k, value=v)
            db.add(tag)

    db.commit()
    db.refresh(new_item)

    return {
        "id": new_item.id,
        "item_name": new_item.item_name,
        "type": new_item.type,
        "upload_date": new_item.upload_date.isoformat(),
        "file_reference": new_item.file_reference,
        "file_url": storage.get_file_url(new_item.file_reference),
        "owner": {"username": user.username},
        "tags": [{"key": t.key, "value": t.value} for t in new_item.tags]
    }


@app.delete("/api/items/{item_id}")
def delete_item(
    item_id: int,
    user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
    storage: S3StorageService = Depends(get_storage_service)
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.user_id != user.id and user.username != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized to delete this item")

    storage.delete_file(item.file_reference)
    db.delete(item)
    db.commit()

    return {"msg": "Item deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    print("Starting Avashya Drop Backend REST API on Port 8000 (0.0.0.0)...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

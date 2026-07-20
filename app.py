import os
import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Form, UploadFile, File, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, or_, and_
from sqlalchemy.orm import Relationship, relationship, Session
import jwt
from passlib.context import CryptContext

from database import Base, engine, get_db
from models import User, Item, ItemTag, ALLOWED_TYPES
from storage import get_storage_service, BaseStorageService

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = "avashya-drop-secret-key-for-local-demo"
ALGORITHM = "HS256"

# Helper functions for authentication & passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

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

# Seed pre-defined demo users (nishad, supreeth, varun)
seed_default_users()

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

# Initialize FastAPI App & Jinja2 Templates
app = FastAPI(title="Avashya Drop - Internal Developer Knowledge Repository")
templates = Jinja2Templates(directory="templates")


# Auth Helper Dependency
def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    if token.startswith("Bearer "):
        token = token[7:]
    payload = decode_access_token(token)
    if not payload:
        return None
    username = payload.get("sub")
    if not username:
        return None
    return db.query(User).filter(User.username == username).first()


# Routes

@app.get("/files/{filename}")
def serve_file(filename: str):
    """Serve uploaded file from local storage directory."""
    file_path = os.path.join("./uploads", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="register.html", context={"user": None})


@app.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(or_(User.username == username, User.email == email)).first()
    if existing_user:
        return templates.TemplateResponse(request=request, name="register.html", context={
            "error": "Username or email already registered.",
            "user": None
        })
    
    hashed_pwd = hash_password(password)
    new_user = User(username=username, email=email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Auto-login after registration
    token = create_access_token({"sub": new_user.username})
    response = RedirectResponse(url="/?msg=Account+created+successfully", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html", context={"user": None})


@app.post("/login")
def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(request=request, name="login.html", context={
            "error": "Invalid username or password.",
            "user": None
        })

    token = create_access_token({"sub": user.username})
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@app.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    q: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    uploader: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    msg: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    storage: BaseStorageService = Depends(get_storage_service)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    query = db.query(Item)

    # 1. Partial String Keyword Matching against Item Name, Tag Keys, and Tag Values
    if q and q.strip():
        search_pattern = f"%{q.strip()}%"
        query = query.outerjoin(ItemTag).filter(
            or_(
                Item.item_name.ilike(search_pattern),
                ItemTag.key.ilike(search_pattern),
                ItemTag.value.ilike(search_pattern)
            )
        ).distinct()

    # 2. Type Filtering
    if type and type in ALLOWED_TYPES:
        query = query.filter(Item.type == type)

    # 3. Uploader Filtering
    if uploader and uploader.strip():
        query = query.join(User).filter(User.username == uploader.strip())

    # 4. Date Range Filtering
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

    # 5. Sorted in descending order of upload date (newest first)
    items = query.order_by(Item.upload_date.desc()).all()

    # Get all users for the uploader filter dropdown
    all_users = db.query(User).order_by(User.username.asc()).all()

    # Populate file URLs dynamically using storage abstraction service
    for item in items:
        item.file_url = storage.get_file_url(item.file_reference)

    return templates.TemplateResponse(request=request, name="index.html", context={
        "user": user,
        "items": items,
        "all_users": all_users,
        "query_q": q or "",
        "selected_type": type or "",
        "selected_uploader": uploader or "",
        "start_date": start_date or "",
        "end_date": end_date or "",
        "msg": msg,
        "error": error
    })


@app.post("/upload")
async def upload_item(
    request: Request,
    db: Session = Depends(get_db),
    storage: BaseStorageService = Depends(get_storage_service)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    item_name = str(form.get("item_name", "")).strip()
    type = str(form.get("type", "")).strip()
    file_obj = form.get("file")

    if not item_name or not type or not file_obj or not hasattr(file_obj, "filename"):
        return RedirectResponse(url="/?error=Missing+required+file+or+fields", status_code=303)

    if type not in ALLOWED_TYPES:
        return RedirectResponse(url=f"/?error=Invalid+file+type.+Allowed:+{','.join(ALLOWED_TYPES)}", status_code=303)

    file_bytes = await file_obj.read()
    if not file_bytes:
        return RedirectResponse(url="/?error=Uploaded+file+is+empty", status_code=303)

    filename = getattr(file_obj, "filename", "upload.bin") or "upload.bin"
    file_ref = storage.save_file(file_bytes, filename)

    # Create Item in SQLite database
    new_item = Item(
        item_name=item_name,
        type=type,
        file_reference=file_ref,
        user_id=user.id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    # Process dynamic Key-Value Metadata Tags (supports tag_keys[], tag_keys, etc.)
    tag_keys = form.getlist("tag_keys[]") + form.getlist("tag_keys")
    tag_values = form.getlist("tag_values[]") + form.getlist("tag_values")

    for key, val in zip(tag_keys, tag_values):
        k_clean = str(key).strip()
        v_clean = str(val).strip()
        if k_clean and v_clean:
            tag = ItemTag(item_id=new_item.id, key=k_clean, value=v_clean)
            db.add(tag)

    db.commit()

    return RedirectResponse(url="/?msg=Item+dropped+successfully", status_code=303)


@app.post("/items/{item_id}/delete")
def delete_item(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
    storage: BaseStorageService = Depends(get_storage_service)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return RedirectResponse(url="/?error=Item+not+found", status_code=303)

    if item.user_id != user.id and user.username != "admin":
        return RedirectResponse(url="/?error=Unauthorized+to+delete+this+item", status_code=303)

    # Delete physical file via storage service
    storage.delete_file(item.file_reference)

    # Delete database record (cascade deletes tags)
    db.delete(item)
    db.commit()

    return RedirectResponse(url="/?msg=Item+deleted+successfully", status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)

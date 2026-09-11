import uuid, re
from pathlib import Path
from fastapi import UploadFile, HTTPException
from .config import UPLOAD_DIR
ALLOWED={"image/png","image/jpeg","image/webp"}
def uid(): return uuid.uuid4().hex
def safe_name(name):
    return re.sub(r"[^A-Za-z0-9_.-]","_",name or "file")
async def save_image(file: UploadFile|None, folder):
    if not file or not file.filename: return ""
    if file.content_type not in ALLOWED: raise HTTPException(400,"Only PNG, JPG, JPEG and WEBP images are allowed.")
    data=await file.read()
    if len(data)>5*1024*1024: raise HTTPException(400,"Image must be 5MB or smaller.")
    dest=UPLOAD_DIR/folder
    dest.mkdir(parents=True,exist_ok=True)
    filename=f"{uid()}_{safe_name(file.filename)}"
    (dest/filename).write_bytes(data)
    return f"/static/uploads/{folder}/{filename}"

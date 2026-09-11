import hashlib, hmac, secrets
from datetime import datetime, timezone
from fastapi import Request
from .database import find_one, get

def now():
    return datetime.now(timezone.utc).isoformat()
def hash_password(password):
    salt=secrets.token_bytes(16)
    dk=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,240000)
    return salt.hex()+"$"+dk.hex()
def verify_password(password, stored):
    try:
        s,h=stored.split("$",1)
        dk=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(s),240000)
        return hmac.compare_digest(dk.hex(),h)
    except Exception:return False
def current_user(request: Request):
    uid=request.session.get("user_id")
    return get("users",uid) if uid else None
def require_user(request):
    u=current_user(request)
    if not u: return None
    return u
def require_admin(request):
    u=current_user(request)
    return u if u and u.get("role")=="admin" else None

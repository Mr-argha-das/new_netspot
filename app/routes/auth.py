from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from ..database import find_one, add
from ..auth import hash_password, verify_password, now
from ..utils import uid
from ..database import settings
router=APIRouter()
def T(request,n,**kw): return request.app.state.templates.TemplateResponse(n,{"request":request,"site_name":settings().get("site_name","NETSPORTS"),"settings":settings(),**kw})
@router.get("/register")
def register(request:Request): return T(request,"register.html")
@router.post("/register")
def register_post(request:Request,name:str=Form(...),email:str=Form(...),game:str=Form(...),game_profile_name:str=Form(...),utr_id:str=Form(...),password:str=Form(...),confirm_password:str=Form(...),phone:str=Form("")):
    if password!=confirm_password:return T(request,"register.html",error="Passwords do not match.")
    if find_one("users",email=email):return T(request,"register.html",error="Email already registered.")
    u={"id":uid(),"name":name.strip(),"email":email.strip().lower(),"game":game,"game_profile_name":game_profile_name.strip(),"utr_id":utr_id.strip(),"phone":phone.strip(),"password_hash":hash_password(password),"role":"user","status":"active","created_at":now()}
    add("users",u)
    add("payments",{"id":uid(),"user_id":u["id"],"utr_id":u["utr_id"],"amount":settings().get("registration_amount","99"),"status":"pending","admin_note":"","created_at":now(),"updated_at":now()})
    request.session["user_id"]=u["id"]
    request.session["flash"]="Account created successfully. You can now create your team."
    return RedirectResponse("/dashboard",303)
@router.get("/login")
def login(request:Request): return T(request,"login.html")
@router.post("/login")
def login_post(request:Request,email:str=Form(...),password:str=Form(...)):
    u=find_one("users",email=email)
    if not u or not verify_password(password,u["password_hash"]): return T(request,"login.html",error="Invalid email or password.")
    request.session["user_id"]=u["id"]
    destination="/admin/dashboard" if u.get("role")=="admin" else "/dashboard"
    return RedirectResponse(destination,303)
@router.get("/logout")
def logout(request:Request):
    request.session.clear(); return RedirectResponse("/",303)

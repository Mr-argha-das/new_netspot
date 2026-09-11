from fastapi import APIRouter,Request,Form,UploadFile,File
from fastapi.responses import RedirectResponse
from ..auth import require_admin,hash_password,now
from ..database import *
from ..utils import uid,save_image
from ..services.notifications import notify
router=APIRouter(prefix="/admin")
def guard(request):
    if not require_admin(request): return RedirectResponse("/login",303)
def T(request,n,**kw): return request.app.state.templates.TemplateResponse(n,{"request":request,"settings":settings(),**kw})
@router.get("")
@router.get("/dashboard")
def dashboard(request:Request):
    g=guard(request)
    if g:return g
    return T(request,"admin/dashboard.html",users=len(read("users")),teams=len(read("teams")),applications=len(read("applications")),payments=len(read("payments")),tournaments=len(read("tournaments")),live=len(read("tournaments")[read("tournaments").status=="live"]) if not read("tournaments").empty else 0)
@router.get("/setup")
def setup(request:Request):
    if find_one("users",role="admin"): return RedirectResponse("/login",303)
    return T(request,"admin/setup.html")
@router.post("/setup")
def setup_post(request:Request,name:str=Form(...),email:str=Form(...),password:str=Form(...)):
    if find_one("users",role="admin"): return RedirectResponse("/login",303)
    u={"id":uid(),"name":name,"email":email.lower(),"game":"","game_profile_name":"","utr_id":"","phone":"","password_hash":hash_password(password),"role":"admin","status":"active","created_at":now()}
    add("users",u); request.session["user_id"]=u["id"]; return RedirectResponse("/admin/dashboard",303)
@router.get("/settings")
def admin_settings(request:Request):
    g=guard(request)
    if g:return g
    return T(request,"admin/settings.html")
@router.post("/settings")
async def admin_settings_post(request:Request,registration_amount:str=Form(...),payment_instructions:str=Form(...),qr:UploadFile|None=File(None),site_name:str=Form("NETSPORTS"),hero_title:str=Form("PLAY. WIN. REPEAT."),hero_description:str=Form("")):
    g=guard(request)
    if g:return g
    set_setting("registration_amount",registration_amount);set_setting("payment_instructions",payment_instructions);set_setting("site_name",site_name);set_setting("hero_title",hero_title);set_setting("hero_description",hero_description)
    if qr and qr.filename:set_setting("payment_qr",await save_image(qr,"qr"))
    request.session["flash"]="Settings saved."
    return RedirectResponse("/admin/settings",303)
@router.get("/tournaments")
def admin_tournaments(request:Request):
    g=guard(request)
    if g:return g
    return T(request,"admin/tournaments.html",items=read("tournaments").to_dict("records"))
@router.post("/tournaments/create")
def tournament_create(request:Request,name:str=Form(...),game:str=Form(...),map:str=Form(""),date:str=Form(""),time:str=Form(""),registration_deadline:str=Form(""),entry_fee:str=Form("0"),first_prize:str=Form("0"),second_prize:str=Form("0"),prize_pool:str=Form("0"),max_teams:str=Form("0"),description:str=Form(""),rules:str=Form("")):
    g=guard(request)
    if g:return g
    add("tournaments",{"id":uid(),"name":name,"game":game,"map":map,"description":description,"rules":rules,"date":date,"time":time,"registration_deadline":registration_deadline,"entry_fee":entry_fee,"first_prize":first_prize,"second_prize":second_prize,"prize_pool":prize_pool,"max_teams":max_teams,"players_per_team":"4","banner":"","status":"upcoming","room_id":"","room_password":"","match_number":"","created_at":now()})
    return RedirectResponse("/admin/tournaments",303)
@router.post("/tournaments/{tid}/delete")
def tournament_delete(request:Request,tid:str):
    g=guard(request)
    if g:return g
    delete("tournaments",tid); return RedirectResponse("/admin/tournaments",303)
@router.post("/tournaments/{tid}/start")
def tournament_start(request:Request,tid:str,room_id:str=Form(...),room_password:str=Form(...),match_number:str=Form("1")):
    g=guard(request)
    if g:return g
    update("tournaments",tid,{"status":"live","room_id":room_id,"room_password":room_password,"match_number":match_number})
    apps=read("applications"); 
    if not apps.empty:
        for _,a in apps[(apps.tournament_id.astype(str)==str(tid))&(apps.status=="approved")].iterrows():
            notify(a.owner_id,"Match started",f"Room ID: {room_id} | Password: {room_password}","match")
    return RedirectResponse("/admin/tournaments",303)
@router.get("/applications")
def applications(request:Request):
    g=guard(request)
    if g:return g
    return T(request,"admin/applications.html",items=read("applications").to_dict("records"))
@router.post("/applications/{aid}/approve")
def app_approve(request:Request,aid:str,note:str=Form("")):
    g=guard(request)
    if g:return g
    a=get("applications",aid)
    if a:
        update("applications",aid,{"status":"approved","admin_note":note,"updated_at":now()})
        notify(a["owner_id"],"Application approved",note or "Your tournament application has been approved.","success")
    return RedirectResponse("/admin/applications",303)
@router.post("/applications/{aid}/reject")
def app_reject(request:Request,aid:str,note:str=Form(...)):
    g=guard(request)
    if g:return g
    a=get("applications",aid)
    if a:
        update("applications",aid,{"status":"rejected","admin_note":note,"updated_at":now()})
        notify(a["owner_id"],"Application rejected",note,"error")
    return RedirectResponse("/admin/applications",303)
@router.get("/payments")
def payments(request:Request):
    g=guard(request)
    if g:return g
    return T(request,"admin/payments.html",items=read("payments").to_dict("records"))
@router.post("/payments/{pid}/verify")
def verify_payment(request:Request,pid:str):
    g=guard(request)
    if g:return g
    p=get("payments",pid)
    if p:
        update("payments",pid,{"status":"verified","updated_at":now()});notify(p["user_id"],"Payment verified","Your registration payment has been verified.","success")
    return RedirectResponse("/admin/payments",303)
@router.post("/payments/{pid}/reject")
def reject_payment(request:Request,pid:str,note:str=Form(...)):
    g=guard(request)
    if g:return g
    p=get("payments",pid)
    if p:
        update("payments",pid,{"status":"rejected","admin_note":note,"updated_at":now()});notify(p["user_id"],"Payment rejected",note,"error")
    return RedirectResponse("/admin/payments",303)

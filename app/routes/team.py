from fastapi import APIRouter,Request,Form,UploadFile,File
from fastapi.responses import RedirectResponse
from ..auth import current_user,now
from ..database import add,read,settings
from ..utils import uid,save_image
from ..services.notifications import notify
router=APIRouter()
def T(request,n,**kw): return request.app.state.templates.TemplateResponse(n,{"request":request,"settings":settings(),**kw})
@router.get("/team/create")
def create(request:Request):
    u=current_user(request)
    if not u:return RedirectResponse("/login",303)
    return T(request,"team_form.html",user=u)
@router.post("/team/create")
async def create_post(request:Request,game:str=Form(...),team_name:str=Form(...),logo:UploadFile|None=File(None),
    p2_id:str=Form(...),p2_name:str=Form(...),p3_id:str=Form(...),p3_name:str=Form(...),p4_id:str=Form(...),p4_name:str=Form(...)):
    u=current_user(request)
    if not u:return RedirectResponse("/login",303)
    if not all([game,team_name,p2_id,p2_name,p3_id,p3_name,p4_id,p4_name]): return T(request,"team_form.html",user=u,error="All player Game IDs and Profile Names are required.")
    existing=read("teams")
    if not existing.empty and ((existing.owner_id.astype(str)==str(u["id"])) & (existing.status.isin(["draft","submitted","approved"]))).any():
        return T(request,"team_form.html",user=u,error="You already have an active team.")
    logo_url=await save_image(logo,"teams")
    tid=uid(); t={"id":tid,"owner_id":u["id"],"game":game,"name":team_name.strip(),"logo":logo_url,"status":"submitted","admin_note":"","created_at":now(),"updated_at":now()}
    add("teams",t)
    add("team_members",{"id":uid(),"team_id":tid,"user_id":u["id"],"slot":1,"game_id":"","profile_name":u["game_profile_name"],"status":"approved","note":""})
    for slot,gid,pn in [(2,p2_id,p2_name),(3,p3_id,p3_name),(4,p4_id,p4_name)]:
        add("team_members",{"id":uid(),"team_id":tid,"user_id":"","slot":slot,"game_id":gid,"profile_name":pn,"status":"pending","note":""})
    notify(u["id"],"Team submitted","You will get your team card after review.","success")
    request.session["flash"]="You will get your team card."
    return RedirectResponse("/dashboard",303)

from fastapi import APIRouter,Request,Form
from fastapi.responses import RedirectResponse
from ..auth import current_user,now
from ..database import read,add,find_one
from ..utils import uid
from ..services.notifications import notify
router=APIRouter()
@router.post("/tournament/{tid}/apply")
def apply(request:Request,tid:str,team_id:str=Form(...)):
    u=current_user(request)
    if not u:return RedirectResponse("/login",303)
    t=find_one("tournaments",id=tid); teams=read("teams")
    if not t:return RedirectResponse("/tournaments",303)
    team=find_one("teams",id=team_id)
    if not team or str(team.get("owner_id"))!=str(u["id"]) or team.get("status") not in ["submitted","approved"]:return RedirectResponse(f"/tournament/{tid}",303)
    apps=read("applications")
    if not apps.empty and ((apps.tournament_id.astype(str)==str(tid))&(apps.team_id.astype(str)==str(team_id))).any():
        request.session["flash"]="Application already submitted."; return RedirectResponse(f"/tournament/{tid}",303)
    add("applications",{"id":uid(),"tournament_id":tid,"team_id":team_id,"owner_id":u["id"],"status":"pending","admin_note":"","created_at":now(),"updated_at":now()})
    notify(u["id"],"Application submitted",f"Your team applied to {t['name']}.","info")
    request.session["flash"]="Application submitted."
    return RedirectResponse("/dashboard",303)

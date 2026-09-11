from fastapi import APIRouter,Request
from fastapi.responses import RedirectResponse
from ..auth import current_user
from ..database import read, settings
router=APIRouter()
def T(request,n,**kw): return request.app.state.templates.TemplateResponse(n,{"request":request,"settings":settings(),**kw})
@router.get("/dashboard")
def dashboard(request:Request):
    u=current_user(request)
    if not u:return RedirectResponse("/login",303)
    teams=read("teams"); team=teams[teams.owner_id.astype(str)==str(u["id"])].iloc[-1].to_dict() if not teams.empty and (teams.owner_id.astype(str)==str(u["id"])).any() else None
    apps=read("applications"); apps=apps[apps.owner_id.astype(str)==str(u["id"])] if not apps.empty else apps
    notes=read("notifications"); notes=notes[notes.user_id.astype(str)==str(u["id"])] if not notes.empty else notes
    return T(request,"dashboard.html",user=u,team=team,applications=apps.to_dict("records"),notifications=notes.sort_values("created_at",ascending=False).head(10).to_dict("records"),tournaments=read("tournaments").to_dict("records"))

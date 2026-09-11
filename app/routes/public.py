from fastapi import APIRouter, Request
from ..database import read, settings
router=APIRouter()
def ctx(request,**kw): return {"request":request,"site_name":settings().get("site_name","NETSPORTS"),"settings":settings(),**kw}
@router.get("/")
def home(request:Request):
    t=read("tournaments").to_dict("records")
    w=read("winners").sort_values("created_at",ascending=False).head(1).to_dict("records")
    lb=read("match_results")
    if not lb.empty:
        lb=lb.groupby("team_id",as_index=False).agg(wins=("rank",lambda x:int((x==1).sum())),points=("points","sum"),prize=("prize","sum"),matches=("id","count")).sort_values(["points","wins"],ascending=False)
        teams=read("teams")[["id","name"]] if not read("teams").empty else read("teams")
        if not teams.empty: lb=lb.merge(teams,left_on="team_id",right_on="id",how="left",suffixes=("","_team"))
        leaderboard=lb.head(10).to_dict("records")
    else: leaderboard=[]
    return request.app.state.templates.TemplateResponse("home.html",ctx(request,tournaments=t,latest_winner=w[0] if w else None,leaderboard=leaderboard))
@router.get("/tournaments")
def tournaments(request:Request):
    return request.app.state.templates.TemplateResponse("tournaments.html",ctx(request,tournaments=read("tournaments").to_dict("records")))
@router.get("/tournament/{tid}")
def tournament_detail(request:Request,tid:str):
    from ..database import get
    x=get("tournaments",tid)
    if not x: return request.app.state.templates.TemplateResponse("404.html",ctx(request),status_code=404)
    return request.app.state.templates.TemplateResponse("tournament_detail.html",ctx(request,tournament=x))
@router.get("/leaderboard")
def leaderboard(request:Request):
    return request.app.state.templates.TemplateResponse("leaderboard.html",ctx(request,leaderboard=[]))
@router.get("/about")
def about(request:Request): return request.app.state.templates.TemplateResponse("about.html",ctx(request))
@router.get("/faq")
def faq(request:Request): return request.app.state.templates.TemplateResponse("faq.html",ctx(request,faqs=read("faq").to_dict("records")))

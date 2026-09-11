from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from .config import BASE_DIR, SITE_NAME
from .database import init_db
from .routes import public, auth, user, team, tournament, admin
from .config import SECRET_KEY
app=FastAPI(title=SITE_NAME)
app.add_middleware(SessionMiddleware,secret_key=SECRET_KEY,max_age=60*60*24*14,same_site="lax")
app.mount("/static",StaticFiles(directory=str(BASE_DIR/"static")),name="static")
templates=Jinja2Templates(directory=str(BASE_DIR/"templates"))
app.state.templates=templates
init_db()
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(team.router)
app.include_router(tournament.router)
app.include_router(admin.router)

@app.exception_handler(404)
async def not_found(request, exc):
    return templates.TemplateResponse("404.html",{"request":request,"site_name":SITE_NAME},status_code=404)

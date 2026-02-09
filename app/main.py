import os

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_302_FOUND
from starlette.templating import Jinja2Templates

from app.db import init_db
from app.auth import authenticate, login_user
from app import notes, export

app = FastAPI()

# Сессии (cookie-based). Секрет лучше хранить в env.
secret = os.environ.get("SESSION_SECRET", "change-me-in-prod")
app.add_middleware(SessionMiddleware, secret_key=secret)

templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup():
    init_db()


# --- Auth pages ---
@app.get("/login")
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})


@app.post("/login")
def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    user = authenticate(username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"},
        )

    login_user(request, user["id"])
    return RedirectResponse("/note", status_code=HTTP_302_FOUND)


# --- Feature routers ---
app.include_router(notes.router)
app.include_router(export.router)
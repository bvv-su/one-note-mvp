from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.db import init_db
from app.auth import authenticate, login_user, logout_user, get_current_user_id
from app.notes import get_note_content, save_note_content

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="dev-change-me",
    same_site="lax",
    https_only=False,
)

templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    user_id = get_current_user_id(request)
    return RedirectResponse(url="/note" if user_id else "/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    user_id = authenticate(username=username, password=password)
    if user_id is None:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    login_user(request, user_id)
    return RedirectResponse(url="/note", status_code=302)


@app.post("/logout")
def logout_post(request: Request):
    logout_user(request)
    return RedirectResponse(url="/login", status_code=302)


@app.get("/note", response_class=HTMLResponse)
def note_get(request: Request):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=302)

    content = get_note_content(user_id)
    return templates.TemplateResponse(
        "note.html",
        {"request": request, "content": content, "msg": None},
    )


@app.post("/note", response_class=HTMLResponse)
def note_post(
    request: Request,
    content: str = Form(""),
):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=302)

    save_note_content(user_id, content)
    # отображаем сохранённый текст + сообщение
    return templates.TemplateResponse(
        "note.html",
        {"request": request, "content": content, "msg": "Saved"},
    )
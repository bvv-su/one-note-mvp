from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from starlette.templating import Jinja2Templates

from app.auth import logout_user, require_auth
from app.db import get_conn

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def root(request: Request):
    # если залогинен — на заметку, иначе — на login
    if request.session.get("user_id"):
        return RedirectResponse("/note", status_code=HTTP_302_FOUND)
    return RedirectResponse("/login", status_code=HTTP_302_FOUND)


@router.get("/note")
def note_page(request: Request, user_id: int = Depends(require_auth)):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT content FROM notes WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    content = row["content"] if row else ""
    return templates.TemplateResponse(
        "note.html",
        {"request": request, "content": content},
    )


@router.post("/note")
def save_note(
    request: Request,
    content: str = Form(...),
    user_id: int = Depends(require_auth),
):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO notes(user_id, content)
            VALUES(?, ?)
            ON CONFLICT(user_id) DO UPDATE SET content=excluded.content
            """,
            (user_id, content),
        )
        conn.commit()

    return RedirectResponse("/note", status_code=HTTP_302_FOUND)


@router.post("/logout")
def logout(request: Request):
    logout_user(request)
    return RedirectResponse("/login", status_code=HTTP_302_FOUND)
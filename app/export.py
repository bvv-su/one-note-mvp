import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.auth import get_current_user
from app.db import get_conn

router = APIRouter()

@router.get("/export/note.csv")
def export_my_note_csv(current_user=Depends(get_current_user)):
    # Берём одну заметку текущего пользователя
    with get_conn() as conn:
        row = conn.execute(
            "SELECT content FROM notes WHERE user_id = ?",
            (current_user["id"],),
        ).fetchone()

    content = row["content"] if row else ""

    # Генерируем CSV в памяти
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_id", "content"])
    writer.writerow([current_user["id"], content])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=note.csv"},
    )
import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.auth import require_auth
from app.db import get_conn

router = APIRouter()


@router.get("/export/note.csv")
def export_my_note_csv(user_id: int = Depends(require_auth)):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT content FROM notes WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    content = row["content"] if row else ""

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_id", "content"])
    writer.writerow([user_id, content])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=note.csv"},
    )
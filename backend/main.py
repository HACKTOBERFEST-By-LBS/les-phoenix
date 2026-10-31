"""API FastAPI. Rôle du code : router (« / » = apprendre, sinon scanner) et gérer les sessions.
Toute l'intelligence (lecture, analyse, verdict, cours, quiz) vient de Gemma."""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, Form, UploadFile  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from . import gemma, learning, scanner  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 10 * 1024 * 1024
MAX_TEXT = 20000
ALLOWED = {"image/png", "image/jpeg", "image/webp", "application/pdf", "text/plain"}

app = FastAPI(title="Vérif'SMS")
SESSIONS: dict = {}  # en mémoire : rien n'est écrit sur disque, rien n'est conservé après arrêt


def _session(sid: str) -> dict:
    if len(SESSIONS) > 500:  # garde-fou mémoire
        SESSIONS.clear()
    return SESSIONS.setdefault(sid, learning.new_state())


async def _read_file(f: UploadFile | None):
    if f is None or not f.filename:
        return None
    mime = f.content_type or ""
    if mime not in ALLOWED:
        raise ValueError("Format non accepté. Envoie une image (PNG, JPG, WEBP), un PDF ou du texte.")
    data = await f.read()
    if len(data) > MAX_BYTES:
        raise ValueError("Fichier trop gros (10 Mo maximum).")
    if mime == "text/plain":
        return {"kind": "text", "text": data.decode("utf-8", "ignore")[:MAX_TEXT]}
    return {"kind": "bytes", "data": data, "mime": mime}


@app.get("/api/exemples")
def exemples():
    path = ROOT / "data" / "exemples_sms.json"
    items = json.loads(path.read_text(encoding="utf-8"))
    # on n'envoie pas la réponse attendue à l'interface
    return [{"id": i["id"], "titre": i["titre"], "texte": i["texte"]} for i in items]


@app.get("/api/sante")
def sante():
    return {"ok": True, "modele": os.getenv("GEMMA_MODEL", gemma.MODEL), "cle": bool(os.getenv("GEMINI_API_KEY"))}


@app.post("/api/chat")
async def chat(
    session_id: str = Form(...),
    message: str = Form(""),
    langue: str = Form("fr"),
    file: UploadFile | None = File(None),
):
    s = _session(session_id[:64])
    msg = (message or "").strip()[:MAX_TEXT]

    try:
        f = await _read_file(file)
        # un .txt est traité comme du texte collé
        if f and f["kind"] == "text":
            msg = (msg + "\n" + f["text"]).strip()
            f = None

        # ---- ROUTAGE : seule une commande « / » entre dans le mode Apprendre
        if msg.startswith("/"):
            return learning.command(s, msg, f)
        if s["mode"] == "learn":
            return learning.free(s, msg, f)

        # ---- Par défaut : scanner d'arnaques
        if not msg and not f:
            return JSONResponse({"type": "info", "mode": "scan", "markdown": "Colle le texte du SMS ou envoie une capture d'écran.", "suggestions": []})
        image = gemma.part_bytes(f["data"], f["mime"]) if f and f["mime"].startswith("image/") else None
        if f and not image:
            return JSONResponse({"type": "info", "mode": "scan", "markdown": "Pour scanner un SMS, envoie une **image** ou colle le texte. Pour un cours, tape d'abord **/apprendre**.", "suggestions": ["/apprendre"]})
        result = scanner.scan(msg, image, langue if langue in ("ewe", "kabiye") else "fr")
        return {"type": "scan", "mode": "scan", "result": result}

    except ValueError as e:
        return JSONResponse({"type": "error", "markdown": str(e)}, status_code=400)
    except gemma.GemmaError as e:
        return JSONResponse({"type": "error", "markdown": f"Le service est indisponible pour l'instant. ({e})"}, status_code=503)


app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")

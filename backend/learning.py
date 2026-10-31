"""Volet « Apprendre » : actif uniquement après une commande qui commence par « / ».
Gemma lit le cours, génère le plan, les quiz et corrige."""
import datetime

from . import gemma, prompts

HELP = ["/plan", "/quiz", "/resume", "/stop"]
MAX_FILES = 5


def new_state() -> dict:
    return {
        "mode": "scan",       # "scan" (défaut) ou "learn"
        "course": [],         # [{"kind": "text"|"bytes", ...}]
        "themes": [],
        "titre": None,
        "weak": [],           # thèmes ratés -> relances adaptatives
        "asked": [],          # questions déjà posées
        "pending": None,      # question de quiz en attente de réponse
        "score": [0, 0],      # [bonnes, total]
        "plan_date": None,
    }


def _course_parts(s) -> list:
    parts = []
    for c in s["course"]:
        if c["kind"] == "bytes":
            parts.append(gemma.part_bytes(c["data"], c["mime"]))
        else:
            parts.append("NOTES DE COURS :\n" + c["text"])
    return parts


def _reply(s, md, suggestions=None, awaiting=False):
    return {
        "type": "learn",
        "mode": s["mode"],
        "markdown": md,
        "suggestions": suggestions if suggestions is not None else HELP,
        "awaiting_answer": awaiting,
    }


def _need_course(s):
    return _reply(
        s,
        "Je n'ai pas encore ton cours. **Envoie un PDF, une photo ou colle tes notes**, puis on commence.",
        ["/stop"],
    )


# ------------------------------------------------------------ cours

def _ingest(s, text: str, file) -> dict:
    if file:
        if len(s["course"]) >= MAX_FILES:
            s["course"].pop(0)
        s["course"].append({"kind": "bytes", "data": file["data"], "mime": file["mime"]})
    if text:
        s["course"].append({"kind": "text", "text": text})
    data = gemma.call_json(prompts.THEMES_SYSTEM, _course_parts(s) + ["Analyse ce cours."])
    if not isinstance(data, dict):
        return _reply(s, "J'ai reçu ton cours, mais je n'arrive pas à le lire. Essaie avec une image plus nette ou un PDF texte.")
    s["themes"] = list(data.get("themes") or [])
    s["titre"] = data.get("titre")
    return _reply(s, data.get("message") or "Cours reçu.")


# ------------------------------------------------------------ commandes

def command(s, message: str, file, today=None) -> dict:
    today = today or datetime.date.today()
    cmd, _, arg = message.strip().partition(" ")
    cmd, arg = cmd.lower(), arg.strip()

    if cmd == "/apprendre":
        s["mode"] = "learn"
        if file or arg:
            return _ingest(s, arg, file)
        if s["course"]:
            return _reply(s, f"Mode apprentissage activé. J'ai déjà ton cours **{s['titre'] or ''}**. Tape /plan, /quiz ou /resume.")
        return _reply(
            s,
            "Mode apprentissage activé. **Téléverse ton cours** (PDF, photo ou texte collé). "
            "Pour la démo, utilise un cours d'exemple ou tes propres notes, jamais de document confidentiel.",
            ["/stop"],
        )

    if cmd == "/stop":
        s.update(mode="scan", pending=None)
        return {
            "type": "info",
            "mode": "scan",
            "markdown": "Mode apprentissage arrêté. Je suis de retour en **scanner d'arnaques** : colle un SMS ou une capture.",
            "suggestions": [],
        }

    if cmd in ("/plan", "/quiz", "/resume", "/résumé"):
        if s["mode"] != "learn":
            return {
                "type": "info",
                "mode": "scan",
                "markdown": "Pour réviser, commence par **/apprendre**.",
                "suggestions": ["/apprendre"],
            }
        if not s["course"]:
            return _need_course(s)
        if cmd == "/plan":
            return _plan(s, arg, today)
        if cmd == "/quiz":
            return _quiz(s)
        return _resume(s)

    return {
        "type": "info",
        "mode": s["mode"],
        "markdown": "Commande inconnue. Commandes : /apprendre, /plan, /quiz, /resume, /stop.",
        "suggestions": ["/apprendre"] if s["mode"] != "learn" else HELP,
    }


def _plan(s, arg, today):
    if not arg:
        return _reply(s, "Pour quelle date est ton examen ? Écris par exemple **/plan 20 novembre**.", ["/stop"])
    s["plan_date"] = arg
    weak = f"\nThèmes que l'étudiant maîtrise mal : {', '.join(s['weak'])}." if s["weak"] else ""
    prompt = f"Date d'aujourd'hui : {today.isoformat()}. Date d'examen indiquée par l'étudiant : {arg}.{weak}\nCrée le plan de révision."
    md = gemma.call(prompts.PLAN_SYSTEM, _course_parts(s) + [prompt], 0.4)
    return _reply(s, md, ["/quiz", "/resume", "/stop"])


def _resume(s):
    md = gemma.call(prompts.RESUME_SYSTEM, _course_parts(s) + ["Produis les fiches de révision."], 0.3)
    return _reply(s, md, ["/quiz", "/plan", "/stop"])


def _quiz(s):
    weak = f"Thèmes faibles à privilégier : {', '.join(s['weak'])}." if s["weak"] else "Aucun thème faible repéré pour l'instant."
    asked = ("Questions déjà posées : " + " | ".join(s["asked"][-8:])) if s["asked"] else ""
    data = gemma.call_json(prompts.QUIZ_SYSTEM, _course_parts(s) + [f"{weak}\n{asked}\nPose la prochaine question."], 0.6)
    if not isinstance(data, dict) or not data.get("question"):
        return _reply(s, "Je n'ai pas réussi à préparer la question. Réessaie /quiz.", ["/quiz", "/stop"])
    s["pending"] = data
    s["asked"].append(data["question"])
    opts = data.get("options")
    md = f"**Question {s['score'][1] + 1}**\n\n{data['question']}"
    if opts:
        md += "\n\n" + "\n".join(f"- {o}" for o in opts)
    md += "\n\n_Écris ta réponse. Tape /stop pour quitter._"
    return _reply(s, md, ["/stop"], awaiting=True)


# ------------------------------------------------------------ texte libre en mode learn

def free(s, text: str, file) -> dict:
    # Nouveau cours (fichier, ou long texte collé sans question en attente)
    if file or (len(text) > 600 and not s["pending"]):
        s["pending"] = None
        return _ingest(s, text, file)
    if not s["course"]:
        return _need_course(s)
    if s["pending"]:
        return _grade(s, text)
    prompt = f"Question de l'étudiant : {text}"
    md = gemma.call(prompts.ASK_SYSTEM, _course_parts(s) + [prompt], 0.3)
    return _reply(s, md)


def _grade(s, answer):
    q = s["pending"]
    prompt = (
        f"Question posée : {q['question']}\nOptions : {q.get('options')}\n"
        f"Réponse attendue : {q.get('reponse_attendue')}\nThème : {q.get('theme')}\n"
        f"Réponse de l'étudiant : {answer}"
    )
    data = gemma.call_json(prompts.GRADE_SYSTEM, _course_parts(s) + [prompt], 0.2)
    if not isinstance(data, dict):
        return _reply(s, "Je n'ai pas pu corriger. Réécris ta réponse.", ["/stop"], awaiting=True)
    s["pending"] = None
    s["score"][1] += 1
    theme = data.get("theme") or q.get("theme") or ""
    if data.get("correct"):
        s["score"][0] += 1
        if theme in s["weak"]:
            s["weak"].remove(theme)
    elif theme and theme not in s["weak"]:
        s["weak"].append(theme)
    md = data.get("message") or ("Bonne réponse !" if data.get("correct") else "Pas tout à fait.")
    md += f"\n\n**Score : {s['score'][0]}/{s['score'][1]}**"
    if s["weak"]:
        md += f" · à retravailler : {', '.join(s['weak'])}"
    return _reply(s, md, ["/quiz", "/resume", "/stop"])

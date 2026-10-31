"""Mesure la fiabilité du scanner conformément au brief officiel (Section 9.5).
Usage : python -m tests.eval
"""
import json
import sys
import time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
CASES_FILE = Path(__file__).resolve().parent / "cases.json"
BASE_URL = "http://127.0.0.1:8000"

s = requests.Session()

# 1. Création compte de test temporaire
pseudo = f"eval_{int(time.time())}"
reg = s.post(f"{BASE_URL}/api/register", json={"pseudo": pseudo, "password": "password123", "lang": "fr"})
if reg.status_code != 200:
    print(f"Erreur d'inscription pour le test: {reg.text}")
    sys.exit(1)

cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))

ok_count = 0
false_ok = 0

print(f"\n--- Evaluation du scanner sur {len(cases)} cas réels & anonymisés ---")

for idx, c in enumerate(cases):
    if idx > 0:
        time.sleep(2)
    
    data = {"text": c["text"], "sender": c.get("sender", ""), "lang": "fr"}
    resp = s.post(f"{BASE_URL}/api/analyse", data=data)
    
    if resp.status_code != 200:
        print(f"KO {c['id']:<20} Erreur API {resp.status_code}: {resp.text}")
        continue
    
    res = resp.json()
    verdict = res.get("verdict")
    expected = c["expected"]
    
    good = (verdict == expected)
    # Si 'douteux' attendu, accepter aussi 'arnaque' par mesure de sécurité
    if expected == "douteux" and verdict in ("douteux", "arnaque"):
        good = True
    
    if expected == "arnaque" and verdict == "ok":
        false_ok += 1
        
    if good:
        ok_count += 1
        
    status = "OK " if good else "KO "
    print(f"{status} {c['id']:<22} attendu={expected:<8} obtenu={verdict:<8} (Montant: {res.get('amount')})")

rate = (ok_count * 100) // len(cases)
print(f"\nScore final : {ok_count}/{len(cases)} ({rate}%)")
print(f"Faux 'ok' sur arnaque (interdit par le brief) : {false_ok}")

if false_ok > 0 or rate < 90:
    sys.exit(1)
sys.exit(0)

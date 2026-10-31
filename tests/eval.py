"""Mesure la fiabilité de Gemma sur data/exemples_sms.json.
Usage (depuis la racine du projet) :  python -m tests.eval
Affiche le taux de bonnes détections : un chiffre à montrer au jury (critère 4)."""
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
from backend import scanner  # noqa: E402

items = json.loads((Path(__file__).resolve().parent.parent / "data" / "exemples_sms.json").read_text(encoding="utf-8"))

MAX_RETRIES = 3
DELAY_BETWEEN = 3  # secondes entre chaque appel pour éviter le rate-limit

ok = 0
faux_positifs = 0
for idx, it in enumerate(items):
    # Petit délai entre les appels (sauf le premier)
    if idx > 0:
        time.sleep(DELAY_BETWEEN)

    # Retry en cas d'erreur transitoire (500, réseau…)
    r = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = scanner.scan(it["texte"], None)
            break
        except Exception as e:
            print(f"  ! {it['id']} tentative {attempt}/{MAX_RETRIES} echouee : {e}")
            if attempt < MAX_RETRIES:
                time.sleep(5 * attempt)  # backoff progressif
            else:
                print(f"  X {it['id']} abandonne apres {MAX_RETRIES} tentatives")
                r = {"verdict": "illisible", "confiance": 0}

    got = r["verdict"]
    good = got == it["attendu"]
    # Un "suspect" attendu accepte aussi "arnaque" ; jamais "legitime"
    if it["attendu"] == "suspect" and got in ("suspect", "arnaque"):
        good = True
    ok += good
    if it["attendu"] == "legitime" and got in ("arnaque",):
        faux_positifs += 1
    print(f"{'OK ' if good else 'KO '} {it['id']:<22} attendu={it['attendu']:<9} obtenu={got:<9} ({r['confiance']} %)")

print(f"\nBonnes détections : {ok}/{len(items)} ({100 * ok // len(items)} %)")
print(f"Vrais SMS classés « arnaque » à tort : {faux_positifs}")
sys.exit(0 if ok == len(items) else 1)

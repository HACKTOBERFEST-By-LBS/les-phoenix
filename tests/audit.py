"""
Script d'audit automatique pour le backend Fraude Scanner.
Lance tous les tests: auth, scanner, historique.
Usage: python -m tests.audit
"""
import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

BASE = "http://localhost:8000"
bugs = []
ok_count = 0

def check(name, condition, detail=""):
    global ok_count
    if condition:
        print(f"  [OK] {name}")
        ok_count += 1
    else:
        print(f"  [BUG] {name}" + (f": {detail}" if detail else ""))
        bugs.append(f"{name}: {detail}")

# --- AUTH ---
print("\n=== AUTH ===")
s = requests.Session()

r = s.post(f"{BASE}/api/register", json={"pseudo": "audit_user", "password": "test123", "lang": "fr"})
check("Register nouveau user -> 200", r.status_code == 200, str(r.text[:80]))
if r.status_code == 200:
    check("Register retourne pseudo", r.json().get("pseudo") == "audit_user")
    check("Register retourne langue", r.json().get("langue") == "fr")

r2 = requests.post(f"{BASE}/api/register", json={"pseudo": "audit_user", "password": "autre", "lang": "fr"})
check("Double register -> 409", r2.status_code == 409, f"recu {r2.status_code}")

r3 = requests.post(f"{BASE}/api/register", json={"pseudo": "x", "password": "test123", "lang": "fr"})
check("Pseudo trop court -> 400", r3.status_code == 400, f"recu {r3.status_code}")

r4 = requests.post(f"{BASE}/api/register", json={"pseudo": "audit2", "password": "ab", "lang": "fr"})
check("MDP trop court -> 400", r4.status_code == 400, f"recu {r4.status_code}")

r5 = s.get(f"{BASE}/api/me")
check("/me apres register -> 200", r5.status_code == 200, str(r5.text[:60]))

s2 = requests.Session()
r6 = s2.post(f"{BASE}/api/login", json={"pseudo": "audit_user", "password": "test123"})
check("Login bon mot de passe -> 200", r6.status_code == 200, str(r6.text[:80]))

r7 = requests.post(f"{BASE}/api/login", json={"pseudo": "audit_user", "password": "mauvais"})
check("Login mauvais mdp -> 401", r7.status_code == 401, f"recu {r7.status_code}")

r8 = requests.post(f"{BASE}/api/login", json={"pseudo": "fantome999", "password": "test123"})
check("Login pseudo inexistant -> 401", r8.status_code == 401, f"recu {r8.status_code}")

r9 = requests.get(f"{BASE}/api/history")
check("Acces sans session -> 401", r9.status_code == 401, f"recu {r9.status_code}")

r10 = s.post(f"{BASE}/api/logout")
check("Logout -> 204", r10.status_code == 204, f"recu {r10.status_code}")

r11 = s.get(f"{BASE}/api/me")
check("Apres logout -> 401", r11.status_code == 401, f"recu {r11.status_code}")

# --- SCANNER ---
print("\n=== SCANNER ===")
s3 = requests.Session()
s3.post(f"{BASE}/api/login", json={"pseudo": "audit_user", "password": "test123"})

r12 = s3.post(f"{BASE}/api/analyse", data={"text": "", "lang": "fr"})
check("SMS vide -> 400", r12.status_code == 400, f"recu {r12.status_code}")

sms_ok = "Depot de 5000 FCFA chez l'agent 90001(PSDTT ETS KOFFI), le 31-10-26 13:21. Frais: 0 FCFA. Nouveau solde Mixx : 7500 FCFA . Ref: 19801100001."
r13 = s3.post(f"{BASE}/api/analyse", data={"text": sms_ok, "lang": "fr", "sender": "Moov Money"})
check("Analyse SMS legitime -> 200", r13.status_code == 200, str(r13.text[:80]))
if r13.status_code == 200:
    d = r13.json()
    check("Verdict present", "verdict" in d)
    check("Conseil securite present", bool(d.get("security_tip")))
    check("Amount present", bool(d.get("amount")))
    check("SMS legitime pas classe arnaque", d.get("verdict") != "arnaque",
          f"classe '{d.get('verdict')}'")
    print(f"      -> verdict: {d.get('verdict')}")

sms_arnaque = "Jai fait un depot de 25000F sur votre compte par erreur. Merci de me renvoyer l'argent au 90000004 c'est urgent."
r14 = s3.post(f"{BASE}/api/analyse", data={"text": sms_arnaque, "lang": "fr"})
check("Analyse arnaque -> 200", r14.status_code == 200)
if r14.status_code == 200:
    d = r14.json()
    check("Arnaque pas classee 'ok' (faux positif)", d.get("verdict") != "ok",
          f"classe '{d.get('verdict')}' -- FAUX POSITIF !")
    print(f"      -> verdict: {d.get('verdict')}")

sms_pin = "Votre code PIN T-Money est requis pour valider votre transaction. Envoyez votre code secret au 90000001."
r15 = s3.post(f"{BASE}/api/analyse", data={"text": sms_pin, "lang": "fr"})
check("SMS demande PIN -> 200", r15.status_code == 200)
if r15.status_code == 200:
    d = r15.json()
    check("SMS PIN force en arnaque", d.get("verdict") == "arnaque",
          f"classe '{d.get('verdict')}'")

r16 = s3.post(f"{BASE}/api/analyse", data={"text": "/apprendre", "lang": "fr"})
check("SMS commence par / -> 400", r16.status_code == 400, f"recu {r16.status_code}")

r17 = s3.post(f"{BASE}/api/analyse", data={"text": sms_arnaque, "lang": "ee"})
check("Analyse en ewe -> 200", r17.status_code == 200)
if r17.status_code == 200:
    d = r17.json()
    check("advice_local present pour ewe", d.get("advice_local") is not None)

# --- HISTORIQUE ---
print("\n=== HISTORIQUE ===")
r18 = s3.get(f"{BASE}/api/history")
check("Historique -> 200", r18.status_code == 200)
if r18.status_code == 200:
    d = r18.json()
    check("Historique a des scans", len(d.get("scans", [])) > 0,
          f"{len(d.get('scans', []))} scans trouves")
    check("Format scans correct", all("verdict" in sc for sc in d.get("scans", [])))

# --- RAPPORT ---
print(f"\n=== RAPPORT FINAL ===")
print(f"  Tests reussis : {ok_count}")
print(f"  Bugs trouves  : {len(bugs)}")
if bugs:
    print("\nBUGS :")
    for b in bugs:
        print(f"  ! {b}")
else:
    print("\nAucun bug backend detecte !")

# Cleanup Supabase
try:
    from supabase import create_client
    sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    sb.table("scan_history").delete().eq("user_pseudo", "audit_user").execute()
    sb.table("users").delete().eq("pseudo", "audit_user").execute()
    print("\nCleanup Supabase OK")
except Exception as e:
    print(f"\nCleanup: {e}")

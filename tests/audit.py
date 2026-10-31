"""Audit complet du backend - bugs et rÃ©gressions."""
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

# â”€â”€â”€ AUTH â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("\n=== AUTH ===")
s = requests.Session()

# 1. Register
r = s.post(f"{BASE}/api/register", json={"pseudo": "audit_user", "password": "test123", "lang": "fr"})
check("Register nouveau user â†’ 200", r.status_code == 200, str(r.text[:80]))
if r.status_code == 200:
    check("Register retourne pseudo", r.json().get("pseudo") == "audit_user")
    check("Register retourne langue", r.json().get("langue") == "fr")

# 2. Double register â†’ 409
r2 = requests.post(f"{BASE}/api/register", json={"pseudo": "audit_user", "password": "autre", "lang": "fr"})
check("Double register â†’ 409", r2.status_code == 409, f"reÃ§u {r2.status_code}")

# 3. Register pseudo trop court â†’ 400
r3 = requests.post(f"{BASE}/api/register", json={"pseudo": "x", "password": "test123", "lang": "fr"})
check("Pseudo trop court â†’ 400", r3.status_code == 400, f"reÃ§u {r3.status_code}")

# 4. Register mdp trop court â†’ 400
r4 = requests.post(f"{BASE}/api/register", json={"pseudo": "audit2", "password": "ab", "lang": "fr"})
check("MDP trop court â†’ 400", r4.status_code == 400, f"reÃ§u {r4.status_code}")

# 5. /me â†’ connectÃ©
r5 = s.get(f"{BASE}/api/me")
check("/me aprÃ¨s register â†’ 200", r5.status_code == 200, str(r5.text[:60]))

# 6. Login
s2 = requests.Session()
r6 = s2.post(f"{BASE}/api/login", json={"pseudo": "audit_user", "password": "test123"})
check("Login bon mot de passe â†’ 200", r6.status_code == 200, str(r6.text[:80]))

# 7. Login mauvais mdp â†’ 401
r7 = requests.post(f"{BASE}/api/login", json={"pseudo": "audit_user", "password": "mauvais"})
check("Login mauvais mdp â†’ 401", r7.status_code == 401, f"reÃ§u {r7.status_code}")

# 8. Login pseudo inexistant â†’ 401
r8 = requests.post(f"{BASE}/api/login", json={"pseudo": "fantome999", "password": "test123"})
check("Login pseudo inexistant â†’ 401", r8.status_code == 401, f"reÃ§u {r8.status_code}")

# 9. Sans session â†’ 401
r9 = requests.get(f"{BASE}/api/history")
check("AccÃ¨s sans session â†’ 401", r9.status_code == 401, f"reÃ§u {r9.status_code}")

# 10. Logout
r10 = s.post(f"{BASE}/api/logout")
check("Logout â†’ 204", r10.status_code == 204, f"reÃ§u {r10.status_code}")

# 11. AprÃ¨s logout â†’ 401
r11 = s.get(f"{BASE}/api/me")
check("AprÃ¨s logout â†’ 401", r11.status_code == 401, f"reÃ§u {r11.status_code}")

# â”€â”€â”€ SCANNER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("\n=== SCANNER ===")
# Nouvelle session
s3 = requests.Session()
s3.post(f"{BASE}/api/login", json={"pseudo": "audit_user", "password": "test123"})

# 12. SMS vide â†’ 400
r12 = s3.post(f"{BASE}/api/analyse", data={"text": "", "lang": "fr"})
check("SMS vide â†’ 400", r12.status_code == 400, f"reÃ§u {r12.status_code}")

# 13. Analyse SMS lÃ©gitime
sms_ok = "Depot de 5000 FCFA chez l'agent 90001(PSDTT ETS KOFFI), le 31-10-26 13:21. Frais: 0 FCFA. Nouveau solde Mixx : 7500 FCFA . Ref: 19801100001."
r13 = s3.post(f"{BASE}/api/analyse", data={"text": sms_ok, "lang": "fr", "sender": "Moov Money"})
check("Analyse SMS lÃ©gitime â†’ 200", r13.status_code == 200, str(r13.text[:80]))
if r13.status_code == 200:
    d = r13.json()
    check("Verdict prÃ©sent", "verdict" in d)
    check("Conseil sÃ©curitÃ© prÃ©sent", bool(d.get("security_tip")))
    check("Amount prÃ©sent", bool(d.get("amount")))
    check("SMS lÃ©gitime pas classÃ© arnaque", d.get("verdict") != "arnaque",
          f"classÃ© '{d.get('verdict')}'")
    print(f"      -> verdict: {d.get('verdict')}")

# 14. Arnaque Ã©vidente
sms_arnaque = "Jai fait un depot de 25000F sur votre compte par erreur. Merci de me renvoyer l'argent au 90000004 c'est urgent."
r14 = s3.post(f"{BASE}/api/analyse", data={"text": sms_arnaque, "lang": "fr"})
check("Analyse arnaque â†’ 200", r14.status_code == 200)
if r14.status_code == 200:
    d = r14.json()
    check("Arnaque pas classÃ©e 'ok' (faux positif)", d.get("verdict") != "ok",
          f"classÃ© '{d.get('verdict')}' â€” FAUX POSITIF !")
    print(f"      -> verdict: {d.get('verdict')}")

# 15. SMS avec demande de code PIN â†’ forcÃ© arnaque
sms_pin = "Votre code PIN T-Money est requis pour valider votre transaction. Envoyez votre code secret au 90000001."
r15 = s3.post(f"{BASE}/api/analyse", data={"text": sms_pin, "lang": "fr"})
check("SMS demande PIN â†’ 200", r15.status_code == 200)
if r15.status_code == 200:
    d = r15.json()
    check("SMS PIN forcÃ© en arnaque", d.get("verdict") == "arnaque",
          f"classÃ© '{d.get('verdict')}'")

# 16. SMS commence par / â†’ 400
r16 = s3.post(f"{BASE}/api/analyse", data={"text": "/apprendre", "lang": "fr"})
check("SMS commence par / â†’ 400", r16.status_code == 400, f"reÃ§u {r16.status_code}")

# 17. Analyse multilingue (Ã©wÃ©)
r17 = s3.post(f"{BASE}/api/analyse", data={"text": sms_arnaque, "lang": "ee"})
check("Analyse en Ã©wÃ© â†’ 200", r17.status_code == 200)
if r17.status_code == 200:
    d = r17.json()
    check("advice_local prÃ©sent pour Ã©wÃ©", d.get("advice_local") is not None)

# â”€â”€â”€ HISTORIQUE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("\n=== HISTORIQUE ===")
r18 = s3.get(f"{BASE}/api/history")
check("Historique â†’ 200", r18.status_code == 200)
if r18.status_code == 200:
    d = r18.json()
    check("Historique a des scans", len(d.get("scans", [])) > 0,
          f"{len(d.get('scans', []))} scans trouvÃ©s")
    check("Format scans correct", all("verdict" in sc for sc in d.get("scans", [])))

# â”€â”€â”€ RAPPORT FINAL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print(f"\n=== RAPPORT FINAL ===")
print(f"  Tests rÃ©ussis : {ok_count}")
print(f"  Bugs trouvÃ©s  : {len(bugs)}")
if bugs:
    print("\nBUGS :")
    for b in bugs:
        print(f"  ! {b}")
else:
    print("\nAucun bug backend dÃ©tectÃ© !")

# Cleanup Supabase
try:
    from supabase import create_client
    sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    sb.table("users").delete().eq("pseudo", "audit_user").execute()
    print("\nCleanup Supabase OK")
except Exception as e:
    print(f"\nCleanup: {e}")

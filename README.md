# Fraude Scanner — Les Phoenix 🦅

**Hackathon "Build with Gemma" — Lomé Business School, 31 Oct 2026**  
**Équipe : les-phoenix**

> Scanner anti-arnaque Mobile Money pour le Togo (T-Money / Moov Money) propulsé par Gemma AI.

---

## Fonctionnalités

- **Scanner SMS** — Détecte les arnaques Mobile Money (dépôt par erreur, faux concours, demande de PIN…)
- **Mode Apprendre** — `/plan`, `/quiz`, `/resume` sur tes cours (PDF, image, texte)
- **4 langues** — Français, Éwé, Kabiyè, English
- **Historique** — Scans et cours sauvegardés dans Supabase
- **Sécurité** — Conseil de sécurité après chaque analyse
- **Auth** — Inscription/connexion sans numéro de téléphone (pseudo + mot de passe)
- **Dark mode** — Automatique selon les préférences système

---

## Stack Technique

| Couche | Technologie |
|--------|------------|
| Backend | FastAPI + Python 3.11 |
| IA | Gemma 4 26B via Google AI SDK |
| Base de données | Supabase (PostgreSQL) |
| Frontend | HTML/CSS/JS vanilla |
| Auth | Sessions HTTPOnly + scrypt |

---

## Installation rapide

```bash
# 1. Cloner le repo
git clone https://github.com/HACKTOBERFEST-By-LBS/les-phoenix.git
cd les-phoenix

# 2. Créer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Remplir GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY dans .env

# 5. Lancer le serveur
uvicorn backend.main:app --port 8000 --host 0.0.0.0
```

Ouvrir : http://localhost:8000

---

## Structure du projet

```
les-phoenix/
├── backend/
│   ├── main.py              # API FastAPI (auth, scanner, cours, historique)
│   ├── formats_officiels.md # Vrais formats SMS Moov Money / T-Money
│   └── gemma.py             # Client Gemma
├── frontend/
│   ├── login.html           # Page d'authentification
│   └── index.html           # Interface principale (scanner + apprendre + historique)
├── data/
│   ├── references.json      # SMS de référence anonymisés
│   └── exemples_sms.json    # Cas de test
├── tests/
│   ├── audit.py             # Tests d'intégration complets
│   └── eval.py              # Benchmark de performance
├── .env.example             # Template des variables d'environnement
├── requirements.txt         # Dépendances Python
└── DOCS.md                  # Documentation complète
```

---

## API

| Route | Méthode | Description |
|-------|---------|-------------|
| `/api/register` | POST | Créer un compte |
| `/api/login` | POST | Se connecter |
| `/api/logout` | POST | Se déconnecter |
| `/api/me` | GET | Profil utilisateur connecté |
| `/api/analyse` | POST | Analyser un SMS (texte + image) |
| `/api/history` | GET | Historique des analyses et cours |
| `/api/course` | POST | Téléverser un cours |
| `/api/learn` | POST | Commandes /plan /quiz /resume |

---

## Sécurité

- Mots de passe hashés avec **scrypt** (jamais en clair)
- Sessions **HTTPOnly cookie** (non accessible depuis JS)
- **Rate limiting** : 5 tentatives max sur 5 minutes
- **0 faux positif** : une arnaque n'est jamais classée "ok"
- `.env` exclu du git (clés API protégées)

---

## Résultats Benchmark

| Métrique | Score |
|----------|-------|
| Taux de détection | 100% (15/15) |
| Faux positifs | 0 |
| Temps de réponse moyen | ~3s |

---

## Équipe les-phoenix

Hackathon "Build with Gemma" — Lomé Business School — 31 Octobre 2026

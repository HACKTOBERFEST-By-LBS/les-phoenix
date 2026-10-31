# Documentation Technique — Fraude Scanner

## Architecture

```
Browser (login.html / index.html)
    |
    | HTTP/REST
    v
FastAPI (backend/main.py) port 8000
    |               |
    v               v
Gemma 4 26B    Supabase (PostgreSQL)
(via AI SDK)   (users, scan_history, course_history)
```

## Variables d'environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| GEMINI_API_KEY | Cle API Google AI | AQ.Ab8RN6... |
| GEMMA_MODEL | Modele Gemma | gemma-4-26b-a4b-it |
| SUPABASE_URL | URL du projet Supabase | https://xxx.supabase.co |
| SUPABASE_KEY | Cle service_role Supabase | eyJ... |

## Modèle de données

### Table: users
| Colonne | Type | Description |
|---------|------|-------------|
| pseudo | TEXT PK | Identifiant unique (insensible casse) |
| salt | TEXT | Sel bcrypt encodé base64 |
| hash | TEXT | Hash scrypt encodé base64 |
| lang | TEXT | Langue par defaut (fr/ee/kbp/en) |
| created_at | TIMESTAMPTZ | Date de creation |

### Table: scan_history
| Colonne | Type | Description |
|---------|------|-------------|
| id | BIGINT PK | Identifiant auto |
| user_pseudo | TEXT FK | Reference utilisateur |
| timestamp | TIMESTAMPTZ | Date de l'analyse |
| sms_preview | TEXT | 80 premiers caracteres du SMS |
| verdict | TEXT | ok / douteux / arnaque |
| amount | TEXT | Montant extrait |
| sender | TEXT | Expediteur affiché |
| advice | TEXT | Conseil genere |

### Table: course_history
| Colonne | Type | Description |
|---------|------|-------------|
| id | BIGINT PK | Identifiant auto |
| user_pseudo | TEXT FK | Reference utilisateur |
| timestamp | TIMESTAMPTZ | Date de l'analyse |
| course_name | TEXT | Nom du fichier cours |
| last_command | TEXT | Derniere commande (/plan, /quiz...) |

## Format de réponse /api/analyse

```json
{
  "verdict": "ok|douteux|arnaque",
  "amount": "5 000 FCFA",
  "sender": "Moov Money",
  "syntax": "Format Moov Money Mixx officiel",
  "reasons": ["Raison 1", "Raison 2"],
  "advice": "Ce message semble authentique...",
  "advice_local": null,
  "security_tip": "Regle d'or: jamais votre PIN..."
}
```

## Sécurité

- **Hachage** : scrypt (n=16384, r=8, p=1, dklen=32)
- **Sessions** : token URLsafe 32 bytes, cookie HTTPOnly SameSite=Lax, TTL 8h
- **Rate limiting** : 5 tentatives / 5 minutes par IP+pseudo
- **Prompt injection** : contenu SMS encapsulé dans balises `<sms>` pour isolation
- **PIN guard** : si SMS contient "pin/code secret/mot de passe" → forcé "arnaque"

## Langues supportées

| Code | Langue |
|------|--------|
| fr | Français (défaut) |
| ee | Éwé (Togo) |
| kbp | Kabiyè (Togo) |
| en | English |

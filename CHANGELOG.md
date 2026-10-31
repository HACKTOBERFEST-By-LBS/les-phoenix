# Changelog — Fraude Scanner

Toutes les modifications notables de ce projet sont documentées ici.

---

## [1.3.0] — 2026-10-31

### Ajouté
- **Support fichiers enrichi** : PDF (pdfplumber), DOCX (python-docx), Markdown (.md), TXT dans `/api/course`
  - PDF scannés : fallback automatique vers Gemini Files API
  - Markdown : nettoyage automatique des balises (titres, gras, liens, images)
- **Bot WhatsApp** (`/api/whatsapp`) : Webhook Twilio pour analyser les SMS suspects directement depuis WhatsApp
  - Supporte texte et images (captures d'écran)
  - Réponse structurée : verdict, montant, conseil, numéro officiel
  - Endpoint `/api/whatsapp/status` pour vérifier la configuration
- **Recherche web** (`/recherche <sujet>`) dans le mode Apprendre
  - Propulsé par Gemini 2.0 Flash avec Google Search grounding
  - Recherche actuelle sur les arnaques / Mobile Money / cybersécurité au Togo
  - Fallback sans recherche si l'API Google Search est indisponible
- **Dictionnaire des fraudes** (`/api/fraud-dictionary`) : 8 types d'arnaques documentées
  - Signaux d'alerte, exemples de SMS réels, conseils de protection
  - 4 Règles d'Or + numéros officiels (T-Money 888 / Moov 101)
- **Onglet Dictionnaire** dans le frontend avec filtres par niveau de danger
- **Badge WhatsApp** dans la sidebar : numéro sandbox Twilio affiché
- **Section WhatsApp** dans l'onglet Historique : instructions d'activation
- **SEARCH_MODEL** : `gemini-2.0-flash` dédié à la recherche web (distinct du modèle scanner)

### Amélioré
- `/api/learn` : nouvelle commande `/recherche` sans avoir besoin d'un cours
- Interface chat : message de bienvenue amélioré avec toutes les commandes disponibles
- Upload cours : message de confirmation avec le type de fichier affiché
- Navigation : 4 onglets (Scanner, Apprendre, Dictionnaire, Historique)
- `gen_with_search()` : double fallback (avec puis sans Google Search)

### Technique
- Packages ajoutés : `python-docx==1.2.0`, `pdfplumber==0.11.10`, `twilio==9.12.0`
- Séparation claire : Gemma scanner SMS / Gemini Flash recherche web
- Données : `data/dictionnaire_fraudes.json` (8 catégories, règles d'or, numéros officiels)

---

## [1.2.0] — 2026-10-31

### Ajouté
- **Supabase** : Migration complète de SQLite vers PostgreSQL cloud
- **Tables** : `users`, `scan_history`, `course_history` avec relations FK
- **Fallback SQLite** : Si Supabase non configuré, SQLite prend le relais automatiquement
- **Fichier** `SUPABASE_SCHEMA.md` : Schéma SQL complet avec index et contraintes
- **Fichier** `DEMO_GUIDE.md` : Guide des 4 scénarios de démonstration
- **Fichier** `run.ps1` : Script de lancement rapide
- **Fichier** `setup.ps1` : Script de configuration automatique
- **Meta tags** SEO sur login.html et index.html
- **Tests** `audit.py` : Suite complète de 25 tests d'intégration

### Corrigé
- **Bug** : Register avec pseudo doublon retournait 400 au lieu de 409
- **Bug** : `pass2.value = ""` crashait silencieusement en mode login
- **Bug** : Apostrophe non échappée dans innerHTML de resetScan
- **Bug** : Fonction `esc` non définie dans le catch de `lancer()`
- **Messages** : Amélioration des textes d'erreur rate-limit et analyse

### Amélioré
- **Docstrings** : Toutes les fonctions DB documentées
- **Séparateurs** : Sections visuelles dans main.py pour lisibilité
- **DOCS.md** : Architecture, schéma DB, format API, sécurité

---

## [1.1.0] — 2026-10-31

### Ajouté
- **Historique** : Section historique des scans SMS et cours
- **Boutons 🔄** : Reset scanner et reset apprendre
- **4 langues** : Français, Éwé, Kabiyè, English avec `advice_local`
- **Conseil sécurité** : Banière après chaque analyse
- **Bouton Copier** et **Bouton Écouter (TTS)** sur les résultats

---

## [1.0.0] — 2026-10-31

### Ajouté
- Scanner SMS anti-arnaque via Gemma 4 26B
- Auth : register/login/logout avec scrypt + sessions HTTPOnly
- Mode Apprendre : /plan /quiz /resume /stop
- Interface responsive dark mode
- Design LBS (bleu marine + rouge)


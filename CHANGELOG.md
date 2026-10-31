# Changelog — Fraude Scanner

Toutes les modifications notables de ce projet sont documentées ici.

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


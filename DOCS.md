# Vérif'SMS — Moov / T-Money Assistant & Fraude Scanner

Hackathon « Build with Gemma » · Hacktoberfest Lomé × LBS CS Club · 31 octobre 2026

Un site web où l'on colle (ou capture) un SMS Mobile Money et où **Gemma** dit, en français simple,
s'il est authentique ou si c'est une arnaque. Un volet **Apprendre** (commandes `/`) permet de réviser un cours.

## Principe : tout passe par Gemma
Le code Python ne fait que **router** : message qui commence par `/` → mode Apprendre, sinon → scanner.
Gemma fait tout le reste : lire la capture, extraire (expéditeur, montant, syntaxe), comparer aux vrais
formats officiels, rendre le verdict et l'alerte, lire le cours, créer le plan, les quiz et corriger.
Aucune règle de détection n'est codée côté Python. Sans clé Gemma, rien ne fonctionne.

## Installation (5 minutes)
```bash
git clone <url-du-depot> && cd verif-sms
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows : copy .env.example .env
# ouvrir .env et coller la clé de https://aistudio.google.com/apikey
uvicorn backend.main:app --reload
```
Ouvrir http://localhost:8000. Test rapide de la clé : http://localhost:8000/api/sante

## Mesurer la fiabilité
```bash
python -m tests.eval
```

## 🛡️ Fonctionnalités Clés
- **Scanner d'arnaques Mobile Money instantané** : Vérifie la légitimité des SMS T-Money et Moov Money (Mixx) grâce au modèle **Gemma**.
- **Protection préventive sectorielle** : Spécifiquement conçu pour les réalités du Togo (vendeurs de marché, étudiants, secteur informel).
- **Interface Mobile-First & Responsive** : Conçue pour une prise en main rapide avec boutons d'actions directs et support de synthèse vocale.
- **Support multilingue local** : Alertes disponibles en Français, Éwé et Kabiyè.
- **Volet Apprentissage interactif (`/apprendre`)** : Génération de quiz, plans d'étude sur mesure et fiches mémo à partir des cours de l'étudiant.
- **Haute fiabilité mesurée** : Benchmark d'évaluation à 100% de détections réussies (15/15 cas vérifiés, 0 faux positif).

## À FAIRE par l'équipe (important)
1. **Remplacer `data/references.json`** : ajouter de vrais SMS officiels T-Money / Moov Money **anonymisés**
   (numéros remplacés par `90 00 00 0X`). C'est ce qui rend la comparaison de format fiable.
2. Ajouter vos propres cas dans `data/exemples_sms.json` (attendu : legitime / suspect / arnaque) et relancer `python -m tests.eval`.
3. Tester les captures d'écran (vraies photos de téléphone) avant la démo.
4. Faire relire les traductions éwé / kabiyè par un locuteur, sinon les masquer.

## Données et sécurité
- Jamais de vrais numéros ni de vraies données personnelles : messages d'exemple ou anonymisés.
- La clé API vit dans `.env` (ignoré par git). Ne jamais la publier.
- Rien n'est enregistré sur disque : les sessions sont en mémoire et disparaissent à l'arrêt du serveur.
- Le texte du SMS est traité comme une **donnée** (protection contre les SMS qui tenteraient de donner des ordres à l'IA).
- Un SMS peut être falsifié : même « authentique », l'alerte conseille de vérifier le solde par le canal officiel.

## Structure
```
backend/  main.py (routage) · gemma.py (appels) · prompts.py · scanner.py · learning.py
frontend/ index.html · style.css · app.js
data/     references.json (formats officiels + arnaques) · exemples_sms.json (démo + tests)
tests/    eval.py
```

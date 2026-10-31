# Guide de démo — Fraude Scanner

## Scénarios de démonstration

### 1. SMS Légitime (Moov Money Mixx)
**Colle dans le scanner :**
```
Dépôt de 5 000 FCFA chez l'agent 90001(PSDTT ETS KOFFI), le 31-10-26 13:21. Frais: 0 FCFA. Nouveau solde Mixx : 7 500 FCFA . Ref: 19801100001.
```
**Attendu :** Verdict ✅ **OK** — Format officiel reconnu, référence 11 chiffres valide.

---

### 2. Arnaque "Dépôt par erreur"
**Colle dans le scanner :**
```
Bonjour, j'ai fait un dépôt de 25 000F sur votre compte par erreur. Merci de me renvoyer l'argent au 90 00 00 04 c'est urgent.
```
**Attendu :** Verdict 🚨 **ARNAQUE** — Signal "dépôt par erreur" + numéro ordinaire.

---

### 3. Arnaque "Faux format officiel"
**Colle dans le scanner :**
```
Dépôt de 50 000 FCFA chez l'agent 90001, le 31-10-26. Frais: 0. Ref: 123. Erreur de depot, veuillez renvoyer 50 000 FCFA au 90 00 00 08.
```
**Attendu :** Verdict 🚨 **ARNAQUE** — Référence trop courte (3 chiffres au lieu de 11) + demande de renvoi.

---

### 4. Faux concours
**Colle dans le scanner :**
```
FELICITATIONS! Vous avez gagné 2 000 000 FCFA au grand concours Moov Money. Pour recevoir votre lot envoyez 15 000 FCFA de frais de dossier au 96 00 00 23. Appelez vite!
```
**Attendu :** Verdict 🚨 **ARNAQUE** — Faux gain + frais à payer + urgence.

---

## Parcours démo recommandé

1. **Ouvrir** http://localhost:8000
2. **Créer un compte** (pseudo + mot de passe)
3. **Scanner le SMS légitime** → voir verdict vert + conseil sécurité
4. **Scanner l'arnaque** → voir verdict rouge + explication détaillée
5. **Changer la langue en Éwé** → relancer → voir conseil traduit
6. **Ouvrir l'Historique** → voir les 2 analyses sauvegardées
7. **Mode Apprendre** → téléverser un cours PDF → `/plan` → `/quiz`


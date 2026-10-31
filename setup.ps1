# Script de configuration de l'environnement
# Usage: .\setup.ps1

Write-Host "=== Setup Fraude Scanner ===" -ForegroundColor Cyan

# 1. Créer le venv si absent
if (-not (Test-Path ".venv")) {
    Write-Host "Creation du venv Python..." -ForegroundColor Yellow
    python -m venv .venv
}

# 2. Installer les dépendances
Write-Host "Installation des dependances..." -ForegroundColor Yellow
& ".venv\Scripts\pip.exe" install -r requirements.txt --quiet

# 3. Vérifier le .env
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Fichier .env cree depuis .env.example" -ForegroundColor Green
    Write-Host "IMPORTANT: Remplis les variables dans .env avant de lancer!" -ForegroundColor Red
} else {
    Write-Host ".env existant conserve" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Setup termine ! ===" -ForegroundColor Green
Write-Host "Lance le serveur avec: .\run.ps1" -ForegroundColor Cyan

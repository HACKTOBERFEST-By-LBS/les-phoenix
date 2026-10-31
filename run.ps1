# Script de lancement rapide du serveur Fraude Scanner
# Usage: .\run.ps1

$venv = ".venv\Scripts\uvicorn.exe"
$app = "backend.main:app"
$port = 8000

Write-Host "Demarrage du serveur Fraude Scanner sur http://localhost:$port" -ForegroundColor Green
Write-Host "Ctrl+C pour arreter." -ForegroundColor Yellow

& $venv $app --port $port --host 0.0.0.0 --reload

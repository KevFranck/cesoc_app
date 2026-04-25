$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$venvPath = Join-Path $projectRoot ".venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"

Set-Location $projectRoot

if (-not (Test-Path $venvPath)) {
    Write-Host "Creation du virtualenv..."
    python -m venv .venv
}

if (-not (Test-Path $pythonExe)) {
    throw "Virtualenv invalide : impossible de trouver $pythonExe"
}

Write-Host "Installation des dependances dans .venv..."
& $pythonExe -m ensurepip --upgrade
& $pythonExe -m pip install -e .

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Fichier .env cree a partir de .env.example"
}

Write-Host ""
Write-Host "Bootstrap termine."
Write-Host "Active le virtualenv avec : .\.venv\Scripts\Activate.ps1"
Write-Host "Puis lance l'API avec : python -m uvicorn server.app.main:app --reload"

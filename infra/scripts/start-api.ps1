$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    throw "Le virtualenv .venv est absent. Lance d'abord .\infra\scripts\bootstrap.ps1"
}

Set-Location $projectRoot
& $pythonExe -m uvicorn server.app.main:app --reload

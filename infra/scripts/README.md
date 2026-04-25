# Scripts d'infrastructure

## Scripts disponibles

- `bootstrap.ps1` : cree `.venv`, installe les dependances et initialise `.env` si absent
- `start-api.ps1` : lance le backend avec l'interpreteur du virtualenv

## Usage

```powershell
powershell -ExecutionPolicy Bypass -File .\infra\scripts\bootstrap.ps1
powershell -ExecutionPolicy Bypass -File .\infra\scripts\start-api.ps1
```

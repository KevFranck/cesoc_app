# CESOC Admin Web

Interface web React pour les administrateurs CESOC.

## Demarrage

```powershell
cd admin-web
npm install
npm run dev
```

L'application tourne par defaut sur :

```text
http://localhost:5173
```

## Configuration

Copier `.env.example` vers `.env` si tu veux changer l'URL de l'API :

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## Mode test

Pour l'instant, l'interface admin s'ouvre directement sans ecran de connexion.

Elle consomme simplement l'endpoint :

- `/api/v1/admin/overview`

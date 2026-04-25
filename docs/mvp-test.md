# MVP test

## Objectif

Verifier rapidement les flux principaux du MVP backend.

## Parcours de test

1. Verifier que l'API repond :
   - `GET /health`

2. Lister les utilisateurs de demo :
   - `GET /api/v1/catalog/users`

3. Lister les postes :
   - `GET /api/v1/catalog/workstations`

4. Connecter un usager :
   - `POST /api/v1/auth/login`

Payload exemple :

```json
{
  "external_id": "CLI-001",
  "workstation_name": "POSTE-01"
}
```

5. Voir les sessions actives :
   - `GET /api/v1/sessions/active`

6. Tester l'impression :
   - `POST /api/v1/prints`

Payload exemple :

```json
{
  "external_id": "CLI-001",
  "workstation_name": "POSTE-01",
  "pages": 4
}
```

7. Depasser le quota :
   - refaire une impression au-dela de 10 pages cumulees

8. Fermer la session :
   - `POST /api/v1/sessions/{session_id}/close`

9. Consulter le rapport :
   - `GET /api/v1/reports/daily`

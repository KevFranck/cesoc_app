# Architecture du projet

## Couches

- `client/` : application desktop executee sur les postes Windows.
- `server/` : API centrale et logique metier.
- `shared/` : contrats de donnees communs entre client et serveur.
- `infra/` : elements d'installation et d'infrastructure locale.

## Modules metier cibles

- Authentification
- Gestion des sessions utilisateurs
- Gestion des impressions
- Gestion des quotas
- Reporting journalier
- Administration et audit

## Convention de responsabilite

- `api/` expose les routes HTTP.
- `services/` contient la logique metier.
- `repositories/` encapsule l'acces PostgreSQL.
- `models/` decrit les entites persistantes.
- `schemas/` decrit les objets d'entree/sortie.

# Client Desktop MVP

## Ecrans disponibles

- ecran de connexion
- panneau compact de session

## Fonctions branchees

- login utilisateur
- affichage du temps de session dans un panneau compact flottant
- minuteur de session local
- alertes avant expiration de session
- ouverture d'applications autorisees de test
- creation d'un dossier de travail local
- surveillance des nouveaux jobs d'impression Windows pendant la session
- blocage tente automatiquement si le quota quotidien est depasse
- masquage et reouverture depuis la zone de notification
- memorisation locale de la position de fenetre
- fermeture de certaines applications lancees par CESOC en fin de session
- fermeture de session
- affichage d'une vue rapide d'usage

## Pre-requis

- API backend en cours d'execution
- variable `CLIENT_API_BASE_URL` pointant vers l'API
- Microsoft Word installe si le bouton `Word` doit fonctionner
- Windows + `pywin32` disponible pour la surveillance d'impression reelle

## Lancement

```powershell
.\.venv\Scripts\python.exe -m client.app.main
```

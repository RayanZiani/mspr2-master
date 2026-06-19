# FutureKawa

Plateforme IoT de surveillance des stocks de cafe vert (Bresil, Equateur, Colombie + siege).

## Demarrage rapide

Prerequis:
- Docker Desktop demarre
- Node.js 18+

Installation:

```powershell
npm install
```

Lancement complet (3 pays + siege):

```powershell
npm start
```

Equivalent PowerShell:

```powershell
.\start.ps1
```

Acces:
- Interface web: http://localhost
- API siege (Swagger): http://localhost/api/docs

Arret:

```powershell
npm run stop
```

Logs:

```powershell
npm run logs
```

Mode detache:

```powershell
npm run start:detached
```

## Variables d'environnement

Le script `scripts/ensure-env.mjs` est execute avant le demarrage. Il cree automatiquement les fichiers `.env` depuis les `.env.example` quand ils sont absents.

Fichiers concernes:
- `siege/.env` depuis `siege/.env.example`
- `pays/bresil/.env` depuis `pays/bresil/.env.example`
- `pays/equateur/.env` depuis `pays/equateur/.env.example`
- `pays/colombie/.env` depuis `pays/colombie/.env.example`

Notes:
- L'API siege utilise `MYSQL_URL` (ou `DATABASE_URL` en fallback).
- Les scripts Python dans `scripts/` utilisent `MYSQL_URL` (chargement via `.env` racine).
- Si `MYSQL_URL` est absent dans `siege/.env`, `ensure-env.mjs` tente de le copier depuis `DATABASE_URL` dans `pays/bresil/.env`.

## Architecture de lancement

Le `docker-compose.yml` racine inclut:
- `pays/bresil/docker-compose.yml`
- `pays/equateur/docker-compose.yml`
- `pays/colombie/docker-compose.yml`
- `siege/docker-compose.yml`

Chaque pays est autonome (broker MQTT + MySQL + API + Node-RED). Le siege agrege les donnees via son API et expose le front via Nginx.

## Ports principaux

- `80`: Nginx siege (entree principale)
- `8001`: API Bresil
- `8002`: API Equateur
- `8003`: API Colombie
- `1883`: MQTT Bresil
- `1884`: MQTT Equateur
- `1885`: MQTT Colombie
- `1880`: Node-RED Bresil
- `1881`: Node-RED Equateur
- `1882`: Node-RED Colombie

## Endpoints utiles

- Siege:
	- `GET /api/stocks`
	- `GET /api/mesures`
	- `GET /api/alertes`
	- Swagger: http://localhost/api/docs
- Pays (debug):
	- Bresil: http://localhost:8001/docs
	- Equateur: http://localhost:8002/docs
	- Colombie: http://localhost:8003/docs

## Scripts utiles

```powershell
# Schema MySQL distant
python scripts/push_mysql_schema.py

# Seed MySQL distant
python scripts/push_mysql_seed.py

# Import jeu de donnees Excel vers MySQL
python scripts/import_demo_excel_to_mysql.py

# Generer un fichier Excel de demo
python scripts/generate_demo_excel.py
```

Les scripts ci-dessus necessitent `MYSQL_URL` (voir `.env.example` racine).

## Tests et CI/CD

```powershell
# Tests unitaires (sans Docker)
pip install -r tests/requirements.txt
npm run test:unit

# Stack complete + tous les tests
npm start
bash ci-cd/scripts/wait_for_stack.sh
npm run test
```

Documentation detaillee :
- `docs/technique/plan_tests.md`
- `docs/technique/ci_cd.md`

## Troubleshooting rapide

- Port 80 deja utilise:
	- arreter le service qui ecoute sur `:80` ou changer le mapping dans `siege/docker-compose.yml`
- Erreur de variable manquante `MYSQL_URL`:
	- verifier `siege/.env` pour l'API siege
	- verifier `.env` racine pour les scripts Python
- Docker indisponible:
	- verifier que Docker Desktop est bien lance

# FutureKawa

Plateforme IoT de surveillance des stocks de café vert (Brésil, Équateur, Colombie + siège).

## Démarrage rapide

Prérequis :
- Docker Desktop démarré
- Node.js 18+
- Compte **Aiven MySQL** configuré (`MYSQL_URL` dans `.env` à la racine)

Installation :

```powershell
npm install
```

Copier la configuration :

```powershell
copy .env.example .env
# Renseigner MYSQL_URL (Aiven) et DISCORD_WEBHOOK_URL si besoin
```

Lancement de la stack siège (UI + API + Redis) :

```powershell
npm start
```

Accès :
- Interface web : http://localhost
- API siège (Swagger) : http://localhost/api/docs

Simulateurs capteurs (écriture dans **Aiven** `releve_capteur`) :

```powershell
npm run sim:clear    # vider les relevés démo (optionnel)
npm run sim:start    # injecter des mesures toutes les 30 s
```

Arrêt :

```powershell
npm run stop
npm run sim:stop
```

Documentation IoT détaillée : [`docs/technique/architecture_iot_local.md`](docs/technique/architecture_iot_local.md)

## Base de données — Aiven uniquement

**Il n'y a pas de MySQL local dans Docker.** Toute l'application (siège, scripts, simulateurs, Render) lit et écrit la **même base Aiven** :

| Composant | Connexion |
|-----------|-----------|
| API siège (local + Render) | `MYSQL_URL` dans `siege/.env` |
| Scripts Python (`scripts/`) | `MYSQL_URL` dans `.env` racine |
| Simulateurs / pont MQTT | `MYSQL_URL` dans `.env` racine |

Le script `scripts/ensure-env.mjs` crée les `.env` manquants depuis les `.env.example`.

## Architecture de lancement

Le `docker-compose.yml` racine inclut uniquement **`siege/docker-compose.yml`** (API siège, Redis, Nginx, frontend).

Les relevés IoT arrivent dans Aiven via :
- `scripts/simulate_releves_aiven.py` (simulateurs EC/CO/BR)
- `scripts/mqtt_bridge_bresil.py` (pont MQTT → Aiven, capteur réel)

## Ports principaux

- `80` : Nginx siège (entrée principale)
- `6379` : Redis (cache siège, réseau Docker interne)
- `1883` : MQTT Brésil (optionnel, `docker-compose.iot.yml`)

## Endpoints utiles

- Siège :
  - `GET /api/stocks`
  - `GET /api/mesures?lot_id=...`
  - `GET /api/alertes`
  - Swagger : http://localhost/api/docs

## Scripts utiles (Aiven)

```powershell
# Schéma sur Aiven
python scripts/push_mysql_schema.py

# Seed minimal sur Aiven
python scripts/push_mysql_seed.py

# Import jeu de données Excel vers Aiven
python scripts/import_demo_excel_to_mysql.py

# Générer un fichier Excel de démo
python scripts/generate_demo_excel.py
```

Ces scripts nécessitent `MYSQL_URL` (voir `.env.example` racine).

## Tests et CI/CD

```powershell
pip install -r tests/requirements.txt
npm run test:unit

# Stack siège + tests complets
npm start
npm run wait:stack
npm run test
```

Documentation détaillée :
- [`docs/technique/plan_tests.md`](docs/technique/plan_tests.md)
- [`docs/technique/ci_cd.md`](docs/technique/ci_cd.md)
- [`docs/deployment/render.md`](docs/deployment/render.md)

## Troubleshooting rapide

- Port 80 déjà utilisé : arrêter le service sur `:80` ou modifier le mapping dans `siege/docker-compose.yml`
- Erreur `MYSQL_URL` manquant : vérifier `.env` racine et `siege/.env`
- Dashboard vide : exécuter `import_demo_excel_to_mysql.py` puis `npm run sim:start`
- Docker indisponible : vérifier que Docker Desktop est lancé

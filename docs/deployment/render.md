# Déploiement Render

## Ce qui est déployé

| Service | URL | Rôle |
|---------|-----|------|
| API Siège | `https://mspr2-master.onrender.com` | Auth, stocks, mesures, alertes |
| Frontend | `https://mspr2-master-front.onrender.com` | Supervision IoT |

Les simulateurs MQTT et le pont ESP32 tournent **en local** sur la machine de dev (voir [`docs/technique/architecture_iot_local.md`](../technique/architecture_iot_local.md)) — ils alimentent la **même base Aiven** que Render.

## Données affichées

Le frontend Render lit **Aiven MySQL** via l'API siège :

- Lots, capteurs, relevés (`releve_capteur`), alertes
- Schéma : `database/schema_mysql.sql`
- Données démo : `scripts/import_demo_excel_to_mysql.py`

## Variables d'environnement (API siège)

| Variable | Description |
|----------|-------------|
| `MYSQL_URL` | Connexion **Aiven MySQL** (obligatoire) |
| `MYSQL_SSL_CA` | Certificat CA Aiven (`database/ca.pem`) |
| `REDIS_URL` | Cache Redis (optionnel sur Render) |
| `JWT_SECRET` / `AUTH_JWT_SECRET` | Secret auth |
| `DISCORD_WEBHOOK_URL` | Webhook Discord pour alertes seuils |

Les variables `API_BRESIL_URL`, `API_EQUATEUR_URL` et `API_COLOMBIE_URL` **ne sont pas utilisées** : l'API siège interroge directement Aiven (`data_service.py`).

### Où ajouter `DISCORD_WEBHOOK_URL` sur Render

1. [dashboard.render.com](https://dashboard.render.com) → service **Web Service** API (`mspr2-master`)
2. **Environment** → **Add Environment Variable**
3. Key : `DISCORD_WEBHOOK_URL`, Value : URL webhook Discord
4. **Save Changes** (redéploiement automatique)

Vérification : bouton **Tester Discord** sur `/config/capteurs`.

**Ne pas** committer l'URL dans Git — uniquement Render + `.env` locaux (gitignored).

## Déploiement

Déclenché par GitHub Actions sur push `master` / `main` → Deploy Hooks Render.

### Configuration Render (Docker)

| Service | Root Directory | Dockerfile Path |
|---------|----------------|-----------------|
| Backend | *(racine repo)* | `siege/api/Dockerfile` |
| Frontend | *(racine repo)* | `siege/frontend/Dockerfile` |

Variable frontend : `VITE_API_BASE_URL=https://mspr2-master.onrender.com`

## Environnements

| | Développement local | Render (production) |
|---|---------------------|---------------------|
| Base de données | **Aiven MySQL** | **Aiven MySQL** (même instance ou clone) |
| API / Frontend | Docker siège (`npm start`) | Services Render |
| Simulateurs IoT | Machine dev → Aiven | Non (hors Render) |
| MQTT / ESP32 | Optionnel local | Non |

## Health check

Render vérifie `GET /health` sur l'API siège.

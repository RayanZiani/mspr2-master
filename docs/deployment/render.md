# Déploiement Render

## Ce qui est déployé aujourd'hui

| Service | URL | Rôle |
|---------|-----|------|
| API Siège | `https://mspr2-master.onrender.com` | Auth, stocks, mesures, alertes |
| Frontend | `https://mspr2-master-front.onrender.com` | Supervision IoT |

Les **APIs pays** et les **simulateurs MQTT** ne sont **pas** sur Render — ils tournent en local (voir `docs/technique/architecture_iot_local.md`).

## Données affichées sur Render

Le frontend Render lit la **base MySQL centrale (Aiven)** via l'API siège :

- Lots, mesures et alertes de **démonstration** (schéma `database/schema_mysql.sql`)
- Comportement actuel conservé : dashboard, courbes, page alertes

## Variables d'environnement (API siège)

| Variable | Description |
|----------|-------------|
| `MYSQL_URL` | Connexion Aiven MySQL |
| `REDIS_URL` | Cache Redis (optionnel) |
| `JWT_SECRET` | Secret auth |
| `DISCORD_WEBHOOK_URL` | Webhook Discord pour alertes seuils (obligatoire pour notifications) |

Les variables `API_BRESIL_URL`, `API_EQUATEUR_URL` et `API_COLOMBIE_URL` ne sont **pas** nécessaires sur Render : l'API siège lit directement la base MySQL centrale. Elles restent requises en local (docker-compose) pour l'agrégateur multi-pays.

### Où ajouter `DISCORD_WEBHOOK_URL` sur Render

1. Ouvrir [dashboard.render.com](https://dashboard.render.com) et se connecter
2. Cliquer sur le service **Web Service** de l'API (ex. `mspr2-master`, pas le frontend)
3. Menu gauche : **Environment** (parfois sous **Settings** selon l'interface)
4. Section **Environment Variables** → **Add Environment Variable**
5. Renseigner :
   - **Key** : `DISCORD_WEBHOOK_URL`
   - **Value** : l'URL complète du webhook Discord
6. **Save Changes** — Render redéploie automatiquement l'API

> Si vous ne voyez pas **Environment** : vous êtes peut‑être sur le mauvais service (frontend static site) ou sur la page **Events/Logs**. Revenez à la liste des services et sélectionnez l'API Python (Docker).

Vérification : bouton **Tester Discord** sur `/config/capteurs` → message vert « Webhook configuré ».

**Ne pas** committer l'URL dans Git — uniquement dans Render + fichiers `.env` locaux (gitignored).

## Déploiement

Déclenché par GitHub Actions sur push `master` / `main` → Deploy Hooks Render (`RENDER_BACKEND_DEPLOY_HOOK`, `RENDER_FRONTEND_DEPLOY_HOOK`).

### Configuration Render (Docker)

Les Dockerfiles supposent un **contexte de build à la racine du dépôt** :

| Service | Root Directory | Dockerfile Path |
|---------|----------------|-----------------|
| Backend | *(vide — racine repo)* | `siege/api/Dockerfile` |
| Frontend | *(vide — racine repo)* | `siege/frontend/Dockerfile` |

Variable frontend : `VITE_API_BASE_URL=https://mspr2-master.onrender.com`

## Local vs Render

| | Local | Render |
|---|-------|--------|
| MQTT / ESP32 | Oui (`mosquitto-bresil`) | Non |
| Simulateurs EC/CO | Oui | Non |
| Frontend | `localhost` (nginx) ou dev Vite | Static site Render |
| Source données | BDD pays (MQTT) | BDD siège Aiven |

## Health check

Render vérifie `GET /health` sur l'API siège.

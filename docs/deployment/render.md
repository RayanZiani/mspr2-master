# Déploiement sur Render

## Configuration des services

### 1. API Brésil (Web Service)
- **Name**: `futurekawa-api-bresil`
- **Root Directory**: `pays/bresil/api`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `DATABASE_URL`: URL MySQL depuis Render
  - `MQTT_BROKER`: Broker MQTT externe ou service Render

### 2. API Équateur (Web Service)
- **Name**: `futurekawa-api-equateur`
- **Root Directory**: `pays/equateur/api`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. API Colombie (Web Service)
- **Name**: `futurekawa-api-colombie`
- **Root Directory**: `pays/colombie/api`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 4. API Siège (Web Service)
- **Name**: `futurekawa-api-siege`
- **Root Directory**: `siege/api`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `MYSQL_URL`: Base de données principale
  - `REDIS_URL`: Redis cache (Render Redis instance)
  - `API_BRESIL_URL`: https://futurekawa-api-bresil.onrender.com
  - `API_EQUATEUR_URL`: https://futurekawa-api-equateur.onrender.com
  - `API_COLOMBIE_URL`: https://futurekawa-api-colombie.onrender.com

### 5. Frontend (Static Site)
- **Name**: `futurekawa-frontend`
- **Root Directory**: `siege/frontend`
- **Build Command**: `npm install && npm run build`
- **Publish Directory**: `dist`
- **Environment Variables**:
  - `VITE_API_URL`: https://futurekawa-api-siege.onrender.com

## Health Checks

Render vérifie automatiquement `/health` pour chaque service. Assurez-vous que tous vos services exposent cet endpoint.

## Tests d'intégration sur Render

Pour tester la stack déployée, configurez ces variables d'environnement dans votre CI/CD :

```bash
export RENDER=true
export BASE_URL=https://futurekawa.onrender.com
export API_BRESIL_URL=https://futurekawa-api-bresil.onrender.com
export API_EQUATEUR_URL=https://futurekawa-api-equateur.onrender.com
export API_COLOMBIE_URL=https://futurekawa-api-colombie.onrender.com

bash ci-cd/scripts/wait_for_stack.sh
```

## Différences avec Docker local

| Aspect | Local Docker | Render Production |
|--------|--------------|-------------------|
| Réseau | `host.docker.internal` | URLs publiques HTTPS |
| Base de données | MySQL local | Render PostgreSQL/MySQL |
| MQTT | Mosquitto local | Service externe (CloudMQTT, etc.) |
| Redis | Redis local | Render Redis |
| Health checks | Script manuel | Render automatique |
| Frontend | Vite dev server | Build statique optimisé |

## Notes importantes

1. **Frontend Vite** : En production, utilisez `npm run build` pour générer des fichiers statiques optimisés
2. **MQTT** : Render ne supporte pas MQTT nativement. Utilisez un service externe comme:
   - CloudMQTT
   - HiveMQ Cloud
   - AWS IoT Core
3. **Bases de données** : Créez des instances PostgreSQL ou MySQL séparées sur Render
4. **Variables d'environnement** : Configurez-les dans le dashboard Render pour chaque service

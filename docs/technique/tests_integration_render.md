# Tests d'intégration — API Siège + Aiven

## Contexte

L'application utilise **une base Aiven MySQL** partagée. En production (Render) et en CI Jenkins, seuls l'**API Siège** et le **frontend** sont déployés :

- API Siège : `https://mspr2-master.onrender.com`
- Frontend : `https://mspr2-master-front.onrender.com`

Les tests d'intégration ciblent l'API Siège, qui lit directement Aiven (`/stocks/`, `/alertes/`, `/mesures/`).

## Mode dual (helpers)

Le fichier `tests/integration/helpers.py` expose les mêmes scénarios partout :

| Donnée | Render / CI (`RENDER=true`) | Docker local (dev) |
|--------|----------------------------|---------------------|
| Lots par pays | `GET /stocks/` (agrégation) | `GET /stocks/` ou API pays legacy |
| Alertes | `GET /alertes/` filtré par pays | idem |
| Mesures | `GET /mesures/?lot_id=...` | idem |

**43 tests, 0 skip** en CI Render depuis la refactorisation dual-mode.

## Configuration Jenkins

```groovy
environment {
    RENDER = 'true'
    API_SIEGE_URL = 'https://mspr2-master.onrender.com'
    FRONTEND_URL = 'https://mspr2-master-front.onrender.com'
}
```

`tests/integration/conftest.py` :
- attend que `/health` et `/auth/login` répondent (retry cold start Render)
- fixtures `auth_headers`, `bresil_lot_id` via agrégation `/stocks/`

## Exécution

```bash
# CI Render (comme Jenkins)
export RENDER=true
export API_SIEGE_URL=https://mspr2-master.onrender.com
bash ci-cd/scripts/run_tests.sh integration

# Local contre API Docker siège (Aiven en backend)
bash ci-cd/scripts/run_tests.sh integration
```

## Fichiers de tests

| Fichier | Rôle |
|---------|------|
| `test_api_auth.py` | Login, JWT, permissions |
| `test_api_countries.py` | FIFO, lots, alertes, mesures (via helpers) |
| `test_api_health.py` | Health siège + disponibilité pays dans `/stocks/` |
| `test_api_siege.py` | Endpoints siège classiques |
| `test_api_siege_aggregation.py` | Structure agrégation multi-pays |

## wait_for_stack.sh

En mode `RENDER=true`, vérifie uniquement l'API Siège et le frontend Render (pas d'APIs pays séparées).

## Avantages

1. **Réalisme** : tests sur l'environnement de production
2. **Couverture** : 100 % des scénarios via agrégation Aiven
3. **Stabilité** : pas de MySQL Docker à provisionner en CI
4. **Maintenabilité** : un seul point d'entrée API en tests

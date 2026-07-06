# Résumé : Tests d'intégration sur Render + Aiven

**Objectif** : suite de tests d'intégration ciblant l'API Siège connectée à **Aiven MySQL**, en local comme en CI.

## Architecture actuelle

| Environnement | API | Base de données |
|---------------|-----|-----------------|
| Render (prod) | `https://mspr2-master.onrender.com` | Aiven |
| Docker local (`npm start`) | `http://localhost/api` | **Même Aiven** |
| CI Jenkins | `RENDER=true` → API Render | Aiven |

Pas d'APIs pays séparées en production. Pas de MySQL Docker.

## Changements tests (2026)

### `tests/integration/helpers.py`

Accès dual aux données pays via agrégation `/stocks/`, `/alertes/`, `/mesures/?lot_id=`.

### Résultat CI

- **43 tests** d'intégration
- **0 skip** sur Render
- Retry cold start + login dans `conftest.py`

### Fichiers clés

- `tests/integration/test_api_countries.py` — FIFO, lots, mesures
- `tests/integration/test_api_siege_aggregation.py` — structure multi-pays
- `ci-cd/scripts/run_tests.sh integration` — log mode Render

## Exécution

```bash
export RENDER=true
export API_SIEGE_URL=https://mspr2-master.onrender.com
bash ci-cd/scripts/run_tests.sh integration
```

Documentation complète : [`tests_integration_render.md`](tests_integration_render.md)

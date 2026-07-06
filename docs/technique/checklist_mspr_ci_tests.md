# Checklist MSPR — viser 30/20 (niveau 3)

## Compétence : Tests applicatifs

| Critère jury | Preuve dans le repo | Statut |
|---|---|---|
| Plan de test (unitaire, intégration, recette) | `docs/technique/plan_tests.md` | OK |
| Données de test + résultats attendus | Seuils 3 pays, comptes `USERS.md`, Postman env | OK |
| Mise en œuvre avec jeux d'essai | 20 tests unitaires + intégration + Newman + Playwright | OK |
| Outil de testing | pytest, Newman, Playwright, Allure | OK |
| Gestion anomalies | `docs/technique/gestion_anomalies_tests.md` | OK |

## Compétence : Intégration continue

| Critère jury | Preuve dans le repo | Statut |
|---|---|---|
| Outil CI installé/paramétré | `docker-compose.ci.yml` + Jenkins Dockerfile | OK |
| Pipeline automatisé | `ci-cd/Jenkinsfile` (12 stages) | OK |
| Build + tests + qualité + packaging | Lint, Bandit, SonarQube, Quality Gate (6 conditions) | OK |
| Documentation + preuve d'exécution | `docs/technique/ci_cd.md` + artefacts JUnit | OK |

## Pipeline Jenkins — 12 stages

1. Checkout
2. Install (Python + Node + Playwright)
3. Lint (Flake8)
4. Build Docker
5. Démarrage stack + health checks
6. Tests unitaires (20 tests)
7. Analyse statique (Pylint + Bandit)
8. Tests intégration (API + auth JWT)
9. Tests API Newman (10 requêtes)
10. Tests E2E Playwright (5 scénarios + auth)
11. SonarQube
12. Quality Gate + Docker Push (main/develop)

## Commandes pour démo jury

```powershell
# 1. Installer
pip install -r tests/requirements.txt
pip install -r pays/bresil/api/requirements.txt
npm install
npx playwright install chromium

# 2. Stack CI (Jenkins + SonarQube)
npm run ci:up

# 3. Stack applicative
npm run start:detached
npm run wait:stack

# 4. Tous les tests
npm run test

# 5. Rapport Allure
npm run allure:report
```

## Captures à préparer pour la soutenance

1. Jenkins Stage View (12 stages verts)
2. SonarQube dashboard — Quality Gate PASSED
3. Rapport coverage HTML dans Jenkins
4. `npm run test:unit` — 20 passed
5. Newman CLI — 0 failed assertions

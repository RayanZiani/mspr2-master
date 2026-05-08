# Plan de tests

## Tests unitaires (pytest)
- `test_alert_service.py` : logique seuils ±3°C / ±2% + péremption 365j
- `test_lots.py` : tri FIFO par date_stockage, changement de statut
- `test_mesures.py` : insertion et récupération de mesures

## Tests API (Postman + Newman)
- Health check de chaque API pays
- CRUD lots via REST
- Agrégation siège (appels multi-pays)

## Tests E2E (Playwright)
- Chargement du dashboard et affichage des lots (AG Grid)
- Navigation vers le détail d'un lot et affichage des courbes (Recharts)

## Rapports (Allure)
- Générer avec : `allure generate tests/reports --clean`

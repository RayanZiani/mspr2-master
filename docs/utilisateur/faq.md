# FAQ — FutureKawa

**Q : Comment lancer la plateforme complète ?**
R : Depuis la racine du repo : `docker compose up --build`

**Q : Comment simuler les capteurs IoT sans ESP32 ?**
R : `python iot/simulator/simulate_sensor.py --pays bresil --entrepot entrepot_A`

**Q : Où voir les alertes ?**
R : Sur l'interface web, onglet Alertes. Les emails sont envoyés automatiquement via Node-RED.

**Q : Comment accéder à la documentation API ?**
R : FastAPI génère Swagger automatiquement sur `/docs` pour chaque API.

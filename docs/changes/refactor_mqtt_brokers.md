Refactor MQTT subscribers & Mosquitto configs

Objectif
- Améliorer la robustesse et la lisibilité des APIs pays et des brokers sans changer la logique métier.

Modifications clés
- `api/main.py` (pour chaque pays) : ajout de logging et protection pour que le démarrage MQTT ne fasse pas planter l'API si le broker est indisponible.
- `api/services/mqtt_subscriber.py` (pour chaque pays) : remplacement du simple `connect()` par une boucle de reconnexion avec logs et handling d'erreurs.
- `broker/mosquitto.conf` (pour chaque pays) : ajout de commentaires, activation de la `persistence` et réglages légers (fichier de persistence, max inflight messages).
- `api/config.py` (bresil) : meilleure gestion de `DATABASE_URL` (support `mysql+aiomysql://`, suppression du param `ssl-mode` pour dev local), et chargement automatique de `.env`.

Pourquoi ces changements ?
- Permettre de démarrer et tester les APIs localement même sans Docker ou sans broker disponible.
- Faciliter la mise en production ultérieure (notes dans le fichier indiquent où sécuriser le broker et activer TLS pour la DB).

Points à présenter
- Ce que j'ai modifié (liste ci-dessus)
- Comment tester rapidement : lancer `uvicorn` localement (avec `PYTHONPATH=..`) ou lancer Docker Compose si Docker est dispo.
- Propositions futures : config TLS pour Aiven, contrôle d'accès MQTT (passwords), et monitors pour le broker.

Exemple de commande pour tester localement (Brésil) :

```powershell
cd "E:\mspr\mspr2 2026\mspr2-master\pays\bresil\api"
$env:PYTHONPATH = ".."
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```



# ARCHITECTURE — FutureKawa IoT

> **Fichier de référence technique** — à lire en premier avant tout travail sur ce repo.
> Contient tout le contexte nécessaire pour comprendre la structure, les choix technologiques, les contraintes et la répartition des responsabilités.

---

## 1. Contexte du projet

**FutureKawa** est une entreprise internationale de caféiculture et logistique de café vert, opérant dans 3 pays : **Brésil, Équateur, Colombie**.

Ce projet est une **MSPR académique** (Mise en Situation Professionnelle Reconstituée) dans le cadre du **Bloc 4 — RNCP 35584 Expert en Informatique et Système d'Information, Niveau 7**. L'évaluation se fait via une soutenance orale collective de 50 minutes (20 min exposé + 30 min questions jury) en **début juillet 2026**.

### Problème métier

Les entrepôts de stockage de café vert souffrent de :
- Relevés de température/humidité **manuels et hétérogènes**
- Absence de **traçabilité fiable** des lots
- Logique **FIFO** (First In First Out) difficile à appliquer sans visibilité centralisée
- Pas de détection proactive des dérives de conditions ou des lots périmés

### Solution cible

Une plateforme IoT multi-pays permettant de :
- **Surveiller automatiquement** les conditions de stockage (température, humidité) via ESP32 + DHT11 (prototype campus USB)
- **Centraliser** les données au siège via une architecture distribuée pays ↔ siège
- **Alerter** automatiquement par email en cas de dérive ou lot trop ancien
- **Visualiser** les stocks et courbes historiques via une interface web

---

## 2. Architecture globale

```
┌─────────────────────────────────────────────────────────────────┐
│              IoT / simulateurs (machine de dev)                  │
│  ESP32 USB → serial_to_mqtt → Mosquitto (optionnel, local)      │
│  simulate_releves_aiven.py / mqtt_bridge_bresil.py              │
└────────────────────────────┬────────────────────────────────────┘
                             │ INSERT releve_capteur
                             ▼
              ┌──────────────────────────────────┐
              │     Aiven MySQL (cloud)          │
              │  lot · capteur · releve_capteur  │
              │  pays · alerte · user_account    │
              └──────────────┬───────────────────┘
                             │ SQL (MYSQL_URL + TLS)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SIÈGE (central)                              │
│  ┌──────────────┐    ┌───────────┐    ┌──────────────────┐      │
│  │  FastAPI     │    │   Redis   │    │  React + Vite    │      │
│  │  API Siège   │◀──▶│  (cache)  │    │  Frontend Web    │      │
│  └──────┬───────┘    └───────────┘    └──────────────────┘      │
│         └──────────── Nginx ───────────────────▲                  │
└─────────────────────────────────────────────────────────────────┘
         Déploiement : Docker local (npm start) ou Render
```

**Règle clé** : **une seule base Aiven MySQL** pour tout le projet. L'API siège lit/écrit directement Aiven (`data_service.py`). Il n'y a **pas** de MySQL dans Docker ni de BDD par pays.

---

## 3. Structure du repo

```
futurekawa/
│
├── README.md                          # prise en main globale, commandes de lancement
├── .gitignore
├── docker-compose.yml                 # compose RACINE : siège uniquement (npm start)
│
├── database/                          # schéma BDD + CA SSL + données démo
│   ├── schema_mysql.sql               # DDL MySQL (tables + vues)
│   ├── seed_mysql.sql                 # seed minimal (BR/EC/CO + exemple)
│   ├── ca.pem                         # certificat CA (Aiven) pour TLS
│   └── demo_data.xlsx                 # jeu de données démo (relevés 5 min)
│
├── scripts/                           # scripts utilitaires (Windows friendly)
│   ├── push_mysql_schema.py           # applique database/schema_mysql.sql sur la BDD distante
│   ├── push_mysql_seed.py             # applique database/seed_mysql.sql sur la BDD distante
│   ├── generate_demo_excel.py         # génère database/demo_data.xlsx
│   └── import_demo_excel_to_mysql.py  # importe demo_data.xlsx dans MySQL (batch)
│
├── Documents/                         # CDC, grille éval, règles validation, techno sheet
│   ├── 25_26_I1_EISI_DEV_Sujet_MSPR_TPRE814.pdf
│   ├── 25_26_I1_EISI_DEV_Grille_évaluation_MSPR_TPRE814.pdf
│   ├── Régles_validation_MSPR.pdf
│   └── techno_stack.png               # image des technologies retenues validées
│
├── pays/
│   ├── bresil/
│   │   ├── docker-compose.yml         # legacy / MQTT optionnel (pas de MySQL local)
│   │   ├── .env.example
│   │   ├── api/                       # FastAPI Python (tests unitaires, legacy)
│   │   │   ├── Dockerfile
│   │   │   ├── requirements.txt
│   │   │   ├── main.py
│   │   │   ├── config.py              # ⚠ seuils Brésil : 29°C / 55% humidité
│   │   │   ├── models/
│   │   │   │   ├── lot.py
│   │   │   │   └── mesure.py
│   │   │   ├── routes/
│   │   │   │   ├── lots.py            # CRUD lots + tri FIFO par date de stockage
│   │   │   │   └── mesures.py         # historique temp/humidité
│   │   │   ├── services/
│   │   │   │   ├── mqtt_subscriber.py # souscrit au broker Mosquitto local
│   │   │   │   └── alert_service.py   # règles seuils ±3°C / ±2% + péremption 365j
│   │   │   └── db/
│   │   │       └── database.py        # SQLAlchemy → Aiven (MYSQL_URL)
│   │   ├── broker/
│   │   │   └── mosquitto.conf         # topic : futurekawa/bresil/{entrepot}/sensors
│   │   └── node-red/
│   │       └── flows.json             # MQTT → règles seuils → email SMTP
│   │
│   ├── equateur/                      # structure identique à bresil/
│   │   └── api/config.py              # ⚠ seuils Équateur : 31°C / 60% humidité
│   │
│   └── colombie/                      # structure identique à bresil/
│       └── api/config.py              # ⚠ seuils Colombie : 26°C / 80% humidité
│
├── siege/
│   ├── docker-compose.yml             # api-siege + redis + nginx + frontend
│   ├── .env.example
│   ├── api/                           # FastAPI central → Aiven
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── config.py                  # MYSQL_URL Aiven, Redis, auth
│   │   ├── routes/
│   │   │   ├── stocks.py
│   │   │   ├── mesures.py
│   │   │   └── alertes.py
│   │   └── services/
│   │       ├── data_service.py        # requêtes SQL directes Aiven
│   │       └── redis_cache.py         # cache Redis
│   │
│   ├── frontend/                      # React + Vite
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   ├── vite.config.js
│   │   ├── src/
│   │   │   ├── main.jsx
│   │   │   ├── App.jsx
│   │   │   ├── components/
│   │   │   │   ├── CountrySelector/
│   │   │   │   ├── LotList/           # tri FIFO, badge statut (conforme/alerte/périmé)
│   │   │   │   ├── LotDetail/
│   │   │   │   ├── Charts/            # ⚠ Recharts ou Chart.js (PAS AG Grid pour les courbes)
│   │   │   │   ├── LotTable/          # AG Grid OK uniquement pour la liste des lots
│   │   │   │   └── AlertBadge/
│   │   │   ├── pages/
│   │   │   │   ├── Dashboard.jsx
│   │   │   │   ├── LotView.jsx
│   │   │   │   └── AlertsPage.jsx
│   │   │   ├── hooks/
│   │   │   │   ├── useStocks.js       # React Query (fetching + cache + refresh auto)
│   │   │   │   └── useAlerts.js
│   │   │   └── services/
│   │   │       └── api.js             # appels vers API siège uniquement
│   │   └── .env.example
│   │
│   └── nginx/
│       └── nginx.conf                 # /api → siege-api  |  / → frontend
│
├── iot/
│   ├── README.md                      # schéma câblage + chaîne USB/série
│   ├── esp32.ino                      # firmware Arduino — DHT11, sortie série USB
│   ├── bridge/
│   │   └── serial_to_mqtt.py          # pont série → MQTT (prototype campus)
│   ├── firmware/                      # référence MicroPython + WiFi (non utilisé campus)
│   │   ├── main.py                    # MicroPython — entry point ESP32
│   │   ├── config.py                  # WiFi SSID/PWD, IP broker, topic MQTT
│   │   ├── mqtt_client.py             # umqtt.simple
│   │   └── sensor_dht.py             # lecture DHT22 (temp + humidité)
│   ├── wiring/
│   │   └── schema_cablage.png
│   └── simulator/
│       └── simulate_sensor.py         # ⚠ fallback si ESP32 défaillant en démo
│
├── ci-cd/
│   ├── Jenkinsfile                    # pipeline : build → pytest → newman → sonar → docker build → push
│   ├── sonar-project.properties
│   └── scripts/
│       ├── run_tests.sh
│       └── build_images.sh
│
├── tests/
│   ├── unit/                          # pytest
│   │   ├── conftest.py
│   │   ├── test_lots.py
│   │   ├── test_mesures.py
│   │   └── test_alert_service.py
│   ├── api/                           # Postman + Newman
│   │   ├── FutureKawa.postman_collection.json
│   │   └── FutureKawa.postman_environment.json
│   ├── e2e/                           # Playwright
│   │   ├── playwright.config.js
│   │   └── specs/
│   │       ├── dashboard.spec.js
│   │       └── lot_detail.spec.js
│   └── reports/
│       └── .gitkeep                   # Allure output — gitignored sauf exemple
│
└── docs/                              # Mohammed (responsable documentation)
    ├── architecture/
    │   ├── schema_global.drawio        # reprend Fig.1 du sujet + complète
    │   └── automatisation_phase2_futurekawa.drawio # capteurs → décision → actionneurs (livrable 9)
    ├── technique/
    │   ├── README_lancement.md
    │   ├── mqtt_topics.md              # topics, formats payload, fréquence
    │   └── plan_tests.md
    ├── utilisateur/
    │   ├── guide_entrepot.md           # profil terrain (livrable 8)
    │   ├── guide_siege.md              # profil supervision
    │   └── faq.md
    └── conduite_changement/
        ├── plan_4_axes.docx            # livrable conduite du changement
        └── questionnaire_phase2.md     # livrable 10 — interview automatisation
```

---

## 4. Stack technologique complète

> Source : grille de validation officielle (techno_stack.png dans `/Documents`)

### Infrastructure / DevOps
| Composant | Technologie | Statut CDC | Notes |
|---|---|---|---|
| Conteneurisation | **Docker Compose** | ⛔ Imposé | 1 compose par pays + 1 compose siège |
| Reverse proxy | **Nginx** | ✅ Validé | Routing API siège → pays |
| Pipeline CI | **Jenkins + Jenkinsfile** | ⛔ Imposé | Étapes : build → pytest → sonar → docker push |
| Qualité code | **SonarQube** | ✅ Validé | Quality Gate dans le Jenkinsfile |
| Registry images | **Docker Hub** | ✅ Validé | Nommer les images `futurekawa-{pays}` |
| Versioning | **Git + GitHub** | ⛔ Imposé | Branches : `main`, `develop`, `feature/*` |

### Backend
| Composant | Technologie | Statut CDC | Notes |
|---|---|---|---|
| Framework API (pays) | **FastAPI (Python)** | ✅ Validé | Swagger auto-généré, async natif |
| Framework API (siège) | **FastAPI (Python)** | ✅ Validé | Cohérence avec backends pays |
| Base de données | **MySQL (Aiven cloud)** | ✅ Validé | Une instance partagée — pas de BDD Docker locale |
| Cache siège | **Redis** | ✅ Validé | Cache stocks/mesures (optionnel sur Render) |
| Communication inter-services | **REST / JSON** | ✅ Validé | Documentable via Swagger |
| Broker MQTT | **Mosquitto × 3** | ⛔ Imposé | 1 broker par pays dans son Docker Compose |
| Alertes email | **Node-RED** | ✅ Validé | Flux MQTT → règles seuils → SMTP |
| Documentation API | **Swagger UI / OpenAPI** | ✅ Validé | Généré automatiquement par FastAPI |

---

## 4.1 Base de données (Aiven MySQL) — Schéma, connexion SSL, données de démo

### Schéma (DDL)
- `database/schema_mysql.sql` : création des tables **pays / exploitation / entrepot / lot / capteur / releve_capteur / alerte** + vues de démo.
- `database/seed_mysql.sql` : seed minimal (BR/EC/CO + 1 exemple).

### Connexion Aiven (SSL)
- **URL** : `MYSQL_URL=mysql://user:pass@host:port/defaultdb?ssl-mode=REQUIRED`
- **Certificat CA** : `database/ca.pem` (monté dans le conteneur API siège)
- **Utilisée par** : API siège (local + Render), scripts Python, simulateurs IoT

⚠️ **Sécurité** : ne jamais commiter `.env` (contient un mot de passe).

### Scripts « push » vers Aiven (sans client mysql local)
- `scripts/push_mysql_schema.py` : applique `database/schema_mysql.sql`
- `scripts/push_mysql_seed.py` : applique `database/seed_mysql.sql`

Commandes :
```powershell
.\.venv\Scripts\python .\scripts\push_mysql_schema.py
.\.venv\Scripts\python .\scripts\push_mysql_seed.py
```

### Données de démonstration (Excel → Aiven)
- Génération : `scripts/generate_demo_excel.py` produit `database/demo_data.xlsx`
  - Relevés toutes les **5 minutes** du **08/05/2026** au **31/07/2026** (pour alimenter les courbes).
- Import : `scripts/import_demo_excel_to_mysql.py` charge l'Excel dans **Aiven**

Commandes :
```powershell
.\.venv\Scripts\python .\scripts\generate_demo_excel.py
.\.venv\Scripts\python .\scripts\import_demo_excel_to_mysql.py
```

### Frontend
| Composant | Technologie | Statut CDC | Notes |
|---|---|---|---|
| Framework | **React + Vite** | ✅ Validé | Dans la webographie du sujet |
| Graphiques courbes | **Recharts ou Chart.js** | ⚠️ À corriger | AG Grid ≠ outil de courbes. Utiliser Recharts/Chart.js pour temp/humidité |
| Tableau liste lots | **AG Grid** | ✅ Validé | OK pour afficher la liste des lots uniquement |
| Styles | **CSS custom** | ✅ Validé | Prévoir Tailwind ou design system léger |
| Gestion d'état | **React Query** | ✅ Validé | Fetching + cache + refresh automatique données IoT |

### IoT
| Composant | Technologie | Notes |
|---|---|---|
| Microcontrôleur | **ESP32** | Arduino (sketch `esp32.ino`) |
| Capteur | **DHT11** | Température + humidité (matériel campus) |
| Connexion | **USB / port série** | Pas de WiFi sur l'ESP32 |
| Pont PC | **`serial_to_mqtt.py`** | Relais série → MQTT sur le PC |
| Protocole | **MQTT (Mosquitto)** | Topics : `futurekawa/{pays}/{entrepot}/sensors` |
| Firmware | **Arduino (`esp32.ino`)** | Référence MicroPython + WiFi dans `iot/firmware/` (non utilisé) |

### Tests
| Type | Outil | Responsable |
|---|---|---|
| Tests unitaires | **pytest** | Julien |
| Tests API | **Postman + Newman** | Julien |
| Tests E2E / UI | **Playwright** | Julien |
| Rapports | **Allure Report** | Julien |

### Collecte des besoins
| Composant | Technologie | Notes |
|---|---|---|
| Questionnaire | **Google Forms** | |
| Retranscription visuelle | **Miro** | User flows + wireframes |

### Documentation / Conduite du changement
| Composant | Technologie | Responsable |
|---|---|---|
| Documentation utilisateur | **Notion** | Mohammed |
| Schéma architecture | **Draw.io** | Mohammed |
| Plan 4 axes + docs | **Notion / Word** | Mohammed |
| Support soutenance | **Diaporama (PowerPoint / Google Slides)** | Mohammed |
| Plan comm. conduite du changement | **Plan comm. 4 axes** | ⛔ Imposé — Mohammed |

---

## 5. Répartition des responsabilités

| Membre | Périmètre | Technos principales |
|---|---|---|
| **Elyes** | IoT + pont MQTT → Aiven | Mosquitto local, scripts simulateurs |
| **Rayan** | API Pays 1/2/3 (collab Elyes) + Frontend Web | FastAPI, React/Vite, Recharts |
| **Julien** | API Siège + CI/CD + Tests | FastAPI, Jenkins, pytest, Playwright, Newman |
| **Mohammed** | Documentation complète + Plan 4 axes + Notion | Draw.io, Notion, Word |

---

## 6. Règles métier critiques

### Seuils de conditions par pays
```python
SEUILS = {
    "bresil":   {"temp": 29, "humidity": 55},
    "equateur": {"temp": 31, "humidity": 60},
    "colombie": {"temp": 26, "humidity": 80},
}
TOLERANCES = {"temp": 3, "humidity": 2}  # ±3°C, ±2%
```

### Logique d'alerte
Une alerte est déclenchée et un email est envoyé au responsable d'exploitation si :
- `abs(mesure.temp - seuil.temp) > 3` (température hors plage)
- `abs(mesure.humidity - seuil.humidity) > 2` (humidité hors plage)
- `(today - lot.date_stockage).days > 365` (lot périmé)

### Modèle de données minimal (par lot)
```
Lot {
  id          : UUID unique
  pays        : bresil | equateur | colombie
  exploitation: string
  entrepot    : string
  date_stockage: datetime          # ← tri FIFO basé sur ce champ
  statut      : conforme | alerte | perime
}

Capteur {
  id          : UUID
  entrepot_id : FK → Entrepot
  numero_serie: string
}

ReleveCapteur {
  id          : int (auto)
  capteur_id  : FK → Capteur
  timestamp   : datetime
  temperature : float (°C)
  humidite    : float (%)
}
```

### Topics MQTT
```
futurekawa/{pays}/{entrepot}/sensors
  payload JSON : { "temp": 29.4, "humidity": 54.1, "timestamp": "...", "lot_id": "..." }

Exemples :
  futurekawa/bresil/entrepot_A/sensors
  futurekawa/equateur/entrepot_B/sensors
  futurekawa/colombie/entrepot_C/sensors
```

---

## 7. Conventions Git

```
Branches :
  main          → stable, démo jury, protégée (merge via PR uniquement)
  develop       → intégration continue, Jenkins build auto
  feature/*     → une branche par tâche (ex: feature/api-siege-aggregator)

Commits :
  feat: ajout de la route /lots avec tri FIFO
  fix: correction seuil humidité Colombie
  ci: ajout stage SonarQube dans Jenkinsfile
  docs: guide utilisateur entrepôt

Images Docker Hub :
  futurekawa-bresil
  futurekawa-equateur
  futurekawa-colombie
  futurekawa-siege-api
  futurekawa-siege-front
```

---

## 8. Lancement rapide (démo jury)

```bash
# Lancer TOUT en une commande depuis la racine
docker compose up --build

# Lancer uniquement un pays
cd pays/bresil && docker compose up --build

# Lancer uniquement le siège
cd siege && docker compose up --build

# Lancer les tests
cd tests && bash ../ci-cd/scripts/run_tests.sh

# Simuler l'IoT sans ESP32 (fallback démo)
python iot/simulator/simulate_sensor.py --pays bresil --entrepot entrepot_A
```

---

## 9. Livrables attendus pour la soutenance (juillet 2025)

| # | Livrable | Responsable | Statut |
|---|---|---|---|
| 1 | Backend pays exemple conteneurisé (Brésil) | Elyes + Rayan | — |
| 2 | Backend central siège + Frontend Web | Julien + Rayan | — |
| 3 | Prototype IoT fonctionnel (ESP32 + DHT11, USB) | Elyes | — |
| 4 | Documentation technique (archi + IoT + tests) | Mohammed | — |
| 5 | Pipelines CI/CD Jenkins | Julien | — |
| 6 | Tests lançables manuellement | Julien | — |
| 7 | Code source versionné sur Git | Tous | — |
| 8 | Documentation utilisateur orientée métier | Mohammed | — |
| 9 | Schéma automatisation phase 2 (Draw.io) | Mohammed | — |
| 10 | Questionnaire interview cadrage phase 2 | Mohammed | — |

---

## 10. Points de vigilance

> Ces points ont été identifiés lors de la lecture de la grille d'évaluation et de la techno sheet validée.

- **AG Grid ≠ courbes** : AG Grid est validé uniquement pour la **liste des lots**. Les courbes température/humidité doivent utiliser **Recharts ou Chart.js**. C'est une erreur que le jury pourrait relever.
- **MySQL vs PostgreSQL** : le CDC cite PostgreSQL mais l'équipe a choisi MySQL. **Préparer une justification orale** (compatibilité, familiarité, performances suffisantes pour le prototype).
- **1 broker par pays** : chaque `docker-compose.yml` pays doit contenir son propre Mosquitto. Ne pas partager un broker entre pays.
- **Swagger** : FastAPI le génère automatiquement sur `/docs`. Ne pas oublier de le mentionner en soutenance — c'est un point de la grille.
- **Branches Git** : le jury peut demander à voir l'historique. S'assurer que `main`, `develop` et au moins quelques `feature/*` existent avant la soutenance.
- **docker compose up doit marcher en 1 commande** depuis la racine. Tester sur une machine vierge si possible.
- **Simulator IoT** : avoir `simulate_sensor.py` fonctionnel est non-négociable comme plan B pour la démo.
- **Allure Report** : générer un rapport de test avant la soutenance et le conserver — le jury aime voir des captures.
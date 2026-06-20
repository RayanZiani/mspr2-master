# Architecture IoT — Aiven unique

## Principe

**Une seule base MySQL (Aiven)** pour toute l'application : siège, lots, capteurs, relevés.

En local, seuls des **scripts Python** simulent les capteurs et écrivent dans `releve_capteur`.

```
scripts/simulate_releves_aiven.py
    │  affichage console toutes les 5 s
    │  INSERT releve_capteur toutes les 60 s
    ▼
Aiven MySQL (releve_capteur, lot, capteur, entrepot…)
    ▲
    │  lecture stocks + courbes
siege/api (Render ou Docker local)
    ▼
frontend siège
```

Il n'y a **plus de MySQL Docker local** ni de table `mesures` séparée par pays.

---

## Démarrage local

### 1. Stack siège (UI + API)

```bash
npm start
# → http://localhost
```

### 2. Vider les anciens relevés démo (une fois)

```bash
npm run sim:clear
# ou : powershell -File scripts/clear_releve_capteur_aiven.ps1
```

Conserve : pays, entrepôts, lots, capteurs, alertes.

### 3. Lancer les simulateurs capteurs

```bash
npm run sim:start
```

Comportement (cycle **30 secondes**) :

- **Console** : releves groupes par pays (`--- BRESIL ---`, `--- EQUATEUR ---`, etc.)
- **BDD** : 1 INSERT par capteur actif a chaque cycle (6 capteurs en mode ALL = 6 lignes, car 2 entrepots par pays dans l'Excel demo)

Un capteur actif par entrepôt Excel (`Entrepôt BR-1`, `Entrepôt EC-1`, etc.) — 6 capteurs au total.

Simuler un seul pays :

```powershell
powershell -File scripts/start_simulateurs.ps1 -Pays EC
```

Arrêter le simulateur (autre terminal) :

```bash
npm run sim:stop
```

**Important** : ne lance qu’**une seule** instance (`sim:start`). Un second processus (ex. test `--pays BR` avec un intervalle différent) fausse les courbes Brésil.

Ancienne stack Docker (MySQL local + MQTT) : si des conteneurs tournent encore, arrête-les :

```bash
docker stop api-bresil api-equateur api-colombie simulator-bresil simulator-equateur simulator-colombie mysql-bresil mysql-equateur mysql-colombie
```

---

## ESP32 Brésil (capteur reel)

Frequence IoT documentee : **toutes les 30 secondes**  
(`iot/firmware/config.py` → `READ_INTERVAL = 30`, aligne avec `docs/technique/mqtt_topics.md`).

### Chaine complete

```
ESP32 DHT22 (30 s)
    |  MQTT futurekawa/bresil/entrepot_A/sensors
    v
mosquitto local (npm run iot:up, port 1883)
    |
scripts/mqtt_bridge_bresil.py (npm run iot:bridge)
    |  map entrepot_A -> Entrepot BR-1 / BR-SENSOR-01
    v
releve_capteur (Aiven) -> dashboard siege
```

### Configuration ESP32

1. Flasher le firmware (`iot/README.md`)
2. Dans `iot/firmware/config.py` :
   - `WIFI_SSID` / `WIFI_PSK` : ton reseau WiFi
   - `MQTT_BROKER` : IP du PC (ex. `192.168.1.100`)
   - `ENTREPOT = "entrepot_A"` : capteur sur **Entrepot BR-1**

### Terminaux (capteur reel + sim EC/CO)

```bash
# T1 — broker MQTT
npm run iot:up

# T2 — pont Brésil -> Aiven (ecoute l'ESP32)
npm run iot:bridge

# T3 — simulateurs Equateur + Colombie uniquement (pas le BR)
npm run sim:start:ec-co
```

Sans ESP32 : `npm run sim:start` simule les 6 capteurs (dont Brésil).

---

## Render (production)

| Service | Rôle |
|---------|------|
| API Siège | Lit Aiven (`releve_capteur`) |
| Frontend | Courbes + stocks multi-pays |

Les simulateurs tournent **sur ta machine** (pas sur Render) et alimentent la même BDD Aiven.

---

## Import initial des lots / entrepôts

Si la BDD est vide (hors relevés) :

```bash
python scripts/import_demo_excel_to_mysql.py
```

Puis `npm run sim:clear` pour repartir sans historique de températures.

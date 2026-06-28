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

Surveillance seuils + Discord (dernier releve Aiven, toutes les 60 s) :

```bash
npm run sim:watch
npm run sim:watch:stop
npm run sim:test-alert    # injecte un releve hors seuil (demo)
```

Documentation detaillee : [`docs/technique/surveillance_seuils.md`](surveillance_seuils.md)

Utile en parallele du simulateur ou du pont MQTT : re-verifie les lots et envoie une alerte Discord si hors seuils.

**Important** : ne lance qu’**une seule** instance (`sim:start`). Un second processus (ex. test `--pays BR` avec un intervalle différent) fausse les courbes Brésil.

Ancienne stack Docker (MySQL local + MQTT) : si des conteneurs tournent encore, arrête-les :

```bash
docker stop api-bresil api-equateur api-colombie simulator-bresil simulator-equateur simulator-colombie mysql-bresil mysql-equateur mysql-colombie
```

---

## ESP32 Brésil (capteur réel, connexion USB)

Fréquence du sketch Arduino : **toutes les 20 secondes**  
(`iot/esp32.ino` → `delay(20000)`).

Pas de WiFi sur l'ESP32 : le PC fait le relais série → MQTT via `iot/bridge/serial_to_mqtt.py`.

### Chaîne complète

```
ESP32 + DHT11 (esp32.ino, ~20 s)
    |  USB / port série (ex. COM3)
    v
iot/bridge/serial_to_mqtt.py (sur le PC)
    |  MQTT futurekawa/bresil/entrepot_A/sensors
    v
mosquitto local (npm run iot:up, port 1883)
    |
scripts/mqtt_bridge_bresil.py (npm run iot:bridge)
    |  map entrepot_A -> Entrepot BR-1 / BR-SENSOR-01
    v
releve_capteur (Aiven) -> dashboard siege
```

### Mise en route

1. Flasher `esp32.ino` (Arduino IDE, voir `iot/README.md`)
2. Brancher l'ESP32 en USB au PC
3. Lancer les terminaux ci-dessous (adapter le port COM dans `npm run iot:serial`)

### Terminaux (capteur réel + sim EC/CO)

```bash
# T1 — broker MQTT
npm run iot:up

# T2 — pont Brésil -> Aiven
npm run iot:bridge

# T3 — pont série -> MQTT (ESP32 USB)
npm run iot:serial

# T4 — simulateurs Equateur + Colombie uniquement (pas le BR)
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

---

## Seuils et alertes Discord

- Seuils **min / max** par pays (table `pays` sur Aiven)
- UI admin : menu compte → **Config capteurs** (`/config/capteurs`)
- Chaque INSERT releve (simulateur ou pont MQTT) :
  - compare temp/humidite aux seuils
  - lot → `ALERTE` + ligne `alerte` + Discord si configure

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

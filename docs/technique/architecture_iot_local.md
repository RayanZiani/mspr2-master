# Architecture IoT — Aiven unique

## Principe

**Une seule base MySQL (Aiven)** pour toute l'application : développement local, CI, Render et simulateurs.

```
scripts/simulate_releves_aiven.py  ──┐
scripts/mqtt_bridge_bresil.py      ──┼──► INSERT releve_capteur
iot/bridge + Mosquitto (optionnel) ──┘
                    │
                    ▼
         Aiven MySQL (lot, capteur, releve_capteur, alerte…)
                    ▲
                    │  SELECT stocks / mesures / alertes
         siege/api (Docker local ou Render)
                    ▼
              frontend siège
```

Pas de conteneur MySQL dans Docker. Pas de table `mesures` séparée par pays.

---

## Démarrage local

### 1. Stack siège (UI + API)

Configurer `MYSQL_URL` (Aiven) dans `.env` et `siege/.env`, puis :

```bash
npm start
# → http://localhost
```

### 2. Vider les anciens relevés démo (une fois)

```bash
npm run sim:clear
```

Conserve : pays, entrepôts, lots, capteurs, alertes.

### 3. Lancer les simulateurs capteurs

```bash
npm run sim:start
```

Comportement (cycle **30 secondes**) :

- **Console** : relevés groupés par pays
- **BDD Aiven** : 1 INSERT par capteur actif à chaque cycle

Simuler un seul pays :

```powershell
powershell -File scripts/start_simulateurs.ps1 -Pays EC
```

Arrêter :

```bash
npm run sim:stop
```

Surveillance seuils + Discord :

```bash
npm run sim:watch
npm run sim:watch:stop
npm run sim:test-alert
```

Documentation : [`surveillance_seuils.md`](surveillance_seuils.md)

**Important** : une seule instance de `sim:start` à la fois.

---

## ESP32 Brésil (capteur réel, USB)

Fréquence sketch : **20 s** (`iot/esp32.ino`).

```
ESP32 + DHT11
    │ USB / série
    v
iot/bridge/serial_to_mqtt.py
    │ MQTT futurekawa/bresil/entrepot_A/sensors
    v
mosquitto local (npm run iot:up, port 1883)
    │
scripts/mqtt_bridge_bresil.py (npm run iot:bridge)
    v
releve_capteur (Aiven) → dashboard siège
```

Terminaux :

```bash
npm run iot:up          # broker MQTT
npm run iot:bridge      # pont → Aiven
npm run iot:serial      # ESP32 USB
npm run sim:start:ec-co # simulateurs EC/CO uniquement
```

Sans ESP32 : `npm run sim:start` simule les 6 capteurs.

---

## Render (production)

| Service | Rôle |
|---------|------|
| API Siège | Lit **Aiven** |
| Frontend | Courbes + stocks multi-pays |

Les simulateurs tournent sur la machine de dev et alimentent **la même Aiven**.

---

## Import initial des lots / entrepôts

Si Aiven est vide (hors relevés) :

```bash
python scripts/import_demo_excel_to_mysql.py
```

Puis `npm run sim:clear` pour repartir sans historique de températures.

---

## Seuils et alertes Discord

- Seuils **min / max** par pays (table `pays` sur Aiven)
- UI admin : **Config capteurs** (`/config/capteurs`)
- Chaque INSERT relevé compare temp/humidité aux seuils et peut notifier Discord

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

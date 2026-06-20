# Topics MQTT

## Format général

```
futurekawa/{pays}/{entrepot}/sensors
```

## Payload JSON

```json
{
  "temp": 29.4,
  "humidity": 54.1,
  "timestamp": "2025-01-15T10:30:00Z",
  "lot_id": "uuid-du-lot"
}
```

## Exemples de topics

| Pays | Entrepôt | Topic complet |
|---|---|---|
| Brésil | entrepot_A | `futurekawa/bresil/entrepot_A/sensors` |
| Équateur | entrepot_B | `futurekawa/equateur/entrepot_B/sensors` |
| Colombie | entrepot_C | `futurekawa/colombie/entrepot_C/sensors` |

## Fréquence

| Source | Intervalle | Config |
|--------|------------|--------|
| **ESP32 réel (DHT22)** | **30 s** | `iot/firmware/config.py` → `READ_INTERVAL = 30` |
| Simulateur MQTT Docker | 30 s | `SIMULATE_INTERVAL` (défaut 30) |
| Simulateur Aiven (EC/CO) | 30 s | `scripts/simulate_releves_aiven.py --interval 30` |

## Brésil réel → dashboard Aiven

L'ESP32 ne parle pas à MySQL directement. Chaîne complète :

```
ESP32 (30 s) --MQTT--> broker local (1883)
                           |
              scripts/mqtt_bridge_bresil.py
                           |
                           v
              releve_capteur (Aiven)  <- Entrepot BR-1 / capteur BR-SENSOR-01
                           ^
              siege / frontend (courbes)
```

Mapping topic MQTT → BDD :

| Topic MQTT | Entrepôt Aiven | Capteur Excel |
|------------|----------------|---------------|
| `futurekawa/bresil/entrepot_A/sensors` | Entrepôt BR-1 | BR-SENSOR-01 |
| `futurekawa/bresil/entrepot_B/sensors` | Entrepôt BR-2 | BR-SENSOR-02 |

Commandes (3 terminaux si capteur réel + sim EC/CO) :

```bash
npm run iot:up              # broker MQTT
npm run iot:bridge          # pont Brésil -> Aiven
npm run sim:start:ec-co     # simule EC + CO seulement (ESP32 = BR)
```

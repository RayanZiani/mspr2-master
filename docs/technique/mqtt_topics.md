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

- Capteur réel (ESP32 + DHT22) : toutes les 30 secondes
- Simulateur démo : configurable via `--interval` (défaut 5s)

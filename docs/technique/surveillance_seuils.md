# Surveillance seuils et alertes Discord

Deux scripts complementaires au simulateur capteurs (`npm run sim:start`) pour **verifier les seuils** et **tester les alertes** sur Aiven.

## Prerequis

Fichier `.env` a la racine du projet :

```env
MYSQL_URL=mysql://...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

Propagation automatique au demarrage Docker : `npm start` execute `scripts/ensure-env.mjs`.

---

## 1. Surveillance periodique — `sim:watch`

**Script** : `scripts/threshold_watch_aiven.py`  
**Role** : toutes les **60 secondes**, lit le **dernier releve** de chaque capteur actif, compare aux seuils du pays, met a jour le statut du lot et envoie Discord si nouvelle alerte.

### Lancer / arreter

```powershell
# Terminal dedie — laisse tourner
npm run sim:watch

# Arret
npm run sim:watch:stop
# ou Ctrl+C dans le terminal
```

### Options avancees

```powershell
python scripts/threshold_watch_aiven.py --interval 60
python scripts/threshold_watch_aiven.py --once          # une seule passe
powershell -File scripts/start_threshold_watch.ps1 -Interval 30
```

### Exemple console

```
[18:15:06 UTC] 6 capteur(s) verifie(s) | 1 hors seuil (deja active)

  Hors seuil en cours (1) :
  >> EC Entrepot EC-1 | T=24.8C [28-34] HORS SEUIL | H=57.6% [58-62] HORS SEUIL | lot ALERTE
```

Nouvelle alerte (bloc detaille + Discord) :

```
==================================================
  ALERTES SEUILS IoT - 18:20:00 UTC
  1 evenement(s)
==================================================

  --- NOUVELLE ALERTE : BRESIL (BR) ---
  Entrepot : Entrepot BR-1
  ...
  Action   : alerte BDD + Discord envoye OK
==================================================
```

### Quand l'utiliser

| Scenario | Commande |
|----------|----------|
| Simulateur + alertes en continu | `sim:start` + `sim:watch` en parallele |
| ESP32 / pont MQTT sans simulateur | `sim:watch` seul |
| Verifier Discord / seuils une fois | `python scripts/threshold_watch_aiven.py --once` |

---

## 2. Alerte de test — `sim:test-alert`

**Script** : `scripts/trigger_test_alert.py`  
**Role** : injecte **un releve volontairement hors seuil** (temperature ou humidite), remet le lot en `CONFORME`, puis declenche la chaine alerte (BDD + Discord + console).

### Lancer

```powershell
# Defaut : Bresil, +8 C au-dessus du seuil max
npm run sim:test-alert

# Autre pays
npm run sim:test-alert -- --pays EC
npm run sim:test-alert -- --pays CO --offset 5

# Humidite hors plage
npm run sim:test-alert -- --pays CO --metric humidity --offset 3
```

### Workflow demo recommande

```powershell
# 1. Surveillance active (terminal 1)
npm run sim:watch

# 2. Injecter l'anomalie (terminal 2)
npm run sim:test-alert

# 3. Verifier : console sim:watch, Discord, page Alertes du frontend
```

---

## Stack complete locale

```powershell
npm start              # UI + API (terminal ou arriere-plan)
npm run sim:start      # capteurs fictifs -> Aiven (30 s)
npm run sim:watch      # seuils + Discord (60 s)
```

Arret :

```powershell
npm run sim:stop
npm run sim:watch:stop
npm stop
```

---

## Fichiers lies

| Fichier | Description |
|---------|-------------|
| `scripts/threshold_watch_aiven.py` | Boucle surveillance |
| `scripts/threshold_alert.py` | Logique seuils, Discord, affichage console |
| `scripts/trigger_test_alert.py` | Injection releve hors seuil |
| `scripts/start_threshold_watch.ps1` | Lanceur Windows |
| `scripts/stop_threshold_watch.ps1` | Arret processus watch |

---

## Depannage

| Probleme | Solution |
|----------|----------|
| `Webhook non configure cote API` (Render) | Render → service **API** → **Environment** → `DISCORD_WEBHOOK_URL` |
| Discord 403 en local | URL webhook invalide ou regeneree dans Discord |
| Pas de nouvelle alerte apres test | Lot deja en `ALERTE` — `sim:test-alert` remet en `CONFORME` avant injection |
| Double simulateur | `npm run sim:stop` puis un seul `sim:start` |

### Format Discord

Discord **ne supporte pas le HTML** dans les webhooks. Les alertes utilisent des **embeds** avec **Markdown** :

- **gras**, `code`, listes, citations `>`
- champs structures (pays, entrepot, lot, temperature, humidite)
- emojis (`:thermometer:`, `:red_circle:`, etc.)
- lien vers le [tableau de bord alertes](https://mspr2-master-front.onrender.com/alertes)

Code : `scripts/discord_embed.py` et `siege/api/services/discord_embed.py`.

Voir aussi : `docs/technique/architecture_iot_local.md`, `docs/deployment/render.md`.

# Comptes de développement — FutureKawa

## 1) Comptes disponibles

| username | password (clair) | role | pays | email |
|---|---|---|---|---|
| `admin_siege` | `Admin@2025!` | ADMIN | SIEGE | admin@futurekawa.com |
| `direction_siege` | `Direction@2025!` | USER | SIEGE | direction@futurekawa.com |
| `supply_siege` | `Supply@2025!` | USER | SIEGE | supply@futurekawa.com |
| `resp_bresil` | `Bresil@2025!` | USER | BRESIL | resp.br@futurekawa.com |
| `entrepot_bresil` | `Entrepot_Br@2025!` | USER | BRESIL | entrepot.br@futurekawa.com |
| `qualite_bresil` | `Qualite_Br@2025!` | USER | BRESIL | qualite.br@futurekawa.com |
| `resp_equateur` | `Equateur@2025!` | USER | EQUATEUR | resp.eq@futurekawa.com |
| `entrepot_equateur` | `Entrepot_Eq@2025!` | USER | EQUATEUR | entrepot.eq@futurekawa.com |
| `qualite_equateur` | `Qualite_Eq@2025!` | USER | EQUATEUR | qualite.eq@futurekawa.com |
| `resp_colombie` | `Colombie@2025!` | USER | COLOMBIE | resp.co@futurekawa.com |
| `entrepot_colombie` | `Entrepot_Co@2025!` | USER | COLOMBIE | entrepot.co@futurekawa.com |
| `qualite_colombie` | `Qualite_Co@2025!` | USER | COLOMBIE | qualite.co@futurekawa.com |

## 2) Matrice des droits

Légende: ✅ autorisé · — lecture seule (si applicable) · 🔒 interdit

| fonctionnalité | ADMIN | USER (SIEGE) | USER (BRESIL/EQUATEUR/COLOMBIE) |
|---|---:|---:|---:|
| créer lot | ✅ | 🔒 | ✅ (pays du user uniquement) |
| modifier lot | ✅ | 🔒 | ✅ (pays du user uniquement) |
| voir stocks (local) | ✅ | — | ✅ (pays du user uniquement) |
| vue multi-pays | ✅ | ✅ | 🔒 |
| courbes IoT | ✅ | — | ✅ (entrepôts de son pays uniquement) |
| alertes email | ✅ | — | ✅ (pays du user uniquement) |
| gérer statuts qualité | ✅ | 🔒 | ✅ (pays du user uniquement) |
| config seuils | ✅ | 🔒 | 🔒 |
| gestion users | ✅ | 🔒 | 🔒 |

## 3) Logique de conditionnement (résumé)

- `ADMIN` (tous pays): accès total (CRUD lots, seuils IoT, users, multi-pays, logs).
- `USER + SIEGE`: lecture consolidée multi-pays (stocks, courbes, alertes, traçabilité).
- `USER + (BRESIL|EQUATEUR|COLOMBIE)`: accès limité à son pays (données + écriture lots).
- Toute donnée hors pays (pour user local) est masquée côté UI **et** bloquée côté API.
- Les destinataires d’alertes email sont les emails des comptes `resp_*` du pays concerné.

## 4) Avertissement

**Ce fichier contient des credentials de développement. Ne pas committer en production. Ajouter à `.gitignore` si nécessaire.**


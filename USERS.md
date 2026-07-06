# Comptes de développement — FutureKawa

## 1) Comptes disponibles

| username | password (clair) | role | pays | email |
|---|---|---|---|---|
| `admin_siege` | `Admin@2025!` | **SUPER_ADMIN** | SIEGE | admin@futurekawa.com |
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

## 2) Hierarchie des roles

| Role | Description |
|------|-------------|
| **SUPER_ADMIN** | Proprietaire plateforme (`admin_siege`) — gestion utilisateurs + tout le reste |
| **ADMIN** | Administration operationnelle — seuils IoT (siège = tous pays, pays local = son pays), lots, vue multi-pays réservée au siège |
| **USER** | Acces metier selon le pays associe |

Migration BDD existante (Aiven) — appliquer le SQL via un client compatible TLS ou étendre `push_mysql_schema.py` :

```bash
python scripts/push_mysql_schema.py
# Puis exécuter manuellement database/migrations/001_add_super_admin_role.sql sur Aiven si nécessaire
```

## 3) Matrice des droits

Legende: ✅ autorise · — lecture seule · 🔒 interdit

| fonctionnalite | SUPER_ADMIN | ADMIN (SIEGE) | ADMIN (pays) | USER (SIEGE) | USER (pays) |
|---|---:|---:|---:|---:|---:|
| gestion utilisateurs | ✅ | 🔒 | 🔒 | 🔒 | 🔒 |
| config seuils IoT | ✅ | ✅ (tous) | ✅ (son pays) | 🔒 | 🔒 |
| webhook Discord global | ✅ | 🔒 | 🔒 | 🔒 | 🔒 |
| creer / modifier lot | ✅ | ✅ (tous) | ✅ (son pays) | 🔒 | ✅ (son pays) |
| vue multi-pays | ✅ | ✅ | 🔒 | ✅ | 🔒 |
| courbes IoT | ✅ | ✅ | ✅ (son pays) | — | ✅ (son pays) |
| alertes | ✅ | ✅ | ✅ (son pays) | — | ✅ (son pays) |

## 4) Logique de conditionnement (resume)

- **SUPER_ADMIN** : acces total incluant `/users` et promotion de roles.
- **ADMIN + SIEGE** : config capteurs tous pays, CRUD lots tous pays, pas d acces gestion utilisateurs ni webhook global.
- **ADMIN + pays** : config seuils **son pays uniquement**, CRUD lots **son pays**, pas de vue multi-pays ni webhook global.
- **USER + SIEGE** : lecture consolidee multi-pays.
- **USER + pays** : acces limite a son pays (donnees + ecriture lots).

## 5) Avertissement

**Ce fichier contient des credentials de developpement. Ne pas committer en production.**

# Collecte des besoins métiers — FutureKawa IoT
> Livrable MSPR TPRE814 — Bloc 4 / Compétence : Collecter les besoins métiers

---

## 1. Contexte et objectif de l'interview

FutureKawa est une entreprise de caféiculture et logistique de café vert opérant au Brésil, en Équateur et en Colombie. Elle souffre d'un suivi semi-manuel des conditions de stockage (température, humidité), d'une traçabilité insuffisante des lots et d'une logique FIFO difficile à appliquer sans visibilité centralisée.

L'objectif de ces interviews est de recueillir les besoins métiers réels des utilisateurs finaux afin de valider les fonctionnalités de la solution IoT FutureKawa et d'identifier les contraintes opérationnelles à prendre en compte.

**Personnes cibles :**

| Profil interviewé | Rôle | Pays |
|---|---|---|
| Responsable d'exploitation | Pilotage production + stockage + expédition locale | Brésil / Équateur / Colombie |
| Responsable entrepôt | Réception, stockage, inventaires, préparation des lots | Brésil / Équateur / Colombie |
| Référent qualité local | Contrôles, alertes qualité, procédures | Brésil / Équateur / Colombie |
| DSI / Responsable SI | Gouvernance, sécurité, infrastructure | Siège |
| Direction Opérations & Supply Chain | Logistique, planification, reporting global | Siège |

---

## 2. Méthodologie de conduite de l'interview

### Déroulé type (45 à 60 minutes par session)

| Étape | Durée | Contenu |
|---|---|---|
| Présentation | 5 min | Présentation de l'équipe projet, objectif de l'interview, rappel que les échanges seront retranscrits |
| Contexte métier | 10 min | Comprendre le quotidien de l'interviewé, ses outils actuels, ses difficultés |
| Besoins fonctionnels | 20 min | Questions sur les fonctionnalités attendues (voir section 3) |
| Contraintes | 10 min | Questions sur les contraintes techniques et organisationnelles (voir section 4) |
| Priorisation | 5 min | Faire noter les fonctionnalités de 1 (indispensable) à 3 (optionnel) |
| Clôture | 5 min | Relecture des points clés, validation, remerciements |

### Méthode de retranscription

Les réponses sont retranscrites dans le tableau de synthèse (section 5) pendant ou immédiatement après l'interview. Pour chaque réponse on note :

- le besoin fonctionnel ou la contrainte identifié
- la priorité (indispensable / important / optionnel)

Un Google Forms est mis à disposition pour les interviewés distants (Brésil, Équateur, Colombie).

---

## 3. Questionnaire — Besoins fonctionnels

### Bloc A — Gestion des stocks et traçabilité des lots

**A1.** Comment gérez-vous aujourd'hui le suivi de vos lots de café en entrepôt ? (outil, fréquence, responsable)

**A2.** Quelles informations sont indispensables sur chaque lot ?
> *Implémenté dans la solution : identifiant unique UUID, pays, exploitation, entrepôt, date d'entrée (entre_le), statut (CONFORME / ALERTE / PÉRIMÉ / EXPÉDIÉ).*

**A3.** Avez-vous des difficultés à appliquer la règle FIFO (premier entré, premier sorti) dans vos expéditions ? Si oui, pourquoi ?
> *Implémenté : index BDD `idx_lot_fifo (entrepot_id, entre_le)` + tri automatique par date d'entrée dans l'interface.*

**A4.** Depuis le siège, avez-vous accès en temps réel à l'état des stocks dans les trois pays ? Qu'est-ce qui manque aujourd'hui ?
> *Implémenté : interface centralisée siège avec sélecteur de pays (Brésil / Équateur / Colombie / vue globale), accès selon le rôle JWT (SUPER_ADMIN, ADMIN SIÈGE, USER local).*

**A5.** Quand un lot passe en alerte ou est périmé, quelle est la procédure actuelle ? Qui est notifié ?
> *Implémenté : alerte email automatique via Node-RED (nœud e-mail) + notification Discord webhook. Lot > 365 jours → statut PÉRIMÉ automatiquement.*

**A6.** Avez-vous besoin d'un historique consultable des statuts et des relevés de vos lots ?
> *Implémenté : courbes de température et d'humidité consultables par lot depuis l'interface (composant Charts/Recharts), historique jusqu'à 365 jours.*

---

### Bloc B — Surveillance IoT (température et humidité)

**B1.** Comment les conditions de stockage sont-elles mesurées aujourd'hui ? (manuelle, automatique, fréquence)

**B2.** À quelle fréquence souhaiteriez-vous des relevés automatiques ?
> *Implémenté : 1 relevé toutes les 30 secondes (ESP32 + DHT, firmware MicroPython, `READ_INTERVAL = 30`). Données envoyées via MQTT → broker Mosquitto → API FastAPI → BDD MySQL.*

**B3.** Les seuils de tolérance vous semblent-ils adaptés à votre pays ?
> *Implémenté dans la BDD (table `pays`, colonnes `temperature_ideale_c`, `humidite_ideale_pct`, `tolerance_temperature_c = 3.0`, `tolerance_humidite_pct = 2.0`) :*
> - *Brésil : 29°C ± 3 / 55% ± 2*
> - *Équateur : 31°C ± 3 / 60% ± 2*
> - *Colombie : 26°C ± 3 / 80% ± 2*

**B4.** En cas de dérive, qui doit être alerté en premier ?
> *Implémenté : email envoyé au `email_responsable` du pays concerné (champ dans la table `pays`). Pas de priorisation par rôle dans la v1.*

**B5.** Souhaitez-vous pouvoir visualiser l'historique des relevés sous forme de courbes graphiques ?
> *Implémenté : composant `Charts` (Recharts) avec courbes température + humidité + lignes pointillées des seuils idéaux par pays.*

**B6.** Avez-vous besoin d'un indicateur de capteur hors ligne ?
> *Implémenté : `get_capteur_status()` dans l'API pays, détection des capteurs déconnectés (`connected: false`), inclus dans les notifications email/Discord.*

---

### Bloc C — Interface web et accès centralisé

**C1.** Qui sont les utilisateurs de l'interface web ? Quel niveau informatique ?
> *Implémenté : 3 rôles via JWT — SUPER_ADMIN (gestion plateforme), ADMIN (administration opérationnelle multi-pays), USER (accès en lecture selon pays_code).*

**C2.** Depuis quel appareil accéderez-vous à l'application ?
> *Implémenté : interface web responsive (React/Vite), accessible via navigateur, servie par Nginx.*

**C3.** Quelles informations voulez-vous voir immédiatement sur le tableau de bord ?
> *Implémenté : page Dashboard avec alertes actives, liste des lots triés FIFO, statuts colorés (badge CONFORME / ALERTE / PÉRIMÉ / EXPÉDIÉ), sélecteur pays.*

**C4.** Avez-vous besoin de filtrer les lots par pays, entrepôt, statut ?
> *Implémenté : composant `LocationFilters` (filtre pays + exploitation + entrepôt) + composant `LotList` avec statut visible.*

**C5.** Le siège doit-il voir toutes les données ou seulement une vue consolidée ?
> *Implémenté : ADMIN SIÈGE et SUPER_ADMIN voient tous les pays. USER local ne voit que son pays (`pays_code` dans le JWT).*

**C6.** Avez-vous besoin d'exporter les données ?
> *Implémenté : export CSV des lots disponible (`exportLotsCsv` — champs : id, pays, exploitation, entrepôt, statut, date_stockage, jours_en_stock).*

---

### Bloc D — Alertes et notifications

**D1.** Par quel canal souhaitez-vous recevoir les alertes ?
> *Implémenté : email via nœud Node-RED (nœud `e-mail`) + Discord webhook (pour le suivi interne équipe). Email au responsable pays.*

**D2.** Souhaitez-vous une alerte dès le premier dépassement ou après un délai ?
> *Implémenté : alerte déclenchée dès que le relevé MQTT est hors plage (vérification en temps réel dans le subscriber MQTT).*

**D3.** Un lot de plus de 365 jours doit-il être automatiquement signalé ?
> *Implémenté : `PEREMPTION_JOURS = 365` dans `config.py`. Statut passé à PÉRIMÉ automatiquement + notification email/Discord.*

**D4.** Souhaitez-vous des alertes en temps réel ou des synthèses périodiques ?
> *Implémenté : alertes en temps réel (subscriber MQTT) + scheduler de notifications périodiques (`notification_scheduler.py`).*

---

## 4. Questionnaire — Contraintes métiers

### Bloc E — Contraintes techniques

**E1.** Quelle est la qualité de la connexion internet dans vos entrepôts ?
> *Contrainte prise en compte : architecture conteneurisée par pays (indépendance réseau), broker MQTT local dans chaque pays.*

**E2.** Avez-vous des contraintes de sécurité des données ?
> *Implémenté : authentification JWT, accès restreint par `pays_code`, rôles RBAC (SUPER_ADMIN / ADMIN / USER), HTTPS via Nginx.*

**E3.** L'application doit-elle fonctionner en mode dégradé si la connexion est coupée ?
> *Architecture pays autonome : chaque pays continue d'enregistrer les relevés localement même si le siège n'est pas joignable.*

### Bloc F — Contraintes organisationnelles

**F1.** Qui sera administrateur de la solution dans chaque pays ?
> *Implémenté : rôle ADMIN par pays_code (BRESIL / EQUATEUR / COLOMBIE) géré via `UsersPage` dans le frontend.*

**F2.** Une formation sera-t-elle nécessaire pour les équipes terrain ?
> *Prévu : guide utilisateur complet (`docs/utilisateur/guide_utilisateur.md`), FAQ (`docs/utilisateur/faq.md`), USERS.md.*

**F3.** Y a-t-il des risques de résistance au changement identifiés ?
> *Traité dans le plan de conduite du changement (voir `docs/conduite_changement/conduite_changement.md`).*

---

## 5. Tableau de retranscription et synthèse

| # | Question | Profil interviewé | Réponse / Besoin identifié | Priorité |
|---|---|---|---|---|
| A2 | Informations indispensables sur un lot | Resp. entrepôt Brésil | ID unique, entrepôt, date entrée, statut visible rapidement | Indispensable |
| A3 | Difficultés FIFO | Resp. exploitation Équateur | Lots anciens parfois oubliés, pas de tri automatique existant | Indispensable |
| A5 | Notification alerte | Resp. qualité Colombie | Email impératif vers le responsable local, immédiat | Indispensable |
| B1 | Mesure conditions aujourd'hui | Resp. entrepôt Brésil | Relevé manuel 2 fois par jour par un agent avec thermomètre | Indispensable |
| B3 | Seuils adaptés | Resp. qualité Équateur | Seuils actuels cohérents avec les pratiques terrain | Important |
| B6 | Capteur hors ligne | DSI Siège | Besoin de savoir si un capteur ne répond plus | Important |
| C3 | Dashboard | Direction Supply Chain | Alertes actives et lots les plus anciens visibles en premier | Indispensable |
| C6 | Export données | Direction Supply Chain | Export CSV nécessaire pour les rapports clients et audits | Important |
| D1 | Canal alerte | Resp. exploitation Colombie | Email vers le responsable pays + outil interne équipe projet | Indispensable |
| E1 | Connexion entrepôt | Resp. entrepôt Brésil | 4G, parfois instable — solution doit être résiliente | Important |

---

## 6. Synthèse des besoins et contraintes

### Besoins retenus et implémentation vérifiée

| Fonctionnalité attendue | Implémenté ? | Preuve |
|---|---|---|
| Suivi des lots avec statut (CONFORME / ALERTE / PÉRIMÉ / EXPÉDIÉ) | ✓ | `schema_mysql.sql` — ENUM statut |
| Tri FIFO automatique par date d'entrée | ✓ | Index `idx_lot_fifo`, tri frontend LotList |
| Relevés automatiques température/humidité toutes les 30s | ✓ | `firmware/config.py` READ_INTERVAL=30 |
| Alertes email automatiques (dérive + péremption 365j) | ✓ | Node-RED flows.json (nœud e-mail) + `PEREMPTION_JOURS=365` |
| Interface centralisée siège multi-pays avec rôles | ✓ | JWT RBAC, `permissions.py`, `CountrySelector` |
| Courbes historiques température/humidité par lot | ✓ | Composant `Charts` (Recharts) |
| Export CSV des stocks | ✓ | `exportCsv.js` — `exportLotsCsv()` |
| Détection capteur hors ligne | ✓ | `get_capteur_status()`, section déconnectés dans notifications |
| Architecture autonome par pays (résilience réseau) | ✓ | docker-compose par pays, broker MQTT local |
| Seuils configurables par pays en BDD | ✓ | Table `pays` avec `temperature_ideale_c`, `tolerance_*` |

### Contraintes respectées

| Contrainte | Prise en compte |
|---|---|
| Connexion intermittente en entrepôt | Architecture locale par pays, broker MQTT local |
| Sécurité des données | JWT, RBAC, accès filtré par pays_code |
| Utilisateurs peu à l'aise avec l'informatique | Interface simple, badges colorés, guide utilisateur |
| Pas de ressource IT locale | Docker Compose, démarrage en une commande (`npm start`) |

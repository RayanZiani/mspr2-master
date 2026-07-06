# Collecte des besoins métiers — FutureKawa IoT
> MSPR TPRE814 — Bloc 4 — Compétence : Collecter les besoins métiers des utilisateurs  
> Critère niveau 3 : interview-type structurée + méthodologie de retranscription + besoins fonctionnels + contraintes métiers

---

## 1. Contexte de la collecte

FutureKawa est une entreprise internationale de caféiculture et logistique de café vert, présente au Brésil, en Équateur et en Colombie. Avant ce projet, les équipes terrain souffraient de :

- relevés de température et d'humidité **manuels** (2 fois par jour par un agent)
- suivi des stocks sur **tableur Excel** sans visibilité centralisée
- application de la règle **FIFO** difficile (pas de tri automatique des lots par ancienneté)
- absence de notification proactive en cas de dérive ou de lot trop ancien

La collecte des besoins a pour but de valider que la solution FutureKawa IoT développée répond aux attentes réelles des utilisateurs métier et d'identifier toutes les contraintes à respecter.

---

## 2. Populations interviewées

| Profil | Rôle | Pays |
|---|---|---|
| Responsable d'exploitation | Pilotage production + stockage + expédition locale | Brésil / Équateur / Colombie |
| Responsable entrepôt | Réception, stockage, inventaires, préparation des lots | Brésil / Équateur / Colombie |
| Référent qualité local | Contrôles qualité, alertes, procédures de non-conformité | Brésil / Équateur / Colombie |
| Direction Opérations & Supply Chain | Logistique, planification, reporting global | Siège |
| DSI / Responsable SI | Gouvernance, sécurité, infrastructure, déploiement | Siège |

---

## 3. Méthodologie de conduite de l'interview

### 3.1 Déroulé type (45 à 60 minutes par session)

| Étape | Durée | Contenu |
|---|---|---|
| Présentation | 5 min | Présentation de l'équipe projet, objectif de l'interview, accord de retranscription |
| Contexte métier | 10 min | Processus actuel, outils utilisés, difficultés quotidiennes |
| Besoins fonctionnels | 20 min | Questions sur les fonctionnalités attendues (blocs A, B, C, D) |
| Contraintes | 10 min | Contraintes techniques, organisationnelles, réglementaires (blocs E, F) |
| Priorisation | 5 min | Notation de chaque besoin : Indispensable / Important / Optionnel |
| Clôture | 5 min | Relecture des points clés, validation par l'interviewé |

### 3.2 Méthode de retranscription

Chaque interview est retranscrite dans le tableau de synthèse (section 5) immédiatement après la session. Pour chaque réponse on capture :

- le **besoin fonctionnel** ou la **contrainte** identifié(e)
- la **priorité** (Indispensable / Important / Optionnel)
- la **correspondance avec la solution développée** (traceability)

Les interviewés distants (Brésil, Équateur, Colombie) répondent via Google Forms : [Lien du formulaire](https://docs.google.com/forms/d/e/1FAIpQLSdtsh1O691HgpIeFaXrkhVKwSwHoxGdw0KOJLQpcl45gv3AZA/viewform)

Les réponses sont agrégées et synthétisées dans le tableau ci-dessous (section 5), puis classées par fonctionnalité implémentée.

---

## 4. Questionnaire — Interview type

### Bloc A — Gestion des stocks et traçabilité des lots

**A1.** Comment gérez-vous aujourd'hui le suivi de vos lots de café en entrepôt ?
*(outil, fréquence de mise à jour, qui est responsable de la saisie)*

**A2.** Quelles informations sont indispensables pour vous sur chaque lot ?
*(identifiant, pays d'origine, exploitation, entrepôt de stockage, date d'entrée, statut)*

> Implémenté : table `lot` — UUID unique, `pays_id`, `exploitation_id`, `entrepot_id`, `entre_le` (date entrée), `statut` ENUM(`CONFORME`, `ALERTE`, `PERIME`, `EXPEDIE`)

**A3.** Avez-vous des difficultés à appliquer la règle FIFO (expédier les lots les plus anciens en priorité) ?

> Implémenté : index BDD `idx_lot_fifo(entrepot_id, entre_le)` + tri automatique par date d'entrée dans la liste des lots (composant `LotList`)

**A4.** Depuis le siège, avez-vous accès en temps réel à l'état des stocks dans les trois pays ?

> Implémenté : API siège `/stocks` avec agrégation multi-pays, sélecteur de pays (`CountrySelector`), accès filtré selon le rôle JWT (`USER SIEGE` = lecture multi-pays, `USER pays` = son pays uniquement)

**A5.** Quand un lot est en alerte ou périmé, quelle est la procédure actuelle de notification ?

> Implémenté : email automatique via Node-RED (nœud `e-mail`) + digest Discord webhook toutes les 5 min (`notification_scheduler.py`, `DIGEST_INTERVAL=300`)

**A6.** Avez-vous besoin d'un historique des relevés de conditions de stockage par lot ?

> Implémenté : table `releve_capteur`, courbes Recharts dans `LotView`, historique jusqu'à 365 jours (`MESURES_DAYS`)

---

### Bloc B — Surveillance IoT (température et humidité)

**B1.** Comment les conditions de stockage sont-elles mesurées aujourd'hui dans vos entrepôts ?
*(manuelle, fréquence, par qui)*

**B2.** À quelle fréquence souhaiteriez-vous des relevés automatiques des capteurs ?

> Implémenté : 1 relevé toutes les **30 secondes** — firmware MicroPython (`READ_INTERVAL = 30` dans `iot/firmware/config.py`), ESP32 + DHT11 (prototype campus, sortie série USB) relayé vers MQTT via `iot/bridge/serial_to_mqtt.py`

**B3.** Les seuils de tolérance par pays vous semblent-ils adaptés à vos conditions terrain ?

> Implémenté en BDD (table `pays`) et dans les `config.py` de chaque API pays :
> - **Brésil** : `SEUIL_TEMP = 29.0°C`, `SEUIL_HUMIDITY = 55.0%`, `TOLERANCE_TEMP = 3.0`, `TOLERANCE_HUMIDITY = 2.0`
> - **Équateur** : `SEUIL_TEMP = 31.0°C`, `SEUIL_HUMIDITY = 60.0%`, tolerances identiques
> - **Colombie** : `SEUIL_TEMP = 26.0°C`, `SEUIL_HUMIDITY = 80.0%`, tolerances identiques
>
> Logique d'alerte : `abs(mesure - seuil) > tolerance` → alerte déclenchée (`alert_service.py`)

**B4.** En cas de dérive, qui doit être alerté en priorité ?

> Implémenté : email envoyé à `email_responsable` du pays concerné (champ dans la table `pays`), inclus dans le digest Discord

**B5.** Souhaitez-vous consulter l'historique sous forme de courbes graphiques ?

> Implémenté : composant `Charts` (Recharts) — courbes température + humidité + lignes pointillées des seuils idéaux, accessible depuis `LotView`

**B6.** Avez-vous besoin d'un indicateur de capteur hors ligne ?

> Implémenté : `get_capteur_status()` dans le subscriber MQTT — détection capteur déconnecté (`connected: false`), section "capteurs HORS LIGNE" dans les digests (`_append_disconnected_section`)

---

### Bloc C — Interface web et accès centralisé

**C1.** Qui sont les utilisateurs de la future interface web ? Niveau de compétences informatiques ?

> Implémenté : 3 rôles RBAC via JWT — `SUPER_ADMIN` (admin plateforme), `ADMIN` (admin opérationnel multi-pays ou pays), `USER` (accès lecture/écriture selon `pays_code`)
>
> Comptes disponibles documentés dans `USERS.md` : 12 comptes préconfigurés par profil

**C2.** Depuis quel appareil accéderez-vous à l'application en priorité ?

> Implémenté : interface React/Vite responsive, servie par Nginx, accessible via navigateur

**C3.** Quelles informations voulez-vous voir immédiatement sur le tableau de bord ?

> Implémenté : page `Dashboard` — alertes actives, liste des lots triés FIFO, badges de statut colorés, `SeuilsSummary` par pays

**C4.** Avez-vous besoin de filtrer les lots par pays, entrepôt ou statut ?

> Implémenté : composant `LocationFilters` (filtre pays + exploitation + entrepôt) + tri par statut dans `LotList`

**C5.** Le siège doit-il voir toutes les données ou seulement une vue consolidée ?

> Implémenté : `USER SIEGE` = lecture consolidée multi-pays ; `SUPER_ADMIN` et `ADMIN SIEGE` = accès complet toutes données

**C6.** Avez-vous besoin d'exporter les données de stocks ?

> Implémenté : export CSV via `exportLotsCsv()` (`siege/frontend/src/utils/exportCsv.js`) — colonnes : `id, pays, exploitation, entrepot, statut, date_stockage, jours_en_stock`

---

### Bloc D — Alertes et notifications

**D1.** Par quel canal souhaitez-vous recevoir les alertes ?

> Implémenté : **email** via nœud Node-RED (`e-mail`, serveur SMTP configurable via `SMTP_HOST`) + **Discord webhook** (`webhook_service.py`, `discord_embed.py`) pour l'équipe projet

**D2.** Souhaitez-vous une alerte immédiate ou après un délai de persistance ?

> Implémenté : alerte déclenchée **dès le premier relevé MQTT hors seuil** (`check_alerts()` dans `alert_service.py`), digest toutes les 5 min pour éviter le spam

**D3.** Un lot de plus de 365 jours doit-il être automatiquement signalé et traité ?

> Implémenté : `PEREMPTION_JOURS = 365` dans chaque `config.py` pays, `is_lot_perime()` dans `alert_service.py`, vue SQL `v_lots_trop_anciens`, statut PÉRIMÉ automatique

**D4.** Souhaitez-vous des alertes en temps réel ou des synthèses périodiques ?

> Implémenté : **les deux** — alerte temps réel via subscriber MQTT + digest périodique `notification_scheduler.py` (thread daemon, intervalle configurable via `DIGEST_INTERVAL`)

---

### Bloc E — Contraintes techniques

**E1.** Quelle est la qualité de la connexion internet dans vos entrepôts ?

> Contrainte prise en compte : broker MQTT **local Mosquitto** pour le prototype ESP32 ; relevés persistés dans **Aiven MySQL** (base unique). L'API siège fonctionne tant qu'Aiven est accessible.

**E2.** Avez-vous des contraintes de sécurité des données ?

> Implémenté : authentification JWT (`auth.py`), RBAC par rôle et `pays_code`, HTTPS via Nginx, hashage des mots de passe (`bcrypt`/`passlib`)

**E3.** L'application doit-elle fonctionner si la connexion entre pays et siège est coupée ?

> Implémenté : les capteurs/simulateurs écrivent dans **Aiven** via scripts locaux ; le dashboard siège lit Aiven — pas de BDD locale par pays.

---

### Bloc F — Contraintes organisationnelles

**F1.** Qui sera administrateur de la solution dans chaque pays ?

> Implémenté : rôle `ADMIN` par `pays_code` (`BRESIL` / `EQUATEUR` / `COLOMBIE`), géré via la page `UsersPage` dans le frontend (accessible uniquement au `SUPER_ADMIN`)

**F2.** Une formation sera-t-elle nécessaire pour les équipes terrain ?

> Prévu : `docs/utilisateur/guide_utilisateur.md` (parcours complet), `docs/utilisateur/faq.md`, `USERS.md` (matrice des droits). Voir aussi le plan de conduite du changement (`docs/conduite_changement/conduite_changement.md`)

**F3.** Y a-t-il des risques de résistance au changement identifiés ?

> Traité dans le plan de conduite du changement — modèle de Bridges, FutureWheel, plan 4 axes

---

## 5. Tableau de retranscription et synthèse

| # | Question | Profil | Réponse / Besoin identifié | Priorité |
|---|---|---|---|---|
| A1 | Suivi lots aujourd'hui | Resp. entrepôt Brésil | Tableur Excel, mise à jour hebdomadaire, pas de vue centralisée | Indispensable |
| A2 | Infos indispensables sur un lot | Resp. entrepôt Équateur | ID unique, entrepôt, date entrée, statut visible immédiatement | Indispensable |
| A3 | Difficultés FIFO | Resp. exploitation Colombie | Lots anciens parfois oubliés en fond d'entrepôt, pas de tri automatique | Indispensable |
| A5 | Notification alerte | Resp. qualité Brésil | Email au responsable local impératif, immédiat | Indispensable |
| B1 | Mesure conditions aujourd'hui | Resp. entrepôt Colombie | Thermomètre manuel 2 fois/jour par un agent, pas de trace numérique | Indispensable |
| B3 | Seuils adaptés | Resp. qualité Équateur | Seuils proposés cohérents avec les pratiques terrain locales | Important |
| B6 | Capteur hors ligne | DSI Siège | Besoin d'alerte si un capteur ne répond plus — risque de faux négatif | Important |
| C3 | Infos dashboard | Direction Supply Chain | Alertes actives + lots les plus anciens visibles immédiatement à l'ouverture | Indispensable |
| C6 | Export données | Direction Supply Chain | Export CSV pour les rapports clients et audits qualité | Important |
| D1 | Canal alerte | Resp. exploitation Colombie | Email vers responsable pays + outil interne équipe projet | Indispensable |
| D3 | Lots périmés | Resp. exploitation Brésil | Lot > 365j doit déclencher une alerte + passage statut automatique | Indispensable |
| E1 | Connexion entrepôt | Resp. entrepôt Brésil | 4G parfois instable — solution doit fonctionner sans connexion siège | Important |
| E2 | Sécurité données | DSI Siège | Accès restreint par pays, authentification obligatoire | Indispensable |
| F2 | Formation | Resp. exploitation Équateur | Guide utilisateur papier + prise en main rapide — pas de formation présentielle disponible | Important |

---

## 6. Synthèse : besoins retenus et vérification d'implémentation

| Besoin identifié en interview | Implémenté | Preuve technique |
|---|---|---|
| Suivi lots avec statut clair | ✓ | `lot.statut` ENUM `CONFORME/ALERTE/PERIME/EXPEDIE` |
| Tri FIFO automatique | ✓ | Index `idx_lot_fifo(entrepot_id, entre_le)` + `LotList` |
| Relevés automatiques toutes les 30s | ✓ | `READ_INTERVAL=30` dans `firmware/config.py` |
| Alerte email automatique (dérive + 365j) | ✓ | Node-RED `e-mail` + `PEREMPTION_JOURS=365` |
| Interface centralisée siège multi-pays | ✓ | JWT RBAC, `CountrySelector`, agrégation `/stocks` |
| Courbes historiques température/humidité | ✓ | Composant `Charts` (Recharts), `LotView` |
| Export CSV | ✓ | `exportLotsCsv()` dans `exportCsv.js` |
| Détection capteur hors ligne | ✓ | `get_capteur_status()`, `_append_disconnected_section` |
| Architecture résiliente | ✓ | Base **Aiven** centralisée + simulateurs locaux |
| Seuils configurables par pays | ✓ | Table `pays` + `config.py` par pays |
| Authentification et RBAC | ✓ | JWT, `permissions.py`, `USERS.md` |

### Contraintes respectées

| Contrainte | Prise en compte |
|---|---|
| Connexion 4G intermittente | Relevés via scripts locaux → Aiven ; dashboard lit Aiven |
| Sécurité des données | JWT, RBAC, HTTPS Nginx, bcrypt |
| Utilisateurs peu à l'aise avec l'informatique | Interface simple, badges colorés, guide utilisateur |
| Pas de ressource IT locale | `docker compose up --build` en une commande, README complet |

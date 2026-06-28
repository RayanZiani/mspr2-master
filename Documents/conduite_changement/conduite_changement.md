# Conduite du changement — FutureKawa IoT
> Livrable MSPR TPRE814 — Bloc 4 / Compétence : Conduire le changement  
> Inclut : Questionnaire phase 2 (Livrable L10)

---

## 1. Contexte du changement

FutureKawa déploie une plateforme IoT de surveillance des stocks de café vert dans trois pays (Brésil, Équateur, Colombie). Ce déploiement représente un changement majeur pour les équipes terrain : passage de relevés manuels sur tableur à un système automatisé, connecté et centralisé.

**Nature du changement :**
- Technique : capteurs IoT ESP32 + DHT, interface web React, alertes email automatiques, architecture multi-pays conteneurisée
- Organisationnel : modification des processus quotidiens (plus de relevés manuels, nouvelles procédures d'alerte)
- Culturel : adoption du numérique par des équipes terrain peu à l'aise avec l'informatique

**Populations impactées :**

| Population | Impact | Résistance potentielle |
|---|---|---|
| Agents / responsables entrepôt (terrain) | Fort — changement de leurs processus quotidiens | Élevée — habitudes ancrées, outil perçu comme complexe |
| Responsables d'exploitation (pays) | Moyen — nouveau reporting via dashboard | Faible — bénéfice visible (alertes automatiques) |
| Équipes Qualité | Moyen — nouveau canal de traçabilité | Faible — historiques consultables directement |
| Direction Opérations / Supply Chain (siège) | Faible — vue consolidée multi-pays en plus | Très faible — demandeurs du projet |
| DSI / IT | Faible — maintenance d'un nouvel outil Docker | Faible — compétences adaptées |

---

## 2. Analyse avec le modèle FutureWheel

Le FutureWheel anticipe les conséquences directes et indirectes du déploiement.

```
                    [Déploiement FutureKawa IoT]
                                |
        ┌───────────────────────┼────────────────────────┐
        │                       │                        │
[Relevés automatiques     [Alertes temps réel      [Interface web
 ESP32 toutes les 30s]     email + Discord]          centralisée siège]
        │                       │                        │
   ┌────┴────┐             ┌────┴────┐              ┌────┴────┐
   │         │             │         │              │         │
[Fin des  [Données      [Réactivité [Réduction    [Vision   [Export CSV
 relevés   fiables +     accrue]    des pertes    globale   pour
 manuels]  traçables]               de lots]      multi-    rapports
   │                        │                     pays]     clients]
[Résistance           [Risque faux
 terrain              positifs →
 initialement]        perte confiance]
```

**Conséquences positives anticipées :**
- Réduction des pertes de lots par dérive de conditions ou péremption oubliée (lots > 365j → statut PÉRIMÉ automatique)
- Gain de temps pour les responsables entrepôt (suppression des relevés manuels 2×/jour)
- Traçabilité complète disponible pour les audits clients (historique courbes température/humidité)
- Décision FIFO facilitée grâce au tri automatique par date d'entrée en entrepôt
- Export CSV pour les rapports clients existants

**Risques et conséquences négatives anticipées :**
- Résistance des agents terrain (perception de surveillance accrue via les capteurs)
- Dépendance à la connectivité 4G en entrepôt (atténuée par l'architecture locale par pays)
- Courbe d'apprentissage pour les utilisateurs peu à l'aise avec le numérique
- Faux positifs dans les alertes si les seuils sont mal calibrés → dégradation de la confiance dans l'outil

---

## 3. Analyse avec le modèle de transition de William Bridges

Le modèle de Bridges distingue trois phases psychologiques vécues par les individus face au changement.

### Phase 1 — La fin (Ending)
*Ce que les équipes doivent "lâcher"*

- Les relevés manuels sur tableur ou papier (2 fois par jour par un agent)
- L'habitude de vérifier les conditions visuellement ou à la main
- L'absence de visibilité centralisée (chaque pays gérait ses stocks indépendamment)
- Les signalements informels d'anomalies (appels téléphoniques, messages WhatsApp)

**Action clé :** Ne pas présenter la solution comme une critique du travail passé. Mettre en avant que c'est la croissance de FutureKawa qui rend ce changement nécessaire, pas une insatisfaction des équipes actuelles.

---

### Phase 2 — La zone neutre (Neutral Zone)
*La période de transition, la plus délicate*

Les équipes ont abandonné l'ancien processus mais ne maîtrisent pas encore le nouveau. Risque de désorientation et d'erreurs.

**Durée estimée :** 3 à 4 semaines après le déploiement dans chaque pays.

**Actions :**
- Maintenir les relevés manuels en parallèle les 2 premières semaines (filet de sécurité)
- Désigner un super-utilisateur référent dans chaque entrepôt, formé en avant-première
- Mettre en place un canal de support simple (email ou WhatsApp groupe)
- Afficher le guide utilisateur plastifié dans chaque entrepôt (`docs/utilisateur/guide_utilisateur.md`)

---

### Phase 3 — Le nouveau départ (New Beginning)
*L'adoption de la nouvelle façon de travailler*

Les équipes voient les bénéfices concrets : moins d'interventions manuelles, alertes traitées à temps, lots périmés évités.

**Signes de succès :**
- Les agents consultent spontanément le dashboard sans qu'on le rappelle
- Les alertes email sont traitées en moins de 2 heures
- Aucun lot n'atteint 365 jours sans action d'expédition
- Les relevés manuels ont cessé

---

## 4. Plan d'action sur les 4 axes

### Axe 1 — Informer

| Action | Cible | Canal | Timing |
|---|---|---|---|
| Email de lancement — "Pourquoi ce changement ?" | Toutes les équipes | Email | J-30 |
| Présentation 15 min — enjeux du projet FutureKawa IoT | Responsables exploitation par pays | Visio | J-21 |
| Fiche synthèse A4 "Ce qui change pour vous" | Agents entrepôt | Document papier | J-14 |
| FAQ disponible dans l'application | Tous | Interface web (page FAQ) | Dès le déploiement |

**Message clé :** "Ce n'est pas un outil de surveillance — c'est un système qui vous alerte avant qu'un lot parte en perte et qui supprime les relevés manuels quotidiens."

---

### Axe 2 — Communiquer

| Action | Cible | Canal | Timing |
|---|---|---|---|
| Réunion de lancement par pays (kick-off local) | Responsables exploitation + entrepôt | Présentiel ou visio | J-7 |
| Canal de feedback dédié (formulaire ou email) | Tous les utilisateurs | Google Forms / email | Dès le déploiement |
| Point hebdomadaire "retours terrain" pendant 4 semaines | Super-utilisateurs par pays | Visio 30 min | Semaines 1 à 4 |
| Bilan mensuel d'usage (taux de connexion, alertes traitées) | Direction Opérations | Email | Mois 1, 2, 3 |

---

### Axe 3 — Former

| Action | Cible | Format | Timing |
|---|---|---|---|
| Guide utilisateur complet (parcours, captures d'écran) | Agents entrepôt | PDF + papier plastifié | Disponible au déploiement |
| Session de formation live par pays | Responsables exploitation + entrepôt | Visio 1h | J+2 après déploiement |
| Fiche "5 actions clés" à afficher en entrepôt | Agents terrain | Document papier A4 | J+0 déploiement |
| Formation administrateur (gestion utilisateurs, lots) | Référent IT local | Visio 2h | J+7 |

**Contenu de la formation utilisateur (basé sur l'interface réelle) :**
1. Se connecter avec son compte (rôle USER local ou ADMIN)
2. Consulter la liste des lots triés FIFO — comprendre les badges de statut (vert = CONFORME, orange = ALERTE, rouge = PÉRIMÉ)
3. Lire les courbes de température et d'humidité d'un lot — comprendre les lignes pointillées (seuils idéaux par pays)
4. Comprendre et traiter une alerte email reçue
5. Créer un nouveau lot dans l'interface
6. Exporter les données en CSV pour un rapport client
7. Contacter le support en cas de capteur hors ligne (indicateur visible dans l'interface)

---

### Axe 4 — Faire participer

| Action | Cible | Modalité | Timing |
|---|---|---|---|
| Atelier de validation des seuils par pays | Référents qualité locaux | Workshop 1h | J-14 |
| Pilote sur 1 entrepôt avant déploiement généralisé | Responsable entrepôt volontaire | Test en conditions réelles | J-7 à J+0 |
| Comité utilisateurs mensuel (retours, évolutions) | 1 référent par pays | Visio 30 min | Mois 1, 2, 3 |
| Vote sur les prochaines fonctionnalités | Tous les utilisateurs | Google Forms | Fin mois 2 |
| Désignation d'un super-utilisateur ambassadeur par pays | Responsables entrepôt | Nomination volontaire | J-21 |

**Rôle du super-utilisateur :** formé en avant-première sur l'interface réelle, il est la personne de référence pour ses collègues pendant la zone neutre. Il remonte les problèmes via le canal de support dédié.

---

## 5. Indicateurs de succès

| Indicateur | Objectif | Mesure |
|---|---|---|
| Taux d'adoption (connexions actives / comptes créés) | ≥ 80% à J+30 | Logs de connexion (interface UsersPage) |
| Délai moyen de traitement des alertes email | ≤ 2h | Suivi via canal Discord interne |
| Nombre de lots arrivant à 365j sans expédition | 0 | Dashboard AlertsPage |
| Satisfaction utilisateurs | ≥ 3,5/5 | Formulaire de satisfaction mois 2 |
| Relevés manuels encore effectués | 0 à partir de la semaine 4 | Auto-déclaration responsables |

---

## 6. Questionnaire phase 2 — Interview de cadrage automatisation (Livrable L10)

> Contexte : FutureKawa envisage une phase 2 d'automatisation des entrepôts (chauffage, humidification, aération pilotés automatiquement par les capteurs IoT existants). Ce questionnaire prépare la prochaine réunion client.

---

### Section A — Objectifs métier de l'automatisation

**A1.** Quels équipements souhaitez-vous automatiser en priorité dans vos entrepôts ?
*(système de chauffage, ventilation/aération, humidificateurs, autre)*

**A2.** Quel est le bénéfice métier principal attendu de cette automatisation ?
*(réduction des pertes de lots, économie d'énergie, réduction de la charge des agents, amélioration de la qualité du café)*

**A3.** Sur quels indicateurs mesurerez-vous le succès de la phase 2 ?
*(ex. : réduction de X% des lots en alerte, économie de Y heures/semaine d'intervention manuelle)*

**A4.** Dans quel délai souhaitez-vous voir cette phase 2 opérationnelle ?

**A5.** La phase 2 doit-elle être déployée simultanément dans les trois pays ou pays par pays ? Dans quel ordre ?

---

### Section B — Contraintes de sécurité et responsabilités

**B1.** En cas de déclenchement automatique d'un équipement, qui est responsable si un incident survient ?
*(équipe terrain, prestataire IoT, direction)*

**B2.** Quelles certifications ou normes de sécurité s'appliquent aux équipements de vos entrepôts ?
*(normes électriques locales, normes alimentaires, autre)*

**B3.** Un arrêt d'urgence manuel doit-il être disponible sur chaque actionneur ? Qui peut l'activer ?

**B4.** En cas de panne du système IoT, les équipements doivent-ils se mettre en sécurité par défaut (tout éteint) ou maintenir leur dernier état actif ?

**B5.** Les accès physiques aux équipements doivent-ils être restreints ou tracés ?
*(log d'accès, badge, autre)*

---

### Section C — Tolérances et modes de fonctionnement

**C1.** Quel est le délai maximal acceptable entre la détection d'une dérive et le déclenchement d'un actionneur ?
*(immédiat, 5 min, 15 min)*

**C2.** Souhaitez-vous un déclenchement automatique direct ou une validation humaine avant chaque action ?

**C3.** Y a-t-il des plages horaires où les actionneurs ne doivent jamais se déclencher automatiquement ?
*(nuit, week-end, lors d'inspections qualité)*

**C4.** Un mode "manuel prioritaire" doit-il toujours permettre à un agent de prendre la main sur l'automatisation ?

**C5.** Quelles tolérances avant déclenchement d'un actionneur ?
*(ex. : ventilation uniquement si la température dépasse le seuil depuis plus de 10 minutes)*

---

### Section D — Maintenance et exploitation

**D1.** Qui sera responsable de la maintenance des actionneurs dans chaque pays ?
*(équipe interne, prestataire externe)*

**D2.** À quelle fréquence les équipements devront-ils être vérifiés ou étalonnés ?

**D3.** En cas de panne d'un capteur, comment le système doit-il se comporter ?
*(passer en mode manuel, alerter, maintenir le dernier ordre connu)*

**D4.** Les actionneurs utiliseront-ils le même réseau que l'IoT de surveillance ou une infrastructure dédiée ?

**D5.** Des logs de fonctionnement des actionneurs sont-ils nécessaires pour vos audits qualité ?

---

### Section E — Priorités de déploiement et indicateurs de réussite

**E1.** Quel entrepôt souhaitez-vous utiliser comme pilote pour la phase 2 ? Sur quels critères ?

**E2.** Quels KPIs devrait afficher le tableau de bord de phase 2 ?
*(température moyenne, nombre de déclenchements automatiques, énergie consommée, taux d'intervention manuelle)*

**E3.** Quel budget approximatif est alloué à la phase 2 ? (matériel, installation, maintenance annuelle)

**E4.** Quelles fonctionnalités sont absolument indispensables pour la mise en production de la phase 2 et lesquelles peuvent attendre ?

---

### Section F — Risques et scénarios d'incident

**F1.** Quel scénario d'incident craignez-vous le plus avec une automatisation complète ?
*(surchauffe, humidification excessive, panne généralisée, cyberattaque)*

**F2.** En cas d'incident grave lié à l'automatisation, quelle est la procédure d'escalade ?
*(qui contacte qui, dans quel délai)*

**F3.** Des incidents similaires se sont-ils déjà produits avec des équipements existants ? Quelles leçons en avez-vous tiré ?

**F4.** Souhaitez-vous des alertes si un actionneur reste actif anormalement longtemps ?
*(ex. : ventilation allumée depuis plus de 4h sans retour à la normale)*

**F5.** Un système de redondance est-il nécessaire ?
*(capteur de secours, actionneur de backup, alimentation UPS)*

---

## 7. Méthode de retranscription du questionnaire phase 2

Les réponses seront collectées lors d'une réunion client (visioconférence) avec la Direction Opérations et la Direction SI de FutureKawa. Un Google Forms complémentaire est mis à disposition pour les participants distants.

**Tableau de synthèse (à compléter lors de la réunion de cadrage) :**

| # | Question | Réponse client | Contrainte / Besoin déduit | Priorité |
|---|---|---|---|---|
| A1 | Équipements à automatiser | — | — | — |
| B3 | Arrêt d'urgence manuel | — | — | — |
| C2 | Validation humaine avant action | — | — | — |
| C4 | Mode manuel prioritaire | — | — | — |
| D1 | Responsable maintenance | — | — | — |
| E1 | Entrepôt pilote | — | — | — |
| F1 | Scénario d'incident redouté | — | — | — |

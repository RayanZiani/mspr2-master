# Conduite du changement — FutureKawa IoT
> MSPR TPRE814 — Bloc 4 — Compétence : Conduire le changement auprès des métiers  
> Critère niveau 3 : plan 4 axes + FutureWheel + modèle de Bridges + mise en application via outil  
> Inclut : Questionnaire phase 2 — Livrable L10

---

## 1. Contexte du changement

FutureKawa déploie une plateforme IoT de surveillance des stocks de café vert dans trois pays (Brésil, Équateur, Colombie). Ce déploiement représente un triple changement pour les équipes :

- **Technique** : capteurs ESP32 + DHT11/DHT22, API FastAPI, interface React, alertes email automatiques, architecture Docker multi-pays
- **Organisationnel** : suppression des relevés manuels quotidiens, nouveau processus de traitement des alertes, logique FIFO gérée par l'outil
- **Culturel** : adoption du numérique par des équipes terrain peu habituées aux outils informatiques

**Populations impactées :**

| Population | Impact | Niveau de résistance anticipé |
|---|---|---|
| Agents / responsables entrepôt (terrain) | Fort — changement de leurs processus quotidiens | Élevé — habitudes ancrées, appréhension du numérique |
| Responsables d'exploitation (pays) | Moyen — nouveau reporting et gestion des alertes | Faible — bénéfice visible immédiat |
| Équipes Qualité | Moyen — nouveau canal de traçabilité et d'audit | Faible — historiques consultables directement |
| Direction Opérations / Supply Chain (siège) | Faible — vue consolidée multi-pays en plus | Très faible — demandeurs du projet |
| DSI / IT | Faible — maintenance d'un nouvel outil Docker | Faible — compétences techniques adaptées |

---

## 2. Outil 1 — Analyse FutureWheel

Le FutureWheel permet d'anticiper les conséquences directes et indirectes du déploiement de FutureKawa IoT sur l'organisation.

```
                        [Déploiement FutureKawa IoT]
                                    |
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
[Relevés automatiques       [Alertes email + Discord     [Interface web
 ESP32 toutes les 30s]       automatiques]                centralisée siège]
         │                          │                          │
    ┌────┴────┐                ┌────┴────┐               ┌────┴────┐
    │         │                │         │               │         │
[Fin des   [Données          [Réactivité [Réduction     [Vision   [Export CSV
 relevés    fiables           accrue      des pertes    globale   → rapports
 manuels]   + traçables]      équipes]    de lots]      3 pays]   clients]
    │                          │
[Résistance             [Risque faux positifs
 terrain               → perte de confiance
 initiale]              si seuils mal calibrés]
```

**Conséquences positives identifiées :**
- Suppression des 2 relevés manuels quotidiens par agent
- Détection automatique des dérives avant perte irrémédiable du lot
- Application fiable du FIFO grâce au tri automatique par date d'entrée
- Traçabilité complète disponible pour les audits clients (courbes historiques)
- Export CSV pour intégration dans les rapports clients existants
- Détection des capteurs hors ligne (`_append_disconnected_section`)

**Risques identifiés et mesures de mitigation :**
- Résistance des agents terrain → plan de formation + super-utilisateur ambassadeur
- Faux positifs dans les alertes → seuils co-construits avec les équipes qualité (axe "Faire participer")
- Dépendance réseau → architecture locale par pays indépendante du siège
- Courbe d'apprentissage → guide utilisateur papier + formation visio par pays

---

## 3. Outil 2 — Modèle de transition de William Bridges

Le modèle de Bridges distingue trois phases psychologiques vécues par les individus lors d'un changement. Contrairement à d'autres modèles, il part du principe que le changement est un événement externe, tandis que la transition est un processus interne vécu par chaque personne.

### Phase 1 — La fin (Ending)
*Ce que les équipes doivent "lâcher" pour adopter la nouvelle solution*

- Les relevés manuels sur tableur ou papier (2 fois par jour par un agent)
- La vérification visuelle ou manuelle des conditions de stockage
- L'absence de visibilité centralisée (chaque pays gérait ses stocks indépendamment)
- Les signalements informels d'anomalies par téléphone ou messagerie WhatsApp

**Action clé :** Reconnaître explicitement la valeur du travail passé. Ne pas présenter l'outil comme une critique de l'existant, mais comme une réponse à la croissance internationale de FutureKawa. Message : *"Ce n'est pas que vous travailliez mal — c'est que l'entreprise a grandi et que les outils doivent suivre."*

### Phase 2 — La zone neutre (Neutral Zone)
*La période de transition la plus délicate*

Les équipes ont abandonné l'ancien processus mais ne maîtrisent pas encore le nouveau. Risque de désorientation, d'erreurs et de démotivation.

**Durée estimée :** 3 à 4 semaines après le déploiement dans chaque pays.

**Actions spécifiques :**
- Maintenir les relevés manuels **en parallèle** les 2 premières semaines (filet de sécurité)
- Désigner un **super-utilisateur référent** dans chaque entrepôt, formé en avant-première
- Canal de support dédié (email ou WhatsApp groupe)
- Guide utilisateur papier (`docs/utilisateur/guide_utilisateur.md`) affiché physiquement dans l'entrepôt

### Phase 3 — Le nouveau départ (New Beginning)
*L'adoption et l'appropriation de la nouvelle façon de travailler*

Les équipes voient les bénéfices concrets : moins d'interventions manuelles, alertes traitées à temps, aucun lot périmé oublié.

**Indicateurs de succès :**
- Les agents consultent spontanément le dashboard sans qu'on le leur rappelle
- Les alertes email sont traitées en moins de 2 heures
- Aucun lot n'atteint 365 jours sans action d'expédition
- Les relevés manuels ont cessé après la semaine 4

---

## 4. Plan d'action sur les 4 axes

### Axe 1 — Informer

*Objectif : s'assurer que toutes les parties prenantes comprennent pourquoi le changement est nécessaire et ce qui va changer concrètement.*

| Action | Cible | Canal | Timing |
|---|---|---|---|
| Email de lancement — "Pourquoi ce changement pour FutureKawa ?" | Toutes les équipes | Email | J-30 avant déploiement |
| Présentation 15 min — enjeux IoT et bénéfices attendus | Responsables exploitation par pays | Visio | J-21 |
| Fiche synthèse A4 "Ce qui change pour vous au quotidien" | Agents entrepôt | Document papier | J-14 |
| FAQ accessible dans l'application (page FAQ) | Tous | Interface web (`docs/utilisateur/faq.md`) | Dès le déploiement |

**Message clé :** *"Ce système supprime les relevés manuels quotidiens et vous alerte automatiquement avant qu'un lot parte en perte. Il ne surveille pas votre travail — il travaille à votre place."*

---

### Axe 2 — Communiquer

*Objectif : créer un dialogue continu entre l'équipe projet et les utilisateurs pendant et après le déploiement.*

| Action | Cible | Canal | Timing |
|---|---|---|---|
| Réunion de lancement par pays (kick-off local) | Responsables exploitation + entrepôt | Présentiel ou visio 1h | J-7 |
| Canal de feedback dédié (Google Forms) | Tous | Google Forms | Dès le déploiement |
| Point hebdomadaire "retours terrain" | Super-utilisateurs par pays | Visio 30 min | Semaines 1 à 4 |
| Bilan mensuel — taux de connexion, alertes traitées | Direction Opérations siège | Email avec indicateurs | Mois 1, 2, 3 |
| Remontée anomalies vers l'équipe dev | Tous | Canal dédié | Continu |

---

### Axe 3 — Former

*Objectif : donner aux utilisateurs les compétences nécessaires pour utiliser l'outil en autonomie.*

| Action | Cible | Format | Timing |
|---|---|---|---|
| Guide utilisateur complet avec captures d'écran | Agents entrepôt | PDF + version papier plastifiée en entrepôt | Disponible au déploiement |
| Session de formation live par pays | Responsables exploitation + entrepôt | Visio 1h | J+2 après déploiement |
| Fiche "5 actions clés" à afficher dans l'entrepôt | Agents terrain | Document papier A4 | J+0 déploiement |
| Formation administrateur (gestion utilisateurs, capteurs, seuils) | Référent IT local par pays | Visio 2h | J+7 |

**Contenu de la formation (basé sur l'interface réelle) :**

1. Se connecter avec son compte (rôle `USER` local ou `ADMIN`) — page Login
2. Consulter la liste des lots triés FIFO — comprendre les badges de statut : **vert** = CONFORME, **orange** = ALERTE, **rouge** = PÉRIMÉ, **gris** = EXPÉDIÉ
3. Lire les courbes de température et d'humidité d'un lot — comprendre les lignes pointillées (seuils idéaux par pays avec tolérance ±3°C / ±2%)
4. Comprendre et traiter une alerte email reçue (Alerte Qualité vs Alerte Péremption)
5. Créer un nouveau lot dans l'interface
6. Exporter les données en CSV pour un rapport client
7. Identifier un capteur hors ligne dans le dashboard et contacter le support
8. Se déconnecter et gérer ses accès

---

### Axe 4 — Faire participer

*Objectif : impliquer les utilisateurs dans la solution pour renforcer leur engagement et la qualité du résultat.*

| Action | Cible | Modalité | Timing |
|---|---|---|---|
| Atelier de validation des seuils par pays | Référents qualité locaux | Workshop 1h — co-construction des seuils MQTT | J-14 |
| Pilote sur 1 entrepôt avant déploiement généralisé | Responsable entrepôt volontaire (Brésil — entrepot_A) | Test en conditions réelles | J-7 à J+0 |
| Comité utilisateurs mensuel — retours et évolutions souhaitées | 1 référent par pays | Visio 30 min | Mois 1, 2, 3 |
| Vote sur les prochaines fonctionnalités (export PDF, notifications SMS…) | Tous les utilisateurs | Google Forms | Fin mois 2 |
| Désignation d'un super-utilisateur ambassadeur dans chaque pays | Responsables entrepôt | Nomination volontaire + formation anticipée | J-21 |

**Rôle du super-utilisateur :** formé en avant-première sur l'interface réelle, il est la référence locale pour ses collègues pendant la zone neutre (phase 2 de Bridges). Il remonte les problèmes au canal de support dédié. Ce n'est pas nécessairement un profil IT — c'est quelqu'un de motivé et d'influent dans l'équipe.

---

## 5. Mise en application via outil — Google Forms

Le plan de conduite du changement est mis en application via plusieurs outils :

- **Google Forms** : collecte des besoins (interviews initiales) + feedback post-déploiement + vote fonctionnalités
  - Lien formulaire : [https://docs.google.com/forms/d/e/1FAIpQLSdtsh1O691HgpIeFaXrkhVKwSwHoxGdw0KOJLQpcl45gv3AZA/viewform](https://docs.google.com/forms/d/e/1FAIpQLSdtsh1O691HgpIeFaXrkhVKwSwHoxGdw0KOJLQpcl45gv3AZA/viewform)
- **Interface web FutureKawa** : page FAQ intégrée (`docs/utilisateur/faq.md`), guide utilisateur accessible depuis l'application
- **Documentation versionnée** : tous les documents du plan sont dans `docs/conduite_changement/` du repo Git, versionnés et accessibles à toute l'équipe

---

## 6. Indicateurs de suivi du plan de conduite du changement

| Indicateur | Objectif | Méthode de mesure |
|---|---|---|
| Taux d'adoption — connexions actives / comptes créés | ≥ 80% à J+30 | Logs de connexion (`last_login_at` dans `user_account`) |
| Délai moyen de traitement des alertes email | ≤ 2h | Suivi via canal Discord interne |
| Nombre de lots atteignant 365j sans expédition | 0 | Dashboard AlertsPage + vue `v_lots_trop_anciens` |
| Relevés manuels encore effectués | 0 à partir de la semaine 4 | Auto-déclaration responsables en réunion hebdo |
| Satisfaction utilisateurs | ≥ 3,5 / 5 | Formulaire Google Forms — mois 2 |
| Tickets support reçus / semaine | Tendance décroissante | Canal de support dédié |

---

## 7. Questionnaire phase 2 — Interview de cadrage automatisation (Livrable L10)

> Contexte : FutureKawa envisage une phase 2 d'automatisation des entrepôts — chauffage, humidification, aération pilotés automatiquement par les capteurs IoT existants. Ce questionnaire prépare la prochaine réunion client pour cadrer le périmètre, les contraintes et les priorités.

---

### Section A — Objectifs métier de l'automatisation

**A1.** Quels équipements souhaitez-vous automatiser en priorité dans vos entrepôts ?
*(système de chauffage, ventilation / aération, humidificateurs, autre)*

**A2.** Quel est le bénéfice métier principal attendu de cette automatisation ?
*(réduction des pertes de lots, économie d'énergie, réduction de la charge des agents, amélioration de la qualité)*

**A3.** Sur quels indicateurs mesurerez-vous le succès de la phase 2 ?
*(ex. : réduction de X% des lots en alerte, économie de Y heures/semaine d'intervention manuelle, zéro lot périmé)*

**A4.** Dans quel délai souhaitez-vous voir cette phase 2 opérationnelle ?

**A5.** La phase 2 doit-elle être déployée simultanément dans les trois pays ou pays par pays ? Dans quel ordre de priorité ?

---

### Section B — Contraintes de sécurité et responsabilités

**B1.** En cas de déclenchement automatique d'un équipement (ex. : activation du chauffage), qui est responsable si un incident survient ?
*(équipe terrain, prestataire IoT, direction)*

**B2.** Quelles certifications ou normes de sécurité s'appliquent aux équipements de vos entrepôts ?
*(normes électriques locales Brésil ABNT / Équateur INEN / Colombie RETIE, normes alimentaires, autre)*

**B3.** Un arrêt d'urgence manuel doit-il être disponible sur chaque actionneur ? Qui est habilité à l'activer ?

**B4.** En cas de panne du système IoT, les équipements doivent-ils passer en sécurité (tout éteint) ou maintenir leur dernier état actif ?

**B5.** Les accès physiques aux équipements doivent-ils être restreints ou tracés ?
*(log d'accès, badge, autre)*

---

### Section C — Tolérances et modes de fonctionnement

**C1.** Quel est le délai maximal acceptable entre la détection d'une dérive et le déclenchement d'un actionneur ?
*(immédiat, 5 min, 15 min — selon criticité)*

**C2.** Souhaitez-vous un déclenchement automatique direct ou une validation humaine avant chaque action ?

**C3.** Y a-t-il des plages horaires où les actionneurs ne doivent jamais se déclencher automatiquement ?
*(nuit, week-end, lors d'inspections qualité, audit clients)*

**C4.** Un mode "manuel prioritaire" permettant à un agent de prendre la main sur l'automatisation doit-il toujours être disponible ?

**C5.** Quelle tolérance avant déclenchement d'un actionneur ?
*(ex. : ventilation uniquement si la température dépasse le seuil depuis plus de 10 minutes — éviter les courts-circuits de chauffage)*

---

### Section D — Maintenance et exploitation

**D1.** Qui sera responsable de la maintenance des actionneurs dans chaque pays ?
*(équipe interne, prestataire externe, équipe IT locale)*

**D2.** À quelle fréquence les équipements devront-ils être vérifiés ou étalonnés ?

**D3.** En cas de panne d'un capteur, comment le système doit-il se comporter ?
*(passer en mode manuel, alerter uniquement, maintenir le dernier ordre connu)*

**D4.** Les actionneurs utiliseront-ils la même infrastructure réseau que l'IoT de surveillance actuel ou un réseau dédié ?

**D5.** Des logs de fonctionnement des actionneurs sont-ils nécessaires pour vos audits qualité ou clients ?

---

### Section E — Priorités de déploiement et indicateurs de réussite

**E1.** Quel entrepôt souhaitez-vous utiliser comme site pilote pour la phase 2 ? Sur quels critères le choisissez-vous ?

**E2.** Quels KPIs devrait afficher le tableau de bord de phase 2 ?
*(température moyenne, nombre de déclenchements automatiques, énergie consommée par équipement, taux d'intervention manuelle)*

**E3.** Quel budget approximatif est alloué à la phase 2 ?
*(matériel, installation, maintenance annuelle — ordre de grandeur accepté)*

**E4.** Quelles fonctionnalités sont absolument indispensables pour la mise en production de la phase 2, et lesquelles peuvent attendre une version suivante ?

---

### Section F — Risques et scénarios d'incident

**F1.** Quel scénario d'incident craignez-vous le plus avec une automatisation complète ?
*(surchauffe d'un entrepôt, humidification excessive causant des moisissures, panne généralisée, cyberattaque)*

**F2.** En cas d'incident grave lié à l'automatisation, quelle est la procédure d'escalade ?
*(qui contacte qui, dans quel délai, quelle autorité de décision)*

**F3.** Des incidents similaires se sont-ils déjà produits avec des équipements existants dans vos entrepôts ? Quelles leçons en avez-vous tiré ?

**F4.** Souhaitez-vous des alertes spécifiques si un actionneur reste actif anormalement longtemps sans retour à la normale ?
*(ex. : ventilation en marche depuis plus de 4h sans que la température revienne dans la plage)*

**F5.** Un système de redondance est-il nécessaire ?
*(capteur de secours, actionneur de backup, alimentation UPS pour éviter la perte de contrôle en cas de coupure)*

---

## 8. Tableau de retranscription questionnaire phase 2

> À compléter lors de la réunion de cadrage client (visioconférence avec Direction Opérations + Direction SI FutureKawa).

| # | Question | Réponse client | Contrainte / Besoin déduit | Priorité |
|---|---|---|---|---|
| A1 | Équipements à automatiser en priorité | — | — | — |
| A2 | Bénéfice métier principal | — | — | — |
| B3 | Arrêt d'urgence manuel | — | — | — |
| B4 | Comportement en cas de panne IoT | — | — | — |
| C2 | Validation humaine avant action | — | — | — |
| C4 | Mode manuel prioritaire | — | — | — |
| D1 | Responsable maintenance actionneurs | — | — | — |
| E1 | Site pilote phase 2 | — | — | — |
| E4 | Fonctionnalités indispensables vs optionnelles | — | — | — |
| F1 | Scénario d'incident redouté | — | — | — |
| F5 | Besoin de redondance | — | — | — |

# Guide Utilisateur — FutureKawa

Bienvenue dans le guide d'utilisation de la plateforme de suivi des stocks FutureKawa. Ce document est destiné aux responsables d'exploitation, aux équipes qualité et aux équipes logistiques en entrepôt.

---

## 1. Prise en main de l'interface Web

L'application Web FutureKawa vous permet de suivre l'état de vos stocks de café vert en temps réel, de consulter les conditions de stockage (IoT) et d'être proactif face aux alertes de qualité.

### 1.1. Connexion et droits d'accès
Selon votre profil (identifiants fournis par le service IT), votre vue sera différente :
- **Profil "Siège" (Admin/Direction)** : Vous avez accès à une vue consolidée de tous les pays (Brésil, Équateur, Colombie).
- **Profil "Local" (Responsable ou Entrepôt d'un pays)** : Vous ne voyez que les lots et les entrepôts de votre pays. Vous êtes les seuls autorisés à créer ou modifier des lots pour votre zone géographique.

### 1.2. Navigation principale
Le menu principal (sur la gauche ou en haut de l'écran selon votre appareil) vous donne accès aux sections suivantes :
1. **Tableau de bord (Dashboard)** : Vue d'ensemble, statistiques des stocks et accès rapide aux alertes récentes.
2. **Gestion des Lots** : Liste complète des lots avec possibilité de filtrage et de recherche.
3. **Surveillance IoT** : Vue détaillée des capteurs pour chaque entrepôt.

---

## 2. Création et consultation des lots (Logique FIFO)

La gestion rigoureuse des lots permet d'assurer une traçabilité parfaite et de faciliter les expéditions en appliquant la règle du **FIFO (First In, First Out)** : les lots stockés en premier doivent être expédiés en priorité.

### 2.1. Consulter les lots
- Allez dans la section **Gestion des Lots**.
- Par défaut, les lots sont triés de manière à afficher les plus anciens en premier pour vous aider à prioriser les sorties (FIFO).
- Le tableau affiche : l'ID du lot, l'entrepôt, la date d'entrée, et un **Badge de Statut** (ex: Conforme, En Alerte, Périmé).

### 2.2. Créer un nouveau lot
1. Cliquez sur le bouton **"Nouveau Lot"** en haut à droite de la liste.
2. Remplissez les informations :
   - **ID du Lot** : Identifiant unique de votre récolte/arrivage.
   - **Entrepôt de destination** : Sélectionnez l'entrepôt physique de stockage.
   - **Date d'entrée** : Date du jour par défaut (modifiable).
3. Enregistrez. Le lot apparaîtra désormais dans votre système de suivi.

---

## 3. Lecture des courbes de Température et d'Humidité

Chaque entrepôt est équipé de capteurs IoT (Internet des Objets) qui mesurent en continu la température et l'humidité pour garantir la préservation des arômes du café vert.

### 3.1. Accéder aux courbes
- Depuis la liste des lots, cliquez sur un lot spécifique pour ouvrir ses **Détails**.
- L'onglet **"Conditions de stockage"** affiche les graphiques d'évolution depuis la création du lot.

### 3.2. Comment lire les graphiques ?
- **Ligne Température (en °C)** : Représente la chaleur dans l'entrepôt.
- **Ligne Humidité (en %)** : Représente le taux d'humidité de l'air.
- **Lignes Pointillées (Seuils de tolérance)** : Elles indiquent les limites à ne pas franchir. Ces limites dépendent de votre pays :
  - *Brésil* : Idéal ~29°C / 55% d'humidité.
  - *Équateur* : Idéal ~31°C / 60% d'humidité.
  - *Colombie* : Idéal ~26°C / 80% d'humidité.
- Si une courbe dépasse la ligne pointillée (en prenant en compte la tolérance de ±3°C ou ±2%), l'application bascule le statut du lot "En Alerte".

---

## 4. Compréhension des alertes et actions attendues

La plateforme détecte automatiquement les risques et lève des alertes pour que vous puissiez agir rapidement.

### 4.1. Les deux types d'alertes automatiques
1. **Alerte Qualité (Conditions non idéales)** : La température ou l'humidité est sortie des seuils de tolérance de votre pays.
2. **Alerte Péremption (Lot trop ancien)** : Un lot est stocké depuis plus de 1 an (365 jours).

### 4.2. Actions attendues en cas d'alerte
Lorsqu'une alerte se déclenche, **un email automatique** est envoyé au responsable d'exploitation de votre pays.

**Si vous recevez une Alerte Qualité (Capteurs) :**
1. Connectez-vous et vérifiez la courbe du lot concerné.
2. S'il s'agit d'un pic ponctuel et que les valeurs sont revenues à la normale, aucune action immédiate n'est requise.
3. Si la dérive persiste, une intervention physique dans l'entrepôt est requise (vérification de la climatisation, ventilation, ou déplacement du lot).

**Si vous recevez une Alerte Péremption :**
1. Identifiez le lot concerné.
2. Lancez une inspection visuelle ou gustative (contrôle qualité) du lot physique.
3. Priorisez immédiatement son expédition, ou dégradez son statut s'il n'est plus commercialisable.

---

## 5. Résolution des problèmes simples (FAQ Métier)

**Q : Je ne vois pas les lots des autres pays, est-ce normal ?**
R : Oui. Pour simplifier l'interface et éviter les erreurs de saisie, les utilisateurs en entrepôt ne voient que les stocks de leur propre pays. Si vous avez besoin d'informations globales, contactez le Siège.

**Q : Le graphique indique "Aucune donnée de capteur", que faire ?**
R : Cela signifie que le module IoT de votre entrepôt est probablement éteint ou déconnecté d'Internet. Vérifiez l'alimentation du boîtier capteur physique dans le hangar.

**Q : Un lot a été expédié, comment le retirer de l'application ?**
R : Vous pouvez modifier le statut du lot pour le passer en "Expédié" (ou le supprimer selon les règles de votre exploitation). Il n'apparaîtra plus dans les stocks actifs devant respecter la règle du FIFO.

**Q : Je n'ai pas reçu d'email d'alerte alors que mon lot est au rouge sur l'application.**
R : Vérifiez vos courriers indésirables (Spams). Si le problème persiste, vérifiez auprès de l'équipe Qualité que votre adresse email est bien configurée comme destinataire des alertes de votre exploitation.

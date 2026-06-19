# Schéma de principe : Automatisation (Phase 2)

Ce document présente le prototype de schéma d'automatisation pour le contrôle du chauffage, de l'aération et de l'humidification des entrepôts de FutureKawa. Il répond à la demande de conception de la phase 2 du projet.

## Diagramme d'automatisation

```mermaid
flowchart TD
    %% Capteurs
    subgraph Capteurs [Capteurs (Solution IoT Existante)]
        T[Capteur Température]
        H[Capteur Humidité]
        S[Capteur de Sécurité<br>Fumée / Porte ouverte]
    end

    %% Interface Utilisateur / Commande
    subgraph Commande [Supervision & Commande Locale]
        AutoManu{Sélecteur<br>Auto / Manuel}
        AU((Bouton<br>Arrêt Urgence))
    end

    %% Logique de Traitement
    subgraph Traitement [Unité de Traitement & Décision]
        MQTT[Broker MQTT Existant<br>Point d'intégration]
        Logic[Régulation Automatique<br>Comparaison aux Seuils]
        Securite[Logique de Sécurité &<br>Interverrouillage]
    end

    %% Actionneurs
    subgraph Actionneurs [Equipements de l'entrepôt]
        Chauffage[Système de Chauffage]
        Aeration[Extracteurs / Ventilateurs]
        Humidificateur[Brumiseurs / Humidificateurs]
    end

    %% Flux des données
    T --> MQTT
    H --> MQTT
    MQTT --> Logic

    Logic --> AutoManu
    AutoManu -- "Mode Auto" --> Securite
    AutoManu -- "Mode Manuel" --> Securite
    
    S -- "Alerte Dégradée" --> Securite
    AU -- "Coupure Critique" --> Securite

    %% Déclenchement
    Securite -- "Activer / Désactiver" --> Chauffage
    Securite -- "Activer / Désactiver" --> Aeration
    Securite -- "Activer / Désactiver" --> Humidificateur

    %% Boucle de retour
    Securite -.-> |"Publication statuts & alertes"| MQTT
```

## Description des cas de fonctionnement

### 1. Point d'intégration avec la solution IoT existante
Les capteurs actuels (ESP32 + DHT22) conservent leur rôle sans modification et continuent d'envoyer leurs relevés sur le **Broker MQTT local**. Le système de régulation s'abonne simplement à ce broker pour recevoir les données comme n'importe quel autre client (c'est le point d'intégration).

### 2. Cas Nominal (Mode Automatique)
- Le système analyse en temps réel les données de température et d'humidité.
- **Régulation :**
  - Si la température chute sous le seuil critique (ex: 26°C au Brésil) → activation du **chauffage**.
  - Si l'humidité est trop élevée (ex: > 60% au Brésil) → activation de l'**aération** pour évacuer l'air humide.
  - Si l'humidité est trop faible → activation des **humidificateurs**.
- Les actions décidées par la logique sont envoyées au module de sécurité qui s'assure qu'aucun verrouillage n'est actif avant d'allumer les équipements physiques.

### 3. Cas Dégradé, Sécurités et Mode Manuel
- **Arrêt d'Urgence (AU) :** Si pressé ou déclenché (panne matérielle, danger), le bloc de sécurité coupe instantanément tous les actionneurs (Chauffage, Aération, Humidification) peu importe les directives du mode automatique ou manuel.
- **Mode Manuel :** L'opérateur peut désactiver l'automatisme pour forcer le fonctionnement ou l'arrêt des équipements (pour la maintenance, par exemple). Les sécurités critiques (AU, Incendie) restent prioritaires et outrepassent le mode manuel.
- **Sécurités annexes (Cas dégradé) :** En cas d'événement anormal (ex: détection de fumée, ou portes du hangar grandes ouvertes depuis 10 minutes), le système se met en sécurité. Il empêche par exemple le chauffage de tourner dans le vide, et remonte l'alerte sur le broker MQTT pour informer la direction et le siège.

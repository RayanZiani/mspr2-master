-- Schéma MySQL 8 (pays "local") pour FutureKawa
-- Objectifs: traçabilité des lots, relevés IoT, alertes, FIFO, intégrité.
--
-- Hypothèses:
-- - MySQL 8.x, moteur InnoDB, encodage utf8mb4.
-- - Les UUID sont stockés en CHAR(36) (simple à lire/déboguer).
-- - Fuseaux horaires: on stocke en UTC côté application (DATETIME).

SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- Drop (optionnel pour repartir propre)
-- DROP VIEW IF EXISTS v_releves_entrepot;
-- DROP VIEW IF EXISTS v_lots_trop_anciens;
-- DROP TABLE IF EXISTS alerte;
-- DROP TABLE IF EXISTS releve_capteur;
-- DROP TABLE IF EXISTS capteur;
-- DROP TABLE IF EXISTS lot;
-- DROP TABLE IF EXISTS entrepot;
-- DROP TABLE IF EXISTS exploitation;
-- DROP TABLE IF EXISTS pays;

CREATE TABLE IF NOT EXISTS pays (
  id SMALLINT NOT NULL AUTO_INCREMENT,
  code VARCHAR(2) NOT NULL,
  nom VARCHAR(100) NOT NULL,
  temperature_ideale_c DECIMAL(5,2) NOT NULL,
  humidite_ideale_pct DECIMAL(5,2) NOT NULL,
  tolerance_temperature_c DECIMAL(5,2) NOT NULL DEFAULT 3.00,
  tolerance_humidite_pct DECIMAL(5,2) NOT NULL DEFAULT 2.00,
  email_responsable VARCHAR(255) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_pays_code (code),
  CONSTRAINT chk_pays_humidite CHECK (humidite_ideale_pct BETWEEN 0 AND 100),
  CONSTRAINT chk_pays_tol_temp CHECK (tolerance_temperature_c >= 0),
  CONSTRAINT chk_pays_tol_hum CHECK (tolerance_humidite_pct >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS exploitation (
  id BIGINT NOT NULL AUTO_INCREMENT,
  pays_id SMALLINT NOT NULL,
  nom VARCHAR(150) NOT NULL,
  cree_le DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  UNIQUE KEY uk_exploitation_pays_nom (pays_id, nom),
  KEY idx_exploitation_pays (pays_id),
  CONSTRAINT fk_exploitation_pays
    FOREIGN KEY (pays_id) REFERENCES pays(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS entrepot (
  id BIGINT NOT NULL AUTO_INCREMENT,
  pays_id SMALLINT NOT NULL,
  exploitation_id BIGINT NULL,
  nom VARCHAR(150) NOT NULL,
  adresse VARCHAR(255) NULL,
  cree_le DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  UNIQUE KEY uk_entrepot_pays_nom (pays_id, nom),
  KEY idx_entrepot_pays (pays_id),
  KEY idx_entrepot_exploitation (exploitation_id),
  CONSTRAINT fk_entrepot_pays
    FOREIGN KEY (pays_id) REFERENCES pays(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_entrepot_exploitation
    FOREIGN KEY (exploitation_id) REFERENCES exploitation(id)
    ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS lot (
  id CHAR(36) NOT NULL DEFAULT (UUID()),
  pays_id SMALLINT NOT NULL,
  exploitation_id BIGINT NOT NULL,
  entrepot_id BIGINT NOT NULL,
  entre_le DATETIME(3) NOT NULL,
  sorti_le DATETIME(3) NULL,
  statut ENUM('CONFORME','ALERTE','PERIME','EXPEDIE') NOT NULL DEFAULT 'CONFORME',
  cree_le DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  KEY idx_lot_pays (pays_id),
  KEY idx_lot_exploitation (exploitation_id),
  KEY idx_lot_entrepot (entrepot_id),
  KEY idx_lot_fifo (entrepot_id, entre_le),
  KEY idx_lot_statut (statut),
  CONSTRAINT fk_lot_pays
    FOREIGN KEY (pays_id) REFERENCES pays(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_lot_exploitation
    FOREIGN KEY (exploitation_id) REFERENCES exploitation(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_lot_entrepot
    FOREIGN KEY (entrepot_id) REFERENCES entrepot(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT chk_lot_dates CHECK (sorti_le IS NULL OR sorti_le >= entre_le)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS capteur (
  id CHAR(36) NOT NULL DEFAULT (UUID()),
  entrepot_id BIGINT NOT NULL,
  numero_serie VARCHAR(100) NOT NULL,
  modele VARCHAR(100) NULL,
  installe_le DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  UNIQUE KEY uk_capteur_numero_serie (numero_serie),
  KEY idx_capteur_entrepot (entrepot_id),
  CONSTRAINT fk_capteur_entrepot
    FOREIGN KEY (entrepot_id) REFERENCES entrepot(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS releve_capteur (
  id BIGINT NOT NULL AUTO_INCREMENT,
  capteur_id CHAR(36) NOT NULL,
  mesure_le DATETIME(3) NOT NULL,
  temperature_c DECIMAL(5,2) NOT NULL,
  humidite_pct DECIMAL(5,2) NOT NULL,
  cree_le DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  UNIQUE KEY uk_releve_capteur_time (capteur_id, mesure_le),
  KEY idx_releve_capteur_temps_desc (capteur_id, mesure_le),
  CONSTRAINT fk_releve_capteur_capteur
    FOREIGN KEY (capteur_id) REFERENCES capteur(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT chk_releve_humidite CHECK (humidite_pct BETWEEN 0 AND 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS alerte (
  id BIGINT NOT NULL AUTO_INCREMENT,
  type ENUM('CONDITION','AGE') NOT NULL,
  pays_id SMALLINT NOT NULL,
  entrepot_id BIGINT NOT NULL,
  lot_id CHAR(36) NULL,
  ouverte_le DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  fermee_le DATETIME(3) NULL,
  email_envoye_le DATETIME(3) NULL,
  message TEXT NOT NULL,
  PRIMARY KEY (id),
  KEY idx_alerte_pays (pays_id),
  KEY idx_alerte_entrepot (entrepot_id),
  KEY idx_alerte_lot (lot_id),
  KEY idx_alerte_entrepot_temps (entrepot_id, ouverte_le),
  CONSTRAINT fk_alerte_pays
    FOREIGN KEY (pays_id) REFERENCES pays(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_alerte_entrepot
    FOREIGN KEY (entrepot_id) REFERENCES entrepot(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_alerte_lot
    FOREIGN KEY (lot_id) REFERENCES lot(id)
    ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT chk_alerte_dates CHECK (fermee_le IS NULL OR fermee_le >= ouverte_le)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Vue: lots trop anciens (> 365 jours)
CREATE OR REPLACE VIEW v_lots_trop_anciens AS
SELECT
  l.*,
  TIMESTAMPDIFF(SECOND, l.entre_le, UTC_TIMESTAMP(3)) AS duree_stockage_secondes
FROM lot l
WHERE l.sorti_le IS NULL
  AND l.entre_le <= (UTC_TIMESTAMP(3) - INTERVAL 365 DAY);

-- Vue: relevés agrégés par entrepôt (moyenne des capteurs)
CREATE OR REPLACE VIEW v_releves_entrepot AS
SELECT
  e.id AS entrepot_id,
  r.mesure_le,
  AVG(r.temperature_c) AS temperature_c,
  AVG(r.humidite_pct) AS humidite_pct
FROM entrepot e
JOIN capteur c ON c.entrepot_id = e.id
JOIN releve_capteur r ON r.capteur_id = c.id
GROUP BY e.id, r.mesure_le;


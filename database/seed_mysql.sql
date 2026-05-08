SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- Pays + règles (issues du cahier des charges)
INSERT INTO pays (code, nom, temperature_ideale_c, humidite_ideale_pct, tolerance_temperature_c, tolerance_humidite_pct, email_responsable)
VALUES
  ('BR', 'Brésil',   29.00, 55.00, 3.00, 2.00, 'responsable.br@futurekawa.local'),
  ('EC', 'Équateur', 31.00, 60.00, 3.00, 2.00, 'responsable.ec@futurekawa.local'),
  ('CO', 'Colombie', 26.00, 80.00, 3.00, 2.00, 'responsable.co@futurekawa.local')
ON DUPLICATE KEY UPDATE
  nom = VALUES(nom),
  temperature_ideale_c = VALUES(temperature_ideale_c),
  humidite_ideale_pct = VALUES(humidite_ideale_pct),
  tolerance_temperature_c = VALUES(tolerance_temperature_c),
  tolerance_humidite_pct = VALUES(tolerance_humidite_pct),
  email_responsable = VALUES(email_responsable);

-- Exemple minimal BR (1 exploitation + 1 entrepôt + 1 lot)
SET @pays_br := (SELECT id FROM pays WHERE code = 'BR' LIMIT 1);

INSERT INTO exploitation (pays_id, nom)
VALUES (@pays_br, 'Fazenda Alpha')
ON DUPLICATE KEY UPDATE nom = VALUES(nom);

SET @exploitation_id := (
  SELECT id FROM exploitation
  WHERE pays_id = @pays_br AND nom = 'Fazenda Alpha'
  LIMIT 1
);

INSERT INTO entrepot (pays_id, exploitation_id, nom, adresse)
VALUES (@pays_br, @exploitation_id, 'Entrepôt São Paulo', 'São Paulo')
ON DUPLICATE KEY UPDATE adresse = VALUES(adresse);

SET @entrepot_id := (
  SELECT id FROM entrepot
  WHERE pays_id = @pays_br AND nom = 'Entrepôt São Paulo'
  LIMIT 1
);

INSERT INTO lot (pays_id, exploitation_id, entrepot_id, entre_le, statut)
VALUES (@pays_br, @exploitation_id, @entrepot_id, (UTC_TIMESTAMP(3) - INTERVAL 10 DAY), 'CONFORME');

SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- Pays + règles (issues du cahier des charges)
INSERT INTO pays (code, nom, temperature_ideale_c, humidite_ideale_pct, tolerance_temperature_c, tolerance_humidite_pct, email_responsable)
VALUES
  ('BR', 'Brésil',   29.00, 55.00, 3.00, 2.00, 'responsable.br@futurekawa.local'),
  ('EC', 'Équateur', 31.00, 60.00, 3.00, 2.00, 'responsable.ec@futurekawa.local'),
  ('CO', 'Colombie', 26.00, 80.00, 3.00, 2.00, 'responsable.co@futurekawa.local')
ON DUPLICATE KEY UPDATE
  nom = VALUES(nom),
  temperature_ideale_c = VALUES(temperature_ideale_c),
  humidite_ideale_pct = VALUES(humidite_ideale_pct),
  tolerance_temperature_c = VALUES(tolerance_temperature_c),
  tolerance_humidite_pct = VALUES(tolerance_humidite_pct),
  email_responsable = VALUES(email_responsable);

-- Exemple minimal BR (1 exploitation + 1 entrepôt + 1 lot)
SET @pays_br := (SELECT id FROM pays WHERE code = 'BR' LIMIT 1);

INSERT INTO exploitation (pays_id, nom)
VALUES (@pays_br, 'Fazenda Alpha')
ON DUPLICATE KEY UPDATE nom = VALUES(nom);

SET @exploitation_id := (
  SELECT id FROM exploitation
  WHERE pays_id = @pays_br AND nom = 'Fazenda Alpha'
  LIMIT 1
);

INSERT INTO entrepot (pays_id, exploitation_id, nom, adresse)
VALUES (@pays_br, @exploitation_id, 'Entrepôt São Paulo', 'São Paulo')
ON DUPLICATE KEY UPDATE adresse = VALUES(adresse);

SET @entrepot_id := (
  SELECT id FROM entrepot
  WHERE pays_id = @pays_br AND nom = 'Entrepôt São Paulo'
  LIMIT 1
);

INSERT INTO lot (pays_id, exploitation_id, entrepot_id, entre_le, statut)
VALUES (@pays_br, @exploitation_id, @entrepot_id, (UTC_TIMESTAMP(3) - INTERVAL 10 DAY), 'CONFORME');


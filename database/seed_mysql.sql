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
VALUES (@pays_br, 'Exploitation BR-1')
ON DUPLICATE KEY UPDATE nom = VALUES(nom);

SET @exploitation_id := (
  SELECT id FROM exploitation
  WHERE pays_id = @pays_br AND nom = 'Exploitation BR-1'
  LIMIT 1
);

INSERT INTO entrepot (pays_id, exploitation_id, nom, adresse)
VALUES (@pays_br, @exploitation_id, 'Entrepôt BR-1', 'Brésil - site 1')
ON DUPLICATE KEY UPDATE adresse = VALUES(adresse);

SET @entrepot_id := (
  SELECT id FROM entrepot
  WHERE pays_id = @pays_br AND nom = 'Entrepôt BR-1'
  LIMIT 1
);

INSERT INTO lot (pays_id, exploitation_id, entrepot_id, entre_le, statut)
VALUES (@pays_br, @exploitation_id, @entrepot_id, (UTC_TIMESTAMP(3) - INTERVAL 10 DAY), 'CONFORME');

-- Comptes applicatifs (siège) — users de développement
INSERT INTO user_account (username, password_hash, role, pays_code, email, active)
VALUES
  ('admin_siege',        '$2b$12$hrcCoLHsdEnHTSB/pucd9.KWhPkmFOqB9f7R0vjHBiO0qq32eOp3a', 'SUPER_ADMIN', 'SIEGE',    'admin@futurekawa.com',        1),
  ('direction_siege',    '$2b$12$7mgmZCs28/vPLx3ej4UADOPw1G999syXUrK5AGOLLb3l6k91/loq6', 'USER',  'SIEGE',    'direction@futurekawa.com',    1),
  ('supply_siege',       '$2b$12$BWhEsz0ydjK.CA0hT46XEeCGVXjenfbsIM9.Dn592b7KReCzY3K6W', 'USER',  'SIEGE',    'supply@futurekawa.com',       1),
  ('resp_bresil',        '$2b$12$IGTl7YjBnncax91d.acQZ.Iyqi/JpkLt16P4Z6k/NEvk17F4rdIam', 'USER',  'BRESIL',   'resp.br@futurekawa.com',      1),
  ('entrepot_bresil',    '$2b$12$PGlRENFr38MKcIECa7548uQlPGbLGiZgPhTf9/CwQ09pefz0Yt7YS', 'USER',  'BRESIL',   'entrepot.br@futurekawa.com',  1),
  ('qualite_bresil',     '$2b$12$TcOzYhijBVlMluyAwV6oquUyns2o6ESYJF7qkYsbt6u/cHBM5dF1O', 'USER',  'BRESIL',   'qualite.br@futurekawa.com',   1),
  ('resp_equateur',      '$2b$12$Vrm6idcHqozQL0nI0OboZOUnhpXIHnjr7IIDUOxdU2l81uVTi.S6C', 'USER',  'EQUATEUR', 'resp.eq@futurekawa.com',      1),
  ('entrepot_equateur',  '$2b$12$gzBY3dCauFY0KDlxwjd3kOAUL.Mj8wjP96al4KEYEePcDYJfc7pG2', 'USER',  'EQUATEUR', 'entrepot.eq@futurekawa.com',  1),
  ('qualite_equateur',   '$2b$12$/72FWHyqMjpoiJs2vT0OgOZNeDlLNMF/2rH/CUconi9vPId/MKDkK', 'USER',  'EQUATEUR', 'qualite.eq@futurekawa.com',   1),
  ('resp_colombie',      '$2b$12$xB0X6kZT3nUUMfJfsK9VY.tJWxKys//bb95GcaEOSCNAdv1T8Cory', 'USER',  'COLOMBIE', 'resp.co@futurekawa.com',      1),
  ('entrepot_colombie',  '$2b$12$Ogi4xC3XnoEgGzxwxAw2BuZ116YZpg0wsDDNfegc5rdg9Zu73Xuea', 'USER',  'COLOMBIE', 'entrepot.co@futurekawa.com',  1),
  ('qualite_colombie',   '$2b$12$bw8YIDoKsDdP1oLSGwfn/e1M6/4rNYhsggONEtkMF6sEqU/DpCLy6', 'USER',  'COLOMBIE', 'qualite.co@futurekawa.com',   1)
ON DUPLICATE KEY UPDATE
  password_hash = VALUES(password_hash),
  role = VALUES(role),
  pays_code = VALUES(pays_code),
  email = VALUES(email),
  active = VALUES(active);

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
VALUES (@pays_br, 'Exploitation BR-1')
ON DUPLICATE KEY UPDATE nom = VALUES(nom);

SET @exploitation_id := (
  SELECT id FROM exploitation
  WHERE pays_id = @pays_br AND nom = 'Exploitation BR-1'
  LIMIT 1
);

INSERT INTO entrepot (pays_id, exploitation_id, nom, adresse)
VALUES (@pays_br, @exploitation_id, 'Entrepôt BR-1', 'Brésil - site 1')
ON DUPLICATE KEY UPDATE adresse = VALUES(adresse);

SET @entrepot_id := (
  SELECT id FROM entrepot
  WHERE pays_id = @pays_br AND nom = 'Entrepôt BR-1'
  LIMIT 1
);

INSERT INTO lot (pays_id, exploitation_id, entrepot_id, entre_le, statut)
VALUES (@pays_br, @exploitation_id, @entrepot_id, (UTC_TIMESTAMP(3) - INTERVAL 10 DAY), 'CONFORME');


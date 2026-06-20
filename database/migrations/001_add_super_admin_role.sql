-- Ajoute le role SUPER_ADMIN et promeut admin_siege (compte proprietaire).
-- A executer une fois sur Aiven si la table existe deja avec ENUM('ADMIN','USER').

ALTER TABLE user_account
  MODIFY role ENUM('SUPER_ADMIN', 'ADMIN', 'USER') NOT NULL DEFAULT 'USER';

UPDATE user_account
SET role = 'SUPER_ADMIN'
WHERE username = 'admin_siege' AND role = 'ADMIN';

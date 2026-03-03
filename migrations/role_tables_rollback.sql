-- Rollback: remove role and user_roles tables

BEGIN;

DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS role;

COMMIT;

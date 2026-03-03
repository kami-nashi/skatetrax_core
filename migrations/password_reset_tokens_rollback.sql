-- Rollback: remove password_reset_tokens table

BEGIN;

DROP TABLE IF EXISTS password_reset_tokens;

COMMIT;

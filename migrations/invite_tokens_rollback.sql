-- Rollback: remove invite_tokens table

BEGIN;

DROP TABLE IF EXISTS invite_tokens;

COMMIT;

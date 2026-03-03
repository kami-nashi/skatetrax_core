-- Create password_reset_tokens table for forgot-password flow

BEGIN;

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(64) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES "uAuthTable"(id),
    created_at TIMESTAMP DEFAULT now(),
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN NOT NULL DEFAULT false
);

COMMIT;

-- Create invite_tokens table for invite-only beta registration

BEGIN;

CREATE TABLE IF NOT EXISTS invite_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(64) UNIQUE NOT NULL,
    created_by INTEGER REFERENCES "uAuthTable"(id),
    created_at TIMESTAMP DEFAULT now(),
    expires_at TIMESTAMP,
    max_uses INTEGER NOT NULL DEFAULT 1,
    use_count INTEGER NOT NULL DEFAULT 0
);

COMMIT;

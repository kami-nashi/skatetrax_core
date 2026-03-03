-- Create role + user_roles tables and migrate data from JSONB

BEGIN;

CREATE TABLE IF NOT EXISTS role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) UNIQUE NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "uAuthTable"(id),
    role_id INTEGER NOT NULL REFERENCES role(id),
    CONSTRAINT uq_user_roles UNIQUE (user_id, role_id)
);

-- Seed role from u_skater_types
INSERT INTO role (id, name, description)
SELECT id, lower(label), label
FROM u_skater_types
ON CONFLICT DO NOTHING;

-- Migrate JSONB role assignments into user_roles
INSERT INTO user_roles (user_id, role_id)
SELECT a.id, r.value::int
FROM "uSkaterConfig" sc,
     jsonb_array_elements(sc."uSkaterRoles") AS r(value),
     "uAuthTable" a
WHERE a."uSkaterUUID" = sc."uSkaterUUID"
  AND r.value::int IN (SELECT id FROM role)
ON CONFLICT ON CONSTRAINT uq_user_roles DO NOTHING;

COMMIT;

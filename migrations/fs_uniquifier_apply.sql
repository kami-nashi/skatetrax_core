-- Add fs_uniquifier column to uAuthTable (Flask-Security-Too 4.0+ requirement).
-- Independent of uSkaterUUID, which remains the data-aggregation key.

BEGIN;

ALTER TABLE "uAuthTable" ADD COLUMN fs_uniquifier VARCHAR(64);

UPDATE "uAuthTable"
SET fs_uniquifier = replace(gen_random_uuid()::text, '-', '')
WHERE fs_uniquifier IS NULL;

ALTER TABLE "uAuthTable" ALTER COLUMN fs_uniquifier SET NOT NULL;

ALTER TABLE "uAuthTable"
  ADD CONSTRAINT uq_uauthtable_fs_uniquifier UNIQUE (fs_uniquifier);

COMMIT;

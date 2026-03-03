-- Rollback: remove fs_uniquifier column from uAuthTable

BEGIN;

ALTER TABLE "uAuthTable" DROP CONSTRAINT IF EXISTS uq_uauthtable_fs_uniquifier;
ALTER TABLE "uAuthTable" DROP COLUMN IF EXISTS fs_uniquifier;

COMMIT;

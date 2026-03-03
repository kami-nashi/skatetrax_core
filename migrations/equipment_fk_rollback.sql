-- Remove the equipment FK constraints (use only if you need to roll back the migration).

BEGIN;

ALTER TABLE "uSkateConfig"   DROP CONSTRAINT IF EXISTS fk_uskateconfig_uskateruuid;
ALTER TABLE "uSkaterBlades" DROP CONSTRAINT IF EXISTS fk_uskaterblades_uskateruuid;
ALTER TABLE "uSkaterBoots"   DROP CONSTRAINT IF EXISTS fk_uskaterboots_uskateruuid;

COMMIT;

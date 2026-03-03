-- Add FK constraints: equipment uSkaterUUID -> uSkaterConfig.uSkaterUUID, ON DELETE CASCADE
-- Run equipment_fk_check_orphans.sql first; fix any orphaned rows before running this.

BEGIN;

ALTER TABLE "uSkateConfig"
  ADD CONSTRAINT fk_uskateconfig_uskateruuid
  FOREIGN KEY ("uSkaterUUID") REFERENCES "uSkaterConfig"("uSkaterUUID") ON DELETE CASCADE;

ALTER TABLE "uSkaterBlades"
  ADD CONSTRAINT fk_uskaterblades_uskateruuid
  FOREIGN KEY ("uSkaterUUID") REFERENCES "uSkaterConfig"("uSkaterUUID") ON DELETE CASCADE;

ALTER TABLE "uSkaterBoots"
  ADD CONSTRAINT fk_uskaterboots_uskateruuid
  FOREIGN KEY ("uSkaterUUID") REFERENCES "uSkaterConfig"("uSkaterUUID") ON DELETE CASCADE;

COMMIT;

-- Run this before equipment_fk_apply.sql.
-- Any non-zero count means you have orphaned rows; fix them before adding FKs.

\echo '=== Orphan check: equipment uSkaterUUID not in uSkaterConfig ==='

SELECT 'uSkateConfig' AS table_name, COUNT(*) AS orphan_count
FROM "uSkateConfig" c
WHERE c."uSkaterUUID" IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM "uSkaterConfig" u WHERE u."uSkaterUUID" = c."uSkaterUUID")
UNION ALL
SELECT 'uSkaterBlades', COUNT(*)
FROM "uSkaterBlades" b
WHERE b."uSkaterUUID" IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM "uSkaterConfig" u WHERE u."uSkaterUUID" = b."uSkaterUUID")
UNION ALL
SELECT 'uSkaterBoots', COUNT(*)
FROM "uSkaterBoots" b
WHERE b."uSkaterUUID" IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM "uSkaterConfig" u WHERE u."uSkaterUUID" = b."uSkaterUUID");

\echo 'If all orphan_count are 0, safe to run equipment_fk_apply.sql'

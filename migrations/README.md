# Schema migrations

Two ways to apply schema changes:

1. **Alembic** (recommended) — versioned migrations, same PGDB_* env as the app. Use for ongoing changes.
2. **Manual SQL** in `migrations/*.sql` — one-off scripts if you prefer not to use Alembic for a step.

**Order of operations:** Check for bad data → fix if needed → apply migration → verify.

---

## Local practice: Postgres 17 in Podman

From `skatetrax_core`:

```bash
./scripts/run_pg17_podman.sh
```

Then copy the printed `export PGDB_*` lines into your shell. Create the base tables, then run Alembic:

```bash
export PGDB_HOST=127.0.0.1
export PGDB_NAME=skatetrax
export PGDB_USER=skatetrax
export PGDB_PASSWORD=skatetrax

python -m skatetrax.models.setup_db -c    # create tables (no FKs on equipment yet)
alembic upgrade head                      # add equipment FKs
alembic current                           # should show 001_equip_fk
```

Optional env before running the script: `PG_USER`, `PG_PASSWORD`, `PG_DB`, `PG_PORT`, `SKATETRAX_PG_CONTAINER`.

---

## Using Alembic

Alembic lives in **skatetrax_core** and uses the same `PGDB_HOST`, `PGDB_NAME`, `PGDB_USER`, `PGDB_PASSWORD` env vars as the app.

**First time (install):**
```bash
cd skatetrax_core
pip install -e .   # or your venv
```

**Before any migration that adds FKs:** run the orphan check (see equipment_fk below) and fix data if needed.

**Apply all pending migrations (dev or prod):**
```bash
cd skatetrax_core
export PGDB_HOST=... PGDB_NAME=... PGDB_USER=... PGDB_PASSWORD=...
alembic upgrade head
```

**See current revision:**
```bash
alembic current
```

**Roll back one revision:**
```bash
alembic downgrade -1
```

**New migration (after changing models):**
```bash
alembic revision -m "describe_change"
# Edit alembic/versions/xxxx_describe_change.py with upgrade() and downgrade()
```

**Existing DB that already has the change (e.g. you ran SQL by hand):** tell Alembic “we’re at head” so it doesn’t re-run:
```bash
alembic stamp head
```

---

## equipment_fk: Add FK on equipment uSkaterUUID columns

Adds `REFERENCES "uSkaterConfig"(uSkaterUUID) ON DELETE CASCADE` to:

- `"uSkateConfig".uSkaterUUID`
- `"uSkaterBlades".uSkaterUUID`
- `"uSkaterBoots".uSkaterUUID`

### 1. Check for orphaned rows (run first)

Orphans = rows whose `uSkaterUUID` is not in `"uSkaterConfig".uSkaterUUID`. The new FK will fail if any exist.

```bash
psql "$DATABASE_URL" -f migrations/equipment_fk_check_orphans.sql
```

If any count is > 0, fix or delete those rows before applying the migration. (You may need to insert missing users in `uSkaterConfig` or delete the orphan equipment rows.)

### 2. Apply the migration

**Option A — Alembic (recommended):**
```bash
cd skatetrax_core
# PGDB_* already set for your env
alembic upgrade head
```

**Option B — Raw SQL:**
```bash
psql "$DATABASE_URL" -f migrations/equipment_fk_apply.sql
# or
psql "postgresql://$PGDB_USER:$PGDB_PASSWORD@$PGDB_HOST/$PGDB_NAME" -f migrations/equipment_fk_apply.sql
```

### 3. Verify

- App still works (e.g. dashboard, equipment views).
- Cascading delete: delete a row from `"uSkaterConfig"` (or a test user); their rows in `uSkateConfig`, `uSkaterBlades`, `uSkaterBoots` should be removed.

### Rollback (if needed)

If you must remove the constraints:

```bash
psql "$DATABASE_URL" -f migrations/equipment_fk_rollback.sql
```

Then you can fix data and re-apply.

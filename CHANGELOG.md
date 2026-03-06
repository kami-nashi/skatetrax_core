# Changelog

All notable changes to this project will be documented in this file.

## [4.1.3] - 2026-03-05
### Added
- Parent/child event structure: `e_events` (model: `SkaterEvent`) and `e_event_entries` (model: `EventEntry`) replace the flat `e_competition` table. One event contains one or more entries (individual segments).
- `entry_date` column on `EventEntry` for multi-day competitions where each segment may occur on a different day. (Migration: `009_entry_date_column`)
- `e_governing_bodies` reference table (model: `GoverningBody`) seeded with None, USFSA, ISI, Other.
- `e_event_types` dimensional table (model: `EventType`) with category, scoring_system, governing_body_id, and single_mark. Replaces `e_competition_types`.
- `e_scores_6_0` table (model: `Score6_0`) for per-judge 6.0 ordinal scoring (judge_number, ordinal, technical_merit, presentation).
- `e_scores_cjs` table (model: `ScoreCJS`) for per-judge CJS component scoring (artistic_appeal, performance, skating_skills). (Migration: `010_rename_cjs_composition` renames `composition` to `performance` to match USFSA terminology.)
- `e_scores_ijs_components` table (model: `ScoreIJSComponent`) for per-judge IJS program component scores (composition, presentation, skating_skills).
- `e_scores_ijs_elements` table (model: `ScoreIJSElement`) for per-element IJS technical scores (element_name, base_value, goe, final_score).
- `e_deductions` table (model: `EventDeduction`) for falls, time violations, and other deductions per entry.
- `Event_Data` class in `pencil.py`:
  - `add_event_with_entries()` creates events with entries, scores (all 3 systems), and deductions in a single transaction.
  - `add_entry()` attaches a single entry with scores and deductions to an existing event (manual wizard path).
  - `resolve_event_type()` looks up an `EventType` UUID from human-readable category/scoring_system/governing_body strings.
- `EventHistory` query class in `data_aggregates.py` with `list_events()` and `get_event_detail()`.
- `EventsTable.list_competitions()` in `data_tables.py` -- DataFrame-based list view with event_date, entry_date, event_label, event_cost, hosting_club, event_segment, event_level, placement, field_size.
- `EventDetail.get()` in `data_details.py` -- single-record detail view joining location, coach, entries, all scoring systems, and deductions. Includes governing body in the event_type block.
- `SkaterAggregates` new methods: `event_count()`, `entry_count()`, `podium_count()` -- all with timeframe support.
- `competition_cost()` now supports timeframe filtering.
- `monthly_times_json()` competition flag now queries `SkaterEvent.event_date` instead of ice_time skate_type hack.
- Migration `007_competition_results_schema` drops legacy tables, creates the new schema, re-points `e_tests.test_type` FK, and seeds governing bodies and event types.
- `e_import_log` table (model: `ImportLog`) for auditing URL-based results imports. (Migration: `008_import_log`)
- `skatetrax/utils/results_parser.py` -- 6.0 ordinal parser for `ijs.usfigureskating.org`. Domain-whitelisted, returns structured standings data.
- `skatetrax/utils/results_parser_ijs.py` -- IJS judge-detail parser. Extracts executed elements, program components, and deductions per skater.
- `skatetrax/utils/results_parser_cjs.py` -- CJS showcase parser. Extracts artistic appeal, performance, and skating skills panel scores.
- `skatetrax/utils/results_importer.py` -- orchestrator with auto-detection of scoring system (6.0/IJS/CJS) from URL pattern and page content. Includes `import_from_url()` (new event) and `import_entry_to_event()` (attach to existing event). Duplicate detection, import logging, score and deduction persistence.

### Changed
- `resolve_event_type()` now accepts nullable `scoring_system` and `governing_body_short` parameters for exhibitions and other unsanctioned events. Auto-creates the `EventType` row if the combination doesn't exist yet.
- `EventsTable.list_competitions()` now includes `video_url`, `location_name`, `location_city`, and `location_state` columns via a join to the `locations` table.
- `competition_cost()` in `SkaterAggregates` now queries `EventCost` line items (instead of removed `event_cost` column) with optional timeframe filtering.
- `monthly_times_json()` competition series sourced from `SkaterEvent.event_date` rather than filtering ice_time by skate_type.
- `ScoreCJS.composition` renamed to `ScoreCJS.performance` to match USFSA CJS terminology.
- `Event_Test.test_type` FK now references `e_event_types` instead of the dropped `e_competition_types`.

### Removed
- `e_competition` table and `Events_Competition` model.
- `e_competition_types` table and `CompetitionType` model.
- `uSkaterRoles` JSONB column from `uSkaterConfig`. Roles are now stored exclusively in the `role` + `user_roles` tables (added in 4.1.0). (Migration: `006_drop_legacy_roles`)
- `uSkaterRoles` model class and its backing `u_skater_types` table -- superseded by the `Role` model in `t_auth.py`.
- `add_skater_roles()` methods from `pencil.py` and `updaters.py`.
- `uSkaterRoles` key from the profile dict returned by `data_aggregates.py`. Profile routes already read roles from `current_user.roles`.

## [4.1.2] - 2026-03-03
### Added
- `skatetrax/auth/` package with `service.py` -- centralizes all auth business logic (user CRUD, roles, invite tokens, password reset tokens) as plain functions with no Flask dependency. Designed to be the single entry point for auth operations from any consumer (`st_bea`, admin scripts, future CLI tools).

## [4.1.1] - 2026-03-03
### Added
- `password_reset_tokens` table for time-limited, single-use forgot-password tokens. (Migration: `005_pw_reset`)
- `PasswordResetToken` model with `is_valid()` (checks `used` flag and 1-hour expiry).

## [4.1.0] - 2026-03-01
### Added
- `fs_uniquifier` column on `uAuthTable` for Flask-Security-Too 4.0+ session token management. Independent of `uSkaterUUID`, which remains the data-aggregation key. (Migration: `002_fs_uniquifier`)
- `role` table and `user_roles` junction table for FST-compatible role management. Seeded from existing `u_skater_types`. (Migration: `003_role_tables`)
- Data migration from `uSkaterConfig.uSkaterRoles` JSONB into `user_roles` junction rows.
- `invite_tokens` table for invite-only beta registration. Supports single-use, multi-use, and unlimited tokens with optional expiration. (Migration: `004_invite_tokens`)
- `Role` model with `get_permissions()` for FST compatibility.
- `UserRoles` junction model.
- `InviteToken` model with `is_valid()` validation (checks expiry and use count; `max_uses=0` means unlimited).
- `roles` relationship and `has_role()` method on `uAuthTable`.
- `active`, `is_authenticated`, `is_active` properties and `get_id()` (returns `fs_uniquifier`) on `uAuthTable` for Flask-Login/FST integration.

### Changed
- `uAuthTable.get_id()` now returns `fs_uniquifier` instead of `str(id)` for FST session management.

## [4.0.0] - 2025-08-12
### Added
- Complete rewrite of backend with PostgreSQL and `skatetrax_core` package.
- New REST API endpoints designed for modern frontend integration.
- Major refactor of data models and database schema.
- Secure user authentication with Flask and hashed passwords.
- React-based frontend planned with clean API separation.
- Containerization considerations.

### Changed
- Dropped backward compatibility with v3.x and earlier versions.
- Removed legacy PHP and MySQL codebase.
- Redesigned app structure and module imports for clarity and scalability.

### Removed
- Legacy UI components incompatible with new API.
- Deprecated database tables and outdated data formats.

---

## Versioning Guidance

We follow [Semantic Versioning](https://semver.org/) (SemVer):

- **MAJOR version (X.y.z)**  
  Increment when you make incompatible API changes or major rewrites that break backward compatibility (like now going from v3 → v4).

- **MINOR version (x.Y.z)**  
  Increment when you add functionality in a backward-compatible manner. Examples: new endpoints, new features, performance improvements without breaking changes.

- **PATCH version (x.y.Z)**  
  Increment when you make backward-compatible bug fixes. Examples: fixing typos, patching security vulnerabilities, small code refactors without changing API behavior.

---

## Example future versions

- 4.0.1 → Bug fix release after 4.0.0 production launch.
- 4.1.0 → Add new API endpoints or frontend features without breaking current clients.
- 5.0.0 → Another major rewrite that breaks backward compatibility.
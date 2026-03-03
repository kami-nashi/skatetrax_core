# Changelog

All notable changes to this project will be documented in this file.

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
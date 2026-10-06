# Database README

MySQL stores the project's operational records. The backend accesses it through SQLAlchemy and PyMySQL; the browser accesses the backend rather than the database.

## Current local configuration

| Setting | Value |
|---|---|
| Version | MySQL 8.0.43 |
| Address | 127.0.0.1:3307 |
| Database | spotting_at_risk |
| Runtime account | at_risk_app; project record CRUD only |
| Migration account | at_risk_migrate; project schema privileges |
| Data directory | data/mysql-project |
| Current revision | 9bc860de2041 |

The isolated project server does not replace the existing MySQL80 service. Generated passwords remain in ignored local files and are excluded from the submission. Explicit environment settings override `.env.local`.

## Table groups

| Group | Tables | Purpose |
|---|---|---|
| Identity | users, user_access, sessions | Accounts, permitted students and expiring sessions |
| Academic | classes, students, subjects, terms, performance, student_status | Student records, assessment evidence and calculated status snapshots |
| Family | parents | Guardian contacts, primary contact and consent |
| Support | extra_classes, extra_class_students | Scheduled sessions, objectives, enrollment, attendance and outcomes |
| Work | assignments, submissions | Class/individual assignments, private file metadata, versions and reviews |
| Reporting | progress_reports, notifications, audit_logs | Report snapshots, notice state and action history |

There are 17 application tables plus Alembic's revision table. Foreign keys enforce references. Unique constraints prevent duplicate student/subject/term assessments and other duplicate relationships. The request layer validates values and workflow permissions before saving.

## Operational and analytical structure

The operational tables store individual actions and records. The Power BI export transforms these records into a star schema with separate dimensions and facts. This avoids treating a submission version or intervention enrollment as an assessment row.

The current demo has 480 students, six classes, three subjects, four terms and 5,684 assessment records. Of 5,760 possible assessments, 76 are absent by design. Missing evidence remains missing and can produce Insufficient Data.

## Setup and migration process

The local setup used installed MySQL binaries to initialize a separate server, generate credentials, create the project database, apply Alembic revisions and copy existing SQLite demonstration records in one transaction. Original IDs and relationships were preserved. The SQLite source remains available as a migration fallback; it is not continuously synchronized.

`tools/setup_mysql.py` is a Windows-specific initial setup utility. It refuses to overwrite existing local configuration or reinitialize an existing database directory. Do not use it to reset the configured project.

For normal use, run the project launcher. It starts and verifies the isolated server when necessary. For schema maintenance, run from the project root:

```powershell
python tools/migrate.py current
python tools/migrate.py upgrade
python tools/migrate.py check
```

Alembic uses the separate migration connection. MySQL application startup checks the revision and refuses an outdated schema. `migrations/versions/` contains the baseline and intervention/review metadata revision. [mysql-schema.sql](../docs/mysql-schema.sql) is a fresh-schema reference, not a script to re-run over existing tables.

## Preservation and limits

Legacy timestamps, review metadata and hashes remain unknown if they were never recorded. New submissions record a SHA-256 hash. Private uploaded content stays in filesystem storage; MySQL stores its metadata.

Portable development without `.env.local` uses SQLite. Production requires its own configuration, approved records and account provisioning. Backups and restoration have not been validated; the preserved SQLite copy is not a complete MySQL backup strategy.

See [local operations](../docs/MYSQL-SETUP.md) and [Power BI README](../powerbi/README.md).


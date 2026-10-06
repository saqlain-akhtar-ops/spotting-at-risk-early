# Project MySQL setup

Configured on this laptop on 6 October 2026:

| Setting | Value |
|---|---|
| Server | MySQL 8.0.43 |
| Host / port | 127.0.0.1 / 3307 |
| Database | spotting_at_risk |
| Runtime user | at_risk_app@localhost; SELECT, INSERT, UPDATE, DELETE only |
| Migration user | at_risk_migrate@localhost; schema privileges on this database only |
| Data directory | data/mysql-project |
| Schema revision | 7a9990df7af4 |

This is a separate loopback-only server. The pre-existing MySQL80 service and its databases were not changed. The project contains synthetic demonstration records, not institutional records.

## Start

Run `Start-Project.ps1` or `python run.py`. The launcher starts the isolated MySQL process when necessary, verifies its data directory, and then starts the application. It does not install a Windows service or modify the existing server. Keep the project directory at its configured location.

Configuration is loaded from the ignored `.env.local`; explicit environment variables take precedence. Passwords are generated locally and are not included in source, Git, Docker build context, or the submission ZIP. Administrative recovery credentials are stored locally in `data/mysql-project/administration.json`; keep that file private. Do not paste either file into chat or commit them.

## Schema maintenance

```powershell
python tools/migrate.py current
python tools/migrate.py upgrade
python tools/migrate.py check
```

The migration tool uses the separate migration account. The application uses the restricted runtime account. Use the project's configured Python installation or virtual environment containing the listed dependencies.

`docs/mysql-schema.sql` is a reference for a fresh schema. For the configured database, use Alembic migrations; do not re-run the raw CREATE TABLE script over existing tables.

## Data preservation and checks

The original `data/application.db` remains preserved. Existing records were copied to MySQL in one transaction, retaining IDs and relationships. Legacy intervention timestamps, reviewer metadata and file hashes remain unknown when not previously recorded; they were not fabricated.

Verified: 480 students, 5,684 assessments, current migration revision, authenticated student list, dashboard summary and live Power BI feed. The isolated application test suite passed all 19 checks. The original SQLite copy is a migration fallback, not an ongoing synchronized database or a replacement for a tested MySQL backup plan.

## Power BI

The REST feeds and CSV export now read this MySQL database through the backend. Refresh CSV snapshots with the administrator's Export action. `analytics/LiveDemo.pq` provides the live REST query; `analytics/POWER-BI.md` describes the model and security rules.

A live data feed does not publish a report or sign into a Microsoft account. Native Desktop/model validation and Power BI account publishing remain incomplete.

## Deployment status

This setup is suitable for the local submission demo. A production deployment requires institutional data, HTTPS, production configuration with demo seeding disabled, approved account provisioning, backups and restore verification. Do not expose the local MySQL port publicly.

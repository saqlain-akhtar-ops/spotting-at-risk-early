# Vercel hosted demonstration

Live URL: **https://spotting-at-risk-early.vercel.app/**. Verified on 6 October 2026 against deployment commit `3578b36`.

The hosted application uses Vercel's Python/FastAPI runtime and a separate Neon PostgreSQL database. Local development continues to use the dedicated MySQL database on the laptop. These databases do not synchronize automatically.

## Architecture

`index.py` exposes the ASGI app. `pyproject.toml` selects Python 3.12 and installs the backend dependencies. `vercel.json` runs `tools/vercel_build.py`, which assembles the frontend, applies Alembic migrations to the cloud database and initializes synthetic demonstration records once.

The frontend and REST API share one HTTPS origin. Authentication uses secure session cookies, with CSRF validation on writes and role/student/class authorization. Private submissions are stored as database binary records, so uploads survive replacement of serverless instances. Hosted uploads are limited to 3 MB; local uploads remain limited to 5 MB. Temporary files are used only for generated downloads.

## Configuration

Neon's integration supplies the secret `DATABASE_URL`. The adapter normalizes this to SQLAlchemy's psycopg driver. SQLite is prohibited in the cloud. Build migrations and runtime currently use the managed database role; institution-specific least-privilege database roles are future deployment work.

The public submission demo uses `APP_ENV=development`, `CLOUD_DEMO=1`, `DEMO_SEED=0`, `COOKIE_SECURE=true`, `API_DOCS=false`, `UPLOAD_STORAGE=database` and `EMAIL_MODE=preview`. Four private `DEMO_<ROLE>_PASSWORD` variables initialize demonstration accounts during the first build. Existing users are not reset during later builds. Do not use these settings with real student records.

Generated hosted demonstration login details are in the ignored local file `data/hosted-demo-credentials.json`. They are excluded from Git and submission bundles. Local login details are separate.

## Data and limits

The dashboard reads persisted synthetic records and polls the REST API every ten seconds while visible. This is a live database-backed demonstration, not an external live school feed. Emails remain previews. Power BI CSV, DAX and model files are supplied separately; deployment does not publish a Power BI Service report.

Vercel Hobby and Neon Free are subject to provider quotas. This setup is intended for a personal, noncommercial submission. Monitor database size, request usage and compute limits in the provider dashboards. Neon suspend/resume can add latency to the first request. Do not enable a paid upgrade without reviewing it.

## Verification and maintenance

Check `/api/ready`, sign in, inspect dashboard counts, filter charts and create/download a private submission. Verify another teacher and a parent cannot download it. Check the deployment logs if readiness fails. Never paste database connection URLs or passwords into issues or the repository.

New commits to the connected GitHub main branch trigger deployment. Schema upgrades run during builds; do not make destructive migrations against shared data without a backup and review. Preview deployments share this demo database unless separate branching is configured.

The local suite has 23 passing checks, including cloud configuration, upload persistence, authorization and bounded dashboard queries. Institutional SSO, distributed login throttling, malware scanning, load testing, backup restoration and native Power BI validation remain separate work.

The hosted checks confirmed database readiness, 480 students, 5,684 assessment rows, class filtering, administrator/teacher/student/parent scopes, the authenticated Power Query feed, and a private uploaded file downloaded in a fresh session. Parents and an unrelated teacher received HTTP 403 for that file. The interactive dashboard category selection changed the displayed group from 480 to 96 At Risk students. A clearly labelled synthetic deployment-verification assignment and submission remain in the demo as evidence.

Official references: [Vercel FastAPI](https://vercel.com/docs/frameworks/backend/fastapi), [Python runtime](https://vercel.com/docs/functions/runtimes/python), [Hobby plan](https://vercel.com/docs/plans/hobby).

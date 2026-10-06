# Deployment and operations

The tested submission is a local synthetic demonstration. Production configuration guards and a container definition are included; infrastructure, native Power BI and real-data workflows have not been validated as a deployed production system.

## Local submission

Install Python dependencies and run `python run.py`. The server listens only on 127.0.0.1 by default. Use `Start-Project.ps1` on Windows if preferred. Do not load `.env.production.example` for the local demonstration: secure cookies require HTTPS and production deliberately refuses demo accounts.

## Container demonstration

Run `docker compose up --build -d`, then open http://127.0.0.1:8000. Credentials are generated on first startup. Read them with `docker compose exec app cat /app/data/demo-credentials.json`. The named student_data volume retains the database, uploads and credentials across container replacement. `docker compose down` stops the service while retaining that volume. This container configuration is provided as source; a Docker engine was not available for build/runtime verification here.

## Institutional deployment

1. Provision a dedicated MySQL database and a restricted service account. Never point this project at an unrelated existing database. Existing schema changes are not managed by automatic migrations; back up, review `docs/mysql-schema.sql`, and apply versioned migrations before upgrades.
2. Set the variables shown in `.env.production.example` using the platform environment/secret manager. `APP_ENV=production` requires an explicit database URL, secure cookies, exact allowed hosts and disabled demo seeding. Production also rejects the example.test demo accounts if they already exist in the selected database.
3. Place the single-worker application behind a trusted HTTPS reverse proxy. Expose only the proxy. Configure a six-megabyte request body limit and connection/rate limits on that proxy. `FORWARDED_ALLOW_IPS` must name only actual trusted proxy addresses; do not set it to `*`. The proxy must replace untrusted forwarding headers. HTTPS termination and forwarding details are documented by [FastAPI](https://fastapi.tiangolo.com/deployment/https/).
4. Mount a persistent, writable DATA_DIR owned by the application service user. Do not expose that folder as static web content. Keep encrypted backups of the database and upload store together; test restoring both into a separate environment.
5. Run `python tools/create_admin.py` interactively with the deployment environment. This creates the first administrator only, prompts for a password without echo, and refuses to replace existing administrators. Provision institutional students, classes, teachers and access mappings through a reviewed onboarding/import process; the current demo seed is not that process.
6. Check `/api/health` for process liveness and `/api/ready` for a database query. Add external availability monitoring, log retention and alerting. API documentation is disabled by default in production.
7. Configure SMTP only after replacing test addresses and recording guardian consent. Default EMAIL_MODE=preview sends no mail. Confirm delivery independently if a send becomes uncertain.

## Security and scaling

The API validates input, checks server-side student/class scope, uses HttpOnly SameSite sessions and CSRF tokens, bounds streamed request bodies before parsing, guards file ownership/type/size, and records audit events. The root frontend also receives a restrictive script policy. Production requires Secure cookies and emits HSTS on HTTPS responses. Host validation uses [Starlette TrustedHostMiddleware](https://www.starlette.io/middleware/).

Run one application worker for this version. Login/feed throttling is held in process memory; multiple workers or replicas need a shared limiter. Synthetic-cohort analytics currently scan the small assessment dataset and are not benchmarked for large institutions. Add indexed query aggregation, load testing, migrations, malware scanning for uploaded files, institutional identity/onboarding and backup/restore evidence before a real-data rollout. These are concrete limits of the current release, not features claimed as implemented.

Power BI Web import requires refresh. Power BI Service needs deployed reachable data/gateway, credentials and tested RLS; the local backend cookie is not a Microsoft sign-in. Native model/report validation and publication remain outstanding.

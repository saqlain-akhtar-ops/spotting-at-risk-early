# Security README

The project controls access in the backend. Hiding a button in the frontend does not grant or revoke permission.

## Authentication process

1. The user submits an email and password to `/api/auth/login`.
2. The backend verifies a salted PBKDF2-HMAC-SHA256 password hash using 310,000 iterations.
3. It creates a random session token and stores its SHA-256 hash, user, expiry and CSRF token in the database.
4. The raw token is sent in an HttpOnly, SameSite=Strict cookie with an eight-hour lifetime.
5. Each protected request checks the session and active account. Authenticated changes also require the matching `X-CSRF-Token`.

Production requires secure cookies. Local loopback development uses HTTP. The current login system is local session authentication; Microsoft SSO is not connected.

## Authorization

| Role | Main scope |
|---|---|
| Administrator | All students; administrative quality/export/audit actions |
| Teacher | Assigned student scope and permitted class workflows |
| Student | Linked student records, permitted submissions and released reports |
| Parent | Linked student records and released reports |

`user_access` maps accounts to students. Backend guards check student and class scope, assignment targeting, file ownership and report release. Unknown or unauthorized access is rejected. Staff actions and administrative actions have additional role checks.

## Validation and private files

- Pydantic forbids extra request fields and validates permitted values.
- Scores, attendance and optional review marks are constrained to 0–100 by request validation.
- Uploaded work is limited to 5 MB and accepted PDF, TXT, PNG and JPEG types, with content/signature checks.
- Stored files are private and retrieved through authorized endpoints; versions retain metadata and new files receive SHA-256 hashes.
- A streamed request middleware limits request bodies to 6 MB.
- Host validation and browser response headers are configured.
- Login attempts are throttled and applicable actions are recorded in an audit table.

Checks do not replace malware scanning. Rate-limit state is held in one process and is not a shared distributed service.

## Database and secrets

The MySQL runtime user has CRUD privileges on this project's database. A separate account applies migrations. The server listens on loopback port 3307. Generated local credentials live in ignored `.env.local` and private project data files; they are excluded from Git, the Docker build context and the submission archive.

Production configuration rejects demo seeding, insecure cookies, wildcard hosts, an implicit database connection and seeded demonstration accounts. Those safeguards are deployment controls, not proof of a completed production security review.

## Guardian communications and Power BI

Guardian notices start in preview mode. SMTP sending requires configured credentials, active contacts and consent. Synthetic `.test` recipients are blocked from live sending; uncertain delivery is not automatically retried.

Power BI REST feeds authenticate and enforce backend row scope. CSV exports are separate files and must be governed separately. Supplied Power BI RLS expressions still require real identity mappings and Desktop/Service role validation.

## Remaining deployment work

Institutional account provisioning, Microsoft SSO, HTTPS deployment, distributed throttling, malware scanning, load testing, backup restoration and native Power BI validation remain incomplete. See [deployment instructions](DEPLOYMENT.md) for the supplied configuration workflow.

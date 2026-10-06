# Backend README

The backend turns academic records into explainable support indicators, saves teacher actions, and provides the data used by the frontend and Power BI. It runs on Python; React runs in the browser.

## Technologies used

| Technology | How this project uses it |
|---|---|
| Python 3.12 | Application logic, status calculation, exports and tools |
| FastAPI | REST endpoints, dependencies and development API documentation |
| Uvicorn | Runs the HTTP application on localhost port 8000 |
| Pydantic | Validates request fields, scores, dates and allowed states |
| SQLAlchemy | Defines relational models, queries and database transactions |
| PyMySQL | Connects SQLAlchemy to MySQL |
| Alembic | Applies versioned MySQL schema migrations |
| python-dotenv | Loads ignored local configuration without overriding explicit environment settings |
| Python standard library | Password hashing, file hashes, private storage, CSV/JSON export and SMTP |

Exact installed dependency pins are in [requirements-runtime.txt](../requirements-runtime.txt). PyJWT and cryptography are installed dependencies, but Microsoft Entra authentication is not implemented; current authentication uses server-side sessions.

## Source files

| File | Responsibility |
|---|---|
| app.py | REST routes, workflow checks, report generation and application startup |
| models.py | Database tables, engine and sessions |
| schemas.py | Request validation |
| security.py | Password hashing, student access scope and audit helpers |
| status.py | Shared academic classification rules |
| config.py | Development/production configuration validation |
| middleware.py | Streamed request size limits |
| analytics.py | Data-quality checks and analytical CSV snapshots |
| powerbi.py | Authenticated live dashboard and analytical table feeds |
| seed.py | Labelled synthetic demonstration data for an empty development database |

## How a request is processed

1. The browser calls an endpoint under `/api/`.
2. FastAPI checks the session and, for authenticated mutations, the CSRF token.
3. Pydantic validates the input. Server-side guards check the role and authorized student/class.
4. SQLAlchemy reads or writes MySQL records. A failed transaction is rolled back.
5. The backend calculates evidence, records applicable audit events and returns JSON.
6. The frontend renders the result; the analytics dashboard refreshes from saved records.

Responses contain `success`, `message`, `data` and `errors`. Current routes use `/api/`, not `/api/v1/`. The complete contract is in [OpenAPI](../docs/openapi.json); development documentation is at http://127.0.0.1:8000/docs.

## Academic logic

Rule version: **EW-Prototype-v1**. Rules run in this order:

| Status | Evidence |
|---|---|
| Insufficient Data | The selected term lacks complete required assessment coverage |
| At Risk | Average below 60, or a decline combined with attendance below 75 |
| Top Performer | Average reaches the institution-wide nearest-rank 90th-percentile cutoff and attendance is at least 90 |
| Slow Learner | Three complete consecutive terms have averages from 60 inclusive to 70 exclusive, current improvement is 0–1 point, and attendance is at least 75 |
| Watch | Average declined from the immediately previous term |
| On Track | Remaining complete records |

The backend returns reason codes and requires teacher review. Missing prior evidence is not replaced with an older term. A subject filter recalculates the diagnostic indicators for that subject. These rules identify support patterns; they are not a trained machine-learning model or a diagnosis.

## Implemented workflows

- Save academic scores and assessment attendance; refresh status snapshots.
- Maintain guardian contacts and communication consent.
- Schedule extra classes, enroll students, record attendance/outcomes and update session state.
- Create class or individual assignments and receive private, versioned submissions.
- Review submissions with feedback, optional marks and reviewer metadata.
- Generate immutable progress-report snapshots and release them to authorized families.
- Preview template-based notices; send only when SMTP and consent are configured.
- Export validated analytical tables and serve scoped live data.

Intervention objectives, assignment targeting and review marks are available in the backend schema/API; some newer fields still need dedicated frontend controls. Legacy metadata is left unknown rather than invented.

## Run and verify

From the project root, install dependencies and run:

```powershell
python -m pip install -r requirements.txt
python run.py
```

This laptop uses the dedicated MySQL database described in the [database README](../database/README.md). MySQL startup verifies that migrations are current. Portable development runs without local configuration default to SQLite.

```powershell
python -m pytest tests -q
python tools/migrate.py check
```

Tests use a temporary database. If this laptop's restricted local host configuration is loaded during testing, set `ALLOWED_HOSTS=testserver` for the test process. The existing suite passed 19 tests; the MySQL-backed authenticated dashboard and feed were also checked separately.

See [security](../docs/SECURITY-README.md) and [end-to-end process](../docs/PROJECT-PROCESS.md).

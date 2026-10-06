# Spotting the At-Risk Early

**TEAM-BLACKCATS · Student performance and academic support · Submission release: 6 October 2026**

A working REST application that helps teachers spot academic decline early, explain the evidence, arrange support, and review student progress. The React dashboard is connected to a Python/FastAPI backend and relational database. Power BI receives the same data through CSV snapshots or authenticated REST feeds.

The included submission uses synthetic records. It is ready to run as a local demonstration. Production configuration and deployment files are supplied, but this release is not a certified or deployed institutional production system. Native Power BI artifacts remain drafts until validated in Desktop.

For separate explanations of the technologies and implementation process, open the [documentation index](docs/README.md). It links to the backend, frontend, database, Power BI, security and project-process READMEs.

## What the project does

1. Record each student's subject scores and attendance by term.
2. Compare the current and immediately prior term, attendance, and three-term patterns.
3. Assign an explainable status with reason codes, rather than an opaque prediction.
4. Let a teacher review the student, schedule extra classes, assign work, and record attendance or feedback.
5. Generate and release progress reports, preview guardian communications, and track recorded support.
6. Show saved changes in the live dashboard and make analytical data available to Power BI.

```text
Student / Teacher / Parent records
              ↓
      Authenticated REST API
              ↓
       Relational database
              ↓
    Validation + status rules
        ↙                ↘
React dashboard       Power BI data model
        ↓                ↓
Review → Extra classes → Work submissions → Progress reports
```

## Run the submission

Requirements: Python 3.12 or newer, a modern browser, and an internet connection for the initial dependency installation. The checked-in React bundle runs without Node.js or a CDN.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

Open **http://127.0.0.1:8000/**. Windows users can also run `Start-Project.ps1` after installing dependencies. This workspace already has local Python dependencies, so its launcher runs directly.

### macOS / Linux

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py
```

First startup creates the synthetic database and random demo account passwords in **data/demo-credentials.json**. Read that local file to sign in. Passwords are not included in the submission archive or Git. The data folder and installed dependencies are generated locally.

| Account | Role and scope |
| --- | --- |
| admin@example.test | Administrator: all 480 students, export and audit tools |
| teacher.a@example.test | Teacher: classes A–C, 240 students |
| teacher.b@example.test | Teacher: classes D–F, 240 students |
| student@example.test | Student 001 and permitted work/report actions |
| parent@example.test | Student 001 and released progress reports |

The application stores passwords as salted PBKDF2 hashes. `python tools/reset_demo_passwords.py` rotates demonstration passwords and updates the local credentials file.

### Optional container launch

```sh
docker compose up --build -d
docker compose exec app cat /app/data/demo-credentials.json
```

The application is published only on the machine's localhost port 8000, and a named volume retains its data. Docker build/runtime has not been tested in this environment. See [deployment instructions](docs/DEPLOYMENT.md).

## Demonstrate it in five minutes

1. Sign in as admin or teacher A. Open Overview, change term/class/subject filters, and select a status category. Explore the charts and review queue.
2. Open a student from the queue or score/attendance plot. Inspect the status reasons, academic records and support history. Student 360 shows latest-term indicators.
3. Record a valid score or attendance change. Return to Overview; the dashboard reads saved database values immediately and on its next visible-page poll.
4. Schedule a mathematics support class with a teacher, class, date, start/end time, room and topic. Assign students; record their attendance/outcomes before completing the session.
5. Create an assignment. Sign in as student@example.test to submit work for Student 001. Return as teacher to review it or request a revision.
6. Generate a Student 001 progress report, inspect it, and release it. Sign in as parent@example.test to view the released report. Use the browser's Print → Save as PDF to export it.
7. Preview a guardian notification. Default preview mode sends no email. As admin, inspect audit events and run data-quality/export tools.

## Features

| Area | Implemented behavior |
| --- | --- |
| React analytics | Eight clickable KPI cards; term trend, status ring, score/attendance plot, score bands, class comparisons, reason counts and review queue |
| Interaction | Status selection, global slicers, chart-to-student navigation, search, sorting, scoped CSV download, rule explanations, theme switch and motion preferences |
| Five academic categories | At Risk, Watch, On Track, Top Performer and Slow Learner; missing evidence is a separate Insufficient Data state |
| Extra classes | Subject/teacher/class IDs, date, start/end, room/topic, enrollment, attendance, outcomes, state and schedule conflict checks |
| Work submissions | Private files, 5 MB limit, accepted PDF/TXT/PNG/JPEG types and signatures, versions and teacher feedback |
| Progress reports | Immutable academic/support snapshots, versioning, teacher comments, release controls and printable HTML |
| Parent contacts | Multiple guardians, primary contact, consent, active state and approved notification templates |
| REST security | Expiring HttpOnly/SameSite sessions, CSRF tokens, server-side role and row scope, login throttling and audit records |
| Deployment controls | Production configuration guards, host validation, streamed request limit, frontend script policy, secure-cookie settings and readiness endpoint |
| Power BI | Ten CSV tables, typed Power Query, 34 DAX definitions, dynamic RLS, theme, relationships and native model drafts |

## Backend rules: what are we trying to detect?

The goal is to identify students who may benefit from timely academic support and show the evidence to a teacher. The rules do not diagnose learning ability or predict dropout.

For a selected term, the backend uses complete subject coverage for the score average. It compares the immediately prior term without skipping missing terms. Attendance is the mean attendance value in assessment records, not a daily attendance ledger. Categories are evaluated in this order:

| Category | Rule |
| --- | --- |
| Insufficient Data | Required assessments or marks are missing |
| At Risk | Average score below 60%, or a declining score with attendance below 75% |
| Top Performer | Score meets the institution-wide 90th-percentile cutoff and attendance is at least 90% |
| Slow Learner | Three complete consecutive terms each at 60–69%, current improvement of 0–1 point, attendance at least 75% |
| Watch | Current score has fallen from the immediately prior term |
| On Track | Remaining complete records |

The institutional top-decile cutoff is independent of the viewer's authorized rows; ties may produce more than 10% top performers. At Risk takes precedence over the other academic categories. The Slow Learner label denotes a measured support pattern, not a diagnosis. Rule version: **EW-Prototype-v1**.

Support assignment is a teacher action; a flag does not automatically send emails or schedule classes. Before/after comparisons describe observed progress and do not prove an intervention caused it.

## REST API

Interactive docs: **http://127.0.0.1:8000/docs** in development. Saved OpenAPI contract: [docs/openapi.json](docs/openapi.json). Production disables interactive docs by default.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | /api/auth/login | Sign in and receive a CSRF token |
| GET / POST | /api/auth/me · /api/auth/logout | Inspect session / sign out |
| GET | /api/metadata | Permitted classes, subjects, terms and staff options |
| GET | /api/students | Authorized student list and filters |
| GET | /api/students/{id} | Student 360 with academic and support evidence |
| GET | /api/students/{id}/status | Explainable status for a selected term |
| PUT | /api/students/{id}/performance | Validate and save scores/attendance; recalculate status snapshots |
| GET / POST / PUT | /api/students/{id}/parents | Guardian records; updates use a parent ID suffix |
| GET / POST | /api/extra-classes | List or schedule support sessions |
| POST / PUT | /api/extra-classes/{id}/students | Enrollment; attendance updates use a student ID suffix |
| GET / POST | /api/assignments · /api/submissions | Work creation and private submissions |
| POST | /api/submissions/{id}/review | Teacher review and feedback |
| POST | /api/students/{id}/progress-report | Generate a draft report |
| POST | /api/reports/{id}/release | Release a report to the linked student/guardian |
| POST | /api/students/{id}/notifications | Create a template-based notice preview |
| GET | /api/power-bi/live | Current dashboard KPIs and student rows |
| GET | /api/power-bi/tables/{table} | Read-only analytical table feed for Power Query |
| POST | /api/admin/export | Administrator-only validated CSV snapshot |
| GET | /api/admin/data-quality · /api/audit | Data quality / audit events |
| GET | /api/health · /api/ready | Process liveness / database readiness |

Browser requests use a same-origin session cookie. Authenticated mutations must include **X-CSRF-Token**. Power Query feeds use Basic authentication, HTTPS for remote access and the same server-side student scope. Passwords belong in a credential dialog, not DAX, M code or Git.

Response structure:

```json
{
  "success": true,
  "message": "Success",
  "data": {},
  "errors": []
}
```

The dashboard fetches current database rows ten seconds after each completed poll while an analytical page is visible. Hidden tabs pause polling. Failed refreshes retain the last result and mark it stale. This is live database polling, not streaming or a Power BI Service refresh schedule.

## Database and demo data

This laptop now runs the project on **MySQL 8.0.43**, at **127.0.0.1:3307**, database **spotting_at_risk**. The ignored `.env.local` contains the local connection configuration. The existing MySQL80 service on port 3306 remains separate. All 480 synthetic students and 5,684 assessments were preserved from the original SQLite database. See [MySQL setup and operations](docs/MYSQL-SETUP.md).

Portable installations without `.env.local` still default to **data/application.db** (SQLite). Explicit process environment settings override `.env.local`.

The committed snapshot in [powerbi/csv](powerbi/csv) contains **480 students, six classes, three subjects, four terms, 5,684 performance records and 1,920 student-term status records**. Of 5,760 possible assessments, 76 are intentionally absent. Missing assessments are reported separately and prevent incomplete progress reports.

Files contain synthetic student labels and example.test identities. No real student dataset, local login passwords, database file or uploaded work is included. The writable application database is generated at startup; CSVs are analytical snapshots. Updating a record changes the frontend without editing CSV files; exporting again is needed to update snapshot-based Power BI models.

## Power BI files

Start with [powerbi/START-HERE.md](powerbi/START-HERE.md).

- **powerbi/csv/**: ten dimension/fact tables with row-count and checksum manifest.
- **powerbi/measures/**: 34 individual New measure expressions. Use measure-catalog.csv for the table and format.
- **powerbi/measures.dax** and **additional-measures.dax**: combined DAX source.
- **powerbi/powerquery/**: typed CSV queries. Create CsvFolder first and set it to your cloned project's powerbi/csv directory.
- **powerbi/LiveDemo.pq**: authenticated REST table import; choose Basic credentials in Power BI.
- **powerbi/rls.dax**: dynamic StudentAccess role expressions.
- **powerbi/theme.json**: dashboard color theme.
- **powerbi/model-draft/**: ten-table native semantic-model source, 11 relationships and the original 21 measures. Add the extra 13 visual measures separately.

Keep Dim_UserAccess disconnected and use the documented single-direction relationships. Replace example.test UPN mappings before publishing to actual users, then test every role and an unknown user.

Stored Fact_Status classifications are across all subjects. A Power BI subject slicer filters performance but does not recompute those statuses. Label stored status visuals accordingly or disable their subject interaction. The application's subject-filtered diagnostic view does recalculate status using that subject.

Web Import queries update visuals when the Power BI model refreshes; they do not provide native continuous DirectQuery. No finished PBIX, Desktop validation, Service workspace, gateway or published report is claimed.

## Project structure

```text
backend/       REST routes, schema, authentication, rules, feeds and exports
frontend/      HTML shell, React analytics, styles and operational forms
powerbi/       Submission CSVs, DAX, Power Query, RLS, theme and model drafts
analytics/     Export/query/model generation sources
tools/         Builds, data checks, packaging and administrator provisioning
tests/         Isolated backend and deployment checks
docs/          OpenAPI, schema, coverage, validation and deployment notes
sources/       Preserved supplied frontend/reference files
Dockerfile     Non-root container definition
compose.yaml   Local container demonstration with persistent storage
```

## Development and checks

```sh
python -m pytest tests -q
python tools/verify_powerbi_delivery.py
```

The final local suite passed **19 tests**. The tests use a separate temporary database and storage directory. They cover authentication, authorization, category boundaries, parent records, extra classes, file ownership/validation, report release, notice previews, saved score changes, live feeds, CSV quality and deployment controls.

To rebuild the React analytics using Node.js:

```sh
npm install
npm run build
python tools/build_frontend.py
```

Windows without npm can use `python tools/install_ui.py`, which downloads pinned packages from the npm registry and builds the bundle. HTML/CSS source changes require tools/build_frontend.py. Original operational forms remain in JavaScript; the analytics area uses React.

See [QA evidence](docs/QA.md), [requirement coverage](docs/IMPLEMENTATION.md), [live feed instructions](docs/LIVE-DEMO.md), and [deployment instructions](docs/DEPLOYMENT.md).

## Deployment status and limits

Production mode refuses demo seeding, insecure cookies, wildcard hosts, an implicit database URL and existing demonstration accounts. Configure a dedicated database, trusted HTTPS proxy, persistent storage and institutional user/access onboarding. Use tools/create_admin.py to provision the first administrator interactively. Environment templates are not loaded automatically; set their values in the process environment or deployment secret manager.

SMTP is in preview mode. Microsoft SSO, institutional onboarding, shared rate limiting for replicas, malware scanning, load testing, tested backup restoration and native Power BI validation remain deployment work. Versioned migrations were applied and verified on the dedicated local MySQL database. Browser tooling blocked local preview access for the new React version, so its click interactions, animations and mobile layout have not been visually verified. Docker deployment has not been executed here.

The submission therefore demonstrates the complete implemented academic-support workflow and provides deployment controls, while clearly separating tested behavior from external production validation.

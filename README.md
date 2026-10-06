# Spotting the At-Risk Early — TEAM-BLACKCATS

A local Python backend and connected dashboard with React analytics for academic signals and student-support workflows, based on the supplied enhanced specification.

## Included project data

`powerbi/csv` contains the synthetic demonstration snapshot: 480 students and 5,684 assessments, plus student status, support, submission, report and access tables. `powerbi` also includes 34 individual DAX measures, Power Query code, RLS, theme and model drafts. Start with `powerbi/START-HERE.md`.

The actual frontend reads the authenticated `/api/power-bi/live` endpoint. Its React charts, KPI cards, student groups and review queue use the current database records and refresh every ten seconds while visible. Python creates the corresponding synthetic database on first startup; the checked-in CSVs are Power BI snapshots rather than the writable database. Saved performance changes update frontend signals without editing the CSVs.

Publishing this repository to GitHub shares the project code. Run the Python server to use the complete dashboard; hosting the HTML alone does not provide its database or login APIs.

## Open the project

Run `Start-Project.ps1` or `python run.py`, then visit **http://127.0.0.1:8000**. On this machine the project includes downloaded dependencies in `.runtime`. For another machine, install Python 3.12+, create a virtual environment, and run `python -m pip install -r requirements.txt` first.

The first startup creates synthetic data and unique random demo passwords in `data/demo-credentials.json`. Accounts:

| Email | Scope |
| --- | --- |
| admin@example.test | All 480 students and administrative tools |
| teacher.a@example.test | Classes A–C, 240 students |
| teacher.b@example.test | Classes D–F, 240 students |
| student@example.test | Student 001 only |
| parent@example.test | Student 001 only; released reports |

The credentials file is local and excluded from Git. Rotate generated demo passwords with `python tools/reset_demo_passwords.py`. Set `DEMO_SEED=0` for an institutional empty deployment.

## Demonstrate the workflows

1. Sign in as an advisor. Review Overview, At-Risk Triage, Slow Learner Support and Top Performers.
2. Open a student. Review evidence, maintain parent contacts and academic records.
3. Schedule an extra class, assign students, record attendance/outcomes and complete the class.
4. Create an assignment. Sign in as the linked student to upload work. Sign back in as teacher to review it.
5. Generate a progress report from Student 360. Release it from Progress Reports. The linked guardian can view/print it. Use the browser's Save as PDF for a PDF copy.
6. Preview a guardian notice using an approved template. No mail is sent in default preview mode.
7. As admin, run data quality and export a validated Power BI snapshot from Project.

## API and backend

Interactive API documentation: **http://127.0.0.1:8000/docs**. OpenAPI contract: `/openapi.json`. Login returns a CSRF token; every state-changing authenticated request sends `X-CSRF-Token`. The browser uses a same-origin HttpOnly session cookie. Every endpoint enforces server-side scope.

Backend: `backend/app.py` (API/workflows), `models.py` (relational tables), `security.py` (auth/scope), `status.py` (classification), `analytics.py` (DQ/export), `seed.py` (synthetic fixture). Frontend source: `frontend/body.html` and `frontend/app.js`. Rebuild the HTML with `python tools/build_frontend.py` after changing `body.html`.

## Database and configuration

The default SQLite database runs immediately. MySQL is supported via `DATABASE_URL=mysql+pymysql://USER:PASSWORD@127.0.0.1:3306/at_risk?charset=utf8mb4`, using a dedicated database and least-privilege credentials. `docs/mysql-schema.sql` contains the generated schema. MySQL was not connected with unknown credentials. Set process environment variables using `.env.example`; that template is not automatically loaded.

For live mail, configure `EMAIL_MODE=smtp`, SMTP host/port/user/password/from, record guardian consent, replace synthetic `.test` addresses, and explicitly send a previewed notice. The service uses STARTTLS, minimal templates and delivery logging. An uncertain SMTP result is not retried automatically.

## Power BI and verification

`analytics/export` contains validated star-schema CSV snapshots and a reconciliation manifest. `analytics/POWER-BI.md` contains model relationships, Power Query, DAX, RLS, report layout and verification instructions. `analytics/model-draft` contains native TMDL source (10 tables, 11 relationships, 21 measures and the dynamic role). Artifacts remain drafts until imported, tested and published in an available Power BI Desktop/Service environment. No existing PBIX was replaced.

Run `python -m pytest tests -q` with `.runtime` on `PYTHONPATH`, or install requirements into your virtual environment. Tests use an isolated temporary database/storage directory. See `docs/IMPLEMENTATION.md` for exact requirement coverage and limits and `docs/QA.md` for verification evidence.

The project is synthetic and explainable; it does not predict dropout or diagnose learners. Parent emails, Service publishing, Microsoft SSO and production infrastructure require deployment setup.

## Live demo data

The React analytics dashboard adds interactive status segments, academic trends, score/attendance plots, score bands, class comparisons, flag evidence and a searchable review queue. KPI cards open the relevant workflows. See `docs/REACT-DASHBOARD.md` for controls, backend logic and build instructions. The original operational forms remain in JavaScript.

The dashboard now polls `/api/power-bi/live` ten seconds after each completed poll while an analytical page is visible. This reads current authorized database rows without exporting CSVs. `backend/powerbi.py` also provides read-only Basic-authenticated analytical table feeds for Power BI Desktop. `analytics/LiveDemo.pq` fetches those rows through Power Query. Native Web import still requires model refresh; it is not DirectQuery. See `docs/LIVE-DEMO.md` for the complete code paths and connection steps.

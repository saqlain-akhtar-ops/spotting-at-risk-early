# Project process README

## Purpose

**Spotting the At-Risk Early** helps teachers notice academic decline, understand the evidence, arrange support and track progress. It combines academic records with recorded interventions rather than only displaying a score chart.

The included records are synthetic. Classifications are explainable prototype rules reviewed by a teacher, not diagnoses or machine-learning predictions.

## End-to-end workflow

```text
Authorized user signs in
          ↓
Frontend requests or submits academic records
          ↓
REST backend checks session, permission and input
          ↓
MySQL stores validated records
          ↓
Shared Python rules calculate indicators and reasons
          ↓
Teacher reviews evidence and decides support
          ↓
Extra class → enrollment → attendance and outcome
Assignment → private submission → teacher review
          ↓
Progress report snapshot → review → release
Guardian notice preview → consent/configuration checks
          ↓
Dashboard refresh / validated Power BI export
```

## Example: mathematics support

1. A teacher reviews a student's mathematics score, prior-term change and attendance using the subject filter.
2. The backend returns the measured status and reason codes. The teacher checks the student's records before deciding what support is appropriate.
3. The teacher schedules a mathematics extra class with a date, start/end time, teacher, room and topic, then enrolls the student.
4. Attendance and an outcome are recorded. The teacher can create an assignment and review the student's uploaded work.
5. Later assessments are saved. The same rule engine recalculates the indicators.
6. A progress-report snapshot combines academic evidence, support history and teacher comments; authorized family accounts can see it after release.

No status flag automatically schedules a class or sends an email. Before/after changes describe observed progress and do not prove support caused the change.

## What each layer contributes

| Layer | Contribution |
|---|---|
| Frontend | Displays charts, gathers inputs and opens review/support workflows |
| Backend | Validates access/data, calculates rules and enforces workflow states |
| MySQL | Preserves records, relationships, versions and action history |
| Analytics export | Checks data quality and transforms operational records into dimensions/facts |
| Power BI source pack | Supplies CSV, Power Query, DAX, role expressions and semantic-model drafts |

There is one configured operational MySQL database on this laptop. Dashboard requests and backend analytical exports read it. CSVs are snapshots; Power BI Import models require refresh. The web dashboard polls the API periodically while visible.

## How the project was assembled

1. Reviewed the supplied project specification, handwritten workflows and existing frontend.
2. Preserved the supplied visual foundation and implemented academic/support REST workflows.
3. Added relational models, validation, session authentication, role scope and audit records.
4. Centralized the academic rules so the API, report snapshots and exports use the same logic.
5. Added React analytics and connected the existing operational forms to the backend.
6. Created labelled demonstration data, CSV exports, DAX, Power Query and native model drafts.
7. Added deployment configuration guards, automated checks and submission packaging.
8. Configured a separate MySQL server, applied versioned migrations, preserved existing demo records and verified the running API.

## Verification and current boundaries

The existing suite passed 19 isolated tests covering authentication, scope, rules and main workflows. The local MySQL revision, 480 students, 5,684 assessments, authenticated dashboard and live analytical feed were verified separately. Submission packaging excludes local secrets and includes migrations.

React is currently used for analytics; operational forms remain JavaScript. Some newer API fields need frontend controls. Browser visual verification, institutional production deployment, Microsoft SSO and a validated/published native Power BI report remain incomplete.

For a presentation, describe the result as a working local academic-support demonstration with a Power BI integration source pack. Do not describe it as a deployed institutional system or a report already published to a Microsoft account.

See the [documentation index](README.md) for each aspect's detailed README.

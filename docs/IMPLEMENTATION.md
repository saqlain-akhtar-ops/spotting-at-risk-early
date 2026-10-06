# Requirements and completion evidence

The DOCX and three project notebook pages informed the feature specification. The fourth page is Git study material. The earlier conversation provides background; it does not independently authorize publication or communication.

| Requirement | Local implementation | Verification / limitation |
| --- | --- | --- |
| Python backend | FastAPI, structured responses, validation, generated API docs | Tested through real HTTP-compatible client |
| Relational database | SQLAlchemy schema, SQLite local runtime, MySQL driver and schema | SQLite tested; existing MySQL service requires user-provided credentials and a dedicated database |
| Authentication / roles | Password hashing, expiring HttpOnly sessions, CSRF, per-student authorization | Admin, two teachers, student and parent scopes tested |
| Parent email | Multiple guardians, primary contact, consent, deactivation, templates, preview/send log | Previews tested. SMTP unconfigured; no real email sent |
| Five statuses | Versioned centralized rules and reason codes | All categories generated; boundaries tested |
| Extra classes | Subject, teacher, class, date, start/end, room, topic, enrollment, attendance, outcome | Assignment and completion workflow tested; overlap validation |
| File submission | Private uploads, size/type/signature validation, versioning, review, authorized downloads | Invalid/oversized/spoofed files and unauthorized access tested |
| Progress reports | Immutable JSON snapshot, teacher notes, follow-up, generation, release, printable HTML | Completeness and release gates tested. Browser print supports Save as PDF |
| Enhanced dashboard | Eight connected pages, filters, KPIs, status lists, student details | Browser inspection recorded in QA notes |
| Data quality | Duplicates, missing marks, range, orphan checks; missing assessments separate | 5,684 rows checked; no blocking issues; 76 absent assessments |
| Star schema / DAX / RLS | Validated CSV bridge, Power Query source definitions, DAX measures, role expressions, source-to-model design pack | Draft Power BI artifacts; not imported or validated in Desktop here |
| Audit | Actor, entity, UTC time and event for sensitive workflows | Audit acceptance checks passed |
| GitHub | Version-control-ready local source and workflow guide | Connector returned no accessible repositories; no push performed |

## Exact prototype status policy

Use a selected term (latest by default). Each student's mean uses all selected subject assessments for that term. Missing required assessments or marks yield **Insufficient Data**, a data-quality state outside the five academic categories. Prior score is the immediately prior term, not the last available score. Attendance is the assessment mean, not a daily attendance model.

1. **At Risk:** current average <60 OR negative prior-term change and attendance <75.
2. **Top Performer:** current score at or above institutional 90th-percentile nearest-rank cutoff AND attendance >=90. Ties are included. This cutoff is calculated institution-wide, independent of viewer scope.
3. **Slow Learner:** three consecutive available complete terms each in [60,70), current change in [0,1] points, attendance >=75.
4. **Watch:** negative term-over-term change.
5. **On Track:** all remaining complete cases.

The API exposes rule version `EW-Prototype-v1`, current score, prior score, change, attendance, percentile cutoff, and contributing reasons. All statuses require advisor review. The rules are demonstration policy, not an institutional diagnosis or a validated predictive model.

## Frontend provenance

The exact supplied `Downloads/index.html` contains a headings exercise. It is preserved at `sources/index.supplied.html`. An adjacent `Downloads/index (1).html` is a relevant dashboard with empty Power BI states. Its untouched copy is `sources/dashboard.reference.html`. The integrated interface retains its layout, theme, navigation, responsive CSS and visual language, with operational workflow sections and server calls added. There was no existing application source, API or analytical model in the initial workspace. If the intended Lovable frontend is elsewhere, this backend provides an explicit reusable REST contract; that source has not been modified.

## Deployment boundary

This is a working local synthetic prototype. Live SMTP, Microsoft SSO, live Power BI account discovery/embed, Service publishing, scheduled refresh, MySQL execution, HTTPS, institutional malware scanning and operational monitoring are not validated here. Native Power BI Desktop was absent from the app inventory and package check. A generic Power BI tag does not supply a tenant, workspace, model or credentials.

Before using real records: configure HTTPS and `COOKIE_SECURE=true`; replace local identities with institution-managed accounts; calibrate rules; add malware scanning; manage encryption/backups/storage quotas; define retention and approval policy; run MySQL-specific migration/integration tests; test RLS as actual Viewer users; provision SMTP. The demo login rate limiter is single-process memory and needs a shared store for multi-worker deployment. Existing reports and generated CSV exports are snapshots, and do not update until regenerated.

Uploaded files are limited to PDF, UTF-8 TXT, PNG and JPEG. DOCX is not accepted by the prototype upload module. Binary signature checking is not malware scanning. Support history in reports is generation-time history, even when viewing an earlier academic term; it is labeled as support history rather than a causal term effect.

# Submission release checks — 6 October 2026

Production settings are validated, streamed request limits cover bodies without Content-Length, root responses carry frontend security headers, and /api/ready checks the database. Empty databases now export all ten analytical table headers safely. The final complete suite passed: **19 tests in 65.98 seconds**, with one dependency deprecation warning. Live checks on the restarted server confirmed /api/health, /api/ready, React asset references and the frontend script policy.

The earlier React production bundle and 480-student server render passed. Browser visual/click/mobile QA remains unverified for that version. Docker, MySQL, HTTPS infrastructure, SMTP delivery and native Power BI have not been run here. The submitted ZIP excludes operational databases, credentials, uploads and installed dependencies.

# Verification evidence

Date: 5 October 2026. Local synthetic prototype, Asia/Kolkata user interface; database audit timestamps are UTC.

## Automated acceptance checks

The tests use an isolated temporary database and file storage. Verified:

Final evidence: **12 passed** in the full suite (78.70 seconds), followed by **1 passed** for the added score-update/report-snapshot test (16.16 seconds): all 13 acceptance checks verified. One non-blocking warning concerns the testing library's future HTTP client migration. Frontend JavaScript syntax check passed.

- Correct login, invalid login, HttpOnly session flow, CSRF rejection and logout.
- Administrator (480), teacher A/B (240 each), student/guardian (1 each) visibility.
- Cross-student and cross-teacher profile, contact, status, report, file and review access denied.
- Status precedence and boundary examples for all five categories plus missing-data state.
- Class/year/status filtering and dashboard count reconciliation.
- Parent-email validation, primary-contact uniqueness and contact-edit ownership.
- Extra-class time validation, overlap detection, scope, assignment, attendance and completion.
- Extension/MIME/signature rejection, 5 MB limit, path traversal normalization and authorized download.
- Submission review and versioned, teacher-approved late resubmission.
- Report completeness, draft visibility, release and guardian access.
- Notification preview without live email delivery and guardian ownership checks.
- Performance range validation and audit events.
- A valid academic update recomputes stored status evidence while preserving a previously generated report snapshot.
- Flat-file DQ corruption injection: one duplicate, three out-of-range scores, 76 missing marks and one orphan, all detected without changing original data.

## Browser verification

Signed in to the running application as its generated demo administrator. Initial latest-term dashboard:

| Metric | Observed |
| --- | --- |
| Students | 480 |
| Average score | 72.7% |
| Average attendance | 87.6% |
| At Risk | 96 |
| Watch | 150 |
| On Track | 89 |
| Top Performer | 49 |
| Slow Learner | 96 |

Selected Class A and opened Student 004. Verified the Slow Learner reason, 64.6% current score, 64.2% prior score, +0.4-point change, 88.0% attendance, subject-term details, and scheduled Mathematics foundations support (12 October, 16:00, Lab 2).

Generated a version-1 term-4 demonstration progress report for Student 004, including advisor notes and follow-up. Released it through the interface and verified the Reports table shows Released and the View / Print PDF link. This changed synthetic local data only.

Responsive check: mobile breakpoint showed a stacked card layout and bottom navigation without document horizontal overflow. Default browser sizing was restored afterward. Browser console inspection found no JavaScript errors. The selected-student refresh race and page-switch scroll position were corrected after browser inspection.

## Data and analytics

Validated export: 5,684 performance records, 480 students, six classes, three subjects, four terms and 1,920 student-term statuses. The 76 deliberately absent assessments are explicitly reported. No blocking range, duplicate, missing-mark or orphan issue appears in clean records.

Power Query source queries, DAX measures, a dynamic RLS role, native TMDL model source and an offline review package are prepared as drafts. No native Power BI import, DAX engine execution, RLS Viewer session, Service publication or scheduled refresh is claimed. MySQL schema is generated; SQLite is the tested operational database. SMTP remains preview-only. GitHub returned no accessible repositories.

## Live-demo extension

Two additional tests passed in 18.14 seconds. Verified that the live summary reads a saved score change without CSV export, preserves class filters and guardian scope, and rejects invalid terms. Verified Power Query feed Basic authentication, authentication challenges, admin/teacher/student/guardian row counts, empty-table schemas, absence of private file/contact/password fields, released-report visibility, and rejection of remote HTTP Basic connections. Power BI Web imports current database rows only when its model refreshes; the browser dashboard polls after ten seconds while visible.

Browser verification showed the live fetch timestamp advancing automatically from 20:35:11 to 20:36:11 Asia/Kolkata without a refresh click. Dashboard totals remained correct and the browser console showed no JavaScript errors. The live preview is saved as `docs/live-demo-preview.jpg`.
# React analytics update — 2026-10-06

The complete isolated backend suite passes: 15 tests in 58.76 seconds. This covers category rules, authorization, support, submissions, reports, previews, data quality, saved academic updates and live Power BI table feeds. One dependency deprecation warning remains in FastAPI's TestClient.

The React production bundle compiles. A separate React server-render check using all 480 students from the running authenticated API passes without React warnings; empty results, missing academic values and escaped student names are covered. These checks do not prove browser interactions, animation or layout. The browser tool rejected local preview access under its URL policy, so this version has not received visual or mobile QA. Earlier screenshots represent the prior JavaScript dashboard.

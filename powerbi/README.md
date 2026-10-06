# Power BI README

This folder contains analytical data and source files for building the Power BI model. It shares the backend's academic rules and current operational data. A finished Desktop report or published account connection is not yet available.

## Technologies and files

| Technology / folder | Purpose |
|---|---|
| CSV / csv/ | Validated analytical snapshots, row counts and checksums |
| Power Query M / powerquery/ | Import and type the CSV tables |
| LiveDemo.pq | Import authenticated REST analytical tables |
| DAX / measures/ | 34 individual measure definitions and formatting catalog |
| measures.dax / additional-measures.dax | Combined measure source |
| TMDL / model-draft/ | Native semantic-model source draft |
| rls.dax | Dynamic student-access role expressions |
| theme.json | Visual color theme |

The native model draft contains the original 21 measures, ten tables and 11 relationships. The other 13 measure definitions are supplied separately. Source checks do not establish that DAX has executed successfully in Desktop.

## Star schema

| Table | Grain or purpose |
|---|---|
| Dim_Student | One student |
| Dim_Class | One class |
| Dim_Subject | One subject |
| Dim_Term | One term |
| Dim_UserAccess | Identity-to-student access mappings |
| Fact_Performance | One student × subject × term assessment |
| Fact_Status | One student × term classification |
| Fact_Intervention | One student × support session enrollment |
| Fact_Submission | One submission version |
| Fact_Report | One progress-report version |

Use the documented single-direction relationships. Keep Dim_UserAccess disconnected; the role expressions use it to filter students. Avoid extra class-to-performance relationships that introduce an ambiguous path.

## Data-to-report process

1. Teachers save academic and support records through the REST backend.
2. The backend validates records and calculates classifications with the shared rule engine.
3. An administrator exports a validated snapshot to `analytics/export`, including a manifest.
4. Refresh the imported Power BI tables from that snapshot or use the authenticated REST queries.
5. Apply relationships, measures, formats, role expressions and theme.
6. Build visuals, reconcile totals with the API, test every role and validate the native model in Desktop.

The committed `csv/` files are submission snapshots. They do not update when the application changes; create and import a new export. Follow [START-HERE.md](START-HERE.md) for the existing import instructions.

## Measures and report plan

Measure sources cover student/status counts, average score and attendance, trends, support attendance, submission states and report coverage. Scores and attendance use a 0–100 scale; ratio measures require their documented percentage formatting.

The report plan includes Executive Overview, At-Risk Triage, Slow Learner Support, Extra Classes, Assignments & Submissions, Progress Reports, Student 360 and Top Performers. These are planned native pages, not eight completed Power BI pages. React charts already exist in the web application and are a separate implementation.

Stored Fact_Status rows classify performance across all subjects. A subject slicer does not recalculate those stored categories. Label those visuals accordingly or disable subject interaction; the backend's subject-filtered diagnostic view calculates a different selection. Pending assignments cannot be inferred from a submissions-only fact.

## Refresh and access

The REST feed reads the configured MySQL database through the backend and applies the authenticated account's scope. Use Power BI's credential dialog for Basic authentication; do not put passwords into M or DAX. Remote feed access requires HTTPS.

Power Query Web imports refresh when the model refreshes. They are not native DirectQuery or continuous streaming. Exported institution-wide CSV files do not inherit the backend's access controls.

RLS expressions are supplied but remain unvalidated in Desktop. Replace demonstration identity mappings with approved real identities, test teacher/student/guardian/unknown access, and review workspace permissions before publishing. No Microsoft account sign-in, gateway, Service refresh schedule, embedding or report publication is configured.

See [analytical design](../analytics/POWER-BI.md), [security](../docs/SECURITY-README.md) and [database](../database/README.md).

# Power BI analytical integration — draft

The operational database is the record of transactions. Power BI consumes validated snapshots through the star schema. This package extends the specified model; no existing Power BI project was supplied or replaced. Power BI Desktop was not available to validate/import these drafts locally.

## Generate data

As an application administrator, use **Project → Export validated Power BI data**. Alternatively run `python -m backend.analytics` with project dependencies available. Files are written to `analytics/export` with row counts, checksums and DQ evidence in `manifest.json`. Do not publish or share these institution-wide exports without the intended access policy. Snapshot files do not inherit backend permissions.

The default snapshot contains 480 students, six classes, three subjects, four terms, 5,684 performance rows, 1,920 student-term status rows and 962 access rows. Rows missing by design are recorded separately and incomplete term statuses become Insufficient Data.

## Import and relationships

Use each corresponding `powerquery/*.pq` query in Power BI Desktop's Blank Query / Advanced Editor. Paths are configured for this workspace. If moving the project, change the path root before refresh. Use fixed data types and promote headers. Do not enable guessed automatic relationships.

Alternatively review `model-draft/AtRisk.SemanticModel`: it contains the native TMDL imports, measures, relationships and role. It must be applied to a saved PBIP and validated in Desktop before being considered a working Power BI model. The plugin's offline source scan is heuristic; its measure detector reported zero despite 21 native measure definitions, so that output is not evidence of DAX execution. Nested live checks could not find a Power BI Desktop endpoint.

| From (one) | To (many) | Key | Direction |
| --- | --- | --- | --- |
| Dim_Class | Dim_Student | class_id | Single |
| Dim_Student | Fact_Performance | student_id | Single |
| Dim_Student | Fact_Status | student_id | Single |
| Dim_Student | Fact_Intervention | student_id | Single |
| Dim_Student | Fact_Submission | student_id | Single |
| Dim_Student | Fact_Report | student_id | Single |
| Dim_Subject | Fact_Performance | subject_id | Single |
| Dim_Subject | Fact_Intervention | subject_id | Single |
| Dim_Term | Fact_Performance | term_id | Single |
| Dim_Term | Fact_Status | term_id | Single |
| Dim_Term | Fact_Report | term_id | Single |

Keep `Dim_UserAccess` disconnected; its identity checks in `rls.dax` filter `Dim_Student` directly. Do not relate `Dim_Class` directly to Fact_Performance as well as through Dim_Student; that would introduce an ambiguous path. Operational facts have their own grain and are not joined to each other.

## DAX and reconciliation

`measures.dax` contains complete draft definitions and a query to reconcile initial values. Create each measure on its named table, or use DAX Query View's supported measure workflow. Count/ratio measure formats are defined by their units: score and attendance values are on 0–100 scales, while Support Attendance Rate is 0–1.

Fact_Status stores classifications and reasons from the shared Python rule engine, preventing threshold drift across screens. Imported class/term status counts must reconcile with `/api/dashboard/summary` for the same viewer and term. The native status snapshot is across all subjects. Subject slicers affect performance and intervention measures, but should not claim to recompute cohort status. Use a label “Status across all subjects” or disable subject interaction for status visuals. The application's subject-filtered view recomputes status against the selected subject and is intentionally a different diagnostic view.

Term slicers should be single-select for snapshot KPIs. Trend charts use Average Score by Term, which retains term-axis context. Score measures use Fact_Status to exclude students with incomplete subject coverage, matching the application. Attendance includes measured attendance even when a mark is missing. Do not average class averages as though they were raw records.

## Dynamic row-level security

Create the StudentAccess role using `rls.dax`. Replace generated example.test identity mappings with real Microsoft Entra UPNs before live use. The backend session email is not automatically a Microsoft identity. Unknown UPNs receive zero authorized students. Admins have explicit access rows for all students; do not implement unconditional admin bypasses in a viewer role.

Test **View as role** with teacher A, teacher B, student, guardian and unknown users. Verify student/fact tables, drillthrough, totals, exports and class slicers. Guardians should receive a separate report excluding unrestricted uploaded files and draft report details. Power BI workspace Admin/Member/Contributor permissions are not subject to ordinary RLS; assign consumers as Viewers and test with real Viewer identities. See [Microsoft RLS documentation](https://learn.microsoft.com/en-us/power-bi/desktop-rls).

## Eight-page report plan

1. **Executive Overview:** student/at-risk/slow/top cards, score and attendance, status distribution, term trend, class/year/term filters.
2. **At-Risk Triage:** filtered status table, reason codes, score/trend/attendance conditional formatting, Student 360 drillthrough.
3. **Slow Learner Support:** persistent-band evidence, three-term trend, intervention assignment state.
4. **Extra Classes:** scheduled/completed counts, subject breakdown, assigned vs attended, outcome table.
5. **Assignments & Submissions:** submitted/late/reviewed/resubmission counts, version-aware submission table. Pending assignment coverage comes from the operational API; do not infer unsubmitted work from a submissions-only fact.
6. **Progress Reports:** generated/released/pending cards and reporting-term table.
7. **Student 360:** drillthrough student filter, subject scores, trend, reasons, support history, released report metadata.
8. **Top Performers:** top-decile count and ranking, attendance, successful subject patterns.

Use the frontend's warm off-white, royal blue, mint, amber and coral theme. Labels should keep measured data distinct from comments and proposed actions. Do not describe post-support score changes as proof that classes caused improvement.

## Refresh and publication boundary

Snapshots require export followed by Power BI refresh. No Service gateway, refresh schedule, OAuth identity, workspace, embedding or publishing has been configured. Configure credentials through Power BI's supported UI, retain least privilege, and verify the exact report/model before publication. `AtRiskModel/codex-model-drafts` records the source-to-model wizard output; it remains a design pack rather than a validated native report. See [Microsoft's project model documentation](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset).

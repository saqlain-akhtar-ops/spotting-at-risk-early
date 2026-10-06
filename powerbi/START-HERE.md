# Power BI project files — TEAM BLACKCATS

These files use the current synthetic database. This committed snapshot contains synthetic demo data only. This is a source/data package, not a tested PBIX report.

1. Open Power BI Desktop. First create a Blank Query named CsvFolder using powerquery/CsvFolder.pq. Set its value to the absolute path of powerbi/csv in your cloned repository. Then create each table query using the other powerquery files and name it after the file (without .pq).
2. Follow the relationship table in POWER-BI.md. Use single-direction active relationships. Dim_UserAccess stays disconnected.
3. For each file in measures, choose New measure on the table listed in measure-catalog.csv and paste the expression. Set the listed format. Score/attendance are 0–100 numbers, not 0–1 percentages.
4. Import theme.json through View → Themes → Browse for themes.
5. Build the eight report pages described in POWER-BI.md. Use Average Score by Term for the trend axis, Status Count with Fact_Status[status] for the ring, and student-filtered score/attendance for the scatter. Use Status Color as field-value formatting on student rows. Add Student 360 drillthrough, page navigation buttons, tooltips, single-select term/class slicers and Reset bookmarks. Keep subject interactions disabled for stored all-subject status visuals.
6. Configure StudentAccess using rls.dax and test every role. Replace example.test mappings with real user identities before publishing. An unknown user must see no student records.
7. Reconcile row counts with csv/manifest.json. Check latest-term KPI counts against the running backend. Then save your PBIX/PBIP.

Live source option: LiveDemo.pq reads the authenticated local backend instead of the snapshot CSVs. It is a Web Import query and needs a Power BI model refresh. See LIVE-DEMO.md. Credentials remain in Power BI's credential dialog.

The native model-draft retains delivery-specific CSV paths; change them before refreshing on another machine. It includes the original 21 measures. The additional visual measures are supplied separately; add them through New measure. All DAX and native artifacts remain drafts until executed and validated in Power BI Desktop. No Desktop report or Service publishing is claimed.

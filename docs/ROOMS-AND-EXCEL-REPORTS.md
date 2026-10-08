# Room availability and editable Excel reports

## Extra classes

Enter Date, Start, End and Room, then select **Check room availability**. It reports whether that room is already booked during the selected interval. Changing an input invalidates the displayed result.

Checks use all non-cancelled extra classes recorded in this application, including bookings outside the viewer's classes. Only occupied time ranges are returned, not another class's student or teacher details. This is not a connection to the university's central room-booking system, and it does not maintain an authoritative list of physical rooms.

Case and repeated spaces are normalized, so `Lab 2` and ` lab   2 ` refer to the same room. Adjacent slots ending/starting at the same time do not overlap. Scheduling rechecks both room and teacher conflicts. An availability preview does not reserve a room; database-level protection against concurrent competing bookings still needs further hardening before a larger rollout.

GET `/api/rooms/availability?date=2031-10-12&start_time=16:00&end_time=17:00&room=Lab%202` requires an authenticated teacher/administrator. Missing/malformed values return validation errors.

## Excel reports

Authorized staff can select **Download Excel** beside **Download PDF** in Progress Reports or Student 360's report list. GET `/api/reports/{report_id}/excel` enforces staff and student-scope checks and downloads an editable `.xlsx` file with six sheets:

1. Report: styled summary, editable teacher comments and follow-up.
2. Student Lookup: the report student's identifier and labels.
3. Guardian Lookup: that student's active contacts, primary contact first.
4. Academic Records: saved subject scores, previous results, changes and attendance.
5. Support: recorded support from the saved report snapshot.
6. Read Me: lookup instructions, privacy and source timing.

Exact-match VLOOKUP formulas retrieve student and primary-guardian labels by Student ID. Excel recalculates formulas when opened. The workbook is scoped to one permitted report/student, not an institution-wide MIS export. Contact information is read at download time; academic/support evidence comes from the report's saved snapshot. No passwords, password hashes, authentication tokens or Microsoft secrets are included.

The workbook is editable locally and uses an offline snapshot. Changes do not write back to the website or fetch new database data. User-entered strings are explicitly stored as text to prevent formula injection; only application-authored lookup cells contain formulas.

The existing PDF download remains available. Microsoft sign-in is prepared separately and disabled until Entra configuration is supplied; see MICROSOFT-LOGIN-SETUP.md.

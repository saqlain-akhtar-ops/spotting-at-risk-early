# React dashboard and backend logic

The interactive analytics area is implemented in React 19.2.0. Existing login and student-support forms remain in the original JavaScript application. Python/FastAPI remains the backend; React is the user interface, not a database or API server.

## What the project does

1. Store academic scores and attendance by student, subject and term.
2. Detect early review signals using the centralized rules in `backend/status.py`.
3. Return a category, reason codes, comparisons and a rule version through authenticated APIs.
4. Let a teacher review evidence, arrange extra classes, review work, and create/release progress reports.
5. Read saved changes on the dashboard and provide analytical tables to Power BI.

The dashboard does not change risk policy or create random updates. Missing assessment evidence is shown separately. Support actions are recorded by authorized staff.

## Interactive visual controls

- Eight KPI cards link to student groups, charts or support workflows.
- Status ring segments and category buttons focus the score, attendance, class, signal and student-review views.
- Term points change the global term slicer. Academic momentum follows global slicers and retains the whole authorized cohort rather than the local category selection.
- Score/attendance dots show individual evidence and open Student 360. Student 360 explicitly displays latest-term indicators.
- Score bands show complete score counts; missing scores are reported separately.
- Class comparison toggles score and attendance averages.
- Reason counts use backend reason codes and may overlap.
- The queue supports name search, priority/score/decline sorting and student detail links. It displays the first 20 matches; scoped CSV download includes all students in the selected category, independently of queue search.
- The rules panel explains category precedence. Dark theme, responsive layouts, focus styles, hover feedback and reduced-motion support are included.

Global year, term, class and subject filters query the server. The local category selector never widens the rows returned by the server. Workflow KPI counts follow the global cohort; the first three KPI cards follow the local category selection.

## Rebuild

The checked-in `frontend/dashboard.bundle.js` runs without npm or a CDN. On a development machine use `npm install` then `npm run build`. `python tools/install_ui.py` offers a Windows fallback when npm is absent, downloading pinned packages from the npm registry. Run `python tools/build_frontend.py` after HTML/CSS edits. The React source is `frontend/dashboard.jsx`; styles are `frontend/dashboard.css`.

## Validation limits

The React production bundle builds successfully. Server rendering is checked against the running demo API, including empty rows, incomplete values and escaped student names. Browser tooling blocked access to the local preview during this update; chart clicks, layout, animation and mobile rendering have not been visually verified for this version. Native Power BI Desktop remains unverified.

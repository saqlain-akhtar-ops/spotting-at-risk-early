# TEAM BLACKCATS — Spotting the At-Risk Early

## Five-person panel presentation and website demonstration

Target: 12 minutes speaking and demonstration, followed by questions. Replace Member 1–5 with your names. These are presentation responsibilities; describe your personal development contributions only if they are true.

Central message: **We turn academic signals into explainable teacher review, recorded support and progress tracking.**

### What you can confidently claim

- Working website with login, role-based access, database-backed analytics, student profiles and  workflows.
- Python/FastAPI REST backend; React analytics plus HTML/CSS/JavaScript workflow screens.
- Local MySQL configuration and hosted Neon PostgreSQL storage; Vercel deployment; GitHub source repository.
- Explainable rules using scores, attendance and term-to-term patterns. This is a rule-based prototype, not a trained machine-learning predictor.
- Synthetic demonstration: 480 students institution-wide; teacher A sees 240 permitted students. Read current values from the screen because filters and saved updates can change them.
- Power BI integration sources: ten analytical CSV tables, Power Query M imports, authenticated analytical REST feeds, 34 DAX definitions, model/relationship drafts, theme and RLS expressions.
- A verified release check included six frontend login tests and 23 backend tests. That is 29 passed tests for that release, not proof that every production concern has been resolved.

### Power BI delivery status — every member should know this

The website charts run in React. Power BI is supported through an analytical data bridge and supplied model sources. A completed native PBIX report, validated native DAX/RLS execution, published Power BI Service report, scheduled Service refresh and embedded report have not been demonstrated. Never introduce a React chart as an embedded Power BI visual.

Say: **“We incorporated Power BI through the reporting data pipeline and model source package. The interactive website is working; native Power BI report validation and publication remain the next delivery step.”**

## 1. Team responsibilities and timing

| Speaker | Time | Responsibility | Screen |
|---|---|---|---|
| Member 1 | 0:00–2:00 | Problem, users and project purpose | Login → Overview |
| Member 2 | 2:00–4:15 | Dashboard and early-warning rules | Overview → At-Risk Triage |
| Member 3 | 4:15–6:45 | Student 360 and intervention story | Student 005 → Extra Classes |
| Member 4 | 6:45–9:15 | Backend, data flow and Power BI | Website, then Power BI source files/diagram |
| Member 5 | 9:15–12:00 | Security, validation, distinction and conclusion | Reports/Overview → closing |

Member 2 should operate the browser throughout so there are no laptop handovers. Each speaker says the handover sentence below. Members 4 and 5 can point to a diagram or files while the operator keeps the website ready.

## 2. Website presentation flowchart

```text
LOGIN with hosted presentation credentials
                 │
                 ▼
OVERVIEW: permitted students, score, attendance, status and trends
                 │
       Change class/term filter; restore latest term + all classes
                 │
                 ▼
AT-RISK TRIAGE: review a student with visible evidence
                 │
          Open Student 005
                 ▼
STUDENT 360: latest status, subject records, prior score, support history
                 │
                 ▼
EXTRA CLASSES: open Mathematics foundations → Manage
                 │
      Show Student 005's saved enrollment; PENDING attendance
                 │
                 ▼
ASSIGNMENTS / SUBMISSIONS: explain the work-and-feedback loop
                 │
                 ▼
PROGRESS REPORTS: explain draft → review → release
                 │
                 ▼
OVERVIEW: recorded support is reflected in the database-backed dashboard
                 │
                 ▼
POWER BI SOURCE PACKAGE: CSV → Power Query → model → DAX → planned report
                 │
                 ▼
CLOSE: detect → explain → support → review progress
```

This is the presentation sequence, not a claim that the app forces every user through every page. The student chosen for the risk story is Student 005; the student/parent demo accounts are linked to Student 001, so avoid switching to those accounts during this story.

## 3. Full script — Member 1: purpose and problem

**Operator:** Start with login visible, credentials ready privately. Do not project the credential file. Use the direct production link listed in section 8 if the main domain fails.

**Speak:**

“Good morning respected panel members. We are Team BlackCats, and our
instead iif waiting until a student fails our syste  helps a faculty t o idetify warinign sign earlt to take actions 


project is **Spotting the At-Risk Early**.

“Let me start with a simple situation. A student attends school regularly, but their marks are falling across terms. Another student’s marks stay in the same range even after repeated teaching. A third student may need attention because falling performance is accompanied by low attendance. These students need different responses, and a single final exam result does not explain their full situation.

“Our problem is delayed identification and disconnected follow-up. Teachers may have marks in one sheet, attendance in another and extra-class records somewhere else. It takes effort to combine those records, identify a pattern and remember whether support was actually provided.

“We built one workspace that brings those stages together. It helps a teacher answer four questions: Who needs review? What evidence raised the concern? What support has been arranged? And what happened after that support?

“Our main users are administrators, teachers, students and parents. Administrators review the institution, teachers review their assigned classes, and students and parents have narrower access to permitted information.

“We are using synthetic student data for this demonstration. That lets us show the workflow without exposing real student records. The full demonstration has 480 students, while the teacher account shows only its assigned group.

“I will now sign in to show the working application.”

**Operator:** Sign in as teacher A. Wait until Overview displays identity, Database connected and charts. If already signed in, say “We have signed in as a teacher” and continue without logging out.

“We have entered the teacher workspace. The purpose of the dashboard is to make the next review decision easier. The teacher remains responsible for understanding the student and deciding what action is appropriate.

“I’ll now hand over to [Member 2 name], who will explain how the dashboard turns academic records into early-warning signals.”

## 4. Full script — Member 2: dashboard and rules

How do we detect a student who may need attention

**Operator:** Stay on Overview. Point to Students in view, Average score, Average attendance and At Risk. For teacher A, the verified scope was 240 students and 48 At Risk; use the values currently displayed.

**Speak:**

“This Overview page summarizes the records the signed-in teacher is allowed to see. We can review the number of students, average score, average attendance, students flagged for review and students already receiving support.

“Each visual answers a different question. The term trend shows whether performance is moving up or down. The status chart summarizes the distribution of academic categories. The score-and-attendance plot helps us examine those two signals together. Class comparison helps the teacher compare groups, and the review queue takes us from a summary directly to an individual student.

“We can filter by academic year, term, class and subject. These are useful when a teacher wants to move from an institution-level question to a particular class or subject.”

**Operator:** Change Class to Class A, show the reduced student count, then restore All permitted classes. Keep Latest term and All subjects before opening the student story. Optional: click the At Risk KPI and show its focused queue, then restore All.

“The backend uses explicit rules rather than an unexplained score from a black box.

“A student is At Risk when the complete average is below 60 percent, or when a declining score is accompanied by attendance below 75 percent. A falling score that does not meet that higher-risk rule is placed under Watch.

“Top Performer uses the institution-wide 90th-percentile score cutoff together with attendance of at least 90 percent. On Track covers the remaining complete records.

“The Slow Learner category is a specific support pattern: three complete consecutive terms in the 60-to-69-percent range, improvement of zero to one point in the current comparison, and attendance of at least 75 percent. We use that label for this prototype’s support category; it is not a diagnosis of a student’s ability.

“Missing evidence is handled separately as Insufficient Data. We do not substitute a zero score and present it as a real result. If multiple academic rules could apply, the At Risk rule takes precedence.

“The result includes reason codes. That means the teacher can inspect why a student was flagged, instead of seeing only a red badge.”

**Operator:** Open At-Risk Triage using the left navigation. Find Student 005.

“This queue includes both At Risk and Watch students for early review. We’ll follow Student 005 to demonstrate how a signal becomes a support action.

“[Member 3 name] will now take us through that student’s profile and intervention workflow.”

## 5. Full script — Member 3: student story and support

once we detect them what do we do actually about them 

**Operator:** In At-Risk Triage, click Open on Student 005. Wait for the heading “Student 005 · Class A” and its records.

**Speak:**

“We are now in Student 360. This page brings the student’s evidence together: current average, attendance, prior average, change, subject-level records and support history.

“In the verified demonstration, Student 005 had a current average of approximately 51 percent, a prior average of approximately 50.7 percent and attendance of approximately 85.4 percent. The displayed reason is SCORE_BELOW_60.

“This is a useful example because the attendance is not particularly low. The flag here comes from academic performance. We do not give every flagged student the same explanation or assume that attendance is always the cause.

“The teacher can inspect Mathematics, Science and English across terms before deciding what kind of support to arrange. The dashboard directs attention; the profile supplies the evidence.”

**Operator:** Point to the academic table and Support history. Then open Extra Classes.

“Once the teacher has reviewed the situation, the next step is a recorded intervention. This Extra Classes page stores the subject, teacher, class, date, start and end time, room and topic. It also records which students were assigned.

“For this demonstration, we have a Mathematics foundations class scheduled for 12 October, from 4 to 5 PM, in Lab 2.”

**Operator:** Click Manage on Mathematics foundations. Show the saved Student 005 enrollment. It was assigned during verification; do not pretend it is newly assigned or repeatedly click Assign. If it is absent, select Student 005 and assign once, then wait for the saved row.

“Student 005 is already assigned to this support class. Attendance remains Pending because this future class has not yet happened. We can later record attendance and a teacher’s outcome note. We are not marking improvement before collecting new evidence.

“The same workflow continues through assignments, student submissions, teacher feedback and progress reports. A teacher can review submitted work or request a revision, then generate a progress report with comments and follow-up actions.

“Reports have a draft and release process, so the teacher can review the record before it becomes visible to the linked student or guardian. Guardian messages are previewed in our demonstration; we are not sending real parent emails during this presentation.

“This is the central value of our project: a flagged student does not disappear after appearing on a chart. Their support and follow-up can be recorded in the same system.

“[Member 4 name] will explain how the backend and Power BI reporting pipeline support this workflow.”

## 6. Full script — Member 4: backend and Power BI

**Operator:** Display the architecture diagram below or keep Extra Classes visible. Then open the project’s powerbi folder in the file browser/editor, with CSV, measures and Power Query sources ready. Do not open any credential file.

**Speak:**

“The interface and backend have different responsibilities. The frontend displays information and collects user actions. Our Python FastAPI backend exposes REST APIs that authenticate the user, validate the request, enforce access, save records and return results.

“For example, when a teacher assigns a student to an extra class, the website sends an authenticated request. The backend checks the teacher’s permissions and the student’s class, saves the enrollment in the relational database and returns the saved result. The dashboard then reads the database values.

“We configured MySQL for the local setup. The hosted website uses Neon PostgreSQL, because a public deployment cannot depend on the MySQL server running on our laptop. SQLAlchemy provides the database access layer, and Alembic manages schema migrations.

“We also prepared a Power BI reporting integration. Power BI is Microsoft’s analytics platform for connecting data, creating calculations and presenting interactive reports.

“Our incorporation has three main parts. First, the backend exposes analytical tables and can export ten CSV tables. Second, Power Query M sources import and type those records. Third, we provide the analytical model, relationships and DAX definitions for metrics such as student counts, average scores, status counts and support coverage.

“The model uses dimensions for students, classes, subjects and terms, and facts for assessments, status, interventions, submissions and reports. This separates descriptive information from the records we measure.

“DAX, or Data Analysis Expressions, defines calculations in the Power BI model. A measure can respond to a selected term or class. We supplied 34 definitions, including current-term At Risk counts and average score calculations.

“The important distinction is that the live website charts you have just seen are React visuals. Our Power BI contribution is the reporting data bridge and source package. A completed native Power BI report still needs Desktop validation and Service publication; we are not claiming an embedded Power BI report today.

“The web dashboard polls the backend about every ten seconds while its analytics page is visible. The Power Query REST option is an import feed that updates when the Power BI model refreshes. Those are different refresh mechanisms.

“Our design keeps the classification rules in one backend and exposes their results to reporting, reducing the chance of maintaining conflicting definitions in different places.

“[Member 5 name] will now explain the safeguards, what distinguishes this project and where we go next.”

### Architecture diagram for this explanation

```text
Teacher / Student / Parent / Administrator
                     │
                     ▼
React analytics + HTML/CSS/JavaScript workflow interface
                     │ authenticated REST requests
                     ▼
FastAPI: authentication → permission checks → validation → rules
                     │
                     ▼
SQLAlchemy → relational database
             Local: MySQL | Hosted: Neon PostgreSQL
                     │
        ┌────────────┴───────────────────┐
        ▼                                ▼
Website API responses              Analytical API / CSV exports
        │                                │
        ▼                                ▼
Live React charts                  Power Query M source
and support workflows                    │
                                         ▼
                              Model + DAX + RLS source drafts
                                         │
                                         ▼
                              Native report validation/publication
                                      (next delivery step)
```

## 7. Full script — Member 5: safeguards, distinction and close

**Operator:** Briefly open Assignments and Progress Reports if they load quickly; explain their workflow without inventing a completed report. Return to Overview for the close.

**Speak:**

“Because this is student information, access matters. Our API checks access on the server. A teacher is limited to assigned students, while the student and parent demonstration accounts have access to their linked student. Hiding a menu alone would not be enough, so the backend also checks the requested records.

“Passwords are stored as salted hashes. The web application uses an expiring session cookie and a CSRF token for changes. We also record audit events for important actions. The Power BI package includes row-level-security expressions, but these still need to be tested in the native Power BI model before publication.

“Validation matters just as much as access. Scores and attendance must be within valid ranges, records must refer to valid entities, and missing assessments must remain visible as missing evidence. The rule version is recorded so an explanation can be tied to a particular definition.

“For the focused deployed login release, six frontend regression tests and 23 backend tests passed. We also demonstrated login, dashboard, At-Risk Triage, Student 360 and a saved support enrollment in the browser. That verifies the demonstrated path; institutional deployment would still need broader operational and security validation.

“We cannot fairly claim that no other team has similar features, because we have not inspected every project. What we can show is our combination of explainable flags, individual evidence, a working intervention record and progress follow-up in one workflow.

“A marks list shows a result. Our project helps a teacher review the pattern and record what they did next. A reporting dashboard offers insight; our operational workspace also lets the teacher act on it.

“The immediate value for a student is earlier, more targeted review. For a teacher, it is a clearer queue and an organized support record. For an administrator, it is visibility into how many students need review and whether support is being recorded.

“Our next steps are to validate and publish the native Power BI report, test the rules with educators, improve the terminology for persistent support needs and run a governed pilot with consented real data. We would measure whether flagged students are reviewed sooner, whether support is attended and how later academic results change. We would not claim that the intervention caused an improvement without a suitable evaluation.

“To conclude, Spotting the At-Risk Early connects four stages: detect the signal, explain the evidence, record the support and review the progress.

“Thank you. We are happy to answer your questions.”

## 8. Exact operator checklist

### Before the panel

1. Open https://spotting-at-risk-early-ct67ydik7-black-cats2.vercel.app/ — this direct production link was verified with teacher A. The main domain previously timed out from this computer; check both before the presentation. This direct URL is tied to the current deployment.
2. Keep hosted credentials in the private data/HACKATHON_LOGIN.txt file. Copy privately, close the file and sign in before projection if practical. Do not use the laptop password for the hosted database.
3. Use teacher A for the spoken script: 240 permitted students at verification. If you use administrator instead, explain the institution-wide scope of 480 students. Do not mix those numbers.
4. Open Overview, confirm Database connected, Latest term, All permitted classes and All subjects.
5. Rehearse locating Student 005, opening the profile and finding Mathematics foundations under Extra Classes.
6. Confirm Student 005 remains enrolled. Its attendance should remain Pending until the scheduled session occurs.
7. Have powerbi/README.md, powerbi/POWER-BI.md, a CSV, a Power Query source and a DAX source ready. Explain them as source artifacts.
8. Keep the saved dashboard screenshots and this script available as a fallback. Do not depend on a Microsoft account login or unfinished PBIX during the timed demonstration.

### Click-by-click website walkthrough

| Step | Click/action | What to explain | Evidence to check |
|---|---|---|---|
| 1 | Sign in as teacher A | Role-scoped workspace | Advisor A · teacher |
| 2 | Overview | KPIs and visible students | Database connected; 240 at verification |
| 3 | Class → Class A | Filtering narrows the working group | Student count changes |
| 4 | Restore all permitted classes | Return to the whole teacher scope | Class filter restored |
| 5 | At-Risk Triage | Review queue combines At Risk and Watch | Evidence and status columns |
| 6 | Student 005 → Open | Explain one real synthetic example | Student 005 · Class A |
| 7 | Student 360 metrics/table | Score below 60; compare prior term | About 51.0%, 85.4% attendance |
| 8 | Support history | Review previous recorded action | Mathematics enrollment if still present |
| 9 | Extra Classes → Manage | Assignment, attendance and outcome workflow | Student 005 row; Pending attendance |
| 10 | Assignments | Work/submission/teacher-feedback stage | Show existing records; no account switching |
| 11 | Progress Reports | Draft, review and release | Show controls; do not invent a released report |
| 12 | Overview | Saved support contributes to dashboard | Two students in support at verification |
| 13 | Power BI source folder | Reporting integration and model | CSV/M/DAX/schema sources |

### If the internet fails

Say: “The live connection is unavailable at this moment. We will show the saved verification images and explain the same workflow.” Use deliverables/Teacher-login-verified.jpg, Hackathon-login-fixed.jpg and Hackathon-intervention.jpg. State clearly that these are saved screenshots. Do not describe them as live data. Return to the website only when the connection is working.

## 9. Panel questions — basic answers

### Q1. What student problem are you solving?

“We address delayed academic review and disconnected support records. We combine scores, attendance and trends so a teacher can identify a concern, inspect the evidence, arrange support and track the follow-up.”

### Q2. What is the business problem for a school or college?

“Institutions need to coordinate teacher attention and support resources. Our prototype makes the review queue and support records visible in one workspace. Reduced review time and better follow-up are intended benefits that a real pilot would need to measure.”

### Q3. What is Power BI?

“Power BI is Microsoft’s business analytics platform. It connects data, supports models and calculations, and presents interactive reports for decision-making.”

### Q4. How exactly have you incorporated Power BI?

“We built the integration inputs: ten analytical tables available as CSV snapshots and authenticated REST feeds, Power Query import code, model relationships, DAX measures, a theme and RLS sources. Native report validation and publication are still pending.”

### Q5. Are these website charts Power BI visuals?

“They are React charts. They use backend data that can also be supplied to Power BI. We have not embedded a published Power BI report in this website.”

### Q6. Why use React when you have Power BI?

“React supports the operational interface: forms, class assignment, submissions and feedback. Power BI is intended for analytical reporting. They can use shared data while serving different user tasks.”

### Q7. What is DAX?

“DAX stands for Data Analysis Expressions. It is a formula language used for calculations in Power BI models. Our measure sources calculate metrics such as current-term At Risk counts, score averages and support attendance rates.”

### Q8. What is Power Query?

“Power Query imports and prepares data before it enters the analytical model. Our M sources read CSV or REST records and assign types such as integer IDs, numeric scores and text statuses.”

### Q9. What is a star schema?

“It organizes measurable records in fact tables and descriptive information in dimension tables. For example, Fact_Performance stores an assessment, while student, subject and term dimensions explain who it belongs to and when it happened.”

### Q10. What are your KPIs?

“Student counts, average score and attendance, status counts, term trends, students in support, pending submissions and report coverage. We also provide evidence counts so a teacher can see the signals behind the categories.”

### Q11. What is a REST API?

“It is the interface the website uses to read and change backend resources over HTTP. For example, the login request authenticates the user, the student endpoint returns a permitted profile and the extra-class endpoint saves a support assignment.”

### Q12. Which technologies did you actually use?

“React for analytics, HTML/CSS/JavaScript for workflow screens, Python FastAPI for REST services, SQLAlchemy for database access and Alembic for migrations. The local database setup is MySQL, the hosted database is Neon PostgreSQL, and the website is deployed on Vercel. Power BI sources include CSV, M, DAX and model definitions. Source code is maintained in GitHub.”

### Q13. Is your data real?

“The current demonstration is synthetic. It is generated to exercise different academic patterns and workflows. We have not collected or analyzed real student records for this demo.”

### Q14. Is the project real time?

“The website reads current saved database values and polls its visible analytics pages about every ten seconds. That is near-real-time polling. The Power Query feed is Import mode and requires a model refresh; it is not DirectQuery or continuous streaming.”

### Q15. Does Power BI decide which student is At Risk?

“The Python backend applies the classification rules and produces reasons. The analytical feed and CSV expose those results; DAX sources summarize them for reporting. This keeps the decision definition centralized.”

## 10. Panel questions — logic, value and difficult follow-ups

### Q16. Is this an AI or machine-learning system?

“This version is an explainable rule-based system. We have not trained a model or measured prediction accuracy. A future model would require consented data, a defined outcome, evaluation, bias review and an explanation strategy.”

### Q17. Why call it early warning if the student already has low marks?

“Low marks are one trigger, but Watch also identifies falling performance across terms, and persistent patterns highlight students whose progress may need review. The warning is early relative to the next term or final outcome. We do not claim to predict a future failure before any evidence exists.”

### Q18. Why are the thresholds 60 percent and 75 percent?

“They are explicit prototype thresholds chosen for demonstration. They should be reviewed against institutional policy and evaluated with educators before real use. Their clarity makes them inspectable, but it does not prove they are universally correct.”

### Q19. Does attendance below 75 percent automatically mean At Risk?

“In the current rule, low attendance contributes to At Risk when the score is also declining. A complete average below 60 percent independently triggers At Risk. We describe the actual rule rather than treating every low-attendance student identically.”

### Q20. What happens when marks are missing?

“Required incomplete assessments produce Insufficient Data instead of an invented zero or a confident academic category. Prior-term comparison uses the immediately prior term rather than skipping a missing term to find a convenient comparison.”

### Q21. What does Slow Learner mean, and could that label be harmful?

“In this prototype it names a measured pattern of persistent scores and limited improvement, not a permanent trait or medical diagnosis. We would prefer educator-reviewed wording such as Persistent Support Need for real deployment. Teachers must interpret the context.”

### Q22. Is Top Performer simply everyone scoring above 90?

“No. It uses an institution-wide 90th-percentile score threshold plus at least 90 percent attendance. The threshold is cohort-based, and ties can mean more than ten percent qualify.”

### Q23. Why are you different from other teams?

“Our demonstrable distinction is the linked workflow: explainable signals, Student 360 evidence, recorded class support, submissions, feedback and progress reports. We cannot claim uniqueness across projects we have not inspected. We can show that our project connects insight to recorded action.”

### Q24. Why not just use Excel?

“Excel can record and analyze marks. Our application adds authenticated access, a central record, teacher support actions, submission history and report release in one workflow. The advantage is coordination and follow-up; spreadsheets can still be useful as data sources.”

### Q25. Why not use only Power BI?

“Power BI is appropriate for analysis and reporting. Our website also handles operational tasks such as assigning students and reviewing work. The backend manages those actions and then exposes data for reporting.”

### Q26. How do you protect student information?

“The current backend checks roles and student scope, stores hashed passwords, uses session cookies and CSRF checks for changes, and records important actions. Real institutional use would still require identity integration, privacy review, retention rules and broader operational validation.”

### Q27. What is RLS? Is it already working in Power BI?

“Row-level security filters records according to the viewer’s identity. Our API scope is implemented, and the Power BI package supplies RLS expressions. Native Power BI RLS still needs role testing before we can claim a published secure report.”

### Q28. Does a CSV automatically have the same security as the website?

“No. A CSV is a separate exported file. Its distribution must be controlled. The authenticated analytical API applies account scope, and a Power BI model needs properly tested RLS and workspace permissions.”

### Q29. What happens after a student is flagged?

“A teacher reviews the evidence and decides what support is suitable. They can schedule a class, enroll the student, record attendance and outcomes, review submitted work and create a progress report. A flag does not automatically send an email or assign a class.”

### Q30. Have you proved that extra classes improve results?

“We have demonstrated recording support and comparing later records. We have not established causal effectiveness. That would require a suitable evaluation with real data and comparable groups.”

### Q31. How would you measure success in a real pilot?

“Time from flag to teacher review, the proportion receiving documented support, support attendance, completeness of follow-up reports and subsequent academic trends. We would also evaluate false flags, missed concerns and differences across groups.”

### Q32. What is your accuracy?

“We do not report machine-learning accuracy because this version is not a trained predictor and has no labeled outcome study. We test whether the rules and workflow behave as specified; that is different from proving predictive accuracy.”

### Q33. Have you actually deployed it? Where is the data stored?

“The demonstration is deployed on Vercel with persistent records and sessions in Neon PostgreSQL. The deployed backend does not need the laptop MySQL server to be running. The current direct deployment URL is available for the demonstration.”

### Q34. Is the project production ready?

“It is a working hackathon prototype with a verified presentation path. We would not label it a fully certified institutional production system. Native Power BI validation, real identity mappings, broader security and load testing, monitoring and a governed pilot remain delivery work.”

### Q35. How did you test it?

“For the focused login release, six frontend tests and 23 backend tests passed. We checked valid and invalid login, secure session creation, authenticated reads, the live dashboard, Student 360 and a persisted synthetic support assignment. We also verified session restoration after reload. We have not represented unfinished audit work as completed testing.”

### Q36. Why does teacher A see 240 students but the administrator sees 480?

“The difference is intentional authorization. Teacher A is assigned classes A–C, while the administrator has institution-wide scope. Counts should reflect the viewer’s permitted records.”

### Q37. Will a subject slicer change stored Power BI categories?

“Stored Fact_Status categories describe all-subject performance for a term. A subject slicer does not recalculate those classifications in Power BI. The backend can calculate subject-filtered diagnostic views, so the report must label or control those interactions to avoid confusing the two.”

### Q38. What would you add next?

“Complete and validate the native Power BI report, test DAX totals and all security roles, publish through approved accounts, evaluate the thresholds with educators, improve support terminology and run a controlled pilot. We would prioritize evidence and dependable operation before adding more features.”

### Q39. Does the parent email feature send real emails today?

“The hosted demo uses preview mode. It generates a reviewable message but does not send real guardian email. SMTP delivery would need approved configuration and consent checks.”

### Q40. What is your strongest one-sentence pitch?

“Spotting the At-Risk Early helps teachers move from academic signals to explainable review, recorded support and accountable follow-up.”

## 11. DAX explanation for a technical judge

Do not read the whole code during the timed pitch. Have this ready if asked. These are supplied source definitions; native execution has not yet been validated.

```dax
Total Students = DISTINCTCOUNT(Dim_Student[student_id])
```

Say: “We count distinct student IDs so assessments across subjects and terms do not inflate the student count.”

```dax
At Risk Students =
VAR T = [Reporting Term]
RETURN
    CALCULATE(
        DISTINCTCOUNT(Fact_Status[student_id]),
        REMOVEFILTERS(Dim_Term),
        Dim_Term[term_id] = T,
        Fact_Status[status] = "At Risk"
    )
```

Say: “This measure uses the reporting term and counts students whose stored status is At Risk. CALCULATE changes the filter context. The reporting-term helper defaults to the latest term when none is selected.”

```dax
Support Attendance Rate = DIVIDE([Support Attended], [Support Assigned])
```

Say: “This ratio compares attended support enrollments with assigned enrollments. DIVIDE handles a zero denominator safely. It measures support attendance, not whether the intervention caused academic improvement.”

Explain the distinction: Power Query prepares data; relationships define how tables filter one another; DAX measures calculate results within that filter context; visuals present the results. The Python rules determine the prototype categories.

## 12. One-minute compressed close if time is cut

Each member says one sentence:

1. “We solve delayed academic review by connecting marks, attendance and support records.”
2. “Our explainable rules identify low performance, decline and persistent support patterns, with missing data handled separately.”
3. “Student 360 connects the evidence to extra classes, submissions, feedback and progress reports.”
4. “FastAPI and a relational database power the website, while CSV, REST, Power Query and DAX sources provide the Power BI reporting bridge.”
5. “Our working prototype demonstrates detect, explain, support and review; native Power BI validation and a governed real-data pilot are next.”

## 13. Statements to replace during rehearsal

| Avoid saying | Accurate replacement |
|---|---|
| “AI predicts dropout with high accuracy.” | “Explicit rules highlight academic patterns for teacher review.” |
| “All website charts are Power BI.” | “The website uses React; we supply Power BI reporting data and model sources.” |
| “Power BI refreshes every ten seconds.” | “The website polls about every ten seconds; Power Query refreshes with its model.” |
| “We published a secure Power BI report.” | “Native report publication and RLS validation remain pending.” |
| “Low attendance alone makes a student At Risk.” | “The current rule combines low attendance with declining scores, or uses score below 60.” |
| “We improved this student's score through extra classes.” | “We recorded support; later results would be needed to assess progress.” |
| “No other team has built this.” | “Our demonstrable strength is the connected evidence-to-support workflow.” |
| “We use real school data.” | “The current demonstration uses synthetic records.” |
| “Every teacher sees the entire institution.” | “The backend limits each teacher to permitted students.” |
| “The app is fully production certified.” | “The hackathon path is verified; broader institutional readiness needs further validation.” |

## 14. Sources and rehearsal material

Project facts were checked against the repository README, backend/status.py, backend/analytics.py, Power BI measure/query files, the focused deployed checkout, and saved browser verification. No competitor comparison or real-outcome study was performed.

For terminology:

- [Microsoft: What is Power BI?](https://learn.microsoft.com/en-us/power-bi/fundamentals/power-bi-overview) — analytics platform, Desktop and Service responsibilities.
- [Microsoft: DAX overview](https://learn.microsoft.com/en-us/dax/dax-overview) — calculations and filter context.
- [Microsoft: What is Power Query?](https://learn.microsoft.com/en-us/power-query/power-query-what-is-power-query) — data connection and preparation.
- [Microsoft: Star schema guidance](https://learn.microsoft.com/power-bi/guidance/star-schema) — fact and dimension model design.

Relevant local files:

- Private credentials: data/HACKATHON_LOGIN.txt — never project or publish.
- Power BI integration explanation: powerbi/README.md.
- Model and visual plan: powerbi/POWER-BI.md.
- Verification: deliverables/HACKATHON_VERIFICATION.md and TEACHER_CONNECTION_CHECK.md.
- Website evidence: deliverables/Teacher-login-verified.jpg and Hackathon-intervention.jpg.

Rehearse once with the exact account, filters, student and support session. Keep the timed pitch focused on one student story; use the questions section for technical detail.

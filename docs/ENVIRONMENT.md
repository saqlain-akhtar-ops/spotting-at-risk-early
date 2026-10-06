# Verified laptop environment — 6 October 2026

Python 3.12.14 and pip 26.2.1 are available through the bundled runtime. Node.js 24.19.0 and Git 2.55.0 are available. VS Code 1.140.0 is installed. npm was not on PATH at inspection.

MySQL Server/client 8.0.43, Workbench and Shell are installed; the MySQL80 service is running. No application DATABASE_URL or usable saved login has been established. Existing databases and account passwords have not been changed.

Power BI Desktop was absent from the Windows app inventory, Store package query and standard desktop installation paths. Windows UI automation is callable, so Desktop automation can be attempted once installed. Docker was not on PATH.

Existing code: FastAPI/SQLAlchemy/Pydantic REST workflows, centralized status rules, role/resource scope, private submissions, reports, notices, audit, React analytics and 19 passing local tests. Existing data is synthetic development data in SQLite; MySQL support is configured in the ORM but a real connection is pending. Existing Power BI TMDL/DAX/Power Query source is unvalidated.

Remaining external dependencies: Power BI installation (license/UAC handled by the user), a dedicated authorized MySQL connection configured locally, institutional data for production, and Microsoft tenant/app/workspace configuration for Entra/Service operations. No workspace IDs, credentials, real users or institutional records are generated or guessed.

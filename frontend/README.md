# Frontend README

The frontend lets teachers review academic evidence, arrange support and track work. Students and guardians see their authorized records. It uses the supplied dashboard design as its visual foundation.

## Technologies used

| Technology | Use |
|---|---|
| HTML | Page shell, navigation and operational forms |
| CSS | Layout, themes, charts, transitions and responsive rules |
| JavaScript | Login, API requests, page switching and workflow forms |
| React 19.2.0 / React DOM | Interactive analytics dashboard |
| SVG | Custom charts rendered by React |
| esbuild 0.25.10 | Bundles React code into a local JavaScript asset |

TypeScript and React type packages are installed development dependencies. The current application source is JavaScript/JSX; it has not been converted into a fully typed TypeScript application. No external chart library is used for the React visuals.

## Files and build process

| File | Purpose |
|---|---|
| body.html | Editable page structure and forms |
| app.js | Browser API client, session state, navigation and operational actions |
| dashboard.jsx | React analytics components and chart interactions |
| dashboard.css | Analytics styles, themes and motion rules |
| dashboard.bundle.js | Generated React bundle served locally |
| index.html | Generated page served by the backend |

`tools/build_frontend.py` combines the supplied reference styles, `body.html` and `dashboard.css` to generate `index.html`. Change those sources rather than editing only the generated page.

From the project root:

```powershell
npm ci
npm run build
python tools/build_frontend.py
python run.py
```

The checked-in bundle runs without Node.js in the browser. If npm is unavailable, the project also provides `python tools/install_ui.py` to obtain the pinned UI dependencies and build the bundle.

## Screens and interactions

- Overview, At-Risk Triage, Top Performers and Slow Learner Support.
- Extra Classes, Assignments & Submissions, Progress Reports and Student 360.
- Administrator project tools for quality checks, export and audit review.
- Eight KPI cards and six chart areas: term trend, status distribution, score/attendance plot, score bands, class comparisons and reason counts.
- Status selection, term/class/subject/year filters, queue search/sorting, chart-to-student navigation and visible-data CSV download.
- A rule explanation panel, theme switching and motion preferences.

React owns the analytics area. Existing operational forms and page switching remain in `app.js`; this is a hybrid frontend, not a complete React rewrite. Some newer backend fields, including intervention objectives and review marks, do not yet have dedicated form inputs.

## How frontend data works

1. Login returns an authorized user and CSRF token; the browser receives an HttpOnly session cookie.
2. The frontend loads `/api/metadata` to populate permitted filters and options.
3. `/api/power-bi/live` returns dashboard summaries and authorized student rows.
4. React receives those values and renders the charts. Classification comes from the backend.
5. Forms send JSON or multipart file uploads to REST endpoints, using `X-CSRF-Token` for authenticated changes.
6. Saved records appear on the next dashboard refresh.

The frontend polls ten seconds after each polling cycle while an analytics page is visible. Hidden tabs pause refresh work. Failed requests retain the last result and mark it stale. This is periodic API polling, not WebSockets or Power BI Service streaming.

Global filters are sent to the server. React's local group selection affects the review charts and queue; term trends retain their global filter context. Workflow KPI cards open the relevant page.

## Permissions and verification

Role-based visibility helps users find permitted actions, but the backend independently enforces authorization. The browser does not connect directly to MySQL or store database credentials.

The bundle and backend integration were checked. Browser tooling blocked local visual preview, so chart click behavior, animations and mobile layouts still require manual visual verification. Open http://127.0.0.1:8000/ and follow the demonstration steps in the [main README](../README.md).

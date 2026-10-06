# Live demo database and Power BI code

The source is the existing synthetic operational database: 480 students and 5,684 performance records. No Microsoft tenant or cloud semantic model is connected.

## Browser dashboard

`GET /api/power-bi/live` reads the current database and returns authorized dashboard KPIs and student rows. It requires the existing login session. The browser polls on visible Overview, Risk, Slow Learner and Top Performer pages, ten seconds after the last poll completed; slow requests increase the effective interval. It pauses in hidden tabs. Filters and server-side row permissions remain effective. A failed refresh leaves the last fetched values visible and labels them stale.

For a demonstration, update an academic record from Student 360, then open Overview. Another signed-in browser showing Overview picks up the saved change at its next successful poll. Data is synthetic; polling does not create random student changes.

## Power BI Desktop feeds

`backend/powerbi.py` implements the feed. `GET /api/power-bi/tables/Fact_Performance` returns current data on every authorized request. Ten analytical tables are supported; `GET /api/power-bi/catalog` lists them. Each response contains columns, rows, row count and a fetch timestamp. File paths, passwords, guardian contacts and report narrative are excluded. Student/guardian feeds exclude draft reports. Users only see authorized students; the administrator's access-mapping feed includes all mappings needed by the draft RLS model.

Paste `analytics/LiveDemo.pq` into a blank Power Query query, then choose **Basic** credentials for the base URL and use an account from `data/demo-credentials.json`. Duplicate the query for other tables and change `TableName`. Credentials belong in the credential dialog, not in M source. Remote Basic requests require HTTPS; localhost HTTP is permitted only for this local demonstration. This flow is separate from the browser's cookie login. Native Power BI connectivity remains unverified on this machine.

Power Query's Web connector imports data: the API reads current values, but Power BI visuals change only when the imported model refreshes. The browser dashboard's ten-second polling is not a Power BI Service refresh schedule. Native automatic page refresh is intended for supported DirectQuery sources; this Web/SQLite demo does not provide DirectQuery. See [Microsoft Web connector authentication](https://learn.microsoft.com/en-us/power-query/connectors/web/web) and [automatic page refresh](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-automatic-page-refresh).

An imported model retains its connection account's data scope. Published consumer-specific access requires the separate Power BI RLS role and real UPN mappings. A localhost URL is not reachable by Power BI Service without a suitable deployment/gateway; no gateway or schedule is configured.

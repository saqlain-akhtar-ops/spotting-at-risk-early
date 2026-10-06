// Power BI Desktop: create a blank query and paste this code.
// Select Basic authentication in the credential dialog; do not put passwords here.
// Make a copy for each required table, changing TableName.
let
    BaseUrl = "http://127.0.0.1:8000",
    TableName = "Fact_Performance",
    Response = Json.Document(Web.Contents(BaseUrl, [
        RelativePath = "api/power-bi/tables/" & TableName,
        Headers = [Accept = "application/json"],
        IsRetry = true,
        Timeout = #duration(0, 0, 2, 0)
    ])),
    Payload = if Response[success] then Response[data] else error Response[message],
    Rows = Table.FromRecords(Payload[rows], Payload[columns], MissingField.UseNull),
    Types = List.Transform(Payload[columns], (Column) => {
        Column,
        if Column = "review_required" then type logical
        else if Text.EndsWith(Column, "_id") or List.Contains({"version", "version_no", "released"}, Column) then Int64.Type
        else if List.Contains({"score", "current_average", "prior_average", "trend_delta", "top_decile_cutoff"}, Column)
             or (Column = "attendance" and TableName <> "Fact_Intervention") then type number
        else type text
    }),
    Typed = Table.TransformColumnTypes(Rows, Types, "en-US")
in
    Typed

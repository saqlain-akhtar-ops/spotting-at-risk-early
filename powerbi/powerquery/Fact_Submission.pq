let
    Source = Csv.Document(File.Contents(CsvFolder & "/Fact_Submission.csv"), [Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"submission_id", Int64.Type}, {"student_id", Int64.Type}, {"assignment_id", Int64.Type}, {"status", type text}, {"version_no", Int64.Type}, {"submitted_at", type text}}, "en-US")
in
    Typed

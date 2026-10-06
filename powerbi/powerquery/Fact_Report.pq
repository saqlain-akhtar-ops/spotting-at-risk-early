let
    Source = Csv.Document(File.Contents(CsvFolder & "/Fact_Report.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"report_id", Int64.Type}, {"student_id", Int64.Type}, {"term_id", Int64.Type}, {"released", Int64.Type}, {"version", Int64.Type}}, "en-US")
in
    Typed

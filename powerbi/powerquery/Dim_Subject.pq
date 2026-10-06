let
    Source = Csv.Document(File.Contents(CsvFolder & "/Dim_Subject.csv"), [Delimiter=",", Columns=2, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"subject_id", Int64.Type}, {"name", type text}}, "en-US")
in
    Typed

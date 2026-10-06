let
    Source = Csv.Document(File.Contents(CsvFolder & "/Dim_Term.csv"), [Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"term_id", Int64.Type}, {"term_name", type text}, {"academic_year", type text}}, "en-US")
in
    Typed

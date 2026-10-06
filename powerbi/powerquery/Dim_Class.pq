let
    Source = Csv.Document(File.Contents(CsvFolder & "/Dim_Class.csv"), [Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"class_id", Int64.Type}, {"class_name", type text}, {"advisor_id", Int64.Type}}, "en-US")
in
    Typed

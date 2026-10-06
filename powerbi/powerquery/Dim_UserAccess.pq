let
    Source = Csv.Document(File.Contents(CsvFolder & "/Dim_UserAccess.csv"), [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"email", type text}, {"student_id", Int64.Type}, {"class_id", Int64.Type}, {"role", type text}}, "en-US")
in
    Typed

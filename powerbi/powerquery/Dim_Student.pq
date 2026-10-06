let
    Source = Csv.Document(File.Contents(CsvFolder & "/Dim_Student.csv"), [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"student_id", Int64.Type}, {"name", type text}, {"class_id", Int64.Type}, {"academic_year", type text}}, "en-US")
in
    Typed

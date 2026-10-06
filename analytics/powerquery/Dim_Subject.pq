let
    Source = Csv.Document(File.Contents("C:/Users/91731/OneDrive/Documents/ChatGPT/MIH_26/analytics/export/Dim_Subject.csv"), [Delimiter=",", Columns=2, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"subject_id", Int64.Type}, {"name", type text}}, "en-US")
in
    Typed

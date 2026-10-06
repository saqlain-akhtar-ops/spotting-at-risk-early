let
    Source = Csv.Document(File.Contents("C:/Users/91731/OneDrive/Documents/ChatGPT/MIH_26/analytics/export/Fact_Performance.csv"), [Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"performance_id", Int64.Type}, {"student_id", Int64.Type}, {"class_id", Int64.Type}, {"subject_id", Int64.Type}, {"term_id", Int64.Type}, {"score", type number}, {"attendance", type number}}, "en-US")
in
    Typed

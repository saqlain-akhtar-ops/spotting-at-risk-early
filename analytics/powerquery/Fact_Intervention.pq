let
    Source = Csv.Document(File.Contents("C:/Users/91731/OneDrive/Documents/ChatGPT/MIH_26/analytics/export/Fact_Intervention.csv"), [Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"enrollment_id", Int64.Type}, {"student_id", Int64.Type}, {"extra_class_id", Int64.Type}, {"subject_id", Int64.Type}, {"attendance", type text}, {"outcome", type text}, {"status_before", type text}, {"state", type text}}, "en-US")
in
    Typed

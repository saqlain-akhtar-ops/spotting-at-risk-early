let
    Source = Csv.Document(File.Contents("C:/Users/91731/OneDrive/Documents/ChatGPT/MIH_26/analytics/export/Fact_Status.csv"), [Delimiter=",", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"student_id", Int64.Type}, {"term_id", Int64.Type}, {"current_average", type number}, {"prior_average", type number}, {"trend_delta", type number}, {"attendance", type number}, {"status", type text}, {"rule_version", type text}, {"review_required", type logical}, {"top_decile_cutoff", type number}, {"reason_codes", type text}}, "en-US")
in
    Typed

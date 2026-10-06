let
    Source = Csv.Document(File.Contents("C:/Users/91731/OneDrive/Documents/ChatGPT/MIH_26/analytics/export/Dim_Class.csv"), [Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"class_id", Int64.Type}, {"class_name", type text}, {"advisor_id", Int64.Type}}, "en-US")
in
    Typed

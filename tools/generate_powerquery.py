"""Generate typed CSV source queries and a native-model-ready design contract."""
from pathlib import Path
import csv, json
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'analytics/powerquery';out.mkdir(exist_ok=True)
decimal={'score','attendance','current_average','prior_average','trend_delta','top_decile_cutoff'}
types={}
for p in (ROOT/'analytics/export').glob('*.csv'):
    with p.open(encoding='utf-8-sig') as f:fields=next(csv.reader(f))
    columns=[]
    for name in fields:
        kind='type number' if name in decimal and p.stem!='Fact_Intervention' else 'Int64.Type' if name.endswith('_id') or name in ('version','version_no','released') else 'type logical' if name=='review_required' else 'type text'
        columns.append('{"'+name+'", '+kind+'}')
    query='let\n    Source = Csv.Document(File.Contents("'+str(p.resolve()).replace('\\','/')+'"), [Delimiter=",", Columns='+str(len(fields))+', Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n    Typed = Table.TransformColumnTypes(Headers, {'+', '.join(columns)+'}, "en-US")\nin\n    Typed\n'
    (out/(p.stem+'.pq')).write_text(query,encoding='utf-8')
    types[p.stem]={'columns':fields,'query_file':str((out/(p.stem+'.pq')).relative_to(ROOT)),'grain':{'Fact_Performance':'student × subject × term','Fact_Status':'student × term','Fact_Intervention':'student × extra class','Fact_Submission':'submission version','Fact_Report':'report version'}.get(p.stem,'dimension or access mapping')}
(ROOT/'analytics/data-contract.json').write_text(json.dumps(types,indent=2),encoding='utf-8')

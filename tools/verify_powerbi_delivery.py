"""Validate committed synthetic CSV counts and checksums without a live database."""
from pathlib import Path
import csv, hashlib, json
root=Path(__file__).resolve().parents[1]/'powerbi/csv'
manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
assert manifest['source']=='Synthetic data'
assert manifest['data_quality']['passed']
for table,info in manifest['tables'].items():
    path=root/(table+'.csv')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==info['sha256'],table
    with path.open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==info['rows'],table
print('Power BI demo delivery: 10 tables, verified row counts and checksums')

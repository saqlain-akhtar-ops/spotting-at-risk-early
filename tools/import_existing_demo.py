"""Copy the existing labelled demo database to the empty project MySQL database."""
from pathlib import Path
import sys,sqlite3,os
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.runtime')]
from backend.models import Base,engine
from sqlalchemy import text
if os.getenv('APP_ENV')!='development' or engine.dialect.name!='mysql':
    raise SystemExit('This utility only supports the development MySQL connection')
source=ROOT/'data/application.db'
if not source.exists():raise SystemExit('Existing demonstration database not found')
with sqlite3.connect(f'file:{source.as_posix()}?mode=ro',uri=True) as old:
    old.row_factory=sqlite3.Row
    old.execute('BEGIN')
    tables={r[0] for r in old.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    with engine.begin() as target:
        if any(target.scalar(text(f'SELECT COUNT(*) FROM `{t.name}`')) for t in Base.metadata.sorted_tables):
            raise SystemExit('Destination contains records; refusing to overwrite or duplicate them')
        total=0
        for table in Base.metadata.sorted_tables:
            if table.name not in tables:continue
            records=[]
            for row in old.execute(f'SELECT * FROM "{table.name}"'):
                record=dict(row)
                for column in table.columns:
                    if column.name not in record:
                        record[column.name]='' if column.name=='objective' else None
                records.append(record)
            if records:target.execute(table.insert(),records)
            total+=len(records)
        print(f'Copied {total} existing demo records transactionally. Original SQLite database preserved.')

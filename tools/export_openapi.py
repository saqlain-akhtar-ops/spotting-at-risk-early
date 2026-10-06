from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.runtime')]
from backend.app import app
(ROOT/'docs/openapi.json').write_text(json.dumps(app.openapi(),indent=2),encoding='utf-8')

"""Create a portable source bundle without local credentials, uploads or installed libraries."""
from pathlib import Path
import zipfile
import argparse
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output',default='Spotting_AtRisk_Backend_PowerBI.zip')
args=parser.parse_args()
OUT=ROOT/'deliverables'/Path(args.output).name
OUT.parent.mkdir(exist_ok=True)
folders=['backend','frontend','tools','tests','sources','docs','powerbi','.github','analytics/powerquery','analytics/model-draft']
files=['Dockerfile','compose.yaml','.dockerignore','.gitattributes','.env.production.example','requirements-runtime.txt','package.json','README.md','requirements.txt','run.py','Start-Project.ps1','.env.example','.gitignore','analytics/LiveDemo.pq','analytics/measures.dax','analytics/additional-measures.dax','analytics/theme.json','analytics/rls.dax','analytics/POWER-BI.md','analytics/data-contract.json']
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as archive:
    for name in folders:
        for path in (ROOT/name).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                archive.write(path,path.relative_to(ROOT).as_posix())
    for name in files:
        archive.write(ROOT/name,name)
with zipfile.ZipFile(OUT) as archive:
    bad=archive.testzip()
    assert bad is None,bad
    assert not any(p.startswith(('data/','.runtime/','.venv/')) for p in archive.namelist())
    assert 'README.md' in archive.namelist()
    assert len([p for p in archive.namelist() if p.startswith('powerbi/csv/') and p.endswith('.csv')])==10
print(f'Created {OUT.name}: {len(archive.namelist())} files, {OUT.stat().st_size} bytes')

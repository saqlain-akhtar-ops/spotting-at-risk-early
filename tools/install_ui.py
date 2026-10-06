"""Fetch pinned npm packages when npm is unavailable. Build assets stay local."""
from pathlib import Path
import io, tarfile, urllib.request, subprocess
ROOT=Path(__file__).resolve().parents[1]
PACKAGES={'react':'19.2.0','react-dom':'19.2.0','scheduler':'0.27.0','esbuild':'0.25.10','@esbuild/win32-x64':'0.25.10'}
for name,version in PACKAGES.items():
    target=ROOT/'node_modules'/name
    if (target/'package.json').exists(): continue
    url=f'https://registry.npmjs.org/{name}/-/{name.split("/")[-1]}-{version}.tgz'
    payload=urllib.request.urlopen(url,timeout=60).read()
    with tarfile.open(fileobj=io.BytesIO(payload),mode='r:gz') as archive:
        for member in archive.getmembers():
            parts=Path(member.name).parts[1:]
            if not member.isfile() or not parts:continue
            dest=target.joinpath(*parts).resolve()
            if not dest.is_relative_to(target.resolve()):raise ValueError('Unsafe package path')
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(archive.extractfile(member).read())
    print(f'Installed {name}@{version}')
subprocess.run([str(ROOT/'node_modules/@esbuild/win32-x64/esbuild.exe'),'frontend/dashboard.jsx','--bundle','--minify','--outfile=frontend/dashboard.bundle.js'],cwd=ROOT,check=True)

from pathlib import Path
import subprocess,sys,os
ROOT=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(ROOT/'tools/build_frontend.py')],check=True)
if os.getenv('VERCEL')=='1':
    subprocess.run([sys.executable,str(ROOT/'tools/prepare_cloud.py')],check=True)

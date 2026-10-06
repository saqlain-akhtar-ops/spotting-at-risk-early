"""Dependency bootstrap for the self-contained local project."""
from pathlib import Path
import sys
import os
sys.path.insert(0, str(Path(__file__).parent / '.runtime'))
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend.app:app', host=os.getenv('HOST','127.0.0.1'), port=int(os.getenv('PORT','8000')),
                proxy_headers=True,forwarded_allow_ips=os.getenv('FORWARDED_ALLOW_IPS','127.0.0.1'),workers=1)

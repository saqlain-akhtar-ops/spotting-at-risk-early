"""Dependency bootstrap for the self-contained local project."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / '.runtime'))
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend.app:app', host='127.0.0.1', port=8000)

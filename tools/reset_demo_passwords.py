"""Rotate ONLY generated example.test demo credentials; never resets real accounts."""
import sys, secrets, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.runtime')]
from backend.models import Session, User, DATA
from backend.security import hash_password
from sqlalchemy import select
with Session() as db:
    credentials=[]
    for u in db.scalars(select(User)):
        if not u.email.endswith('@example.test'):continue
        password='Demo-'+secrets.token_urlsafe(12)
        u.password_hash=hash_password(password)
        credentials.append({'role':u.role,'email':u.email,'password':password})
    db.commit()
    (DATA/'demo-credentials.json').write_text(json.dumps(credentials,indent=2),encoding='utf-8')
print('Synthetic demo passwords rotated and saved locally.')

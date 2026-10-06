"""Provision the first administrator interactively in a dedicated empty deployment."""
import sys, getpass
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'.runtime'))
from sqlalchemy import select
from backend.models import Base,engine,Session,User
from backend.security import hash_password,audit
from backend.config import load_settings
from backend.schemas import ParentInput

def main():
    settings=load_settings()
    if settings.demo_seed:raise SystemExit('Set DEMO_SEED=0 before provisioning an institutional administrator')
    email=input('Administrator email: ').strip().lower()
    ParentInput(name='Administrator',email=email)
    if email.endswith('@example.test'):raise SystemExit('Use an institutional email, not a demonstration identity')
    name=input('Administrator name: ').strip()
    if not name or len(name)>100:raise SystemExit('Name must contain 1–100 characters')
    password=getpass.getpass('Password (at least 14 characters): ')
    if len(password)<14 or len(password)>200:raise SystemExit('Password must contain 14–200 characters')
    if password!=getpass.getpass('Confirm password: '):raise SystemExit('Passwords do not match')
    Base.metadata.create_all(engine)
    with Session() as db:
        if db.scalar(select(User.id).where(User.role=='admin')):raise SystemExit('An administrator already exists; this tool does not alter accounts')
        user=User(name=name,email=email,role='admin',password_hash=hash_password(password))
        db.add(user);db.flush();audit(db,user,'ADMIN_PROVISIONED','users',user.id);db.commit()
    print('Administrator created. Password was neither saved in plaintext nor printed.')
if __name__=='__main__':main()

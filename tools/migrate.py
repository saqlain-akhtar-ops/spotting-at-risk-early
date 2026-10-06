"""Apply reviewed versioned migrations to the configured project database."""
from pathlib import Path
import sys, os
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.runtime')]
from dotenv import load_dotenv
load_dotenv(ROOT/'.env.local',override=False)
if os.getenv('MIGRATION_DATABASE_URL'):
    os.environ['DATABASE_URL']=os.environ['MIGRATION_DATABASE_URL']
from alembic.config import Config
from alembic import command
if __name__=='__main__':
    args=sys.argv[1:]
    config=Config(str(ROOT/'alembic.ini'))
    if args==['upgrade']:command.upgrade(config,'head')
    elif args==['current']:command.current(config)
    elif args==['check']:command.check(config)
    elif args[:1]==['revision'] and len(args)==2:command.revision(config,message=args[1],autogenerate=True)
    else:raise SystemExit('Usage: python tools/migrate.py upgrade | current | check | revision MESSAGE')

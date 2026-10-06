"""Apply migrations to a configured cloud database; optionally initialize a labelled demo."""
from pathlib import Path
import sys,os
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.runtime')]
from backend.cloud import configure_cloud

def prepare():
    if os.getenv('VERCEL')!='1':raise RuntimeError('This tool is for an explicitly configured Vercel deployment')
    configure_cloud()
    from alembic import command
    from alembic.config import Config
    from backend.models import Session,User
    from sqlalchemy import select,func
    config=Config(str(ROOT/'alembic.ini'))
    config.set_main_option('script_location',str(ROOT/'database/migrations'))
    command.upgrade(config,'head')
    if os.getenv('CLOUD_DEMO')=='1':
        if os.getenv('APP_ENV','development')!='development':raise RuntimeError('Synthetic cloud demo requires development mode')
        for role in ('ADMIN','TEACHER','STUDENT','PARENT'):
            if len(os.getenv('DEMO_'+role+'_PASSWORD',''))<16:
                raise RuntimeError('Configure private demo passwords of at least 16 characters before initialization')
        from backend.seed import seed
        with Session() as db:seed(db)
    with Session() as db:
        print('Cloud schema prepared; authorized account count:',db.scalar(select(func.count(User.id))))

if __name__=='__main__':
    if not (os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')):
        print('Cloud database not connected yet; backend will show setup-required state.')
    else:prepare()

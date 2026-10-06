"""Explicit serverless configuration; never use temporary SQLite as a cloud database."""
import os
from pathlib import Path

def configure_cloud(env=None):
    env=os.environ if env is None else env
    if env.get('VERCEL')!='1':return
    env.setdefault('DATA_DIR','/tmp/at-risk')
    env.setdefault('UPLOAD_STORAGE','database')
    env.setdefault('COOKIE_SECURE','true')
    env.setdefault('DEMO_SEED','0')
    env.setdefault('API_DOCS','false')
    hosts=['spotting-at-risk-early.vercel.app']
    for key in ('VERCEL_URL','VERCEL_PROJECT_PRODUCTION_URL','VERCEL_BRANCH_URL'):
        host=env.get(key,'')
        if host and '/' not in host and ':' not in host:hosts.append(host)
    env.setdefault('ALLOWED_HOSTS',','.join(dict.fromkeys(hosts)))
    url=env.get('DATABASE_URL') or env.get('POSTGRES_URL')
    if not url:raise RuntimeError('Connect a persistent cloud database before enabling the backend')
    if url.startswith('postgres://'):url='postgresql+psycopg://'+url[len('postgres://'):]
    elif url.startswith('postgresql://'):url='postgresql+psycopg://'+url[len('postgresql://'):]
    if not url.startswith(('postgresql+psycopg://','mysql+pymysql://')):
        raise RuntimeError('Cloud database must use supported PostgreSQL or MySQL; temporary SQLite is prohibited')
    env['DATABASE_URL']=url

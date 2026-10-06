import pytest
from backend.cloud import configure_cloud

def test_cloud_rejects_missing_or_temporary_database():
    for url in ('','sqlite:////tmp/demo.db'):
        env={'VERCEL':'1','DATABASE_URL':url}
        with pytest.raises(RuntimeError):configure_cloud(env)

def test_cloud_connection_and_host_defaults():
    env={'VERCEL':'1','POSTGRES_URL':'postgresql://service:example@database.example/project?sslmode=require','VERCEL_URL':'preview.example.vercel.app'}
    configure_cloud(env)
    assert env['DATABASE_URL'].startswith('postgresql+psycopg://')
    assert env['COOKIE_SECURE']=='true' and env['DEMO_SEED']=='0'
    assert env['UPLOAD_STORAGE']=='database'
    assert '*' not in env['ALLOWED_HOSTS'] and 'preview.example.vercel.app' in env['ALLOWED_HOSTS']

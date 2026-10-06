import pytest
from backend.config import load_settings
from backend.middleware import RequestSizeLimit
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.testclient import TestClient

def test_production_configuration_fails_closed():
    good={'APP_ENV':'production','DATABASE_URL':'sqlite:///production-test.db','ALLOWED_HOSTS':'school.example.org'}
    settings=load_settings(good)
    assert not settings.demo_seed and settings.cookie_secure and not settings.api_docs
    for update in [{'DEMO_SEED':'1'},{'COOKIE_SECURE':'false'},{'ALLOWED_HOSTS':'*'},{'DATABASE_URL':''},{'ALLOWED_HOSTS':''}]:
        with pytest.raises(ValueError):load_settings({**good,**update})
    with pytest.raises(ValueError):load_settings({'APP_ENV':'typo'})

def test_stream_limit_without_content_length_and_host_validation():
    async def echo(request):return PlainTextResponse(str(len(await request.body())))
    app=Starlette(routes=[Route('/',echo,methods=['POST'])])
    app.add_middleware(RequestSizeLimit,max_bytes=32)
    app.add_middleware(TrustedHostMiddleware,allowed_hosts=['testserver'],www_redirect=False)
    with TestClient(app) as client:
        assert client.post('/',content=iter([b'x'*16,b'y'*16])).text=='32'
        response=client.post('/',content=iter([b'x'*16,b'y'*17]))
        assert response.status_code==413
        assert response.json()['message']=='Request too large'
        assert client.post('/',content=b'ok',headers={'Host':'attacker.example'}).status_code==400

def test_empty_database_exports_typed_headers(tmp_path,monkeypatch):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from backend.models import Base
    from backend import analytics
    from backend.powerbi import COLUMNS
    import csv
    engine=create_engine('sqlite://')
    Base.metadata.create_all(engine)
    monkeypatch.setattr(analytics,'EXPORT',tmp_path/'export')
    with Session(engine) as db:manifest=analytics.export_data(db)
    assert manifest['data_quality']['passed']
    assert len(manifest['tables'])==10
    for name,columns in COLUMNS.items():
        assert manifest['tables'][name]['rows']==0
        with (tmp_path/'export'/(name+'.csv')).open(encoding='utf-8-sig') as f:
            assert next(csv.reader(f))==columns

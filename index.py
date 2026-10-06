"""Vercel ASGI entrypoint. An unconfigured deployment reports an explicit setup state."""
import os
from pathlib import Path
from backend.cloud import configure_cloud

if os.getenv('VERCEL')=='1' and not (os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')):
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse,JSONResponse
    app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
    @app.get('/')
    def setup():
        return HTMLResponse('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Spotting the At-Risk Early · Setup</title><body style="font:18px system-ui;background:#f5f3ee;color:#172033;max-width:700px;margin:80px auto;padding:24px"><h1>Spotting the At-Risk Early</h1><h2>Cloud database setup required</h2><p>The website is deployed, but the application is not ready to use. Connect a persistent database, apply the project migrations and provision the demo accounts, then redeploy.</p><p>The hosted application does not connect to your laptop or save student records in temporary storage.</p></body></html>',status_code=503,headers={'Cache-Control':'no-store'})
    @app.get('/api/health')
    def health():return {'success':True,'data':{'status':'running','configured':False}}
    @app.api_route('/api/{path:path}',methods=['GET','POST','PUT','DELETE'])
    def unavailable(path:str):
        return JSONResponse({'success':False,'message':'Cloud database setup required','data':None,'errors':['Connect persistent storage and apply migrations']},status_code=503)
else:
    configure_cloud()
    from backend.app import app

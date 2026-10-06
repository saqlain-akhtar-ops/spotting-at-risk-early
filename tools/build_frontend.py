from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
reference=(root/'sources/dashboard.reference.html').read_text(encoding='utf-8')
style=re.search(r'<style>(.*?)</style>',reference,re.S).group(1)
extra='''[hidden]{display:none!important} input,textarea,select{font:inherit;color:var(--ink);background:var(--surface);border:1px solid var(--line);padding:11px;border-radius:10px;width:100%;margin:6px 0}input[type=checkbox]{width:auto}label{display:block;font-size:13px;font-weight:650;margin:14px 0}textarea{min-height:90px}.form-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px 20px}form.card,.view>.card{margin-top:20px}form .btn{margin-top:12px}.login-cover{position:fixed;inset:0;z-index:90;background:var(--bg);display:grid;place-items:center;overflow:auto;padding:24px}.login-cover .card{width:min(500px,100%)}.trend{display:grid;gap:28px;padding:30px 0}.error{border-color:var(--coral);color:var(--danger)}pre{overflow:auto;white-space:pre-wrap;max-height:600px;font-size:12px}.rail{overflow:auto}.nav button{height:43px}.grid.kpis{margin-top:15px}@media(max-width:700px){.form-grid{grid-template-columns:1fr}#identity{display:none}}'''
body=(root/'frontend/body.html').read_text(encoding='utf-8')
(root/'frontend/index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Spotting the At-Risk Early</title><style>'+style+extra+(root/'frontend/dashboard.css').read_text(encoding='utf-8')+'</style></head><body>'+body+'</body></html>',encoding='utf-8')

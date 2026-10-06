"""Read the local synthetic demo for the React rendering check; no record changes."""
from pathlib import Path
import urllib.request, http.cookiejar, json
root=Path(__file__).resolve().parents[1]
account=next(x for x in json.loads((root/'data/demo-credentials.json').read_text()) if x['role']=='admin')
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
request=urllib.request.Request('http://127.0.0.1:8000/api/auth/login',data=json.dumps({'email':account['email'],'password':account['password']}).encode(),headers={'Content-Type':'application/json'})
with opener.open(request,timeout=30) as response:json.load(response)
with opener.open('http://127.0.0.1:8000/api/power-bi/live',timeout=60) as response:live=json.load(response)['data']
(root/'data/dashboard-qa.json').write_text(json.dumps(live),encoding='utf-8')
print(f"Read {len(live['students'])} scoped demo students from the running API")

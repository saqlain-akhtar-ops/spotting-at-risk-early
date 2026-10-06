import os, tempfile, json
from pathlib import Path
TEST_ROOT=Path(tempfile.mkdtemp(prefix='at-risk-tests-'))
os.environ['DATA_DIR']=str(TEST_ROOT)
os.environ['DATABASE_URL']='sqlite:///'+(TEST_ROOT/'test.db').as_posix()
os.environ['EMAIL_MODE']='preview'
from fastapi.testclient import TestClient
from sqlalchemy import select, func
from backend.app import app
from backend.models import Session, User, Performance, Audit, Notification, Report, DATA
from backend.security import hash_password
from backend.status import classify, indicators
import pytest

@pytest.fixture(scope='module')
def client():
    # Startup seeds the isolated database. It does not touch the application database.
    with TestClient(app) as client:
        with Session() as db:
            for u in db.scalars(select(User)):u.password_hash=hash_password('Testing-Only-2026')
            db.commit()
        yield client
def login(client,email):
    r=client.post('/api/auth/login',json={'email':email,'password':'Testing-Only-2026'})
    assert r.status_code==200,r.text
    client.headers['X-CSRF-Token']=r.json()['data']['csrf_token']
def data(r):
    assert r.status_code==200,r.text
    return r.json()['data']
def test_login_csrf_logout(client):
    assert client.post('/api/auth/login',json={'email':'unknown@example.test','password':'no'}).status_code==401
    login(client,'admin@example.test')
    csrf=client.headers.pop('X-CSRF-Token')
    assert client.post('/api/auth/logout').status_code==403
    client.headers['X-CSRF-Token']=csrf
    assert client.post('/api/auth/logout').status_code==200
    assert client.get('/api/students').status_code==401
def test_role_scope(client):
    for email,count in [('admin@example.test',480),('teacher.a@example.test',240),('teacher.b@example.test',240),('student@example.test',1),('parent@example.test',1)]:
        login(client,email);assert len(data(client.get('/api/students')))==count
    for path in ['/api/students/2','/api/students/2/status','/api/students/2/parents','/api/students/2/progress-report']:
        assert client.get(path).status_code==403
    assert client.post('/api/students/1/parents',json={'name':'Bad','email':'bad@example.test'}).status_code==403
    login(client,'teacher.b@example.test')
    assert client.get('/api/students/1').status_code==403
    assert client.post('/api/admin/export').status_code==403
def test_status_boundaries_and_precedence():
    assert classify(59.99,65,95,[65,63,59.99],90)[0]=='At Risk'
    assert classify(80,85,74,[85,83,80],90)[0]=='At Risk'
    assert classify(95,94,92,[93,94,95],90)[0]=='Top Performer'
    assert classify(64.5,64,88,[63.8,64,64.5],90)[0]=='Slow Learner'
    assert classify(64,65,90,[66,65,64],90)[0]=='Watch'
    assert classify(75,None,80,[75],90)[0]=='On Track'
    assert classify(None,None,0,[],None)[0]=='Insufficient Data'
def test_dashboard_and_filters(client):
    login(client,'admin@example.test');d=data(client.get('/api/dashboard/summary'))
    assert d['total_students']==480 and sum(d['statuses'].values())==480
    assert all(d['statuses'][k]>0 for k in ['At Risk','Watch','On Track','Top Performer','Slow Learner'])
    assert data(client.get('/api/dashboard/summary?class_id=1'))['total_students']==80
    assert data(client.get('/api/dashboard/summary?academic_year=1999'))['total_students']==0
    assert len(data(client.get('/api/students?status=Slow%20Learner')))>0
    assert data(client.get('/api/dashboard/summary?class_id=1&term_id=1'))['average_score'] is not None
def test_parent_validation_primary_privacy(client):
    login(client,'teacher.a@example.test')
    assert client.post('/api/students/1/parents',json={'name':'Guardian','email':'not-email'}).status_code==422
    p=data(client.post('/api/students/1/parents',json={'name':'Second Guardian','email':'second@example.test','primary':True,'consent':True}))
    ps=data(client.get('/api/students/1/parents'));assert sum(x['primary'] for x in ps)==1
    assert client.put(f'/api/students/2/parents/{p["id"]}',json={'name':'x','email':'x@example.test'}).status_code==404
    login(client,'student@example.test');assert client.get('/api/students/1/parents').status_code==403
def test_extra_class_full_workflow(client):
    login(client,'teacher.a@example.test')
    body={'subject_id':1,'teacher_id':2,'class_id':1,'date':'2026-12-12','start_time':'16:00','end_time':'17:00','room':'Room 9','topic':'Algebra support'}
    assert client.post('/api/extra-classes',json={**body,'end_time':'15:00'}).status_code==422
    eid=data(client.post('/api/extra-classes',json=body))['id']
    assert client.post('/api/extra-classes',json=body).status_code==409
    assert client.post(f'/api/extra-classes/{eid}/students',json={'student_ids':[241]}).status_code==403
    assert client.post(f'/api/extra-classes/{eid}/students',json={'student_ids':[1]}).status_code==200
    assert client.put(f'/api/extra-classes/{eid}',json={'state':'COMPLETED'}).status_code==422
    assert client.put(f'/api/extra-classes/{eid}/students/1',json={'attendance':'PRESENT','outcome':'Practiced fractions'}).status_code==200
    assert client.put(f'/api/extra-classes/{eid}',json={'state':'COMPLETED'}).status_code==200
    assert data(client.get('/api/dashboard/interventions'))['attended']>=1
def test_files_validation_review_and_ownership(client):
    login(client,'student@example.test')
    fields={'assignment_id':'1','student_id':'1'}
    assert client.post('/api/submissions',data=fields,files={'file':('malware.exe',b'MZ','application/octet-stream')}).status_code==422
    assert client.post('/api/submissions',data=fields,files={'file':('fake.pdf',b'MZ','application/pdf')}).status_code==422
    assert client.post('/api/submissions',data=fields,files={'file':('big.txt',b'x'*(5*1024*1024+1),'text/plain')}).status_code==413
    sub=data(client.post('/api/submissions',data=fields,files={'file':('../../homework.txt',b'My fractions practice','text/plain')}))
    assert sub['original_filename']=='homework.txt' and 'stored_filename' not in sub
    sid=sub['id'];assert client.get(f'/api/submissions/{sid}/download').content==b'My fractions practice'
    assert client.post('/api/submissions',data={**fields,'student_id':'2'},files={'file':('a.txt',b'Hello','text/plain')}).status_code==403
    login(client,'parent@example.test');assert client.get(f'/api/submissions/{sid}/download').status_code==403
    login(client,'teacher.b@example.test');assert client.get(f'/api/submissions/{sid}').status_code==403
    assert client.post(f'/api/submissions/{sid}/review',json={'status':'REVIEWED','feedback':'Good'}).status_code==403
    login(client,'teacher.a@example.test');assert client.post(f'/api/submissions/{sid}/review',json={'status':'REVIEWED','feedback':'Good'}).status_code==200
def test_reports_completeness_release_and_scope(client):
    login(client,'teacher.a@example.test')
    r=data(client.post('/api/students/1/progress-report',json={'term_id':4,'comments':'Progress observed','follow_up':'Advisor A reviews next month'}));rid=r['id']
    login(client,'parent@example.test');assert client.get(f'/api/reports/{rid}/download').status_code==403
    assert client.get('/api/students/1/progress-report').status_code==404
    login(client,'teacher.a@example.test');assert client.post(f'/api/reports/{rid}/release').status_code==200
    login(client,'parent@example.test');assert 'Progress observed' in client.get(f'/api/reports/{rid}/download').text
    assert data(client.get('/api/students/1/progress-report'))['released']==1
    login(client,'admin@example.test')
    assert client.post('/api/students/405/progress-report',json={'term_id':1}).status_code==422
    assert data(client.get('/api/students/405/status?term_id=1'))['status']=='Insufficient Data'
def test_email_preview_not_live_delivery(client):
    login(client,'teacher.a@example.test')
    p=data(client.get('/api/students/1/parents'))[0]
    n=data(client.post('/api/students/1/notifications',json={'parent_id':p['id'],'template':'extra_class'}))
    assert n['status']=='PREVIEW' and 'score' not in n['message']
    assert client.post(f'/api/notifications/{n["id"]}/send').status_code in (409,422)
    assert client.post('/api/students/2/notifications',json={'parent_id':p['id'],'template':'extra_class'}).status_code==422
def test_performance_ranges_and_audit(client):
    login(client,'teacher.a@example.test')
    for score in [-1,101]:assert client.put('/api/students/1/performance',json={'subject_id':1,'term_id':4,'score':score,'attendance':90}).status_code==422
    login(client,'admin@example.test')
    audits=data(client.get('/api/audit'));actions={a['action'] for a in audits}
    assert {'LOGIN','LOGIN_FAILED','FILE_UPLOADED','SUBMISSION_REVIEWED','REPORT_GENERATED','REPORT_RELEASED','STUDENT_ASSIGNED'}<=actions
    q=data(client.get('/api/admin/data-quality'));assert q['passed'] and q['records']==5684 and q['absent_assessments']==76
def test_late_submission_and_teacher_requested_resubmission(client):
    from datetime import datetime,timedelta,timezone
    login(client,'teacher.a@example.test')
    a=data(client.post('/api/assignments',json={'subject_id':1,'class_id':1,'title':'Past-due practice','due_date':(datetime.now(timezone.utc)-timedelta(days=1)).isoformat()}))
    login(client,'student@example.test')
    fields={'assignment_id':str(a['id']),'student_id':'1'}
    s=data(client.post('/api/submissions',data=fields,files={'file':('late.txt',b'Practice work','text/plain')}));assert s['status']=='LATE'
    assert client.post('/api/submissions',data=fields,files={'file':('again.txt',b'Updated work','text/plain')}).status_code==409
    login(client,'teacher.a@example.test');data(client.post(f'/api/submissions/{s["id"]}/review',json={'status':'RESUBMISSION_REQUESTED','feedback':'Please revise'}))
    login(client,'student@example.test');s2=data(client.post('/api/submissions',data=fields,files={'file':('revised.txt',b'Revised work','text/plain')}));assert s2['version_no']==2 and s2['status']=='LATE'
def test_academic_update_recomputes_status_and_keeps_report_snapshot(client):
    from backend.models import StudentStatus
    login(client,'teacher.a@example.test')
    r=data(client.post('/api/students/1/progress-report',json={'term_id':4}));original=json.loads(r['summary'])
    updated=data(client.put('/api/students/1/performance',json={'subject_id':1,'term_id':4,'score':0,'attendance':90}))
    assert updated['status']=='At Risk' and updated['current_average']<60
    with Session() as db:
        stored=db.scalar(select(StudentStatus).where(StudentStatus.student_id==1,StudentStatus.term_id==4))
        assert stored.status=='At Risk' and json.loads(stored.evidence)['current_average']==updated['current_average']
        report=db.get(Report,r['id']);assert json.loads(report.summary)==original
    login(client,'teacher.b@example.test')
    assert client.put('/api/students/1/performance',json={'subject_id':1,'term_id':4,'score':100,'attendance':99}).status_code==403
def test_live_demo_reads_saved_changes_without_csv_export(client):
    login(client,'teacher.a@example.test')
    before=data(client.get('/api/power-bi/live?class_id=1'))
    assert before['synthetic'] and not before['cloud_power_bi_connected']
    assert before['summary']['total_students']==80
    assert len(before['students'])==80
    original=next(r for r in before['students'] if r['id']==2)['current_average']
    data(client.put('/api/students/2/performance',json={'subject_id':1,'term_id':4,'score':0,'attendance':90}))
    after=data(client.get('/api/power-bi/live?class_id=1'))
    changed=next(r for r in after['students'] if r['id']==2)
    assert changed['current_average']!=original and changed['status']=='At Risk'
    assert after['fetched_at']!=before['fetched_at']
    assert client.get('/api/power-bi/live?term_id=9999').status_code==422
    login(client,'parent@example.test')
    linked=data(client.get('/api/power-bi/live'))
    assert len(linked['students'])==1 and linked['students'][0]['id']==1
def test_power_query_feed_auth_scope_and_empty_schema(client):
    unauth=client.get('https://testserver/api/power-bi/tables/Fact_Performance')
    assert unauth.status_code==401 and unauth.headers['www-authenticate']=='Basic'
    assert client.get('https://testserver/api/power-bi/tables/Fact_Performance',auth=('student@example.test','bad')).status_code==401
    for email,count in [('admin@example.test',480),('teacher.a@example.test',240),('teacher.b@example.test',240),('student@example.test',1),('parent@example.test',1)]:
        payload=data(client.get('https://testserver/api/power-bi/tables/Dim_Student',auth=(email,'Testing-Only-2026')))
        assert payload['row_count']==count
        assert 'password_hash' not in str(payload)
    performance=data(client.get('https://testserver/api/power-bi/tables/Fact_Performance',auth=('student@example.test','Testing-Only-2026')))
    assert all(r['student_id']==1 for r in performance['rows'])
    contacts=client.get('https://testserver/api/power-bi/tables/parents',auth=('student@example.test','Testing-Only-2026'))
    assert contacts.status_code==404
    reports=data(client.get('https://testserver/api/power-bi/tables/Fact_Report',auth=('parent@example.test','Testing-Only-2026')))
    assert all(r['released']==1 and r['student_id']==1 for r in reports['rows'])
    empty=data(client.get('https://testserver/api/power-bi/tables/Fact_Submission',auth=('teacher.b@example.test','Testing-Only-2026')))
    assert empty['rows']==[] and 'student_id' in empty['columns']
    remote=client.get('http://testserver/api/power-bi/tables/Dim_Student',auth=('admin@example.test','Testing-Only-2026'))
    assert remote.status_code==403

def test_readiness_and_frontend_security_headers(client):
    assert client.get('/api/health').json()['data']['status']=='running'
    assert client.get('/api/ready').json()['data']['status']=='ready'
    response=client.get('/')
    assert response.status_code==200
    assert "script-src 'self'" in response.headers['content-security-policy']
    assert response.headers['x-content-type-options']=='nosniff'
    assert response.headers['x-frame-options']=='DENY'
    assert 'camera=()' in response.headers['permissions-policy']

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter, defaultdict
from statistics import mean
import hashlib, secrets, time, json, os, html, smtplib
from email.message import EmailMessage
from fastapi import FastAPI, Depends, Request, Response, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
import logging
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from .models import *
from .security import *
from .schemas import (LoginInput, StudentInput, ParentInput, ExtraInput, AssignmentInput,
    EnrollmentInput, AttendanceInput, ReviewInput, StateInput, ReportInput, EmailInput, PerformanceInput)
from .status import indicators, RULE_VERSION, STATUSES
from .seed import seed

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    if os.getenv('DEMO_SEED', '1') == '1':
        with Session() as db: seed(db)
    yield
app = FastAPI(title='Spotting the At-Risk Early', version='1.0.0', lifespan=lifespan)
def ok(data=None, message='Success'):
    return {'success': True, 'message': message, 'data': data, 'errors': []}
@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    logging.getLogger('at-risk').exception('Unhandled application error', exc_info=exc)
    return JSONResponse(status_code=500,content={'success':False,'message':'An unexpected error occurred','data':None,'errors':['Please retry or contact the administrator']})
@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return JSONResponse(status_code=exc.status_code,headers=exc.headers, content={'success':False,'message':str(exc.detail),'data':None,'errors':[str(exc.detail)]})
@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    errors = [{'field': '.'.join(str(p) for p in e['loc']), 'message':e['msg']} for e in exc.errors()]
    return JSONResponse(status_code=422, content={'success':False,'message':'Validation failed','data':None,'errors':errors})
@app.exception_handler(IntegrityError)
async def integrity_error(request, exc):
    return JSONResponse(status_code=409, content={'success':False,'message':'Conflicting or invalid record','data':None,'errors':['Database constraint failed']})
@app.middleware('http')
async def headers_and_limits(request, call_next):
    length = request.headers.get('content-length')
    if length and (not length.isdigit() or int(length) > 6 * 1024 * 1024):
        return JSONResponse(status_code=413, content={'success':False,'message':'Request too large','data':None,'errors':['Maximum request: 6 MB']})
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['Cache-Control'] = 'no-store'
    return response
def database():
    with Session() as db:
        try: yield db
        except Exception:
            db.rollback(); raise
def actor(request: Request, db=Depends(database)):
    token = request.cookies.get('session', '')
    session = db.get(LoginSession, hashlib.sha256(token.encode()).hexdigest())
    if not session or session.expires < time.time(): raise HTTPException(401, 'Please sign in')
    user = db.get(User, session.user_id)
    if not user or not user.active: raise HTTPException(401, 'Account inactive')
    if request.method not in ('GET','HEAD','OPTIONS') and not secrets.compare_digest(request.headers.get('x-csrf-token', ''), session.csrf):
        raise HTTPException(403, 'Invalid request token')
    request.state.auth_session = session
    return user
def public(obj, omit=()):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns if c.name not in omit}
def class_guard(db, user, cid):
    cls = db.get(SchoolClass, cid)
    if not cls: raise HTTPException(404, 'Class not found')
    if user.role != 'admin' and (user.role != 'teacher' or cls.advisor_id != user.id): raise HTTPException(403, 'Class outside your scope')
    return cls
def extra_guard(db, user, eid, write=False):
    item = db.get(ExtraClass, eid)
    if not item: raise HTTPException(404, 'Extra class not found')
    if write: staff(user); class_guard(db, user, item.class_id)
    elif user.role != 'admin':
        allowed = scope(db, user)
        if not db.scalar(select(Enrollment.id).where(Enrollment.extra_class_id==eid, Enrollment.student_id.in_(allowed))) and not (user.role=='teacher' and db.get(SchoolClass,item.class_id).advisor_id==user.id):
            raise HTTPException(403, 'Extra class outside your scope')
    return item
def assignment_guard(db, user, aid, write=False):
    a = db.get(Assignment, aid)
    if not a: raise HTTPException(404, 'Assignment not found')
    if write: staff(user); class_guard(db, user, a.class_id)
    elif user.role != 'admin' and not db.scalar(select(Student.id).where(Student.id.in_(scope(db,user)), Student.class_id==a.class_id)):
        raise HTTPException(403, 'Assignment outside your scope')
    return a
def require_lookup(db, model, key):
    if not db.get(model, key): raise HTTPException(422, f'Invalid {model.__tablename__} reference')

login_attempts = defaultdict(list)
@app.post('/api/auth/login')
def login(body: LoginInput, request:Request, response:Response, db=Depends(database)):
    key = request.client.host if request.client else 'local'
    recent = [t for t in login_attempts[key] if t > time.time()-300]
    login_attempts[key] = recent
    if len(recent) >= 15: raise HTTPException(429, 'Too many attempts; try again in five minutes')
    user = db.scalar(select(User).where(User.email==body.email.lower(), User.active==1))
    # Equalize expensive hash work for unknown users.
    encoded = user.password_hash if user else hash_password('dummy')
    valid = verify_password(body.password, encoded)
    if not user or not valid:
        login_attempts[key].append(time.time())
        audit(db,None,'LOGIN_FAILED','users','unknown'); db.commit()
        raise HTTPException(401, 'Invalid email or password')
    token = secrets.token_urlsafe(32); csrf = secrets.token_urlsafe(24)
    db.add(LoginSession(token_hash=hashlib.sha256(token.encode()).hexdigest(),user_id=user.id,csrf=csrf,expires=time.time()+28800))
    audit(db,user,'LOGIN','users',user.id); db.commit()
    response.set_cookie('session',token,httponly=True,samesite='strict',secure=os.getenv('COOKIE_SECURE','false')=='true',max_age=28800,path='/')
    return ok({'user':public(user,('password_hash',)), 'csrf_token':csrf})
@app.get('/api/auth/me')
def me(request:Request, user=Depends(actor)):
    return ok({'user':public(user,('password_hash',)), 'csrf_token':request.state.auth_session.csrf})
@app.post('/api/auth/logout')
def logout(request:Request,response:Response,user=Depends(actor),db=Depends(database)):
    db.delete(request.state.auth_session); audit(db,user,'LOGOUT','users',user.id); db.commit(); response.delete_cookie('session'); return ok()
@app.get('/api/metadata')
def metadata(user=Depends(actor), db=Depends(database)):
    ids=scope(db,user)
    cids=list(db.scalars(select(Student.class_id).where(Student.id.in_(ids)).distinct()))
    return ok({'classes':[public(x) for x in db.scalars(select(SchoolClass).where(SchoolClass.id.in_(cids)))],
               'subjects':[public(x) for x in db.scalars(select(Subject))], 'terms':[public(x) for x in db.scalars(select(Term))],
               'statuses':STATUSES, 'teachers':[public(x,('password_hash',)) for x in db.scalars(select(User).where(User.role=='teacher'))] if user.role in ('admin','teacher') else [],
               'email_mode':os.getenv('EMAIL_MODE','preview'), 'synthetic_data':True})

def student_rows(db,user,term_id=None,class_id=None,subject_id=None,academic_year=None,status=None):
    if term_id is not None:require_lookup(db,Term,term_id)
    if subject_id is not None:require_lookup(db,Subject,subject_id)
    ids=scope(db,user)
    students=list(db.scalars(select(Student).where(Student.id.in_(ids))))
    info=indicators(db,ids,term_id,subject_id)
    return [{**public(s), 'class_name':db.get(SchoolClass,s.class_id).name, **info[s.id]} for s in students
            if (not class_id or s.class_id==class_id) and (not academic_year or s.academic_year==academic_year) and (not status or info[s.id]['status']==status)]
@app.get('/api/students')
def students(term_id:int|None=None,class_id:int|None=None,subject_id:int|None=None,academic_year:str|None=None,status:str|None=None,q:str='',user=Depends(actor),db=Depends(database)):
    return ok([r for r in student_rows(db,user,term_id,class_id,subject_id,academic_year,status) if q.lower() in r['name'].lower() or q==str(r['id'])])
@app.get('/api/students/{sid}')
def student(sid:int,user=Depends(actor),db=Depends(database)):
    s=student_guard(db,user,sid)
    return ok({**public(s),'class_name':db.get(SchoolClass,s.class_id).name,**indicators(db,[sid])[sid],
        'performance':[public(r) for r in db.scalars(select(Performance).where(Performance.student_id==sid))],
        'support':[{**public(r),'session':public(db.get(ExtraClass,r.extra_class_id))} for r in db.scalars(select(Enrollment).where(Enrollment.student_id==sid))],
        'submissions':[public(r,('stored_filename',)) for r in db.scalars(select(Submission).where(Submission.student_id==sid))]})
@app.put('/api/students/{sid}')
def update_student(sid:int,body:StudentInput,user=Depends(actor),db=Depends(database)):
    staff(user); s=student_guard(db,user,sid); s.name=body.name
    audit(db,user,'PROFILE_UPDATED','students',sid);db.commit();return ok(public(s))
@app.get('/api/students/{sid}/status')
def status(sid:int,term_id:int|None=None,user=Depends(actor),db=Depends(database)):
    student_guard(db,user,sid)
    if term_id is not None:require_lookup(db,Term,term_id)
    return ok(indicators(db,[sid],term_id)[sid])
@app.put('/api/students/{sid}/performance')
def performance(sid:int,body:PerformanceInput,user=Depends(actor),db=Depends(database)):
    staff(user); student_guard(db,user,sid);require_lookup(db,Subject,body.subject_id);require_lookup(db,Term,body.term_id)
    row=db.scalar(select(Performance).where(Performance.student_id==sid,Performance.subject_id==body.subject_id,Performance.term_id==body.term_id))
    if not row: row=Performance(student_id=sid,**body.model_dump());db.add(row)
    else:
        for k,v in body.model_dump().items():setattr(row,k,v)
    db.flush()
    # Percentile thresholds can affect every student; refresh snapshots for the whole institution.
    db.query(StudentStatus).delete()
    for tid in db.scalars(select(Term.id)):
        for student_id,i in indicators(db,list(db.scalars(select(Student.id))),tid).items():
            db.add(StudentStatus(student_id=student_id,term_id=tid,status=i['status'],rule_version=RULE_VERSION,evidence=json.dumps(i)))
    audit(db,user,'PERFORMANCE_UPDATED','students',sid);db.commit();return ok(indicators(db,[sid])[sid])
@app.get('/api/students/{sid}/parents')
def parents(sid:int,user=Depends(actor),db=Depends(database)):
    student_guard(db,user,sid)
    if user.role=='student':raise HTTPException(403,'Parent contacts are staff/guardian information')
    return ok([public(p) for p in db.scalars(select(Parent).where(Parent.student_id==sid))])
def save_parent(db,user,sid,body,pid=None):
    staff(user);student_guard(db,user,sid)
    p=db.get(Parent,pid) if pid else Parent(student_id=sid)
    if not p or p.student_id!=sid:raise HTTPException(404,'Parent contact not found')
    if body.primary and not body.active:raise HTTPException(422,'Primary contact must be active')
    if body.primary:
        for other in db.scalars(select(Parent).where(Parent.student_id==sid)):other.primary=0
    for k,v in body.model_dump().items():setattr(p,k,v)
    db.add(p);db.flush();audit(db,user,'PARENT_UPDATED','parents',p.id);db.commit();return ok(public(p))
@app.post('/api/students/{sid}/parents')
def add_parent(sid:int,body:ParentInput,user=Depends(actor),db=Depends(database)):return save_parent(db,user,sid,body)
@app.put('/api/students/{sid}/parents/{pid}')
def edit_parent(sid:int,pid:int,body:ParentInput,user=Depends(actor),db=Depends(database)):return save_parent(db,user,sid,body,pid)

@app.get('/api/extra-classes')
def extras(user=Depends(actor),db=Depends(database)):
    out=[];ids=scope(db,user)
    for e in db.scalars(select(ExtraClass)):
        enrollments=list(db.scalars(select(Enrollment).where(Enrollment.extra_class_id==e.id,Enrollment.student_id.in_(ids))))
        if user.role=='admin' or enrollments or (user.role=='teacher' and db.get(SchoolClass,e.class_id).advisor_id==user.id):
            out.append({**public(e),'subject':db.get(Subject,e.subject_id).name,'students':[public(r) for r in enrollments]})
    return ok(out)
@app.post('/api/extra-classes')
def add_extra(body:ExtraInput,user=Depends(actor),db=Depends(database)):
    staff(user);cls=class_guard(db,user,body.class_id);require_lookup(db,Subject,body.subject_id)
    teacher=db.get(User,body.teacher_id)
    if not teacher or teacher.role!='teacher' or teacher.id!=cls.advisor_id:raise HTTPException(422,'Choose the class advisor as teacher')
    if body.end_time<=body.start_time:raise HTTPException(422,'End time must be after start time')
    if body.date<datetime.now().date().isoformat():raise HTTPException(422,'Schedule a future or current date')
    overlaps=list(db.scalars(select(ExtraClass).where(ExtraClass.date==body.date,ExtraClass.state!='CANCELLED',ExtraClass.start_time<body.end_time,ExtraClass.end_time>body.start_time)))
    if any(x.teacher_id==body.teacher_id or (body.room and x.room==body.room) for x in overlaps):raise HTTPException(409,'Teacher or room already booked')
    e=ExtraClass(**body.model_dump());db.add(e);db.flush();audit(db,user,'CLASS_CREATED','extra_classes',e.id);db.commit();return ok(public(e))
@app.post('/api/extra-classes/{eid}/students')
def enroll(eid:int,body:EnrollmentInput,user=Depends(actor),db=Depends(database)):
    e=extra_guard(db,user,eid,True)
    if e.state!='SCHEDULED':raise HTTPException(409,'Class is not scheduled')
    for sid in set(body.student_ids):
        s=student_guard(db,user,sid)
        if s.class_id!=e.class_id:raise HTTPException(422,'Student must belong to this class')
        if not db.scalar(select(Enrollment.id).where(Enrollment.extra_class_id==eid,Enrollment.student_id==sid)):
            db.add(Enrollment(extra_class_id=eid,student_id=sid,status_before=indicators(db,[sid])[sid]['status']))
        audit(db,user,'STUDENT_ASSIGNED','extra_classes',eid,{'student_id':sid})
    db.commit();return ok()
@app.put('/api/extra-classes/{eid}/students/{sid}')
def attendance(eid:int,sid:int,body:AttendanceInput,user=Depends(actor),db=Depends(database)):
    extra_guard(db,user,eid,True);student_guard(db,user,sid)
    r=db.scalar(select(Enrollment).where(Enrollment.extra_class_id==eid,Enrollment.student_id==sid))
    if not r:raise HTTPException(404,'Enrollment not found')
    r.attendance=body.attendance;r.outcome=body.outcome;audit(db,user,'ATTENDANCE_UPDATED','extra_class_students',r.id);db.commit();return ok(public(r))
@app.put('/api/extra-classes/{eid}')
def extra_state(eid:int,body:StateInput,user=Depends(actor),db=Depends(database)):
    e=extra_guard(db,user,eid,True)
    assigned=list(db.scalars(select(Enrollment).where(Enrollment.extra_class_id==eid)))
    if body.state=='COMPLETED' and (not assigned or any(r.attendance=='PENDING' for r in assigned)):raise HTTPException(422,'Record attendance for assigned students before completing')
    e.state=body.state;audit(db,user,'CLASS_STATE_UPDATED','extra_classes',eid);db.commit();return ok(public(e))

@app.get('/api/assignments')
def assignments(user=Depends(actor),db=Depends(database)):
    cids=list(db.scalars(select(Student.class_id).where(Student.id.in_(scope(db,user))).distinct()))
    return ok([public(a) for a in db.scalars(select(Assignment).where(Assignment.class_id.in_(cids)))])
@app.post('/api/assignments')
def new_assignment(body:AssignmentInput,user=Depends(actor),db=Depends(database)):
    staff(user);class_guard(db,user,body.class_id);require_lookup(db,Subject,body.subject_id)
    a=Assignment(**body.model_dump(),teacher_id=user.id);db.add(a);db.flush();audit(db,user,'ASSIGNMENT_CREATED','assignments',a.id);db.commit();return ok(public(a))
@app.get('/api/submissions')
def submissions(user=Depends(actor),db=Depends(database)):
    return ok([public(s,('stored_filename',)) for s in db.scalars(select(Submission).where(Submission.student_id.in_(scope(db,user))))])
@app.post('/api/submissions')
async def upload(assignment_id:int=Form(...),student_id:int=Form(...),file:UploadFile=File(...),user=Depends(actor),db=Depends(database)):
    if user.role!='student':raise HTTPException(403,'Only students submit assignment files')
    student=student_guard(db,user,student_id);a=assignment_guard(db,user,assignment_id)
    if a.class_id!=student.class_id:raise HTTPException(403,'Assignment is for another class')
    prior=list(db.scalars(select(Submission).where(Submission.assignment_id==assignment_id,Submission.student_id==student_id).order_by(Submission.version_no)))
    if prior and datetime.fromisoformat(a.due_date)<datetime.now(timezone.utc) and prior[-1].status!='RESUBMISSION_REQUESTED':raise HTTPException(409,'Replacement after deadline requires a teacher resubmission request')
    filename=Path((file.filename or 'file').replace('\\','/')).name[:200]
    ext=Path(filename).suffix.lower()
    allowed={'.pdf':'application/pdf','.txt':'text/plain','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg'}
    if ext not in allowed or file.content_type!=allowed[ext]:raise HTTPException(422,'Permitted files: PDF, UTF-8 text, PNG and JPEG with matching MIME type')
    content=await file.read(5*1024*1024+1)
    if len(content)>5*1024*1024:raise HTTPException(413,'File exceeds 5 MB')
    if not content:raise HTTPException(422,'Empty file')
    valid=(ext=='.pdf' and content.startswith(b'%PDF-')) or (ext=='.png' and content.startswith(b'\x89PNG\r\n\x1a\n')) or (ext in ('.jpg','.jpeg') and content.startswith(b'\xff\xd8\xff'))
    if ext=='.txt':
        try:content.decode('utf-8');valid=b'\x00' not in content
        except UnicodeDecodeError:valid=False
    if not valid:raise HTTPException(422,'File signature does not match its type')
    stored=secrets.token_hex(20)+ext
    s=Submission(assignment_id=assignment_id,student_id=student_id,original_filename=filename,stored_filename=stored,mime_type=allowed[ext],file_size=len(content),version_no=len(prior)+1,status='LATE' if datetime.now(timezone.utc)>datetime.fromisoformat(a.due_date) else 'SUBMITTED')
    path=UPLOADS/stored
    try:
        path.write_bytes(content);db.add(s);db.flush();audit(db,user,'FILE_UPLOADED','submissions',s.id);db.commit()
    except Exception:
        path.unlink(missing_ok=True);raise
    return ok(public(s,('stored_filename',)))
def submission_guard(db,user,subid):
    s=db.get(Submission,subid)
    if not s:raise HTTPException(404,'Submission not found')
    student_guard(db,user,s.student_id);return s
@app.get('/api/submissions/{subid}')
def get_submission(subid:int,user=Depends(actor),db=Depends(database)):
    return ok(public(submission_guard(db,user,subid),('stored_filename',)))
@app.get('/api/submissions/{subid}/download')
def download(subid:int,user=Depends(actor),db=Depends(database)):
    s=submission_guard(db,user,subid)
    if user.role=='parent':raise HTTPException(403,'Guardians may view status, not assignment files')
    audit(db,user,'FILE_DOWNLOADED','submissions',s.id);db.commit()
    return FileResponse(UPLOADS/s.stored_filename,media_type=s.mime_type,filename=s.original_filename)
@app.post('/api/submissions/{subid}/review')
def review(subid:int,body:ReviewInput,user=Depends(actor),db=Depends(database)):
    staff(user);s=submission_guard(db,user,subid);s.status=body.status;s.feedback=body.feedback
    audit(db,user,'SUBMISSION_REVIEWED','submissions',s.id);db.commit();return ok(public(s,('stored_filename',)))

def report_data(db,sid,tid,comments='',follow_up=''):
    s=db.get(Student,sid);require_lookup(db,Term,tid)
    records=list(db.scalars(select(Performance).where(Performance.student_id==sid,Performance.term_id==tid)))
    expected=db.scalar(select(func.count(Subject.id)))
    if len(records)!=expected or any(r.score is None for r in records):raise HTTPException(422,'Report requires complete marks for every subject in the selected term')
    prior_tid=max((t for t in db.scalars(select(Term.id)) if t<tid),default=0)
    previous={r.subject_id:r.score for r in db.scalars(select(Performance).where(Performance.student_id==sid,Performance.term_id==prior_tid))}
    subjects=[{'subject':db.get(Subject,r.subject_id).name,'score':r.score,'attendance':r.attendance,'previous':previous.get(r.subject_id),'delta':round(r.score-previous[r.subject_id],2) if previous.get(r.subject_id) is not None else None} for r in records]
    return dict(student={**public(s),'class_name':db.get(SchoolClass,s.class_id).name},term=public(db.get(Term,tid)),
                indicators=indicators(db,[sid],tid)[sid],subjects=subjects,
                history=[{'term_id':t,**indicators(db,[sid],t)[sid]} for t in db.scalars(select(Term.id)) if t<=tid],
                support=[{**public(e),'class':public(db.get(ExtraClass,e.extra_class_id))} for e in db.scalars(select(Enrollment).where(Enrollment.student_id==sid))],
                submissions=[public(x,('stored_filename',)) for x in db.scalars(select(Submission).where(Submission.student_id==sid))],
                assignments=[public(x) for x in db.scalars(select(Assignment).where(Assignment.class_id==s.class_id))],
                comments=comments,follow_up=follow_up,note='Prototype indicators require advisor review. Support changes are descriptive, not causal evidence.')
@app.get('/api/students/{sid}/progress-report')
def progress(sid:int,term_id:int|None=None,user=Depends(actor),db=Depends(database)):
    student_guard(db,user,sid)
    if user.role in ('parent','student'):
        query=select(Report).where(Report.student_id==sid,Report.released==1)
        if term_id:query=query.where(Report.term_id==term_id)
        r=db.scalar(query.order_by(Report.id.desc()))
        if not r:raise HTTPException(404,'No released report available')
        return ok({**public(r), 'summary':json.loads(r.summary)})
    tid=term_id or db.scalar(select(func.max(Term.id)))
    return ok(report_data(db,sid,tid))
@app.post('/api/students/{sid}/progress-report')
def generate_report(sid:int,body:ReportInput,user=Depends(actor),db=Depends(database)):
    staff(user);student_guard(db,user,sid);data=report_data(db,sid,body.term_id,body.comments,body.follow_up)
    version=(db.scalar(select(func.max(Report.version)).where(Report.student_id==sid,Report.term_id==body.term_id)) or 0)+1
    r=Report(student_id=sid,term_id=body.term_id,version=version,summary=json.dumps(data),comments=body.comments,follow_up=body.follow_up)
    db.add(r);db.flush();audit(db,user,'REPORT_GENERATED','progress_reports',r.id);db.commit();return ok(public(r))
@app.get('/api/reports')
def reports(user=Depends(actor),db=Depends(database)):
    query=select(Report).where(Report.student_id.in_(scope(db,user)))
    if user.role in ('parent','student'):query=query.where(Report.released==1)
    return ok([public(r,('summary',)) for r in db.scalars(query)])
@app.post('/api/reports/{rid}/release')
def release(rid:int,user=Depends(actor),db=Depends(database)):
    staff(user);r=db.get(Report,rid)
    if not r:raise HTTPException(404,'Report not found')
    student_guard(db,user,r.student_id);r.released=1;audit(db,user,'REPORT_RELEASED','progress_reports',rid);db.commit();return ok(public(r,('summary',)))
@app.get('/api/reports/{rid}/download',response_class=HTMLResponse)
def report_download(rid:int,user=Depends(actor),db=Depends(database)):
    r=db.get(Report,rid)
    if not r:raise HTTPException(404,'Report not found')
    student_guard(db,user,r.student_id)
    if user.role in ('parent','student') and not r.released:raise HTTPException(403,'Report is not released')
    d=json.loads(r.summary);esc=lambda v:html.escape(str(v))
    rows=''.join('<tr>'+''.join(f'<td>{esc(s[k])}</td>' for k in ['subject','score','previous','delta','attendance'])+'</tr>' for s in d['subjects'])
    body=f'<h1>Student progress report</h1><p>{esc(d["student"]["name"])} · {esc(d["student"]["class_name"])} · {esc(d["term"]["name"])}</p><p>Version {r.version} · {esc(r.generated_at)} · {"Released" if r.released else "Draft"}</p><h2>Measured academic indicators</h2><pre>{esc(json.dumps(d["indicators"],indent=2))}</pre><table><tr><th>Subject</th><th>Score</th><th>Previous</th><th>Delta</th><th>Attendance</th></tr>{rows}</table><h2>Support history</h2><pre>{esc(json.dumps(d["support"],indent=2))}</pre><h2>Assignments and submissions</h2><pre>{esc(json.dumps({"assignments":d["assignments"],"submissions":d["submissions"]},indent=2))}</pre><h2>Teacher comments</h2><p>{esc(r.comments)}</p><h2>Follow-up actions</h2><p>{esc(r.follow_up)}</p><p>{esc(d["note"])}</p>'
    audit(db,user,'REPORT_DOWNLOADED','progress_reports',rid);db.commit()
    return HTMLResponse('<!doctype html><meta charset="utf-8"><title>Student report</title><style>body{max-width:900px;margin:40px auto;font:16px system-ui;padding:20px;color:#172033}td,th{padding:10px;border-bottom:1px solid #ddd}pre{white-space:pre-wrap}h2{margin-top:35px}@media print{body{margin:0;font-size:11px}}</style>'+body)

TEMPLATES={'progress_report':'A progress report is available in your authorized school portal. Please sign in to review it.', 'extra_class':'An academic support session has been assigned. Please sign in to the school portal for the subject, date, time and location.', 'assignment':'A learning assignment is available. Please sign in to the school portal for instructions and the deadline.', 'follow_up':'Your advisor has requested a follow-up. Please sign in to the school portal or contact the school.'}
@app.post('/api/students/{sid}/notifications')
def notification(sid:int,body:EmailInput,user=Depends(actor),db=Depends(database)):
    staff(user);student_guard(db,user,sid);p=db.get(Parent,body.parent_id)
    if not p or p.student_id!=sid or not p.active:raise HTTPException(422,'Choose an active guardian for this student')
    n=Notification(student_id=sid,parent_id=p.id,template=body.template,message=TEMPLATES[body.template])
    db.add(n);db.flush();audit(db,user,'EMAIL_PREVIEW_CREATED','notifications',n.id);db.commit();return ok(public(n))
@app.get('/api/notifications')
def notifications(user=Depends(actor),db=Depends(database)):
    staff(user);return ok([public(n) for n in db.scalars(select(Notification).where(Notification.student_id.in_(scope(db,user))))])
@app.post('/api/notifications/{nid}/send')
def send_email(nid:int,user=Depends(actor),db=Depends(database)):
    staff(user);n=db.get(Notification,nid)
    if not n:raise HTTPException(404,'Notification not found')
    student_guard(db,user,n.student_id);p=db.get(Parent,n.parent_id)
    if n.status in ('SENT','SENDING','UNKNOWN'):raise HTTPException(409,'Already sent or uncertain delivery; inspect before retrying')
    if not p.active or not p.consent:raise HTTPException(422,'Guardian communication consent is required')
    if os.getenv('EMAIL_MODE','preview')!='smtp':raise HTTPException(409,'Preview mode: SMTP is not configured; no email was sent')
    required=['SMTP_HOST','SMTP_FROM','SMTP_USER','SMTP_PASSWORD']
    if any(not os.getenv(k) for k in required):raise HTTPException(503,'SMTP configuration is incomplete')
    if p.email.endswith('.test'):raise HTTPException(422,'Synthetic .test recipients cannot receive live emails')
    n.status='SENDING';n.attempts+=1;db.commit()
    message=EmailMessage();message['Subject']='School portal update';message['From']=os.environ['SMTP_FROM'];message['To']=p.email;message.set_content(n.message)
    try:
        with smtplib.SMTP(os.environ['SMTP_HOST'],int(os.getenv('SMTP_PORT','587')),timeout=15) as smtp:
            smtp.starttls();smtp.login(os.environ['SMTP_USER'],os.environ['SMTP_PASSWORD']);smtp.send_message(message)
        n.status='SENT';n.sent_at=now();n.error=''
    except Exception:
        # Do not automatically retry an ambiguous SMTP result.
        n.status='UNKNOWN';n.error='Delivery uncertain; verify with mail provider before retrying'
    audit(db,user,'EMAIL_SEND_ATTEMPT','notifications',nid,{'status':n.status});db.commit();return ok(public(n))

@app.get('/api/dashboard/summary')
def dashboard(term_id:int|None=None,class_id:int|None=None,subject_id:int|None=None,academic_year:str|None=None,status:str|None=None,user=Depends(actor),db=Depends(database)):
    rows=student_rows(db,user,term_id,class_id,subject_id,academic_year,status);ids=[r['id'] for r in rows]
    counts=Counter(r['status'] for r in rows);scores=[r['current_average'] for r in rows if r['current_average'] is not None];att=[r['attendance'] for r in rows if r['attendance'] is not None]
    term=term_id or db.scalar(select(func.max(Term.id)))
    interventions=list(db.scalars(select(Enrollment).where(Enrollment.student_id.in_(ids))))
    eids={r.extra_class_id for r in interventions}
    if user.role in ('admin','teacher') and status is None:
        eids.update(db.scalars(select(ExtraClass.id).where(ExtraClass.class_id.in_({r['class_id'] for r in rows}))))
    latest_sub={}
    for s in db.scalars(select(Submission).where(Submission.student_id.in_(ids)).order_by(Submission.version_no)):latest_sub[(s.student_id,s.assignment_id)]=s
    pending=0
    for student in rows:
        for a in db.scalars(select(Assignment).where(Assignment.class_id==student['class_id'])):
            if (student['id'],a.id) not in latest_sub or latest_sub[(student['id'],a.id)].status=='RESUBMISSION_REQUESTED':pending+=1
    generated=set(db.scalars(select(Report.student_id).where(Report.student_id.in_(ids),Report.term_id==term)))
    released=set(db.scalars(select(Report.student_id).where(Report.student_id.in_(ids),Report.term_id==term,Report.released==1)))
    return ok({'total_students':len(rows),'average_score':round(mean(scores),2) if scores else None,'average_attendance':round(mean(att),2) if att else None,
               'statuses':{k:counts[k] for k in STATUSES+['Insufficient Data']},'students_in_support':len({x.student_id for x in interventions}),
               'extra_classes_pending':sum(db.get(ExtraClass,eid).state=='SCHEDULED' for eid in eids),'pending_submissions':pending,
               'reports_pending':len(ids)-len(generated),'reports_unreleased':len(ids)-len(released),
               'trend':[{'term_id':t,'average_score':round(mean(vals),2) if (vals:=[v['current_average'] for v in indicators(db,ids,t,subject_id).values() if v['current_average'] is not None]) else None} for t in db.scalars(select(Term.id))],
               'rule_version':RULE_VERSION,'data_source':'Synthetic operational data','refreshed_at':now()})
@app.get('/api/dashboard/interventions')
def intervention_metrics(user=Depends(actor),db=Depends(database)):
    ids=scope(db,user);rows=list(db.scalars(select(Enrollment).where(Enrollment.student_id.in_(ids))))
    return ok({'assigned':len(rows),'attended':sum(r.attendance in ('PRESENT','LATE') for r in rows),'pending':sum(r.attendance=='PENDING' for r in rows),
               'subject_breakdown':dict(Counter(db.get(Subject,db.get(ExtraClass,r.extra_class_id).subject_id).name for r in rows)),
               'status_comparisons':[{'student_id':r.student_id,'before':r.status_before,'current':indicators(db,[r.student_id])[r.student_id]['status'],'note':'Descriptive comparison; not causal evidence'} for r in rows]})
@app.get('/api/audit')
def audits(user=Depends(actor),db=Depends(database)):
    if user.role!='admin':raise HTTPException(403,'Administrator access required')
    return ok([public(a) for a in db.scalars(select(Audit).order_by(Audit.id.desc()).limit(500))])
@app.get('/api/admin/data-quality')
def dq(user=Depends(actor),db=Depends(database)):
    if user.role!='admin':raise HTTPException(403,'Administrator access required')
    from .analytics import quality
    return ok(quality(db))
@app.post('/api/admin/export')
def export(user=Depends(actor),db=Depends(database)):
    if user.role!='admin':raise HTTPException(403,'Administrator access required')
    from .analytics import export_data
    manifest=export_data(db);audit(db,user,'ANALYTICS_EXPORTED','analytics','snapshot');db.commit();return ok(manifest)
from .powerbi import install_routes
install_routes(app,database,actor,ok,dashboard,students)

@app.get('/api/health')
def health():return ok({'status':'running'})
app.mount('/assets',StaticFiles(directory=ROOT/'frontend'),name='assets')
@app.get('/',include_in_schema=False)
def index():return FileResponse(ROOT/'frontend'/'index.html')

"""Read current operational rows for the demo Power BI model.

No CSV cache, provider token, or invented cloud connection is used here.
Authentication is supplied by the application when this router is installed.
"""
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from .models import (Student, SchoolClass, Subject, Term, Performance, User, Access,
                     Enrollment, ExtraClass, Submission, Report, now)
from .security import scope, verify_password, audit
from .status import indicators
import time

COLUMNS = {
    'Dim_Student': ['student_id','name','class_id','academic_year'],
    'Dim_Class': ['class_id','class_name','advisor_id'],
    'Dim_Subject': ['subject_id','name'],
    'Dim_Term': ['term_id','term_name','academic_year'],
    'Dim_UserAccess': ['email','student_id','class_id','role'],
    'Fact_Performance': ['performance_id','student_id','class_id','subject_id','term_id','score','attendance'],
    'Fact_Status': ['student_id','term_id','current_average','prior_average','trend_delta','attendance','status','rule_version','review_required','top_decile_cutoff','reason_codes'],
    'Fact_Intervention': ['enrollment_id','student_id','extra_class_id','subject_id','attendance','outcome','status_before','state'],
    'Fact_Submission': ['submission_id','student_id','assignment_id','status','version_no','submitted_at'],
    'Fact_Report': ['report_id','student_id','term_id','released','version'],
}

def current_rows(db, user, table):
    if table not in COLUMNS: raise HTTPException(404, 'Unknown analytical table')
    ids=scope(db,user)
    students=list(db.scalars(select(Student).where(Student.id.in_(ids))))
    smap={s.id:s for s in students}; cids={s.class_id for s in students}
    if table=='Dim_Student':
        return [{'student_id':s.id,'name':s.name,'class_id':s.class_id,'academic_year':s.academic_year} for s in students]
    if table=='Dim_Class':
        return [{'class_id':c.id,'class_name':c.name,'advisor_id':c.advisor_id} for c in db.scalars(select(SchoolClass).where(SchoolClass.id.in_(cids)))]
    if table=='Dim_Subject':
        return [{'subject_id':s.id,'name':s.name} for s in db.scalars(select(Subject))]
    if table=='Dim_Term':
        return [{'term_id':t.id,'term_name':t.name,'academic_year':t.academic_year} for t in db.scalars(select(Term))]
    if table=='Dim_UserAccess':
        users=list(db.scalars(select(User).where(User.active==1))) if user.role=='admin' else [user]
        return [{'email':u.email,'student_id':sid,'class_id':smap[sid].class_id,'role':u.role}
                for u in users for sid in scope(db,u) if sid in smap]
    if table=='Fact_Performance':
        return [{'performance_id':r.id,'student_id':r.student_id,'class_id':smap[r.student_id].class_id,'subject_id':r.subject_id,'term_id':r.term_id,'score':r.score,'attendance':r.attendance}
                for r in db.scalars(select(Performance).where(Performance.student_id.in_(ids)))]
    if table=='Fact_Status':
        return [{'student_id':sid,'term_id':tid,**{k:v for k,v in info.items() if k not in ('reason_codes','term_id')},'reason_codes':';'.join(info['reason_codes'])}
                for tid in db.scalars(select(Term.id)) for sid,info in indicators(db,ids,tid).items()]
    if table=='Fact_Intervention':
        rows=[]
        for r in db.scalars(select(Enrollment).where(Enrollment.student_id.in_(ids))):
            extra=db.get(ExtraClass,r.extra_class_id)
            rows.append({'enrollment_id':r.id,'student_id':r.student_id,'extra_class_id':r.extra_class_id,'subject_id':extra.subject_id,'attendance':r.attendance,'outcome':r.outcome,'status_before':r.status_before,'state':extra.state})
        return rows
    if table=='Fact_Submission':
        return [{'submission_id':s.id,'student_id':s.student_id,'assignment_id':s.assignment_id,'status':s.status,'version_no':s.version_no,'submitted_at':s.submitted_at}
                for s in db.scalars(select(Submission).where(Submission.student_id.in_(ids)))]
    query=select(Report).where(Report.student_id.in_(ids))
    if user.role in ('student','parent'):query=query.where(Report.released==1)
    return [{'report_id':r.id,'student_id':r.student_id,'term_id':r.term_id,'released':r.released,'version':r.version} for r in db.scalars(query)]

def install_routes(app, database, actor, ok, summary, student_list):
    """Install live dashboard and Basic-authenticated read-only Power Query feeds."""
    basic=HTTPBasic(auto_error=False)
    failures={}
    def feed_actor(request:Request,credentials:HTTPBasicCredentials|None=Depends(basic),db=Depends(database)):
        if not credentials:raise HTTPException(401,'Use Basic authentication for the Power BI feed',headers={'WWW-Authenticate':'Basic'})
        if request.url.scheme!='https' and (not request.client or request.client.host not in ('127.0.0.1','::1')):
            raise HTTPException(403,'Use HTTPS for remote Power BI connections')
        key=request.client.host if request.client else 'unknown'
        attempts=[t for t in failures.get(key,[]) if t>time.time()-300];failures[key]=attempts
        if len(attempts)>=15:raise HTTPException(429,'Too many authentication attempts')
        user=db.scalar(select(User).where(User.email==credentials.username.lower(),User.active==1))
        if not user or not verify_password(credentials.password,user.password_hash):
            attempts.append(time.time());audit(db,None,'POWERBI_AUTH_FAILED','users','unknown');db.commit()
            raise HTTPException(401,'Invalid credentials',headers={'WWW-Authenticate':'Basic'})
        return user

    @app.get('/api/power-bi/live')
    def live(term_id:int|None=None,class_id:int|None=None,subject_id:int|None=None,academic_year:str|None=None,status:str|None=None,user=Depends(actor),db=Depends(database)):
        kwargs=dict(term_id=term_id,class_id=class_id,subject_id=subject_id,academic_year=academic_year,status=status,user=user,db=db)
        return ok({'summary':summary(**kwargs)['data'],'students':student_list(**kwargs)['data'],
                   'fetched_at':now(),'source':'Demo operational database','synthetic':True,
                   'delivery':'On-demand database query; dashboard polls 10 seconds after each completed request',
                   'cloud_power_bi_connected':False})

    @app.get('/api/power-bi/catalog')
    def catalog(user=Depends(actor)):
        return ok({'tables':[{'name':k,'columns':v} for k,v in COLUMNS.items()],
                   'refresh':'Live API reads; Power Query Web uses Import refresh', 'synthetic':True})

    @app.get('/api/power-bi/tables/{table}')
    def feed(table:str,user=Depends(feed_actor),db=Depends(database)):
        rows=current_rows(db,user,table)
        return ok({'table':table,'columns':COLUMNS[table],'rows':rows,'row_count':len(rows),
                   'fetched_at':now(),'source':'Demo operational database','synthetic':True})

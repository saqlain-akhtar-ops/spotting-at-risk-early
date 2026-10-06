"""Validated snapshot bridge from operational data to a Power BI star schema."""
import csv, json, hashlib
from collections import Counter
from sqlalchemy import select, func
from .models import *
from .status import indicators
from .powerbi import COLUMNS

EXPORT=ROOT/'analytics'/'export'
def quality(db):
    rows=list(db.scalars(select(Performance)))
    keys=Counter((r.student_id,r.subject_id,r.term_id) for r in rows)
    errors=[]
    for r in rows:
        if r.score is None:errors.append({'type':'missing_mark','id':r.id})
        elif not 0<=r.score<=100:errors.append({'type':'invalid_score','id':r.id})
        if not 0<=r.attendance<=100:errors.append({'type':'invalid_attendance','id':r.id})
        for model,key in [(Student,r.student_id),(Subject,r.subject_id),(Term,r.term_id)]:
            if not db.get(model,key):errors.append({'type':'orphan','id':r.id})
    errors.extend({'type':'duplicate','key':list(k)} for k,n in keys.items() if n>1)
    expected=db.scalar(select(func.count(Student.id)))*db.scalar(select(func.count(Subject.id)))*db.scalar(select(func.count(Term.id)))
    return {'checked_at':now(),'records':len(rows),'expected_assessments':expected,'absent_assessments':expected-len(rows),'issues':errors,'passed':not errors,
            'note':'Absent assessments are reported separately; reports require full subject coverage.'}
def export_data(db):
    check=quality(db)
    if not check['passed']:raise ValueError('Data quality failed; snapshot refused')
    EXPORT.mkdir(parents=True,exist_ok=True)
    students=list(db.scalars(select(Student)));smap={s.id:s for s in students};ids=list(smap)
    tables={
        'Dim_Student':[{'student_id':s.id,'name':s.name,'class_id':s.class_id,'academic_year':s.academic_year} for s in students],
        'Dim_Class':[{'class_id':c.id,'class_name':c.name,'advisor_id':c.advisor_id} for c in db.scalars(select(SchoolClass))],
        'Dim_Subject':[{'subject_id':s.id,'name':s.name} for s in db.scalars(select(Subject))],
        'Dim_Term':[{'term_id':t.id,'term_name':t.name,'academic_year':t.academic_year} for t in db.scalars(select(Term))],
        'Fact_Performance':[{'performance_id':r.id,'student_id':r.student_id,'class_id':smap[r.student_id].class_id,'subject_id':r.subject_id,'term_id':r.term_id,'score':r.score,'attendance':r.attendance} for r in db.scalars(select(Performance))],
        'Dim_UserAccess':[{'email':u.email,'student_id':sid,'class_id':smap[sid].class_id,'role':u.role} for u in db.scalars(select(User).where(User.active==1)) for sid in (ids if u.role=='admin' else db.scalars(select(Access.student_id).where(Access.user_id==u.id)))],
        'Fact_Status':[{'student_id':sid,'term_id':tid,**{k:v for k,v in info.items() if k not in ('reason_codes','term_id')},'reason_codes':';'.join(info['reason_codes'])} for tid in db.scalars(select(Term.id)) for sid,info in indicators(db,ids,tid).items()],
        'Fact_Intervention':[{'enrollment_id':r.id,'student_id':r.student_id,'extra_class_id':r.extra_class_id,'subject_id':db.get(ExtraClass,r.extra_class_id).subject_id,'attendance':r.attendance,'outcome':r.outcome,'status_before':r.status_before,'state':db.get(ExtraClass,r.extra_class_id).state} for r in db.scalars(select(Enrollment))],
        'Fact_Submission':[{'submission_id':s.id,'student_id':s.student_id,'assignment_id':s.assignment_id,'status':s.status,'version_no':s.version_no,'submitted_at':s.submitted_at} for s in db.scalars(select(Submission))],
        'Fact_Report':[{'report_id':r.id,'student_id':r.student_id,'term_id':r.term_id,'released':r.released,'version':r.version} for r in db.scalars(select(Report))]
    }
    defaults=COLUMNS
    manifest={'created_at':now(),'source':'Synthetic data','data_quality':check,'tables':{}}
    for name,rows in tables.items():
        path=EXPORT/f'{name}.csv';fields=list(rows[0]) if rows else defaults[name]
        with path.open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
        manifest['tables'][name]={'rows':len(rows),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    (EXPORT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    return manifest
if __name__=='__main__':
    with Session() as db:print(json.dumps(export_data(db),indent=2))

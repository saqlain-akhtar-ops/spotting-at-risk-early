"""Deterministic synthetic sample; never represents actual student information."""
import random, json, os
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from .models import *
from .security import hash_password
from .status import indicators, RULE_VERSION

def seed(db):
    if db.scalar(select(func.count(User.id))): return
    credentials = []
    def user(name, email, role):
        password = os.getenv('DEMO_'+role.upper()+'_PASSWORD') or 'Demo-' + __import__('secrets').token_urlsafe(12)
        u = User(name=name, email=email, role=role, password_hash=hash_password(password))
        db.add(u); db.flush()
        credentials.append({'role': role, 'email': email, 'password': password})
        return u
    admin = user('Demo Administrator', 'admin@example.test', 'admin')
    ta = user('Advisor A', 'teacher.a@example.test', 'teacher')
    tb = user('Advisor B', 'teacher.b@example.test', 'teacher')
    stu = user('Student 001', 'student@example.test', 'student')
    par = user('Guardian 001', 'parent@example.test', 'parent')
    for i in range(1, 7): db.add(SchoolClass(id=i, name=f'Class {chr(64+i)}', advisor_id=ta.id if i <= 3 else tb.id))
    for i, name in enumerate(['Mathematics', 'Science', 'English'], 1): db.add(Subject(id=i, name=name))
    for i in range(1, 5): db.add(Term(id=i, name=f'Term {i}', academic_year='2026-27'))
    db.flush(); rng = random.Random(2026)
    for sid in range(1, 481):
        cid = (sid-1)//80 + 1
        db.add(Student(id=sid, name=f'Student {sid:03}', class_id=cid))
        db.flush()
        db.add(Access(user_id=ta.id if cid <= 3 else tb.id, student_id=sid))
        if sid == 1:
            db.add_all([Access(user_id=stu.id, student_id=sid), Access(user_id=par.id, student_id=sid)])
        db.add(Parent(student_id=sid, name=f'Guardian {sid:03}', email=f'guardian{sid:03}@example.test', primary=1, consent=0))
        kind = sid % 5
        for tid in range(1, 5):
            for sub in range(1, 4):
                # 5,760 possible rows, with 76 intentionally absent assessments.
                if sid >= 405 and tid == 1 and sub == 3: continue
                base = [52, 83 - tid*3, 77 + tid, 95, 63 + tid*.4][kind]
                noise = rng.uniform(-.3,.3) if kind == 4 else rng.uniform(-3,3)
                db.add(Performance(student_id=sid, subject_id=sub, term_id=tid, score=round(min(100, base+noise),2), attendance=round(rng.uniform(90,99) if kind==3 else rng.uniform(78,94),2)))
    db.add(Assignment(subject_id=1, teacher_id=ta.id, class_id=1, title='Mathematics practice — fractions', instructions='Upload a PDF, text file, PNG or JPEG (maximum 5 MB).', due_date=(datetime.now(timezone.utc)+timedelta(days=7)).isoformat()))
    db.add(ExtraClass(subject_id=1, teacher_id=ta.id, class_id=1, date='2026-10-12', start_time='16:00', end_time='17:00', room='Lab 2', topic='Mathematics foundations'))
    db.flush()
    db.add(Enrollment(extra_class_id=1, student_id=4, status_before='Slow Learner'))
    db.commit()
    for sid, info in indicators(db, list(db.scalars(select(Student.id)))).items():
        db.add(StudentStatus(student_id=sid, term_id=info['term_id'], status=info['status'], rule_version=RULE_VERSION, evidence=json.dumps(info)))
    db.commit()
    (DATA/'demo-credentials.json').write_text(json.dumps(credentials, indent=2), encoding='utf-8')

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    with Session() as db: seed(db)

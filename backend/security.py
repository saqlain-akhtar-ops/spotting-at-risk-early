import hashlib, secrets, hmac
from fastapi import HTTPException
from sqlalchemy import select
from .models import Access, Student, Audit
import json

def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 310000).hex()
    return f'pbkdf2_sha256$310000${salt}${digest}'
def verify_password(password, encoded):
    _, iterations, salt, digest = encoded.split('$')
    actual = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), int(iterations)).hex()
    return hmac.compare_digest(actual, digest)
def scope(db, user):
    if user.role == 'admin': return list(db.scalars(select(Student.id)))
    return list(db.scalars(select(Access.student_id).where(Access.user_id == user.id)))
def student_guard(db, user, sid):
    if sid not in scope(db, user): raise HTTPException(403, 'Student is outside your authorized scope')
    student = db.get(Student, sid)
    if not student: raise HTTPException(404, 'Student not found')
    return student
def staff(user):
    if user.role not in ('teacher', 'admin'): raise HTTPException(403, 'Staff access required')
def audit(db, user, action, entity, eid, details=None):
    db.add(Audit(user_id=user.id if user else None, action=action, entity=entity, entity_id=str(eid), details=json.dumps(details or {})))

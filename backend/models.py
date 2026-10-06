from datetime import datetime, timezone
from sqlalchemy import create_engine, event, String, Integer, Float, Text, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env.local', override=False)
DATA = Path(os.getenv('DATA_DIR', str(ROOT / 'data')))
DATA.mkdir(parents=True,exist_ok=True)
UPLOADS = DATA / 'uploads'
UPLOADS.mkdir(exist_ok=True)
def now():
    return datetime.now(timezone.utc).isoformat()
url = os.getenv('DATABASE_URL', f'sqlite:///{(DATA / "application.db").as_posix()}')
engine = create_engine(url, **({'connect_args': {'check_same_thread': False}} if url.startswith('sqlite') else {'pool_pre_ping': True}))
if url.startswith('sqlite'):
    @event.listens_for(engine, 'connect')
    def pragmas(conn, _):
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('PRAGMA busy_timeout=10000')
Session = sessionmaker(engine, expire_on_commit=False)
class Base(DeclarativeBase): pass
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    role: Mapped[str] = mapped_column(String(20))
    active: Mapped[int] = mapped_column(default=1)
    __table_args__ = (CheckConstraint("role IN ('admin','teacher','student','parent')",name='valid_user_role'),)
class Access(Base):
    __tablename__ = 'user_access'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'), index=True)
    __table_args__ = (UniqueConstraint('user_id', 'student_id'),)
class LoginSession(Base):
    __tablename__ = 'sessions'
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    csrf: Mapped[str] = mapped_column(String(64))
    expires: Mapped[float] = mapped_column(Float)
class SchoolClass(Base):
    __tablename__ = 'classes'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True)
    advisor_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
class Student(Base):
    __tablename__ = 'students'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    class_id: Mapped[int] = mapped_column(ForeignKey('classes.id'), index=True)
    academic_year: Mapped[str] = mapped_column(String(20), default='2026-27')
class Parent(Base):
    __tablename__ = 'parents'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'), index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254))
    phone: Mapped[str] = mapped_column(String(30), default='')
    relationship: Mapped[str] = mapped_column(String(40), default='Guardian')
    primary: Mapped[int] = mapped_column(default=0)
    consent: Mapped[int] = mapped_column(default=0)
    active: Mapped[int] = mapped_column(default=1)
class Subject(Base):
    __tablename__ = 'subjects'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
class Term(Base):
    __tablename__ = 'terms'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40))
    academic_year: Mapped[str] = mapped_column(String(20))
class Performance(Base):
    __tablename__ = 'performance'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'))
    term_id: Mapped[int] = mapped_column(ForeignKey('terms.id'))
    score: Mapped[float] = mapped_column(Float, nullable=True)
    attendance: Mapped[float] = mapped_column(Float)
    __table_args__ = (UniqueConstraint('student_id', 'subject_id', 'term_id'), CheckConstraint('score IS NULL OR (score >= 0 AND score <= 100)',name='score_range'), CheckConstraint('attendance >= 0 AND attendance <= 100',name='attendance_range'))
class StudentStatus(Base):
    __tablename__ = 'student_status'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'), index=True)
    term_id: Mapped[int] = mapped_column(ForeignKey('terms.id'))
    status: Mapped[str] = mapped_column(String(30))
    rule_version: Mapped[str] = mapped_column(String(40))
    evidence: Mapped[str] = mapped_column(Text)
    calculated_at: Mapped[str] = mapped_column(String(40), default=now)
    __table_args__ = (UniqueConstraint('student_id', 'term_id'),)
class ExtraClass(Base):
    __tablename__ = 'extra_classes'
    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'))
    teacher_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    class_id: Mapped[int] = mapped_column(ForeignKey('classes.id'))
    date: Mapped[str] = mapped_column(String(10))
    start_time: Mapped[str] = mapped_column(String(5))
    end_time: Mapped[str] = mapped_column(String(5))
    room: Mapped[str] = mapped_column(String(100))
    topic: Mapped[str] = mapped_column(String(250))
    state: Mapped[str] = mapped_column(String(20), default='SCHEDULED')
    objective: Mapped[str] = mapped_column(Text, default='')
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=True)
    created_at: Mapped[str] = mapped_column(String(40),default=now,nullable=True)
    updated_at: Mapped[str] = mapped_column(String(40),default=now,onupdate=now,nullable=True)
class Enrollment(Base):
    __tablename__ = 'extra_class_students'
    id: Mapped[int] = mapped_column(primary_key=True)
    extra_class_id: Mapped[int] = mapped_column(ForeignKey('extra_classes.id'))
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'), index=True)
    attendance: Mapped[str] = mapped_column(String(20), default='PENDING')
    outcome: Mapped[str] = mapped_column(Text, default='')
    status_before: Mapped[str] = mapped_column(String(30), default='')
    __table_args__ = (UniqueConstraint('extra_class_id', 'student_id'),)
class Assignment(Base):
    __tablename__ = 'assignments'
    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'))
    teacher_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    class_id: Mapped[int] = mapped_column(ForeignKey('classes.id'))
    title: Mapped[str] = mapped_column(String(200))
    due_date: Mapped[str] = mapped_column(String(40))
    instructions: Mapped[str] = mapped_column(Text, default='')
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'),nullable=True,index=True)
    created_at: Mapped[str] = mapped_column(String(40),default=now,nullable=True)
class Submission(Base):
    __tablename__ = 'submissions'
    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey('assignments.id'))
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'), index=True)
    original_filename: Mapped[str] = mapped_column(String(200))
    stored_filename: Mapped[str] = mapped_column(String(100), unique=True)
    mime_type: Mapped[str] = mapped_column(String(100))
    file_size: Mapped[int] = mapped_column(Integer)
    version_no: Mapped[int] = mapped_column(default=1)
    submitted_at: Mapped[str] = mapped_column(String(40), default=now)
    status: Mapped[str] = mapped_column(String(40), default='SUBMITTED')
    feedback: Mapped[str] = mapped_column(Text, default='')
    file_hash: Mapped[str] = mapped_column(String(64),nullable=True)
    marks: Mapped[float] = mapped_column(Float,nullable=True)
    reviewed_by: Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=True)
    reviewed_at: Mapped[str] = mapped_column(String(40),nullable=True)
class Report(Base):
    __tablename__ = 'progress_reports'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'), index=True)
    term_id: Mapped[int] = mapped_column(ForeignKey('terms.id'))
    version: Mapped[int] = mapped_column(default=1)
    generated_at: Mapped[str] = mapped_column(String(40), default=now)
    released: Mapped[int] = mapped_column(default=0)
    summary: Mapped[str] = mapped_column(Text)
    comments: Mapped[str] = mapped_column(Text, default='')
    follow_up: Mapped[str] = mapped_column(Text, default='')
class Notification(Base):
    __tablename__ = 'notifications'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'))
    parent_id: Mapped[int] = mapped_column(ForeignKey('parents.id'))
    template: Mapped[str] = mapped_column(String(40))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default='PREVIEW')
    attempts: Mapped[int] = mapped_column(default=0)
    error: Mapped[str] = mapped_column(String(200), default='')
    created_at: Mapped[str] = mapped_column(String(40), default=now)
    sent_at: Mapped[str] = mapped_column(String(40), nullable=True)
class Audit(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    action: Mapped[str] = mapped_column(String(60))
    entity: Mapped[str] = mapped_column(String(60))
    entity_id: Mapped[str] = mapped_column(String(60))
    details: Mapped[str] = mapped_column(Text, default='{}')
    timestamp: Mapped[str] = mapped_column(String(40), default=now)

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date, time
import re

class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True, allow_inf_nan=False)
class LoginInput(Strict):
    email: str = Field(max_length=254)
    password: str = Field(min_length=1, max_length=200)
class StudentInput(Strict):
    name: str = Field(min_length=1, max_length=100)
class ParentInput(Strict):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=254)
    phone: str = Field(default='', max_length=30)
    relationship: str = Field(default='Guardian', max_length=40)
    primary: bool = False
    consent: bool = False
    active: bool = True
    @field_validator('email')
    @classmethod
    def email_check(cls, v):
        if not re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+', v): raise ValueError('Invalid email address')
        return v.lower()
class ExtraInput(Strict):
    subject_id: int
    teacher_id: int
    class_id: int
    date: str
    start_time: str
    end_time: str
    room: str = Field(default='', max_length=100)
    topic: str = Field(min_length=1, max_length=250)
    objective: str = Field(default='',max_length=5000)
    @field_validator('date')
    @classmethod
    def valid_date(cls, v):
        date.fromisoformat(v); return v
    @field_validator('start_time', 'end_time')
    @classmethod
    def valid_time(cls, v):
        if not re.fullmatch(r'\d{2}:\d{2}', v): raise ValueError('Use HH:MM')
        time.fromisoformat(v); return v
class AssignmentInput(Strict):
    subject_id: int
    class_id: int
    title: str = Field(min_length=1, max_length=200)
    due_date: str
    instructions: str = Field(default='', max_length=5000)
    student_id: int | None = Field(default=None,gt=0)
    @field_validator('due_date')
    @classmethod
    def due(cls, v):
        d = datetime.fromisoformat(v.replace('Z', '+00:00'))
        if d.tzinfo is None: raise ValueError('Timezone is required')
        return d.isoformat()
class EnrollmentInput(Strict):
    student_ids: list[int] = Field(min_length=1, max_length=480)
class AttendanceInput(Strict):
    attendance: str = Field(pattern='^(PRESENT|ABSENT|LATE|PENDING)$')
    outcome: str = Field(default='', max_length=5000)
class ReviewInput(Strict):
    status: str = Field(pattern='^(UNDER_REVIEW|REVIEWED|RESUBMISSION_REQUESTED)$')
    feedback: str = Field(default='', max_length=5000)
    marks: float | None = Field(default=None,ge=0,le=100)
class StateInput(Strict):
    state: str = Field(pattern='^(SCHEDULED|COMPLETED|CANCELLED)$')
class ReportInput(Strict):
    term_id: int
    comments: str = Field(default='', max_length=5000)
    follow_up: str = Field(default='', max_length=5000)
class EmailInput(Strict):
    parent_id: int
    template: str = Field(pattern='^(progress_report|extra_class|assignment|follow_up)$')
class PerformanceInput(Strict):
    subject_id: int
    term_id: int
    score: float | None = Field(default=None, ge=0, le=100)
    attendance: float = Field(ge=0, le=100)

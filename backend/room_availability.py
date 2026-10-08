"""One overlap rule shared by availability previews and scheduling."""
from datetime import date, time
from fastapi import HTTPException
from sqlalchemy import select
from .models import ExtraClass

def normalize_room(value):
    return ' '.join(value.split()).casefold()

def overlapping_sessions(db, day, start, end):
    try:
        date.fromisoformat(day)
        time.fromisoformat(start)
        time.fromisoformat(end)
    except (ValueError, TypeError):
        raise HTTPException(422, 'Use a valid date and HH:MM times')
    if len(start) != 5 or len(end) != 5 or end <= start:
        raise HTTPException(422, 'End time must be after start time, using HH:MM')
    return list(db.scalars(select(ExtraClass).where(
        ExtraClass.date == day, ExtraClass.state != 'CANCELLED',
        ExtraClass.start_time < end, ExtraClass.end_time > start)))

def room_availability(db, day, start, end, room):
    key = normalize_room(room)
    if not key or len(room) > 100:
        raise HTTPException(422, 'Enter a room name, up to 100 characters')
    conflicts = [x for x in overlapping_sessions(db, day, start, end)
                 if normalize_room(x.room) == key]
    return {'room': ' '.join(room.split()), 'date': day,
            'start_time': start, 'end_time': end, 'available': not conflicts,
            'busy_slots': [{'start_time': x.start_time, 'end_time': x.end_time}
                           for x in conflicts],
            'note': 'Checks extra classes recorded in this project. Availability is rechecked when scheduling.'}

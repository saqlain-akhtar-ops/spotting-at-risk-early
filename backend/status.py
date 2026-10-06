"""Explainable prototype rules. Shared by API, reports and analytical export."""
from statistics import mean
from math import ceil
from sqlalchemy import select
from .models import Performance, Student, Subject, Term
RULE_VERSION = 'EW-Prototype-v1'
STATUSES = ['At Risk', 'Watch', 'On Track', 'Top Performer', 'Slow Learner']
def classify(current, prior, attendance, history, cutoff):
    if current is None:
        return 'Insufficient Data', ['MISSING_MARKS']
    delta = None if prior is None else current - prior
    if current < 60 or (delta is not None and delta < 0 and attendance < 75):
        return 'At Risk', ['SCORE_BELOW_60'] if current < 60 else ['DECLINING_SCORE', 'LOW_ATTENDANCE']
    if cutoff is not None and current >= cutoff and attendance >= 90:
        return 'Top Performer', ['TOP_DECILE_SCORE', 'EXEMPLARY_ATTENDANCE']
    if len(history) >= 3 and all(60 <= s < 70 for s in history[-3:]) and delta is not None and 0 <= delta <= 1 and attendance >= 75:
        return 'Slow Learner', ['PERSISTENT_60_69', 'LIMITED_IMPROVEMENT', 'ADEQUATE_ATTENDANCE']
    if delta is not None and delta < 0:
        return 'Watch', ['NEGATIVE_MOMENTUM']
    return 'On Track', ['STABLE_OR_IMPROVING']

def indicators(db, student_ids, term_id=None, subject_id=None):
    # Cohort cutoff is calculated across the institution, independent of viewer scope.
    rows = list(db.scalars(select(Performance)))
    latest = term_id or max((r.term_id for r in rows), default=0)
    grouped = {}
    for r in rows:
        if r.term_id <= latest and (subject_id is None or r.subject_id == subject_id):
            grouped.setdefault((r.student_id, r.term_id), []).append(r)
    expected = 1 if subject_id is not None else len(list(db.scalars(select(Subject.id))))
    averages = {key: mean(r.score for r in rs) for key, rs in grouped.items() if len(rs)==expected and all(r.score is not None for r in rs)}
    cohort = sorted(v for (sid, tid), v in averages.items() if tid == latest)
    cutoff = cohort[max(0, ceil(.9 * len(cohort)) - 1)] if cohort else None
    result = {}
    prior_terms = sorted(t for t in db.scalars(select(Term.id)) if t < latest)
    history_terms = (prior_terms + [latest])[-3:]
    for sid in student_ids:
        rs = grouped.get((sid, latest), [])
        current = averages.get((sid, latest))
        prior = averages.get((sid, prior_terms[-1])) if prior_terms else None
        history = [averages[(sid, t)] for t in history_terms if (sid, t) in averages]
        attendance = mean(r.attendance for r in rs) if rs else None
        status, reasons = classify(current, prior, attendance or 0, history, cutoff)
        result[sid] = dict(term_id=latest, current_average=round(current, 2) if current is not None else None,
                           prior_average=round(prior, 2) if prior is not None else None,
                           trend_delta=round(current-prior, 2) if current is not None and prior is not None else None,
                           attendance=round(attendance, 2) if attendance is not None else None,
                           status=status, reason_codes=reasons, rule_version=RULE_VERSION,
                           review_required=True, top_decile_cutoff=round(cutoff, 2) if cutoff is not None else None)
    return result

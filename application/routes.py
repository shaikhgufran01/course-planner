from datetime import date

from flask import Blueprint, jsonify, request

from . import db, termcal
from .termcal import term_range
from .models import Course, Plan, PlanItem, Student

bp = Blueprint("api", __name__, url_prefix="/api")

MAX_COURSES_PER_TERM = 4
MAX_TERMS = 14
LEVEL_ORDER = {"degree": 0, "l4_degree": 1, "l5_degree": 2, "gate": 3}
LEVEL_LABELS = {"degree": "Degree", "l4_degree": "L4 Degree", "l5_degree": "L5 Degree", "gate": "GATE"}


# ---------- anonymous per-browser identity (no login) ----------
def get_student() -> Student:
    cid = (request.headers.get("X-Client-Id") or "").strip()
    if not 8 <= len(cid) <= 64:
        from werkzeug.exceptions import BadRequest
        raise BadRequest("Missing or invalid X-Client-Id header")
    s = Student.query.filter_by(client_id=cid).first()
    if not s:
        s = Student(client_id=cid, start_index=termcal.term_index(date.today()))
        db.session.add(s)
        db.session.commit()
    elif s.total_credits != 142:
        s.total_credits = 142
        db.session.commit()
    return s


@bp.errorhandler(400)
def bad_request(e):
    return jsonify(detail=str(e.description)), 400


# ---------- helpers ----------
def course_out(c: Course, done: set, planned: set = frozenset()):
    return {
        "id": c.id, "name": c.name, "credits": c.credits, "level": c.level, "kind": c.kind,
        "course_type": c.course_type, "fee": c.fee, "new_fee": c.new_fee,
        "corequisite": c.corequisite,
        "prerequisites": [p.id for p in c.prerequisites],
        "prereqs_met": all(p.id in done for p in c.prerequisites),
        "completed": c.id in done, "planned": c.id in planned,
    }


def level_totals(s: Student):
    done = {c.id for c in s.completed}
    out = {}
    for lvl in LEVEL_ORDER:
        rows = Course.query.filter_by(level=lvl).all()
        out[lvl] = {
            "label": LEVEL_LABELS[lvl],
            "total_credits": sum(c.credits for c in rows),
            "completed_credits": sum(c.credits for c in rows if c.id in done),
        }
    return out


def progress_of(s: Student):
    done = {c.id for c in s.completed}
    completed = s.completed_credits + sum(c.credits for c in s.completed)
    planned_courses = {i.course_id: i.course for p in s.plans for i in p.items if i.course_id not in done}
    return {
        "completed_credits": completed,
        "planned_credits": sum(c.credits for c in planned_courses.values()),
        "remaining_credits": s.total_credits - completed,
        "total_credits": s.total_credits,
        "completed_courses": len(done),
        "percent": round(completed / s.total_credits * 100, 1) if s.total_credits else 0,
    }


# ---------- student ----------
@bp.get("/student")
def student():
    s = get_student()
    cur = termcal.term_index(date.today())
    return jsonify({
        "name": s.name, "program": s.program, "status": s.status,
        "level": s.current_level,
        "current_term": termcal.label(cur), "current_term_code": termcal.code(cur),
        "next_term": termcal.label(cur + 1),
        "upcoming_terms": termcal.upcoming(MAX_TERMS),
        "all_terms": term_range(),
        "start_term": termcal.code(s.start_index),
        "total_terms": max(cur - s.start_index + 1, 1),
        "max_courses_per_term": MAX_COURSES_PER_TERM,
        **progress_of(s),
    })


@bp.put("/student")
def update_student():
    s = get_student()
    body = request.get_json(force=True) or {}
    name = (body.get("name") or "").strip()
    if not name:
        return jsonify(detail="name is required"), 422
    s.name = name[:60]
    db.session.commit()
    return jsonify(name=s.name)


# ---------- courses ----------
@bp.get("/courses")
def courses():
    s = get_student()
    done = {c.id for c in s.completed}
    planned = {i.course_id for p in s.plans for i in p.items} - done
    rows = sorted(Course.query.all(), key=lambda c: (LEVEL_ORDER.get(c.level, 99), c.kind, c.id))
    return jsonify([course_out(c, done, planned) for c in rows])


@bp.get("/recommendations")
def recommendations():
    s = get_student()
    done = {c.id for c in s.completed}
    eligible = [c for c in Course.query.all()
                if c.id not in done and all(p.id in done for p in c.prerequisites)]
    eligible.sort(key=lambda c: (LEVEL_ORDER.get(c.level, 99), c.kind, c.id))
    return jsonify([course_out(c, done) for c in eligible[: MAX_COURSES_PER_TERM * 2]])


@bp.get("/progress")
def progress():
    s = get_student()
    return jsonify({**progress_of(s), "by_level": level_totals(s)})


@bp.post("/courses/<course_id>/complete")
def mark_complete(course_id):
    s = get_student()
    c = Course.query.get(course_id)
    if not c:
        return jsonify(detail="Course not found"), 404
    if c not in s.completed:
        s.completed.append(c)
        db.session.commit()
    return jsonify(progress_of(s))


@bp.delete("/courses/<course_id>/complete")
def unmark_complete(course_id):
    s = get_student()
    c = Course.query.get(course_id)
    if c and c in s.completed:
        s.completed.remove(c)
        db.session.commit()
    return jsonify(progress_of(s))


# ---------- plans (multi-term) ----------
def validate_terms(s: Student, terms: list[list[str]]):
    errors = []
    if not terms:
        return {}, ["Add at least one term."]
    if len(terms) > MAX_TERMS:
        errors.append(f"A plan can have at most {MAX_TERMS} terms.")
    ids = {i for t in terms for i in t}
    rows = {c.id: c for c in Course.query.filter(Course.id.in_(ids)).all()}
    done = {c.id for c in s.completed}
    for n, t in enumerate(terms, 1):
        if not t:
            errors.append(f"Term {n} has no courses.")
            continue
        if len(t) > MAX_COURSES_PER_TERM:
            errors.append(f"Term {n}: at most {MAX_COURSES_PER_TERM} courses per term.")
        if len(set(t)) != len(t):
            errors.append(f"Term {n}: duplicate courses.")
        for cid in t:
            c = rows.get(cid)
            if not c:
                errors.append(f"Unknown course {cid}.")
            elif cid in done:
                errors.append(f"Term {n}: {cid} is already completed or planned in an earlier term.")
            else:
                missing = [p.id for p in c.prerequisites if p.id not in done]
                if missing:
                    errors.append(f"Term {n}: {cid} requires {', '.join(missing)} in an earlier term.")
        done |= set(t)
    return rows, errors


def plan_out(p: Plan):
    groups: dict[int, dict] = {}
    for it in p.items:
        g = groups.setdefault(it.term_index, {"label": it.term_label, "courses": []})
        g["courses"].append({"id": it.course.id, "name": it.course.name,
                             "credits": it.course.credits, "kind": it.course.kind})
    terms = []
    for idx in sorted(groups):
        g = groups[idx]
        g["total_credits"] = sum(c["credits"] for c in g["courses"])
        terms.append(g)
    return {
        "id": p.id, "name": p.name, "created_at": p.created_at.isoformat(),
        "total_credits": sum(t["total_credits"] for t in terms),
        "course_count": sum(len(t["courses"]) for t in terms),
        "terms": terms,
    }


@bp.post("/plans/validate")
def validate():
    s = get_student()
    body = request.get_json(force=True) or {}
    _, errors = validate_terms(s, body.get("terms") or [])
    return jsonify(valid=not errors, errors=errors)


@bp.get("/plans")
def list_plans():
    s = get_student()
    return jsonify([plan_out(p) for p in sorted(s.plans, key=lambda p: p.created_at, reverse=True)])


@bp.post("/plans")
def create_plan():
    s = get_student()
    body = request.get_json(force=True) or {}
    name = (body.get("name") or "").strip()
    terms = body.get("terms") or []
    term_labels = body.get("term_labels") or []
    if not name:
        return jsonify(detail="name is required"), 422
    rows, errors = validate_terms(s, terms)
    if errors:
        return jsonify(detail=errors), 422
    # Use client-supplied labels when available, fall back to upcoming()
    fallback_labels = termcal.upcoming(max(MAX_TERMS, len(terms)))
    if len(term_labels) < len(terms):
        term_labels = fallback_labels
    plan = Plan(student_id=s.id, name=name[:80])
    db.session.add(plan)
    db.session.flush()
    for ti, t in enumerate(terms):
        lbl = term_labels[ti] if ti < len(term_labels) else fallback_labels[ti]
        idx = termcal.label_to_index(lbl) or ti
        for pos, cid in enumerate(t):
            db.session.add(PlanItem(plan_id=plan.id, course_id=cid, term_index=idx,
                                     term_label=lbl, position=pos))
    db.session.commit()
    return jsonify(plan_out(plan)), 201


@bp.delete("/plans/<int:plan_id>")
def delete_plan(plan_id):
    s = get_student()
    plan = Plan.query.get(plan_id)
    if not plan or plan.student_id != s.id:
        return jsonify(detail="Plan not found"), 404
    db.session.delete(plan)
    db.session.commit()
    return "", 204


@bp.get("/plans/<int:plan_id>")
def get_plan(plan_id):
    s = get_student()
    plan = Plan.query.get(plan_id)
    if not plan or plan.student_id != s.id:
        return jsonify(detail="Plan not found"), 404
    return jsonify(plan_out(plan))


@bp.put("/plans/<int:plan_id>")
def update_plan(plan_id):
    s = get_student()
    plan = Plan.query.get(plan_id)
    if not plan or plan.student_id != s.id:
        return jsonify(detail="Plan not found"), 404
    body = request.get_json(force=True) or {}
    name = (body.get("name") or "").strip()
    terms = body.get("terms") or []
    term_labels = body.get("term_labels") or []
    if not name:
        return jsonify(detail="name is required"), 422
    rows, errors = validate_terms(s, terms)
    if errors:
        return jsonify(detail=errors), 422
    # Update plan name
    plan.name = name[:80]
    # Remove old items
    for item in list(plan.items):
        db.session.delete(item)
    db.session.flush()
    # Re-insert new items
    fallback_labels = termcal.upcoming(max(MAX_TERMS, len(terms)))
    if len(term_labels) < len(terms):
        term_labels = fallback_labels
    for ti, t in enumerate(terms):
        lbl = term_labels[ti] if ti < len(term_labels) else fallback_labels[ti]
        idx = termcal.label_to_index(lbl) or ti
        for pos, cid in enumerate(t):
            db.session.add(PlanItem(plan_id=plan.id, course_id=cid, term_index=idx,
                                     term_label=lbl, position=pos))
    db.session.commit()
    return jsonify(plan_out(plan))


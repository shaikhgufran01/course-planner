from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from . import models, auth
from .database import engine, get_db
from .seed import seed
from fastapi.security import OAuth2PasswordRequestForm

MAX_COURSES_PER_TERM = 4
LEVEL_ORDER = {"foundation": 0, "diploma": 1, "degree": 2}

models.Base.metadata.create_all(engine)
seed()

app = FastAPI(title="Course Planner API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Student).filter(models.Student.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


def course_out(c: models.Course, done_ids: set, planned_ids: set = frozenset()):
    return {
        "id": c.id, "name": c.name, "credits": c.credits,
        "level": c.level, "kind": c.kind,
        "prerequisites": [p.id for p in c.prerequisites],
        "prereqs_met": all(p.id in done_ids for p in c.prerequisites),
        "completed": c.id in done_ids,
        "planned": c.id in planned_ids,
    }


def planned_ids_of(s: models.Student, done_ids: set) -> set:
    return {c.id for p in s.plans for c in p.courses} - done_ids


def progress_of(s: models.Student):
    done_ids = {c.id for c in s.completed}
    completed = sum(c.credits for c in s.completed)
    planned_ids = planned_ids_of(s, done_ids)
    planned = sum(c.credits for p in s.plans for c in p.courses if c.id in planned_ids)
    return {
        "completed_credits": completed,
        "planned_credits": planned,
        "remaining_credits": s.total_credits - completed,
        "total_credits": s.total_credits,
        "completed_courses": len(done_ids),
        "percent": round(completed / s.total_credits * 100, 1),
    }


@app.get("/api/student")
def student(db: Session = Depends(get_db), s: models.Student = Depends(auth.get_current_user)):
    return {
        "id": s.id, "name": s.name, "program": s.program, "status": s.status,
        "level": s.level, "current_term": s.current_term, "next_term": s.next_term,
        "start_term": s.start_term, "total_terms": s.total_terms,
        "max_courses_per_term": MAX_COURSES_PER_TERM,
        **progress_of(s),
    }


@app.get("/api/courses")
def courses(level: str | None = None, db: Session = Depends(get_db), s: models.Student = Depends(auth.get_current_user)):
    done = {c.id for c in s.completed}
    planned = planned_ids_of(s, done)
    q = db.query(models.Course)
    if level:
        q = q.filter(models.Course.level == level)
    rows = sorted(q.all(), key=lambda c: (LEVEL_ORDER[c.level], c.kind, c.id))
    return [course_out(c, done, planned) for c in rows]


@app.get("/api/recommendations")
def recommendations(db: Session = Depends(get_db), s: models.Student = Depends(auth.get_current_user)):
    done = {c.id for c in s.completed}
    eligible = [
        c for c in db.query(models.Course).all()
        if c.id not in done and all(p.id in done for p in c.prerequisites)
    ]
    eligible.sort(key=lambda c: (LEVEL_ORDER[c.level], c.kind, c.id))
    return [course_out(c, done) for c in eligible[:MAX_COURSES_PER_TERM * 2]]


@app.get("/api/progress")
def progress(db: Session = Depends(get_db), s: models.Student = Depends(auth.get_current_user)):
    out = progress_of(s)
    by_level = {}
    for lvl in LEVEL_ORDER:
        courses_l = db.query(models.Course).filter(models.Course.level == lvl).all()
        by_level[lvl] = {
            "total_credits": sum(c.credits for c in courses_l),
            "completed_credits": sum(c.credits for c in s.completed if c.level == lvl),
        }
    return {**out, "by_level": by_level,
            "completed": [course_out(c, {c.id for c in s.completed}) for c in s.completed]}


class ValidateIn(BaseModel):
    course_ids: list[str]


def validate_selection(db: Session, s: models.Student, ids: list[str]):
    errors = []
    if len(set(ids)) != len(ids):
        errors.append("Duplicate courses selected.")
    if not ids:
        errors.append("Select at least one course.")
    if len(ids) > MAX_COURSES_PER_TERM:
        errors.append(f"You can take at most {MAX_COURSES_PER_TERM} courses per term.")
    done = {c.id for c in s.completed}
    rows = db.query(models.Course).filter(models.Course.id.in_(ids)).all()
    if len(rows) != len(set(ids)):
        errors.append("One or more courses do not exist.")
    for c in rows:
        if c.id in done:
            errors.append(f"{c.id} is already completed.")
        missing = [p.id for p in c.prerequisites if p.id not in done]
        if missing:
            errors.append(f"{c.id} requires: {', '.join(missing)}.")
    return rows, errors


@app.post("/api/plans/validate")
def validate(body: ValidateIn, db: Session = Depends(get_db), s: models.Student = Depends(auth.get_current_user)):
    _, errors = validate_selection(db, s, body.course_ids)
    return {"valid": not errors, "errors": errors}


class PlanIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    course_ids: list[str]


def plan_out(p: models.Plan):
    return {
        "id": p.id, "name": p.name, "term": p.term,
        "created_at": p.created_at.isoformat(),
        "total_credits": sum(c.credits for c in p.courses),
        "courses": [{"id": c.id, "name": c.name, "credits": c.credits, "kind": c.kind}
                    for c in p.courses],
    }


@app.get("/api/plans")
def list_plans(db: Session = Depends(get_db), s: models.Student = Depends(auth.get_current_user)):
    return [plan_out(p) for p in sorted(s.plans, key=lambda p: p.created_at, reverse=True)]


@app.post("/api/plans", status_code=201)
def create_plan(body: PlanIn, db: Session = Depends(get_db), s: models.Student = Depends(auth.get_current_user)):
    rows, errors = validate_selection(db, s, body.course_ids)
    if errors:
        raise HTTPException(status_code=422, detail=errors)
    plan = models.Plan(student_id=s.id, name=body.name, term=s.next_term, courses=rows)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan_out(plan)


@app.delete("/api/plans/{plan_id}", status_code=204)
def delete_plan(plan_id: int, db: Session = Depends(get_db), s: models.Student = Depends(auth.get_current_user)):
    plan = db.get(models.Plan, plan_id)
    if not plan or plan.student_id != s.id:
        raise HTTPException(404, "Plan not found")
    db.delete(plan)
    db.commit()


@app.post("/api/courses/{course_id}/complete")
def mark_complete(course_id: str, db: Session = Depends(get_db), s: models.Student = Depends(auth.get_current_user)):
    """Mark a course completed (used by the Credit Progress Tracker)."""
    c = db.get(models.Course, course_id)
    if not c:
        raise HTTPException(404, "Course not found")
    if c not in s.completed:
        s.completed.append(c)
        db.commit()
    return progress_of(s)


@app.delete("/api/courses/{course_id}/complete")
def unmark_complete(course_id: str, db: Session = Depends(get_db), s: models.Student = Depends(auth.get_current_user)):
    c = db.get(models.Course, course_id)
    if c and c in s.completed:
        s.completed.remove(c)
        db.commit()
    return progress_of(s)

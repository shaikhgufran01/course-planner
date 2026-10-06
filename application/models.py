from datetime import datetime
from . import db

prereqs = db.Table(
    "prereqs",
    db.Column("course_id", db.String, db.ForeignKey("courses.id"), primary_key=True),
    db.Column("prereq_id", db.String, db.ForeignKey("courses.id"), primary_key=True),
)

completed_courses = db.Table(
    "completed_courses",
    db.Column("student_id", db.Integer, db.ForeignKey("students.id"), primary_key=True),
    db.Column("course_id", db.String, db.ForeignKey("courses.id"), primary_key=True),
)


class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    credits = db.Column(db.Integer, default=4)
    level = db.Column(db.String, nullable=False)        # degree | l4_degree | l5_degree | gate
    kind = db.Column(db.String, default="theory")        # theory | project | exam
    course_type = db.Column(db.String, default="")       # Core_BP, BD, BP, HM, SE, etc.
    fee = db.Column(db.Integer, default=10000)
    new_fee = db.Column(db.Integer, default=12000)
    corequisite = db.Column(db.String, default="")       # corequisite course id
    prerequisites = db.relationship(
        "Course", secondary=prereqs,
        primaryjoin=id == prereqs.c.course_id,
        secondaryjoin=id == prereqs.c.prereq_id,
    )


class Student(db.Model):
    """One row per browser (anonymous, identified by a random client_id)."""
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String, unique=True, index=True, nullable=False)
    name = db.Column(db.String, default="Student")
    program = db.Column(db.String, default="BS in Data Science and Applications")
    status = db.Column(db.String, default="Active")
    start_index = db.Column(db.Integer, nullable=False)
    total_credits = db.Column(db.Integer, default=142)
    completed_credits = db.Column(db.Integer, default=70)
    current_level = db.Column(db.String, default="degree")
    completed = db.relationship("Course", secondary=completed_courses)
    plans = db.relationship("Plan", backref="student", cascade="all, delete-orphan")


class Plan(db.Model):
    __tablename__ = "plans"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship(
        "PlanItem", cascade="all, delete-orphan",
        order_by="(PlanItem.term_index, PlanItem.position)",
    )


class PlanItem(db.Model):
    __tablename__ = "plan_items"
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"))
    course_id = db.Column(db.String, db.ForeignKey("courses.id"))
    term_index = db.Column(db.Integer, nullable=False)
    term_label = db.Column(db.String, nullable=False)
    position = db.Column(db.Integer, default=0)
    course = db.relationship("Course")

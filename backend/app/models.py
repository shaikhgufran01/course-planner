from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Table, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base

prereqs = Table(
    "prereqs", Base.metadata,
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
    Column("prereq_id", ForeignKey("courses.id"), primary_key=True),
)

plan_courses = Table(
    "plan_courses", Base.metadata,
    Column("plan_id", ForeignKey("plans.id"), primary_key=True),
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
)

completed_courses = Table(
    "completed_courses", Base.metadata,
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
)


class Course(Base):
    __tablename__ = "courses"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    credits: Mapped[int] = mapped_column(Integer, default=4)
    level: Mapped[str] = mapped_column(String)  # foundation | diploma | degree
    kind: Mapped[str] = mapped_column(String, default="theory")  # theory | project
    prerequisites = relationship(
        "Course", secondary=prereqs,
        primaryjoin=id == prereqs.c.course_id,
        secondaryjoin=id == prereqs.c.prereq_id,
    )


class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    program: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="Active")
    level: Mapped[str] = mapped_column(String, default="foundation")
    current_term: Mapped[str] = mapped_column(String)
    next_term: Mapped[str] = mapped_column(String)
    start_term: Mapped[str] = mapped_column(String)
    total_terms: Mapped[int] = mapped_column(Integer, default=1)
    total_credits: Mapped[int] = mapped_column(Integer, default=142)
    completed = relationship("Course", secondary=completed_courses)
    plans = relationship("Plan", back_populates="student", cascade="all, delete-orphan")


class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    name: Mapped[str] = mapped_column(String)
    term: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    student = relationship("Student", back_populates="plans")
    courses = relationship("Course", secondary=plan_courses)

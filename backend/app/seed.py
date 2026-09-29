from .models import Course, Student
from .database import SessionLocal
from .auth import get_password_hash

# (id, name, credits, level, kind, [prereq ids])
COURSES = [
    ("MA1001", "Mathematics for Data Science I", 4, "foundation", "theory", []),
    ("MA1002", "Statistics for Data Science I", 4, "foundation", "theory", []),
    ("CS1001", "Computational Thinking", 4, "foundation", "theory", []),
    ("HS1001", "English I", 4, "foundation", "theory", []),
    ("MA1003", "Mathematics for Data Science II", 4, "foundation", "theory", ["MA1001"]),
    ("MA1004", "Statistics for Data Science II", 4, "foundation", "theory", ["MA1002"]),
    ("CS1002", "Programming in Python", 4, "foundation", "theory", []),
    ("HS1002", "English II", 4, "foundation", "theory", ["HS1001"]),
    ("CS2001", "Database Management Systems", 4, "diploma", "theory", ["CS1002"]),
    ("CS2002", "Programming, Data Structures and Algorithms using Python", 4, "diploma", "theory", ["CS1002"]),
    ("CS2003", "Modern Application Development I", 4, "diploma", "theory", ["CS1002"]),
    ("CS2004", "Modern Application Development II", 4, "diploma", "theory", ["CS2003"]),
    ("CS2005", "Machine Learning Foundations", 4, "diploma", "theory", ["MA1003", "MA1004"]),
    ("CS2006", "Business Data Management", 4, "diploma", "theory", ["MA1004"]),
    ("CS2007", "Machine Learning Practice", 4, "diploma", "theory", ["CS2005"]),
    ("CS2008", "Tools in Data Science", 3, "diploma", "theory", ["CS1002"]),
    ("CS2P01", "Software Engineering Project", 2, "diploma", "project", ["CS2003"]),
    ("CS3001", "Deep Learning", 4, "degree", "theory", ["CS2005"]),
    ("CS3002", "Large Language Models", 4, "degree", "theory", ["CS3001"]),
    ("CS3P01", "Capstone Project", 4, "degree", "project", ["CS2007"]),
]


def seed():
    db = SessionLocal()
    try:
        if db.query(Course).count():
            return
        by_id = {}
        for cid, name, cr, level, kind, _ in COURSES:
            c = Course(id=cid, name=name, credits=cr, level=level, kind=kind)
            by_id[cid] = c
            db.add(c)
        for cid, *_, pre in COURSES:
            by_id[cid].prerequisites = [by_id[p] for p in pre]
        s = Student(
            email="demo@example.com",
            password_hash=get_password_hash("password123"),
            name="Demo Student", program="BS in Data Science and Applications",
            current_term="September 2026", next_term="January 2027",
            start_term="F3-2026", total_terms=1, total_credits=142,
        )
        s.completed = [by_id["HS1001"]]
        db.add(s)
        db.commit()
    finally:
        db.close()

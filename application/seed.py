from . import db
from .models import Course

# (id, level, name, course_type, prereq_ids, corequisite, credits, fee, new_fee, kind)
COURSES = [
    # ── DEGREE level ──────────────────────────────────────────────────
    ("BSCS3001", "degree", "Software Engineering",                        "Core_BP", [],            "",         4, 10000, 12000, "theory"),
    ("BSCS3002", "degree", "Software Testing",                            "Core_BP", [],            "",         4, 10000, 12000, "theory"),
    ("BSCS3003", "degree", "AI: Search Methods for Problem Solving",      "Core_BD", [],            "",         4, 10000, 12000, "theory"),
    ("BSCS3004", "degree", "Deep Learning",                               "Core_BD", [],            "",         4, 10000, 12000, "theory"),
    ("BSGN3001", "degree", "Strategies for Professional Growth",          "Core_HM", [],            "",         4, 10000, 12000, "theory"),
    ("BSCS3005", "degree", "Programming in C",                            "BP",      [],            "",         4, 10000, 12000, "theory"),
    ("BSCS3031", "degree", "Computer Systems Design",                     "BP",      [],            "BSCS3005", 4, 10000, 12000, "theory"),
    ("BSCS3021", "degree", "Theory of Computation",                       "BP",      [],            "",         4, 10000, 12000, "theory"),
    ("BSMA3001", "degree", "Discrete Mathematics",                        "BP",      [],            "",         4, 10000, 12000, "theory"),
    ("BSMA2001", "degree", "Mathematical Thinking",                       "SE",      [],            "",         4, 10000, 12000, "theory"),
    ("BSMA3012", "degree", "Linear Statistical Models",                   "SE",      [],            "",         4, 10000, 12000, "theory"),
    ("BSMA3014", "degree", "Statistical Computing",                       "SE",      [],            "",         4, 10000, 12000, "theory"),
    ("BSMS3002", "degree", "Market Research",                             "HM",      [],            "",         4, 10000, 12000, "theory"),
    ("BSMS3033", "degree", "Managerial Economics",                        "HM",      [],            "",         4, 10000, 12000, "theory"),
    ("BSMS3034", "degree", "Corporate Finance",                           "HM",      [],            "",         4, 10000, 12000, "theory"),
    ("EE5102",   "degree", "Digital IC Design",                           "SE",      [],            "",         4, 10000, 12000, "theory"),
    ("EE2105",   "degree", "Electronic Testing and Measurement",          "SE",      [],            "",         4, 10000, 12000, "theory"),
    ("EE3106",   "degree", "Semiconductor Devices and VLSI Technology",   "SE",      [],            "",         4, 10000, 12000, "theory"),
    ("EE5101",   "degree", "Internet of Things (IoT)",                    "",        [],            "",         4, 10000, 12000, "theory"),
    ("EE4103",   "degree", "Communication Systems",                       "SE",      [],            "",         4, 10000, 12000, "theory"),
    ("EE2103",   "degree", "Digital System Design",                       "SE",      [],            "",         4, 10000, 12000, "theory"),
    ("EE2106",   "degree", "Computer Organisation",                       "SE",      [],            "",         4, 10000, 12000, "theory"),
    ("BSMA3015", "degree", "Linear Model with Applications",             "SE",      [],            "",         4, 10000, 12000, "theory"),

    # ── L4 DEGREE level ───────────────────────────────────────────────
    ("BSBT4001", "l4_degree", "Algorithmic Thinking in Bioinformatics",                "BD/BP", [],            "",         4, 20000, 20000, "theory"),
    ("BSBT4002", "l4_degree", "Big Data and Biological Networks",                      "BD/BP", [],            "",         4, 20000, 20000, "theory"),
    ("BSCS4001", "l4_degree", "Data Visualization Design",                             "BD",    [],            "",         4, 20000, 20000, "theory"),
    ("BSEE4001", "l4_degree", "Speech Technology",                                     "BD",    [],            "",         4, 20000, 20000, "theory"),
    ("BSMS4002", "l4_degree", "Design Thinking for Data-Driven App Development",       "HM/BP", [],            "",         4, 20000, 20000, "theory"),
    ("BSMS4001", "l4_degree", "Industry 4.0",                                          "HM/BD", [],            "",         4, 20000, 20000, "theory"),
    ("BSMS4003", "l4_degree", "Financial Forensics",                                   "HM/BD", [],            "",         4, 20000, 20000, "theory"),
    ("BSCS4021", "l4_degree", "Advanced Algorithms",                                   "BP",    [],            "",         4, 20000, 20000, "theory"),
    ("BSCS4022", "l4_degree", "Operating Systems",                                     "BP",    ["BSCS3031"],  "",         4, 20000, 20000, "theory"),
    ("BSCS4024", "l4_degree", "Computer Networks",                                     "BP",    ["BSCS3005"],  "",         4, 20000, 20000, "theory"),
    ("BSCS4003", "l4_degree", "Privacy & Security in Online Social Media",             "BD/BP", [],            "",         4, 20000, 20000, "theory"),
    ("BSMS4023", "l4_degree", "Game Theory and Strategy",                              "HM/BD", [],            "",         4, 20000, 20000, "theory"),
    ("BSCS4032", "l4_degree", "Compiler Design",                                       "BP",    ["BSCS3005"],  "",         4, 20000, 20000, "theory"),
    ("BSCS4010", "l4_degree", "Application Development Lab",                           "BP",    [],            "",         4, 20000, 20000, "project"),
    ("BSDA4001", "l4_degree", "Data Science and AI Lab",                               "BD",    ["BSCS3004"],  "",         4, 20000, 20000, "project"),

    # ── L5 DEGREE level ───────────────────────────────────────────────
    ("BSDA5001", "l5_degree", "Introduction to Big Data",                              "BD/BP", [],            "",         4, 20000, 20000, "theory"),
    ("BSDA5005", "l5_degree", "Introduction to Natural Language Processing (i-NLP)",   "BD",    [],            "",         4, 20000, 20000, "theory"),
    ("BSDA5006", "l5_degree", "Deep Learning for Computer Vision",                     "BD",    [],            "",         4, 20000, 20000, "theory"),
    ("BSDA5004", "l5_degree", "Large Language Models",                                 "BD",    ["BSCS3004"],  "",         4, 20000, 20000, "theory"),
    ("BSDA5007", "l5_degree", "Reinforcement Learning",                                "BD",    [],            "BSCS3004", 4, 20000, 20000, "theory"),
    ("BSDA5014", "l5_degree", "ML Ops",                                                "BP",    [],            "",         4, 20000, 20000, "theory"),
    ("BSDA5002", "l5_degree", "Mathematical Foundations of Generative AI",             "BD/BP", [],            "",         4, 20000, 20000, "theory"),
    ("BSDA5003", "l5_degree", "Algorithms for Data Science",                           "BD/BP", [],            "",         4, 20000, 20000, "theory"),
    ("BSDA5013", "l5_degree", "Deep Learning Practice",                                "BD/BP", ["BSCS3004"],  "",         4, 20000, 20000, "theory"),
    ("BSDA6004", "l5_degree", "Sequential Decision Making",                            "BD",    [],            "",         4, 20000, 20000, "theory"),

    # ── GATE (Comprehensive Exams) ────────────────────────────────────
    ("BSDA4002", "gate", "Comprehensive Exam - Data Science & Artificial Intelligence", "BD", [],  "",  2, 10000, 10000, "exam"),
    ("BSCS4009", "gate", "Comprehensive Exam - Computer Science & Information Technology", "BP", [], "", 2, 10000, 10000, "exam"),
]


def seed():
    if Course.query.count():
        return
    by_id = {}
    for cid, level, name, ctype, _, coreq, cr, fee, new_fee, kind in COURSES:
        by_id[cid] = Course(
            id=cid, name=name, credits=cr, level=level, kind=kind,
            course_type=ctype, fee=fee, new_fee=new_fee, corequisite=coreq,
        )
        db.session.add(by_id[cid])
    # Set prerequisites (only for courses whose prereqs are in the catalogue)
    for cid, _, _, _, pre, *_ in COURSES:
        by_id[cid].prerequisites = [by_id[p] for p in pre if p in by_id]
    db.session.commit()

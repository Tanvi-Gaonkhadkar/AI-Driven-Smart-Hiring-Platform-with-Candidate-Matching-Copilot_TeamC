import sqlite3
import random
from datetime import date, timedelta

DB_NAME = "database/recruitment.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# ==========================================================
# ONLY NEW CANDIDATES
# Existing candidates are preserved:
# Rahul Sharma
# Sneha Patil
# Aditi Joshi
# Rohan Shah
# ==========================================================

NEW_CANDIDATES = [

# ---------------- Applied ----------------

{
    "name":"Aarav Mehta",
    "email":"aarav.mehta@gmail.com",
    "phone":"9876500001",
    "role":"AI Engineer",
    "experience":"Fresher",
    "skills":"Python, Machine Learning, SQL",
    "resume":"uploads/Aarav_Mehta_Resume.pdf",
    "candidate_status":"Applied",
    "round_name":"Applied",
    "interview_status":"Applied"
},

{
    "name":"Priya Nair",
    "email":"priya.nair@gmail.com",
    "phone":"9876500002",
    "role":"AI Engineer",
    "experience":"1 Year",
    "skills":"Python, NLP, LangChain",
    "resume":"uploads/Priya_Nair.pdf",
    "candidate_status":"Applied",
    "round_name":"Applied",
    "interview_status":"Applied"
},

# ---------------- AI Reviewed ----------------

{
    "name":"Aman Verma",
    "email":"aman.verma@gmail.com",
    "phone":"9876500003",
    "role":"AI Engineer",
    "experience":"2 Years",
    "skills":"YOLOv8, OpenCV, Python",
    "resume":"uploads/Aman_Verma.pdf",
    "candidate_status":"AI Reviewed",
    "round_name":"AI Reviewed",
    "interview_status":"Under AI Review"
},

{
    "name":"Neha Kulkarni",
    "email":"neha.k@gmail.com",
    "phone":"9876500004",
    "role":"AI Engineer",
    "experience":"2 Years",
    "skills":"Machine Learning, Pandas, SQL",
    "resume":"uploads/Neha_Kulkarni.pdf",
    "candidate_status":"AI Reviewed",
    "round_name":"AI Reviewed",
    "interview_status":"Under AI Review"
},

# ---------------- Shortlisted ----------------

{
    "name":"Siddharth Kulkarni",
    "email":"siddharth@gmail.com",
    "phone":"9876500005",
    "role":"AI Engineer",
    "experience":"3 Years",
    "skills":"Python, FastAPI, SQL",
    "resume":"uploads/Siddharth_Kulkarni.pdf",
    "candidate_status":"Shortlisted",
    "round_name":"Shortlisted",
    "interview_status":"Shortlisted"
},

{
    "name":"Isha Kapoor",
    "email":"isha@gmail.com",
    "phone":"9876500006",
    "role":"AI Engineer",
    "experience":"2 Years",
    "skills":"TensorFlow, Deep Learning, Python",
    "resume":"uploads/Isha_Kapoor.pdf",
    "candidate_status":"Shortlisted",
    "round_name":"Shortlisted",
    "interview_status":"Shortlisted"
},

# ---------------- Interview Round 2 ----------------

{
    "name":"Kavya Iyer",
    "email":"kavya@gmail.com",
    "phone":"9876500007",
    "role":"AI Engineer",
    "experience":"3 Years",
    "skills":"CNN, TensorFlow, Python",
    "resume":"uploads/Kavya_Iyer.pdf",
    "candidate_status":"Interview Round 2",
    "round_name":"Interview Round 2",
    "interview_status":"Scheduled"
},

{
    "name":"Vikram Rao",
    "email":"vikram@gmail.com",
    "phone":"9876500008",
    "role":"AI Engineer",
    "experience":"4 Years",
    "skills":"Docker, AWS, FastAPI",
    "resume":"uploads/Vikram_Rao.pdf",
    "candidate_status":"Interview Round 2",
    "round_name":"Interview Round 2",
    "interview_status":"Scheduled"
},

# ---------------- Interview Round 3 ----------------

{
    "name":"Rohit Kumar",
    "email":"rohit@gmail.com",
    "phone":"9876500009",
    "role":"AI Engineer",
    "experience":"3 Years",
    "skills":"Power BI, SQL, Python",
    "resume":"uploads/Rohit_Kumar.pdf",
    "candidate_status":"Interview Round 3",
    "round_name":"Interview Round 3",
    "interview_status":"Scheduled"
},

{
    "name":"Anjali Deshmukh",
    "email":"anjali@gmail.com",
    "phone":"9876500010",
    "role":"AI Engineer",
    "experience":"2 Years",
    "skills":"Transformers, NLP, Python",
    "resume":"uploads/Anjali_Deshmukh.pdf",
    "candidate_status":"Interview Round 3",
    "round_name":"Interview Round 3",
    "interview_status":"Scheduled"
},

# ---------------- Selected ----------------

{
    "name":"Arjun Patil",
    "email":"arjun@gmail.com",
    "phone":"9876500011",
    "role":"AI Engineer",
    "experience":"4 Years",
    "skills":"MongoDB, FastAPI, Python",
    "resume":"uploads/Arjun_Patil.pdf",
    "candidate_status":"Selected",
    "round_name":"Selected",
    "interview_status":"Selected"
},

# ---------------- Offer Sent ----------------

{
    "name":"Mohit Gupta",
    "email":"mohit@gmail.com",
    "phone":"9876500012",
    "role":"AI Engineer",
    "experience":"5 Years",
    "skills":"MLOps, Docker, Kubernetes",
    "resume":"uploads/Mohit_Gupta.pdf",
    "candidate_status":"Offer Sent",
    "round_name":"Offer Sent",
    "interview_status":"Offer Sent"
}

]

INTERVIEWERS = [

    "Mr. Amit Sharma",
    "Ms. Priya Kulkarni",
    "Mr. Kunal Joshi",
    "Ms. Neha Desai",
    "Mr. Rakesh Kumar"

]

TIMES = [

    "10:00 AM",
    "11:00 AM",
    "12:00 PM",
    "02:00 PM",
    "03:30 PM",
    "04:30 PM"

]

MEETING_MODES = [

    "Online",
    "Offline"

]

print("Loaded", len(NEW_CANDIDATES), "new candidates.")
# ==========================================================
# INSERT NEW CANDIDATES (MERGE SAFE)
# ==========================================================

for candidate in NEW_CANDIDATES:

    # ---------------------------------------------
    # Check whether candidate already exists
    # ---------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM candidates
        WHERE email=?
        """,
        (candidate["email"],)
    )

    existing = cursor.fetchone()

    if existing:

        candidate_id = existing[0]
        print(f"✓ {candidate['name']} already exists.")

    else:

        cursor.execute(
            """
            INSERT INTO candidates(

                name,
                email,
                phone,
                role_applied,
                experience,
                skills,
                resume_path,
                status

            )

            VALUES(

                ?,?,?,?,?,?,?,?

            )
            """,
            (

                candidate["name"],
                candidate["email"],
                candidate["phone"],
                candidate["role"],
                candidate["experience"],
                candidate["skills"],
                candidate["resume"],
                candidate["candidate_status"]

            )
        )

        candidate_id = cursor.lastrowid

        print(f"Added Candidate : {candidate['name']}")

    # ---------------------------------------------
    # Check Interview
    # ---------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM interviews
        WHERE candidate_id=?
        """,
        (candidate_id,)
    )

    interview = cursor.fetchone()

    if interview:

        interview_id = interview[0]
        print(f"Interview already exists for {candidate['name']}")
        continue

    interview_date = (
        date.today()
        + timedelta(days=random.randint(1, 12))
    ).isoformat()

    interview_time = random.choice(TIMES)

    interviewer = random.choice(INTERVIEWERS)

    meeting_mode = random.choice(MEETING_MODES)

    meeting_link = (
        "https://meet.google.com/"
        + candidate["name"].lower().replace(" ", "")
    )

    technical_score = random.randint(72,95)

    communication_score = random.randint(75,96)

    cursor.execute(
        """
        INSERT INTO interviews(

            candidate_id,

            round_name,

            interviewer,

            interview_date,

            interview_time,

            meeting_mode,

            meeting_link,

            technical_score,

            communication_score,

            technical_notes,

            communication_notes,

            overall_notes,

            ai_feedback,

            feedback,

            recommendation,

            invitation_sent,

            status

        )

        VALUES(

            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?

        )
        """,
        (

            candidate_id,

            candidate["round_name"],

            interviewer,

            interview_date,

            interview_time,

            meeting_mode,

            meeting_link,

            technical_score,

            communication_score,

            "Awaiting interview.",

            "Awaiting interview.",

            "Interview scheduled.",

            "",

            "",

            "",

            1,

            candidate["interview_status"]

        )

    )

print("\n✅ Candidate & Interview seeding completed.\n")
# ==========================================================
# AI INTERVIEW SUMMARY
# ==========================================================

cursor.execute("""

SELECT

interviews.id,

candidates.status

FROM interviews

JOIN candidates

ON interviews.candidate_id=candidates.id

""")

rows=cursor.fetchall()

for interview_id,status in rows:

    if status in (

        "Applied",

        "AI Reviewed",

        "Shortlisted"

    ):

        continue

    cursor.execute("""

    SELECT id

    FROM ai_interview_summary

    WHERE interview_id=?

    """,(interview_id,))

    if cursor.fetchone():

        continue

    technical=random.randint(80,96)

    communication=random.randint(78,95)

    confidence=random.randint(82,98)

    overall=round(

        (

            technical+

            communication+

            confidence

        )/3

    )

    if overall>=90:

        recommendation="Strong Hire"

    elif overall>=80:

        recommendation="Hire"

    elif overall>=70:

        recommendation="Hold"

    else:

        recommendation="Reject"

    summary=f"""

Candidate demonstrated good technical knowledge,
clear communication and confidence during interview.

Overall Recommendation : {recommendation}

"""

    cursor.execute("""

    INSERT INTO ai_interview_summary(

    interview_id,

    technical_score,

    communication_score,

    confidence_score,

    overall_score,

    recommendation,

    summary

    )

    VALUES(

    ?,?,?,?,?,?,?

    )

    """,(

    interview_id,

    technical,

    communication,

    confidence,

    overall,

    recommendation,

    summary

    ))

print("AI Interview Summary Added")


# ==========================================================
# DOCUMENTS
# ==========================================================

cursor.execute("""

SELECT

id,

resume_path

FROM candidates

""")

rows=cursor.fetchall()

for candidate_id,resume in rows:

    cursor.execute("""

    SELECT id

    FROM candidate_documents

    WHERE candidate_id=?

    """,(candidate_id,))

    if cursor.fetchone():

        continue

    cursor.execute("""

    INSERT INTO candidate_documents(

    candidate_id,

    employee_id,

    document_name,

    file_path,

    upload_status,

    verification_status

    )

    VALUES(

    ?,?,?,?,?,?

    )

    """,(

    candidate_id,

    None,

    "Resume",

    resume,

    "Uploaded",

    "Verified"

    ))

print("Candidate Documents Added")


# ==========================================================
# DOCUMENT VERIFICATION
# ==========================================================

cursor.execute("""

SELECT id

FROM candidates

""")

rows=cursor.fetchall()

for (candidate_id,) in rows:

    cursor.execute("""

    SELECT id

    FROM document_verification

    WHERE candidate_id=?

    """,(candidate_id,))

    if cursor.fetchone():

        continue

    trust=random.uniform(92,99)

    fraud=100-trust

    cursor.execute("""

    INSERT INTO document_verification(

    candidate_id,

    document_name,

    trust_score,

    fraud_probability,

    ai_result,

    remarks

    )

    VALUES(

    ?,?,?,?,?,?

    )

    """,(

    candidate_id,

    "Resume",

    round(trust,2),

    round(fraud,2),

    "Verified",

    "AI verification successful."

    ))

print("Document Verification Added")
# ==========================================================
# ONBOARDING
# ==========================================================

cursor.execute("""

SELECT

id,

status

FROM candidates

""")

rows = cursor.fetchall()

for candidate_id, status in rows:

    if status not in (

        "Selected",

        "Offer Sent"

    ):

        continue

    cursor.execute("""

    SELECT id

    FROM onboarding

    WHERE candidate_id=?

    """,(candidate_id,))

    if cursor.fetchone():

        continue

    if status=="Selected":

        onboarding_status="In Progress"
        progress=75
        hr_status="Preparing Offer"

    else:

        onboarding_status="Completed"
        progress=100
        hr_status="Offer Sent"

    joining_date=(

        date.today()

        +

        timedelta(days=15)

    ).isoformat()

    cursor.execute("""

    INSERT INTO onboarding(

        candidate_id,

        onboarding_status,

        onboarding_progress,

        joining_date,

        hr_status

    )

    VALUES(

        ?,?,?,?,?

    )

    """,(

        candidate_id,

        onboarding_status,

        progress,

        joining_date,

        hr_status

    ))

print("Onboarding Added")


# ==========================================================
# ONBOARDING TIMELINE
# ==========================================================

cursor.execute("""

SELECT

candidate_id,

onboarding_status

FROM onboarding

""")

rows=cursor.fetchall()

for candidate_id,status in rows:

    cursor.execute("""

    SELECT id

    FROM onboarding_timeline

    WHERE candidate_id=?

    """,(candidate_id,))

    if cursor.fetchone():

        continue

    events=[

        ("Documents Uploaded","Completed"),

        ("Documents Verified","Completed"),

        ("Background Verification","Completed"),

        ("Offer Released","Completed"),

        ("Joining","Pending")

    ]

    if status=="Completed":

        events[-1]=(

            "Joining",

            "Completed"

        )

    for event_name,event_status in events:

        cursor.execute("""

        INSERT INTO onboarding_timeline(

            candidate_id,

            event_name,

            event_status

        )

        VALUES(

            ?,?,?

        )

        """,(

            candidate_id,

            event_name,

            event_status

        ))

print("Onboarding Timeline Added")


# ==========================================================
# DATABASE SUMMARY
# ==========================================================

cursor.execute(

    "SELECT COUNT(*) FROM candidates"

)

candidate_count=cursor.fetchone()[0]

cursor.execute(

    "SELECT COUNT(*) FROM interviews"

)

interview_count=cursor.fetchone()[0]

cursor.execute(

    "SELECT COUNT(*) FROM ai_interview_summary"

)

summary_count=cursor.fetchone()[0]

cursor.execute(

    "SELECT COUNT(*) FROM onboarding"

)

onboarding_count=cursor.fetchone()[0]


# ==========================================================
# SAVE
# ==========================================================

conn.commit()

conn.close()

print("\n")

print("="*60)

print(" DEMO DATA SEEDED SUCCESSFULLY ")

print("="*60)

print(f"Candidates             : {candidate_count}")

print(f"Interviews             : {interview_count}")

print(f"AI Interview Summary   : {summary_count}")

print(f"Onboarding             : {onboarding_count}")

print("="*60)

print("Existing data preserved.")

print("Only missing records were added.")

print("="*60)
import os
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.getenv('DATABASE_URL')

def get_conn():
    if not DATABASE_URL:
        raise RuntimeError('DATABASE_URL not set')
    return psycopg2.connect(DATABASE_URL)

def save_candidate(record):
    """record: dict with keys name,email,phone,skills,education,raw_text"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO candidates (name, email, phone, skills, education, raw_text) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
        (record.get('name'), record.get('email'), record.get('phone'), record.get('skills'), record.get('education'), record.get('raw_text'))
    )
    cid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return cid

def list_candidates(limit=50):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id,name,email,phone,skills,education,created_at FROM candidates ORDER BY created_at DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    keys = ["id","name","email","phone","skills","education","created_at"]
    return [dict(zip(keys,row)) for row in rows]
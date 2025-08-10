import re
import pdfplumber
import os
import io
from typing import List
import spacy
from collections import Counter

# load spaCy model lazily
_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load('en_core_web_sm')
    return _nlp

EMAIL_RE = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_RE = re.compile(r'(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?|\d{3}[\s-]?)\d{3}[\s-]?\d{4}')

# Simple skill list — extend for your domain
COMMON_SKILLS = [
    'python','java','c++','c#','javascript','sql','postgresql','docker','kubernetes','flask','django','react','aws','azure','gcp','machine learning','nlp','tensorflow','pytorch','opencv','spaCy'
]

EDU_KEYWORDS = ['bachelor', 'master', "b\.sc", "m\.sc", 'btech','bs','ms','mba','phd','doctor']


def extract_text_from_pdf(fp) -> str:
    text = []
    try:
        with pdfplumber.open(fp) as pdf:
            for page in pdf.pages:
                p = page.extract_text()
                if p:
                    text.append(p)
    except Exception:
        # fallback: read raw bytes
        try:
            fp.seek(0)
            text.append(fp.read().decode('utf-8', errors='ignore'))
        except Exception:
            pass
    return "\n".join(text)


def extract_basic(text: str) -> dict:
    nlp = get_nlp()
    doc = nlp(text)

    # Name: first PERSON entity or capitalized first lines heuristic
    name = None
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            name = ent.text.strip()
            break

    # emails and phones
    emails = EMAIL_RE.findall(text)
    phones = PHONE_RE.findall(text)
    email = emails[0] if emails else None
    phone = phones[0] if phones else None

    # Skills: simple substring matching + frequency
    lower = text.lower()
    found_skills = []
    for skill in COMMON_SKILLS:
        if skill.lower() in lower:
            found_skills.append(skill)

    # Education: find lines containing edu keywords
    education_lines = []
    for line in text.splitlines():
        low = line.lower()
        if any(k in low for k in EDU_KEYWORDS):
            education_lines.append(line.strip())

    education = '; '.join(education_lines[:3]) if education_lines else None

    return {
        'name': name,
        'email': email,
        'phone': phone,
        'skills': ', '.join(found_skills) if found_skills else None,
        'education': education,
        'raw_text': text
    }


def parse_pdf_file(file_storage) -> dict:
    # file_storage: werkzeug FileStorage
    # read into BytesIO so pdfplumber can seek
    fp = io.BytesIO(file_storage.read())
    text = extract_text_from_pdf(fp)
    if not text.strip():
        # try decoding as utf-8
        fp.seek(0)
        try:
            text = fp.read().decode('utf-8', errors='ignore')
        except Exception:
            text = ''
    return extract_basic(text)
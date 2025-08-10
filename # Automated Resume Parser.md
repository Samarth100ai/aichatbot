# Automated Resume Parser

Extracts candidate details (name, skills, education, email, phone) from uploaded resumes (PDF/DOCX) and stores records in PostgreSQL. Built with Flask, spaCy, and pdfplumber.

## Features
- Upload PDF resumes via web UI
- Text extraction using `pdfplumber` (PDF) and fallback for plain text
- Named-Entity Recognition (spaCy) to get names
- Regex-based email/phone extraction
- Skill matching against a configurable list
- Saves parsed records to PostgreSQL

## Quickstart (local)
1. Create a Python virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
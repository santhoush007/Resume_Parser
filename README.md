# Automated Resume Parser

Extracts candidate details (name, email, phone, skills, education) from
PDF/Word resumes and stores them in a searchable PostgreSQL database.

**Stack:** Python, Flask, PostgreSQL, spaCy, pdfplumber, python-docx

## Project structure

```
resume_parser/
├── app.py                 # Flask app factory
├── run.py                 # Entry point (python run.py)
├── config.py              # Config (reads .env)
├── extensions.py          # SQLAlchemy instance
├── models.py               # Candidate / Skill / Education models
├── init_db.py              # One-time DB table creation script
├── parser/
│   ├── extractor.py        # PDF/DOCX -> raw text
│   ├── nlp_parser.py        # raw text -> structured fields (spaCy + regex)
│   └── skills_list.py       # Keyword list used for skill matching
├── routes/
│   ├── upload.py            # /upload (form) + /api/upload (JSON)
│   └── candidates.py         # /candidates (search/list/detail) + JSON API
├── templates/                # Jinja2 HTML pages
├── static/style.css
├── uploads/                  # Saved resume files (gitignored)
├── requirements.txt
└── .env.example
```

## Setup

### 1. Clone / unzip and create a virtual environment

```bash
cd resume_parser
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Download the spaCy language model

```bash
python -m spacy download en_core_web_sm
```

> If this model isn't available, the parser still works — it falls back
> to a simple heuristic for name detection instead of crashing.

### 3. Create the PostgreSQL database

```bash
# in psql or any Postgres client
CREATE DATABASE resume_parser;
```

### 4. Configure environment variables

```bash
cp .env.example .env
# then edit .env with your actual DB credentials
```

### 5. Create the tables

```bash
python init_db.py
```

### 6. Run the app

```bash
python run.py
```

Visit **http://localhost:5000**

## Usage

### Web UI
- `/` — landing page
- `/upload` — upload a PDF/DOCX resume
- `/candidates` — search/browse candidates (filter by `?name=` or `?skill=`)
- `/candidates/<id>` — full candidate detail, including raw extracted text

### JSON API
- `POST /api/upload` — multipart form upload, returns parsed candidate JSON
  ```bash
  curl -F "resume=@sample_resume.pdf" http://localhost:5000/api/upload
  ```
- `GET /api/candidates?skill=python&name=john` — list/search candidates
- `GET /api/candidates/<id>` — single candidate detail

## How parsing works

1. **Text extraction** (`parser/extractor.py`) — `pdfplumber` for PDFs,
   `python-docx` for Word files (including table cells, since many resumes
   use tables for layout).
2. **Field extraction** (`parser/nlp_parser.py`):
   - **Name** — spaCy NER (`PERSON` entities) on the top of the document,
     falling back to the first short line if no entity is found.
   - **Email / phone** — regex.
   - **Skills** — keyword matching against `parser/skills_list.py` (edit
     this list to recognize more skills without touching any logic).
   - **Education** — lines containing degree/institution keywords
     (e.g. "B.Tech", "MBA", "University").
3. **Storage** — `Candidate`, `Skill` (many-to-many), and `Education`
   tables via SQLAlchemy.

## Possible improvements

- Use PostgreSQL full-text search (`tsvector`) over `raw_text` for fuzzier
  search instead of `ILIKE`.
- Add authentication for recruiters/admins.
- Extract years of experience and work history as a separate section.
- Add pagination on the candidates list for large datasets.
- Add automated tests (`pytest`) for the parser functions — they're pure
  functions, so this is straightforward.

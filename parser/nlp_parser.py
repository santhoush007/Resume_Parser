"""Turn raw resume text into structured fields: name, email, phone,
skills, and education.

Name extraction uses spaCy's Named Entity Recognition (PERSON entities)
when the model is available, with a simple heuristic fallback so the
parser still works if the model hasn't been downloaded yet.
"""

import re

import spacy

from parser.skills_list import SKILLS

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(
    r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{3,4}"
)

_EDUCATION_KEYWORDS = [
    "bachelor", "master", "b.tech", "btech", "m.tech", "mtech", "b.e", "be ",
    "m.e", "phd", "doctorate", "mba", "bca", "mca", "b.sc", "bsc", "m.sc",
    "msc", "diploma", "university", "college", "institute of technology",
]

_nlp = None
_nlp_load_attempted = False


def _load_model():
    """Lazily load the spaCy model. Returns None if it isn't installed,
    so the rest of the parser can fall back to simpler heuristics
    instead of crashing.
    """
    global _nlp, _nlp_load_attempted
    if not _nlp_load_attempted:
        _nlp_load_attempted = True
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            _nlp = None
    return _nlp


def extract_email(text: str):
    match = _EMAIL_RE.search(text)
    return match.group(0) if match else None


def extract_phone(text: str):
    for match in _PHONE_RE.finditer(text):
        candidate = match.group(0)
        digits = re.sub(r"\D", "", candidate)
        if 7 <= len(digits) <= 13:
            return candidate.strip()
    return None


def extract_name(text: str):
    """Look at the top few lines of the resume (where names usually
    appear) and try spaCy NER first, falling back to the first
    short, email-free line.
    """
    top_lines = text.strip().splitlines()[:5]
    top_chunk = "\n".join(top_lines)

    nlp = _load_model()
    if nlp:
        doc = nlp(top_chunk)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()

    for line in top_lines:
        line = line.strip()
        if line and len(line.split()) <= 5 and not _EMAIL_RE.search(line):
            return line
    return None


def extract_skills(text: str):
    lowered = text.lower()
    found = set()
    for skill in SKILLS:
        pattern = r"(?<![a-zA-Z0-9+#.])" + re.escape(skill) + r"(?![a-zA-Z0-9+#])"
        if re.search(pattern, lowered):
            found.add(skill)
    return sorted(found)


def extract_education(text: str):
    results = []
    for line in text.splitlines():
        lowered = line.lower()
        if any(keyword in lowered for keyword in _EDUCATION_KEYWORDS):
            cleaned = line.strip()
            if cleaned:
                results.append(cleaned)
    return results


def parse_resume(text: str) -> dict:
    """Run all extractors and return a structured dict."""
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
    }

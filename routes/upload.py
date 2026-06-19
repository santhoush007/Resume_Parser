import os

from flask import (
    Blueprint, current_app, flash, jsonify, redirect, render_template,
    request, url_for,
)
from werkzeug.utils import secure_filename

from extensions import db
from models import Candidate, Education, Skill
from parser.extractor import extract_text
from parser.nlp_parser import parse_resume

upload_bp = Blueprint("upload", __name__)


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def _build_candidate(parsed, filename, raw_text):
    """Create a Candidate object (with skills/education attached) from
    parsed fields. Reuses existing Skill rows instead of duplicating them.
    """
    candidate = Candidate(
        name=parsed["name"],
        email=parsed["email"],
        phone=parsed["phone"],
        file_name=filename,
        raw_text=raw_text,
    )

    for skill_name in parsed["skills"]:
        skill = Skill.query.filter_by(name=skill_name).first()
        if not skill:
            skill = Skill(name=skill_name)
            db.session.add(skill)
        candidate.skills.append(skill)

    for edu_line in parsed["education"]:
        candidate.education.append(Education(raw_line=edu_line))

    return candidate


@upload_bp.route("/")
def index():
    return render_template("index.html")


@upload_bp.route("/upload", methods=["GET", "POST"])
def upload_resume():
    if request.method == "GET":
        return render_template("upload.html")

    file = request.files.get("resume")
    if not file or file.filename == "":
        flash("Please choose a resume file to upload.")
        return redirect(url_for("upload.upload_resume"))

    if not _allowed_file(file.filename):
        flash("Only PDF and Word (.docx) files are supported.")
        return redirect(url_for("upload.upload_resume"))

    filename = secure_filename(file.filename)
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    try:
        raw_text = extract_text(save_path)
        parsed = parse_resume(raw_text)
    except Exception as exc:
        flash(f"Could not parse the resume: {exc}")
        return redirect(url_for("upload.upload_resume"))

    candidate = _build_candidate(parsed, filename, raw_text)
    db.session.add(candidate)
    db.session.commit()

    flash(f"Resume parsed successfully for {candidate.name or 'candidate'}.")
    return redirect(url_for("candidates.candidate_detail", candidate_id=candidate.id))


@upload_bp.route("/api/upload", methods=["POST"])
def api_upload_resume():
    """JSON API version of the upload endpoint, e.g. for curl/Postman:

    curl -F "resume=@my_resume.pdf" http://localhost:5000/api/upload
    """
    file = request.files.get("resume")
    if not file or file.filename == "":
        return jsonify({"error": "No file provided"}), 400
    if not _allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    try:
        raw_text = extract_text(save_path)
        parsed = parse_resume(raw_text)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    candidate = _build_candidate(parsed, filename, raw_text)
    db.session.add(candidate)
    db.session.commit()

    return jsonify(candidate.to_dict()), 201

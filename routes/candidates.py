from flask import Blueprint, jsonify, render_template, request

from models import Candidate, Skill

candidates_bp = Blueprint("candidates", __name__)


def _filtered_query(args):
    skill_filter = args.get("skill", "").strip().lower()
    name_filter = args.get("name", "").strip()

    query = Candidate.query
    if skill_filter:
        query = query.join(Candidate.skills).filter(
            Skill.name.ilike(f"%{skill_filter}%")
        )
    if name_filter:
        query = query.filter(Candidate.name.ilike(f"%{name_filter}%"))

    return query.order_by(Candidate.created_at.desc()), skill_filter, name_filter


@candidates_bp.route("/candidates")
def list_candidates():
    query, skill_filter, name_filter = _filtered_query(request.args)
    candidates = query.all()
    return render_template(
        "candidates.html",
        candidates=candidates,
        skill_filter=skill_filter,
        name_filter=name_filter,
    )


@candidates_bp.route("/candidates/<int:candidate_id>")
def candidate_detail(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    return render_template("candidate_detail.html", candidate=candidate)


@candidates_bp.route("/api/candidates")
def api_list_candidates():
    query, _, _ = _filtered_query(request.args)
    candidates = query.all()
    return jsonify([c.to_dict() for c in candidates])


@candidates_bp.route("/api/candidates/<int:candidate_id>")
def api_candidate_detail(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    return jsonify(candidate.to_dict())

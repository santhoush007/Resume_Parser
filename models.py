from datetime import datetime

from extensions import db

# Many-to-many link between candidates and skills
candidate_skills = db.Table(
    "candidate_skills",
    db.Column("candidate_id", db.Integer, db.ForeignKey("candidates.id"), primary_key=True),
    db.Column("skill_id", db.Integer, db.ForeignKey("skills.id"), primary_key=True),
)


class Candidate(db.Model):
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), index=True)
    phone = db.Column(db.String(40))
    file_name = db.Column(db.String(255))
    raw_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    skills = db.relationship("Skill", secondary=candidate_skills, backref="candidates")
    education = db.relationship(
        "Education", backref="candidate", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "file_name": self.file_name,
            "skills": [s.name for s in self.skills],
            "education": [e.raw_line for e in self.education],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)

    def __repr__(self):
        return f"<Skill {self.name}>"


class Education(db.Model):
    __tablename__ = "education"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"))
    raw_line = db.Column(db.Text)

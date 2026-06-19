import os

from flask import Flask
from config import Config
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    from routes.candidates import candidates_bp
    from routes.upload import upload_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(candidates_bp)

    return app


# Create app and initialize DB tables
app = create_app()


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    skills = db.Column(db.Text)
    education = db.Column(db.Text)


with app.app_context():
    db.create_all()

print("Database and table created!")

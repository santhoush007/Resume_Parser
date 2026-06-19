import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = "secret-key"
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI = "sqlite:///resume_parser.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER", os.path.join(os.path.dirname(__file__), "uploads")
    )
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload size
    ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

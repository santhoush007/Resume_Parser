"""Run this once (after creating the Postgres database itself) to
create all tables:

    python init_db.py
"""
from app import create_app
from extensions import db

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created successfully.")

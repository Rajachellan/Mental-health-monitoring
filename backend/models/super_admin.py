from datetime import datetime

from backend.database.db import db


class SuperAdmin(db.Model):
    """Platform-wide administrator (all organizations & aggregate analytics)."""

    __tablename__ = 'super_admins'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SuperAdmin {self.email}>'

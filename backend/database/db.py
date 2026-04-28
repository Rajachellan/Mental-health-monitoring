from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def _sqlite_column_names(connection, table):
    rows = connection.execute(text(f'PRAGMA table_info({table})')).fetchall()
    return {row[1] for row in rows}


def migrate_schema(app):
    """Add columns introduced after initial deploy (SQLite ALTER TABLE)."""
    uri = app.config.get('SQLALCHEMY_DATABASE_URI') or ''
    if not uri.startswith('sqlite'):
        return
    with app.app_context():
        engine = db.engine
        with engine.connect() as conn:
            org_cols = _sqlite_column_names(conn, 'organizations')
            if 'password_hash' not in org_cols:
                conn.execute(text('ALTER TABLE organizations ADD COLUMN password_hash VARCHAR(256)'))
                conn.commit()
            emp_cols = _sqlite_column_names(conn, 'employees')
            if 'password_hash' not in emp_cols:
                conn.execute(text('ALTER TABLE employees ADD COLUMN password_hash VARCHAR(256)'))
                conn.commit()
            asm_defs = [
                ('transcript', 'TEXT'),
                ('sentiment_compound', 'FLOAT'),
                ('sentiment_pos', 'FLOAT'),
                ('sentiment_neg', 'FLOAT'),
                ('sentiment_neu', 'FLOAT'),
                ('sentiment_label', 'VARCHAR(32)'),
            ]
            for col_name, col_type in asm_defs:
                asm_cols = _sqlite_column_names(conn, 'assessments')
                if col_name not in asm_cols:
                    conn.execute(text(f'ALTER TABLE assessments ADD COLUMN {col_name} {col_type}'))
                    conn.commit()


def init_db(app):
    """Initialize database with the Flask app"""
    db.init_app(app)
    with app.app_context():
        import backend.models.super_admin  # noqa: F401 — register metadata
        db.create_all()
        migrate_schema(app)


def reset_db(app):
    """Reset database - drop all tables and recreate"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        migrate_schema(app)

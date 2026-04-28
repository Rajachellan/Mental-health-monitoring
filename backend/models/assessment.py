from datetime import datetime
from backend.database.db import db

class Assessment(db.Model):
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Assessment results
    score = db.Column(db.Float, nullable=False)  # 0-100
    status = db.Column(db.String(50), nullable=False)  # good, fair, poor, critical
    summary = db.Column(db.Text, nullable=True)
    recommendations = db.Column(db.Text, nullable=True)
    
    # Call details
    call_duration = db.Column(db.Integer, nullable=True)  # in seconds
    call_status = db.Column(db.String(50), nullable=False, default='pending')  # pending, in_progress, completed, failed
    call_notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Assessment {self.employee_id} - {self.score}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'assessment_date': self.assessment_date.isoformat(),
            'score': self.score,
            'status': self.status,
            'summary': self.summary,
            'recommendations': self.recommendations,
            'call_duration': self.call_duration,
            'call_status': self.call_status,
            'call_notes': self.call_notes,
            'created_at': self.created_at.isoformat()
        }

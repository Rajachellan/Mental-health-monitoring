from datetime import datetime
from backend.database.db import db

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    employee_id = db.Column(db.String(50), nullable=False)
    
    # Assessment status
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, failed
    last_assessment_date = db.Column(db.DateTime, nullable=True)
    assessment_score = db.Column(db.Float, nullable=True)  # 0-100 score
    assessment_status_details = db.Column(db.Text, nullable=True)  # Additional details from assessment
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessments = db.relationship('Assessment', backref='employee', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'designation': self.designation,
            'employee_id': self.employee_id,
            'status': self.status,
            'last_assessment_date': self.last_assessment_date.isoformat() if self.last_assessment_date else None,
            'assessment_score': self.assessment_score,
            'assessment_status_details': self.assessment_status_details,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

from backend.models.assessment import Assessment
from backend.models.employee import Employee
from backend.database.db import db

class AssessmentService:
    
    @staticmethod
    def create_assessment(employee_id, score, status, summary=None, recommendations=None, call_notes=None):
        """Create a new assessment for an employee"""
        
        employee = Employee.query.get(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID {employee_id} not found")
        
        assessment = Assessment(
            employee_id=employee_id,
            score=score,
            status=status,
            summary=summary,
            recommendations=recommendations,
            call_status='completed',
            call_notes=call_notes
        )
        
        db.session.add(assessment)
        
        # Update employee's last assessment info
        employee.last_assessment_date = assessment.assessment_date
        employee.assessment_score = score
        employee.status = 'completed'
        
        db.session.commit()
        return assessment
    
    @staticmethod
    def get_assessment(assessment_id):
        """Get assessment by ID"""
        return Assessment.query.get(assessment_id)
    
    @staticmethod
    def get_employee_assessments(employee_id):
        """Get all assessments for an employee"""
        return Assessment.query.filter_by(employee_id=employee_id).order_by(Assessment.assessment_date.desc()).all()
    
    @staticmethod
    def get_latest_assessment(employee_id):
        """Get the latest assessment for an employee"""
        return Assessment.query.filter_by(employee_id=employee_id).order_by(Assessment.assessment_date.desc()).first()
    
    @staticmethod
    def update_assessment(assessment_id, **kwargs):
        """Update an assessment"""
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment with ID {assessment_id} not found")
        
        for key, value in kwargs.items():
            if hasattr(assessment, key) and key not in ['id', 'created_at', 'assessment_date']:
                setattr(assessment, key, value)
        
        db.session.commit()
        return assessment

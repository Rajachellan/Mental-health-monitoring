from werkzeug.security import generate_password_hash

from backend.models.organization import Organization
from backend.models.employee import Employee
from backend.database.db import db

class OrganizationService:
    
    @staticmethod
    def create_organization(name, email, phone=None, address=None, industry=None, admin_password=None):
        """Create a new organization"""
        # Check if organization already exists
        existing = Organization.query.filter_by(name=name).first()
        if existing:
            raise ValueError(f"Organization '{name}' already exists")
        
        existing_email = Organization.query.filter_by(email=email).first()
        if existing_email:
            raise ValueError(f"Email '{email}' is already registered")
        
        org = Organization(
            name=name,
            email=email,
            phone=phone,
            address=address,
            industry=industry,
            password_hash=generate_password_hash(admin_password)
            if admin_password
            else None,
        )
        db.session.add(org)
        db.session.commit()
        return org
    
    @staticmethod
    def get_organization(org_id):
        """Get organization by ID"""
        return Organization.query.get(org_id)
    
    @staticmethod
    def get_organization_by_name(name):
        """Get organization by name"""
        return Organization.query.filter_by(name=name).first()
    
    @staticmethod
    def list_organizations():
        """List all organizations"""
        return Organization.query.all()
    
    @staticmethod
    def update_organization(org_id, **kwargs):
        """Update organization details"""
        org = Organization.query.get(org_id)
        if not org:
            raise ValueError(f"Organization with ID {org_id} not found")
        
        for key, value in kwargs.items():
            if hasattr(org, key) and key not in ['id', 'created_at', 'updated_at']:
                setattr(org, key, value)
        
        db.session.commit()
        return org
    
    @staticmethod
    def delete_organization(org_id):
        """Delete organization and all its employees"""
        org = Organization.query.get(org_id)
        if not org:
            raise ValueError(f"Organization with ID {org_id} not found")
        
        db.session.delete(org)
        db.session.commit()
    
    @staticmethod
    def get_organization_stats(org_id):
        """Get statistics for an organization"""
        org = Organization.query.get(org_id)
        if not org:
            raise ValueError(f"Organization with ID {org_id} not found")
        
        total_employees = len(org.employees)
        completed = sum(1 for e in org.employees if e.status == 'completed')
        pending = sum(1 for e in org.employees if e.status == 'pending')
        in_progress = sum(1 for e in org.employees if e.status == 'in_progress')
        failed = sum(1 for e in org.employees if e.status == 'failed')
        
        avg_score = None
        scores = [e.assessment_score for e in org.employees if e.assessment_score is not None]
        if scores:
            avg_score = sum(scores) / len(scores)
        
        return {
            'organization': org.to_dict(),
            'total_employees': total_employees,
            'assessment_status': {
                'completed': completed,
                'pending': pending,
                'in_progress': in_progress,
                'failed': failed
            },
            'average_score': avg_score
        }

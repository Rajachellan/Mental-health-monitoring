from werkzeug.security import generate_password_hash

from backend.models.employee import Employee
from backend.models.organization import Organization
from backend.database.db import db

class EmployeeService:
    
    @staticmethod
    def add_employee(
        organization_id,
        first_name,
        last_name,
        email,
        phone,
        employee_id,
        department=None,
        designation=None,
        portal_password=None,
    ):
        """Add a new employee to organization"""
        
        # Check if organization exists
        org = Organization.query.get(organization_id)
        if not org:
            raise ValueError(f"Organization with ID {organization_id} not found")
        
        # Check if employee already exists (by email or employee_id)
        existing = Employee.query.filter_by(organization_id=organization_id, email=email).first()
        if existing:
            raise ValueError(f"Employee with email '{email}' already exists in this organization")
        
        existing_emp_id = Employee.query.filter_by(organization_id=organization_id, employee_id=employee_id).first()
        if existing_emp_id:
            raise ValueError(f"Employee ID '{employee_id}' already exists in this organization")
        
        employee = Employee(
            organization_id=organization_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            employee_id=employee_id,
            department=department,
            designation=designation,
            status='pending',
            password_hash=generate_password_hash(portal_password)
            if portal_password
            else None,
        )
        
        db.session.add(employee)
        org.total_employees += 1
        db.session.commit()
        return employee
    
    @staticmethod
    def get_employee(employee_id):
        """Get employee by ID"""
        return Employee.query.get(employee_id)
    
    @staticmethod
    def get_employees_by_organization(organization_id):
        """Get all employees in an organization"""
        return Employee.query.filter_by(organization_id=organization_id).all()
    
    @staticmethod
    def update_employee_status(employee_id, status, score=None, details=None):
        """Update employee assessment status"""
        from datetime import datetime
        
        employee = Employee.query.get(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID {employee_id} not found")
        
        employee.status = status
        if score is not None:
            employee.assessment_score = score
        if details:
            employee.assessment_status_details = details
        
        if status == 'completed':
            employee.last_assessment_date = datetime.utcnow()
        
        db.session.commit()
        return employee
    
    @staticmethod
    def get_employee_status(employee_id):
        """Get employee assessment status"""
        employee = Employee.query.get(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID {employee_id} not found")
        
        return {
            'id': employee.id,
            'name': employee.get_full_name(),
            'employee_id': employee.employee_id,
            'email': employee.email,
            'department': employee.department,
            'status': employee.status,
            'score': employee.assessment_score,
            'last_assessment_date': employee.last_assessment_date.isoformat() if employee.last_assessment_date else None,
            'details': employee.assessment_status_details
        }
    
    @staticmethod
    def delete_employee(employee_id):
        """Delete an employee"""
        employee = Employee.query.get(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID {employee_id} not found")
        
        org = employee.organization
        db.session.delete(employee)
        org.total_employees -= 1
        db.session.commit()
    
    @staticmethod
    def bulk_add_employees(organization_id, employees_list):
        """Add multiple employees at once"""
        org = Organization.query.get(organization_id)
        if not org:
            raise ValueError(f"Organization with ID {organization_id} not found")
        
        added_employees = []
        for emp_data in employees_list:
            try:
                employee = EmployeeService.add_employee(
                    organization_id=organization_id,
                    first_name=emp_data['first_name'],
                    last_name=emp_data['last_name'],
                    email=emp_data['email'],
                    phone=emp_data['phone'],
                    employee_id=emp_data['employee_id'],
                    department=emp_data.get('department'),
                    designation=emp_data.get('designation'),
                    portal_password=emp_data.get('portal_password'),
                )
                added_employees.append(employee)
            except Exception as e:
                # Log error but continue with other employees
                print(f"Error adding employee {emp_data.get('employee_id', 'unknown')}: {str(e)}")
        
        return added_employees

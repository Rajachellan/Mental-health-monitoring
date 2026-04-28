"""
Example usage of the Mental Health Monitoring system
This script demonstrates how to programmatically use the services
"""

from app import create_app
from backend.services.organization_service import OrganizationService
from backend.services.employee_service import EmployeeService
from backend.services.assessment_service import AssessmentService

# Create Flask app
app = create_app()

def main():
    with app.app_context():
        print("=" * 70)
        print("Mental Health Monitoring System - Example Usage")
        print("=" * 70)
        
        # 1. Create an organization
        print("\n[1] Creating Organization...")
        try:
            org = OrganizationService.create_organization(
                name="Tech Corporation",
                email="hr@techcorp.com",
                phone="+91-9876543210",
                address="123 Tech Park, Bangalore",
                industry="Information Technology"
            )
            print(f"✓ Organization created: {org.name} (ID: {org.id})")
        except ValueError as e:
            print(f"✗ Error: {e}")
            org = OrganizationService.get_organization_by_name("Tech Corporation")
        
        if not org:
            print("Failed to create or retrieve organization. Exiting.")
            return
        
        # 2. Add employees
        print("\n[2] Adding Employees...")
        employees_data = [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@techcorp.com',
                'phone': '+91-9876543211',
                'employee_id': 'EMP001',
                'department': 'Engineering',
                'designation': 'Senior Developer'
            },
            {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@techcorp.com',
                'phone': '+91-9876543212',
                'employee_id': 'EMP002',
                'department': 'Human Resources',
                'designation': 'HR Manager'
            },
            {
                'first_name': 'Bob',
                'last_name': 'Johnson',
                'email': 'bob.johnson@techcorp.com',
                'phone': '+91-9876543213',
                'employee_id': 'EMP003',
                'department': 'Sales',
                'designation': 'Sales Executive'
            },
            {
                'first_name': 'Alice',
                'last_name': 'Williams',
                'email': 'alice.williams@techcorp.com',
                'phone': '+91-9876543214',
                'employee_id': 'EMP004',
                'department': 'Marketing',
                'designation': 'Marketing Manager'
            }
        ]
        
        employees = []
        for emp_data in employees_data:
            try:
                emp = EmployeeService.add_employee(
                    organization_id=org.id,
                    **emp_data
                )
                employees.append(emp)
                print(f"  ✓ Added: {emp.get_full_name()} ({emp.employee_id})")
            except ValueError as e:
                print(f"  ✗ Error: {e}")
                # Try to retrieve existing employee
                emp = EmployeeService.get_employees_by_organization(org.id)
                if emp:
                    employees.extend(emp)
        
        # 3. Get organization details
        print("\n[3] Organization Details...")
        stats = OrganizationService.get_organization_stats(org.id)
        print(f"  Total Employees: {stats['total_employees']}")
        print(f"  Completed Assessments: {stats['assessment_status']['completed']}")
        print(f"  Pending Assessments: {stats['assessment_status']['pending']}")
        print(f"  Average Score: {stats['average_score']}")
        
        # 4. View all employees
        print("\n[4] Employee List...")
        all_employees = EmployeeService.get_employees_by_organization(org.id)
        for emp in all_employees:
            status_info = EmployeeService.get_employee_status(emp.id)
            print(f"  - {emp.get_full_name():20} | Status: {emp.status:12} | Score: {emp.assessment_score or '-'}")
        
        # 5. Simulate assessment completion
        print("\n[5] Simulating Assessment Completion...")
        if all_employees:
            emp = all_employees[0]
            updated_emp = EmployeeService.update_employee_status(
                employee_id=emp.id,
                status='completed',
                score=82.5,
                details='Good mental health indicators. No concerns detected.'
            )
            print(f"  ✓ {updated_emp.get_full_name()} assessment updated to: {updated_emp.status} (Score: {updated_emp.assessment_score})")
        
        # 6. Final statistics
        print("\n[6] Final Statistics...")
        stats = OrganizationService.get_organization_stats(org.id)
        print(f"  Organization: {stats['organization']['name']}")
        print(f"  Total Employees: {stats['total_employees']}")
        print(f"  Completed: {stats['assessment_status']['completed']}")
        print(f"  Pending: {stats['assessment_status']['pending']}")
        print(f"  In Progress: {stats['assessment_status']['in_progress']}")
        print(f"  Failed: {stats['assessment_status']['failed']}")
        print(f"  Average Score: {stats['average_score']}")
        
        print("\n" + "=" * 70)
        print("Example completed successfully!")
        print("=" * 70)

if __name__ == '__main__':
    main()

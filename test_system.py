#!/usr/bin/env python
"""
Test script to verify the Mental Health Monitoring System works correctly
Run this after installation to validate the setup
"""

import sys
from app import create_app
from backend.services.organization_service import OrganizationService
from backend.services.employee_service import EmployeeService

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_imports():
    """Test that all imports work"""
    print_section("TEST 1: Import Validation")
    try:
        from backend.models.organization import Organization
        from backend.models.employee import Employee
        from backend.models.assessment import Assessment
        from backend.services.organization_service import OrganizationService
        from backend.services.employee_service import EmployeeService
        from backend.services.assessment_service import AssessmentService
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_database_creation():
    """Test database creation"""
    print_section("TEST 2: Database Creation")
    try:
        app = create_app('sqlite:///:memory:')  # Use in-memory database for testing
        print("✓ Database created successfully")
        return True, app
    except Exception as e:
        print(f"✗ Database creation failed: {e}")
        return False, None

def test_organization_operations(app):
    """Test organization CRUD operations"""
    print_section("TEST 3: Organization Operations")
    with app.app_context():
        try:
            # Create
            org = OrganizationService.create_organization(
                name="Test Company",
                email="test@example.com",
                phone="+91-1234567890",
                industry="Testing"
            )
            print(f"✓ Created organization: {org.name} (ID: {org.id})")
            
            # Read
            fetched_org = OrganizationService.get_organization(org.id)
            assert fetched_org.name == "Test Company"
            print(f"✓ Retrieved organization: {fetched_org.name}")
            
            # Update
            updated_org = OrganizationService.update_organization(
                org.id, 
                phone="+91-9876543210"
            )
            assert updated_org.phone == "+91-9876543210"
            print(f"✓ Updated organization phone: {updated_org.phone}")
            
            # List
            orgs = OrganizationService.list_organizations()
            assert len(orgs) >= 1
            print(f"✓ Listed organizations: {len(orgs)} found")
            
            return True, org.id
        except Exception as e:
            print(f"✗ Organization operations failed: {e}")
            return False, None

def test_employee_operations(app, org_id):
    """Test employee CRUD operations"""
    print_section("TEST 4: Employee Operations")
    with app.app_context():
        try:
            # Create
            employee = EmployeeService.add_employee(
                organization_id=org_id,
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                phone="+91-1111111111",
                employee_id="EMP001",
                department="Engineering",
                designation="Developer"
            )
            print(f"✓ Added employee: {employee.get_full_name()} (ID: {employee.id})")
            
            # Read
            fetched_emp = EmployeeService.get_employee(employee.id)
            assert fetched_emp.first_name == "John"
            print(f"✓ Retrieved employee: {fetched_emp.get_full_name()}")
            
            # Get status
            status = EmployeeService.get_employee_status(employee.id)
            assert status['status'] == 'pending'
            print(f"✓ Employee status: {status['status']}")
            
            # Update status
            updated_emp = EmployeeService.update_employee_status(
                employee_id=employee.id,
                status='completed',
                score=85.5,
                details='Assessment completed'
            )
            assert updated_emp.status == 'completed'
            assert updated_emp.assessment_score == 85.5
            print(f"✓ Updated employee status to: {updated_emp.status} (Score: {updated_emp.assessment_score})")
            
            # List by organization
            employees = EmployeeService.get_employees_by_organization(org_id)
            assert len(employees) >= 1
            print(f"✓ Listed employees in organization: {len(employees)} found")
            
            return True, employee.id
        except Exception as e:
            print(f"✗ Employee operations failed: {e}")
            return False, None

def test_statistics(app, org_id):
    """Test statistics generation"""
    print_section("TEST 5: Statistics")
    with app.app_context():
        try:
            stats = OrganizationService.get_organization_stats(org_id)
            print(f"✓ Organization: {stats['organization']['name']}")
            print(f"✓ Total employees: {stats['total_employees']}")
            print(f"✓ Completed assessments: {stats['assessment_status']['completed']}")
            print(f"✓ Pending assessments: {stats['assessment_status']['pending']}")
            print(f"✓ Average score: {stats['average_score']}")
            return True
        except Exception as e:
            print(f"✗ Statistics failed: {e}")
            return False

def test_bulk_operations(app, org_id):
    """Test bulk employee operations"""
    print_section("TEST 6: Bulk Operations")
    with app.app_context():
        try:
            employees_data = [
                {
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'email': 'jane@example.com',
                    'phone': '+91-2222222222',
                    'employee_id': 'EMP002',
                    'department': 'HR'
                },
                {
                    'first_name': 'Bob',
                    'last_name': 'Johnson',
                    'email': 'bob@example.com',
                    'phone': '+91-3333333333',
                    'employee_id': 'EMP003',
                    'department': 'Sales'
                }
            ]
            
            added = EmployeeService.bulk_add_employees(org_id, employees_data)
            assert len(added) == 2
            print(f"✓ Bulk added {len(added)} employees")
            
            return True
        except Exception as e:
            print(f"✗ Bulk operations failed: {e}")
            return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "Mental Health Monitoring System - Test Suite".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    
    results = {}
    
    # Test 1: Imports
    results['imports'] = test_imports()
    if not results['imports']:
        print("\n✗ Import validation failed. Please run: pip install -r requirements.txt")
        return False
    
    # Test 2: Database
    results['database'], app = test_database_creation()
    if not results['database'] or not app:
        print("\n✗ Database creation failed.")
        return False
    
    # Test 3: Organization
    results['organization'], org_id = test_organization_operations(app)
    if not results['organization'] or not org_id:
        print("\n✗ Organization operations failed.")
        return False
    
    # Test 4: Employee
    results['employee'], emp_id = test_employee_operations(app, org_id)
    if not results['employee']:
        print("\n✗ Employee operations failed.")
        return False
    
    # Test 5: Statistics
    results['statistics'] = test_statistics(app, org_id)
    
    # Test 6: Bulk
    results['bulk'] = test_bulk_operations(app, org_id)
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name.upper():20} {status}")
    
    print(f"\n  Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "="*70)
        print("  🎉 ALL TESTS PASSED! System is ready to use.")
        print("="*70)
        print("\n  Next steps:")
        print("  1. Read QUICKSTART.md for usage examples")
        print("  2. Run: python example_usage.py")
        print("  3. Start API: python app.py")
        print("  4. Use CLI: python cli.py --help")
        print("\n")
        return True
    else:
        print("\n" + "="*70)
        print("  ✗ Some tests failed. Please check the errors above.")
        print("="*70 + "\n")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

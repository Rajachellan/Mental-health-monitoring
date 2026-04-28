"""
Test employee addition via API
"""

from app import create_app
import json

app = create_app()

with app.test_client() as client:
    print("=" * 60)
    print("Testing Employee Addition via API")
    print("=" * 60)
    
    # Get organizations
    print("\n1. Getting organizations...")
    response = client.get('/api/organizations')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        orgs = response.get_json()['data']
        if orgs:
            org_id = orgs[0]['id']
            print(f"   ✓ Using organization {org_id} ({orgs[0]['name']})")
        else:
            print("   ✗ No organizations found")
            org_id = None
    else:
        print(f"   ✗ Failed to get organizations: {response.get_json()}")
        org_id = None
    
    if org_id:
        # Add employee
        print("\n2. Adding employee...")
        emp_data = {
            "organization_id": org_id,
            "first_name": "Test",
            "last_name": "Employee",
            "email": "test.emp.api@test.com",
            "phone": "+91-9999999999",
            "employee_id": "TEST_EMP_API_001"
        }
        print(f"   Payload: {json.dumps(emp_data)}")
        
        response = client.post('/api/employees', 
                              data=json.dumps(emp_data), 
                              content_type='application/json')
        print(f"   Status: {response.status_code}")
        resp_data = response.get_json()
        print(f"   Response: {json.dumps(resp_data, indent=2)}")
        
        if response.status_code == 201:
            print(f"\n   ✓ Employee added successfully!")
            emp = resp_data['data']
            print(f"     Employee ID: {emp['id']}")
            print(f"     Full Name: {emp['full_name']}")
            print(f"     Email: {emp['email']}")
        else:
            print(f"\n   ✗ Failed to add employee")
            if 'error' in resp_data:
                print(f"     Error: {resp_data['error']}")

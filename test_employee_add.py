"""
Test script to debug employee addition issue
"""

import requests
import json
import time

# Wait for server to be ready
time.sleep(3)

BASE_URL = "http://localhost:8080/api"

# Step 1: Get existing organization or create one
print("=" * 60)
print("Step 1: Getting Organization")
print("=" * 60)

try:
    response = requests.get(f"{BASE_URL}/organizations")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        orgs = response.json()['data']
        if orgs:
            org_id = orgs[0]['id']
            print(f"✓ Using existing organization: ID = {org_id}")
        else:
            # Create new organization
            org_data = {
                "name": "Debug Corp",
                "email": "debug@corp.com",
                "phone": "+91-9999999999",
                "address": "Debug Address",
                "industry": "Testing"
            }
            response = requests.post(f"{BASE_URL}/organizations", json=org_data)
            if response.status_code == 201:
                org = response.json()['data']
                org_id = org['id']
                print(f"✓ Organization created: ID = {org_id}")
            else:
                print(f"✗ Failed to create organization: {response.text}")
                exit(1)
    else:
        print(f"✗ Failed to fetch organizations: {response.text}")
        exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 2: Add an employee
print("\n" + "=" * 60)
print("Step 2: Adding Employee")
print("=" * 60)

emp_data = {
    "organization_id": org_id,
    "first_name": "API Test",
    "last_name": "User",
    "email": f"api.test.{int(time.time())}@corp.com",
    "phone": "+91-8888888888",
    "employee_id": f"EMP_API_{int(time.time())}",
    "department": "Testing",
    "designation": "Tester"
}

try:
    print(f"Sending: POST {BASE_URL}/employees")
    print(f"Data: {json.dumps(emp_data, indent=2)}")
    response = requests.post(f"{BASE_URL}/employees", json=emp_data, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        emp = response.json()['data']
        print(f"✓ Employee added successfully: ID = {emp['id']}")
    else:
        print(f"✗ Failed to add employee")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

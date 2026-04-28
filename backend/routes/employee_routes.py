from flask import Blueprint, request, jsonify
from backend.services.employee_service import EmployeeService

emp_routes = Blueprint('employees', __name__, url_prefix='/api/employees')

@emp_routes.route('', methods=['GET'])
def list_all_employees():
    """Get all employees across all organizations"""
    try:
        from backend.models.employee import Employee
        employees = Employee.query.all()
        return jsonify({
            'data': [emp.to_dict() for emp in employees]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@emp_routes.route('', methods=['POST'])
def add_employee():
    """Add a new employee"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['organization_id', 'first_name', 'last_name', 'email', 'phone', 'employee_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {", ".join(required_fields)}'}), 400
        
        employee = EmployeeService.add_employee(
            organization_id=data['organization_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            employee_id=data['employee_id'],
            department=data.get('department'),
            designation=data.get('designation')
        )
        
        return jsonify({
            'message': 'Employee added successfully',
            'data': employee.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@emp_routes.route('/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """Get employee details"""
    try:
        employee = EmployeeService.get_employee(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        return jsonify({'data': employee.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@emp_routes.route('/<int:employee_id>/status', methods=['GET'])
def get_employee_status(employee_id):
    """Get employee assessment status"""
    try:
        status = EmployeeService.get_employee_status(employee_id)
        return jsonify({'data': status}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@emp_routes.route('/<int:employee_id>/status', methods=['PUT'])
def update_employee_status(employee_id):
    """Update employee assessment status"""
    try:
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        employee = EmployeeService.update_employee_status(
            employee_id=employee_id,
            status=data['status'],
            score=data.get('score'),
            details=data.get('details')
        )
        
        return jsonify({
            'message': 'Employee status updated successfully',
            'data': employee.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@emp_routes.route('/organization/<int:org_id>', methods=['GET'])
def get_organization_employees(org_id):
    """Get all employees in an organization"""
    try:
        employees = EmployeeService.get_employees_by_organization(org_id)
        return jsonify({
            'data': [emp.to_dict() for emp in employees]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@emp_routes.route('/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Delete an employee"""
    try:
        EmployeeService.delete_employee(employee_id)
        return jsonify({'message': 'Employee deleted successfully'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@emp_routes.route('/bulk-add', methods=['POST'])
def bulk_add_employees():
    """Add multiple employees at once"""
    try:
        data = request.get_json()
        
        if 'organization_id' not in data or 'employees' not in data:
            return jsonify({'error': 'organization_id and employees list are required'}), 400
        
        employees = EmployeeService.bulk_add_employees(
            organization_id=data['organization_id'],
            employees_list=data['employees']
        )
        
        return jsonify({
            'message': f'{len(employees)} employees added successfully',
            'data': [emp.to_dict() for emp in employees]
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

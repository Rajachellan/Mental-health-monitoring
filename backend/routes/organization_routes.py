from flask import Blueprint, request, jsonify
from backend.services.organization_service import OrganizationService
from backend.services.employee_service import EmployeeService

org_routes = Blueprint('organizations', __name__, url_prefix='/api/organizations')

@org_routes.route('', methods=['POST'])
def create_organization():
    """Create a new organization"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('email'):
            return jsonify({'error': 'Name and email are required'}), 400
        
        org = OrganizationService.create_organization(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address'),
            industry=data.get('industry')
        )
        
        return jsonify({
            'message': 'Organization created successfully',
            'data': org.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@org_routes.route('', methods=['GET'])
def list_organizations():
    """List all organizations"""
    try:
        orgs = OrganizationService.list_organizations()
        return jsonify({
            'data': [org.to_dict() for org in orgs]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@org_routes.route('/<int:org_id>', methods=['GET'])
def get_organization(org_id):
    """Get organization by ID"""
    try:
        org = OrganizationService.get_organization(org_id)
        if not org:
            return jsonify({'error': 'Organization not found'}), 404
        
        return jsonify({'data': org.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@org_routes.route('/<int:org_id>', methods=['PUT'])
def update_organization(org_id):
    """Update organization"""
    try:
        data = request.get_json()
        org = OrganizationService.update_organization(org_id, **data)
        
        return jsonify({
            'message': 'Organization updated successfully',
            'data': org.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@org_routes.route('/<int:org_id>', methods=['DELETE'])
def delete_organization(org_id):
    """Delete organization"""
    try:
        OrganizationService.delete_organization(org_id)
        return jsonify({'message': 'Organization deleted successfully'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@org_routes.route('/<int:org_id>/stats', methods=['GET'])
def get_organization_stats(org_id):
    """Get organization statistics"""
    try:
        stats = OrganizationService.get_organization_stats(org_id)
        return jsonify({'data': stats}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

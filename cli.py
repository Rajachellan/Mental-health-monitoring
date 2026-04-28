import click
from tabulate import tabulate
from app import create_app
from backend.database.db import db
from backend.services.organization_service import OrganizationService
from backend.services.employee_service import EmployeeService

app = create_app()

@click.group()
def cli():
    """Mental Health Monitoring - CLI Tool"""
    pass

# ===================== ORGANIZATION COMMANDS =====================

@cli.group()
def org():
    """Organization management commands"""
    pass

@org.command()
@click.option('--name', prompt='Organization name', help='Name of the organization')
@click.option('--email', prompt='Email', help='Organization email')
@click.option('--phone', prompt='Phone (optional)', default='', help='Phone number')
@click.option('--address', prompt='Address (optional)', default='', help='Address')
@click.option('--industry', prompt='Industry (optional)', default='', help='Industry type')
def create(name, email, phone, address, industry):
    """Create a new organization"""
    with app.app_context():
        try:
            org = OrganizationService.create_organization(
                name=name,
                email=email,
                phone=phone if phone else None,
                address=address if address else None,
                industry=industry if industry else None
            )
            click.secho(f'✓ Organization "{org.name}" created successfully!', fg='green')
            click.echo(f'  Organization ID: {org.id}')
        except ValueError as e:
            click.secho(f'✗ Error: {str(e)}', fg='red')

@org.command()
def list():
    """List all organizations"""
    with app.app_context():
        orgs = OrganizationService.list_organizations()
        if not orgs:
            click.echo('No organizations found.')
            return
        
        data = []
        for org in orgs:
            data.append([
                org.id,
                org.name,
                org.email,
                org.phone or '-',
                org.industry or '-',
                org.total_employees
            ])
        
        headers = ['ID', 'Name', 'Email', 'Phone', 'Industry', 'Total Employees']
        click.echo(tabulate(data, headers=headers, tablefmt='grid'))

@org.command()
@click.option('--org-id', type=int, prompt='Organization ID', help='ID of the organization')
def view(org_id):
    """View organization details"""
    with app.app_context():
        org = OrganizationService.get_organization(org_id)
        if not org:
            click.secho(f'✗ Organization with ID {org_id} not found', fg='red')
            return
        
        stats = OrganizationService.get_organization_stats(org_id)
        
        click.secho(f'\n{"="*60}', fg='cyan')
        click.secho(f'Organization: {org.name}', fg='cyan', bold=True)
        click.secho(f'{"="*60}', fg='cyan')
        
        info = [
            ['ID', org.id],
            ['Name', org.name],
            ['Email', org.email],
            ['Phone', org.phone or '-'],
            ['Address', org.address or '-'],
            ['Industry', org.industry or '-'],
            ['Total Employees', org.total_employees],
            ['Created At', org.created_at.strftime('%Y-%m-%d %H:%M:%S')],
        ]
        click.echo(tabulate(info, tablefmt='simple'))
        
        click.secho(f'\nAssessment Statistics:', fg='cyan', bold=True)
        status_info = [
            ['Completed', stats['assessment_status']['completed']],
            ['Pending', stats['assessment_status']['pending']],
            ['In Progress', stats['assessment_status']['in_progress']],
            ['Failed', stats['assessment_status']['failed']],
            ['Average Score', f"{stats['average_score']:.2f}" if stats['average_score'] else '-'],
        ]
        click.echo(tabulate(status_info, tablefmt='simple'))
        click.echo()

# ===================== EMPLOYEE COMMANDS =====================

@cli.group()
def emp():
    """Employee management commands"""
    pass

@emp.command()
@click.option('--org-id', type=int, prompt='Organization ID', help='ID of the organization')
@click.option('--first-name', prompt='First name', help='Employee first name')
@click.option('--last-name', prompt='Last name', help='Employee last name')
@click.option('--email', prompt='Email', help='Employee email')
@click.option('--phone', prompt='Phone', help='Employee phone')
@click.option('--employee-id', prompt='Employee ID', help='Unique employee ID')
@click.option('--department', prompt='Department (optional)', default='', help='Department')
@click.option('--designation', prompt='Designation (optional)', default='', help='Designation')
def add(org_id, first_name, last_name, email, phone, employee_id, department, designation):
    """Add a new employee"""
    with app.app_context():
        try:
            employee = EmployeeService.add_employee(
                organization_id=org_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                employee_id=employee_id,
                department=department if department else None,
                designation=designation if designation else None
            )
            click.secho(f'✓ Employee "{employee.get_full_name()}" added successfully!', fg='green')
            click.echo(f'  Employee ID: {employee.id}')
        except ValueError as e:
            click.secho(f'✗ Error: {str(e)}', fg='red')

@emp.command()
@click.option('--org-id', type=int, prompt='Organization ID', help='ID of the organization')
def list_org_employees(org_id):
    """List all employees in an organization"""
    with app.app_context():
        employees = EmployeeService.get_employees_by_organization(org_id)
        if not employees:
            click.echo('No employees found in this organization.')
            return
        
        data = []
        for emp in employees:
            data.append([
                emp.id,
                emp.employee_id,
                emp.get_full_name(),
                emp.email,
                emp.department or '-',
                emp.status,
                f"{emp.assessment_score:.1f}" if emp.assessment_score else '-'
            ])
        
        headers = ['ID', 'Emp ID', 'Name', 'Email', 'Department', 'Status', 'Score']
        click.echo(tabulate(data, headers=headers, tablefmt='grid'))

@emp.command()
@click.option('--emp-id', type=int, prompt='Employee ID', help='ID of the employee')
def view(emp_id):
    """View employee details and status"""
    with app.app_context():
        employee = EmployeeService.get_employee(emp_id)
        if not employee:
            click.secho(f'✗ Employee with ID {emp_id} not found', fg='red')
            return
        
        status_info = EmployeeService.get_employee_status(emp_id)
        
        click.secho(f'\n{"="*60}', fg='cyan')
        click.secho(f'Employee: {status_info["name"]}', fg='cyan', bold=True)
        click.secho(f'{"="*60}', fg='cyan')
        
        info = [
            ['ID', status_info['id']],
            ['Employee ID', status_info['employee_id']],
            ['Name', status_info['name']],
            ['Email', status_info['email']],
            ['Department', status_info['department'] or '-'],
            ['Assessment Status', status_info['status']],
            ['Score', f"{status_info['score']}" if status_info['score'] else '-'],
            ['Last Assessment', status_info['last_assessment_date'] or '-'],
        ]
        click.echo(tabulate(info, tablefmt='simple'))
        
        if status_info['details']:
            click.secho(f'\nDetails:', fg='cyan', bold=True)
            click.echo(status_info['details'])
        click.echo()

@emp.command()
@click.option('--emp-id', type=int, prompt='Employee ID', help='ID of the employee')
@click.option('--status', type=click.Choice(['pending', 'in_progress', 'completed', 'failed']), 
              prompt='Assessment Status', help='Assessment status')
@click.option('--score', type=float, default=None, help='Assessment score (0-100)')
@click.option('--details', default='', help='Additional details')
def update_status(emp_id, status, score, details):
    """Update employee assessment status"""
    with app.app_context():
        try:
            employee = EmployeeService.update_employee_status(
                employee_id=emp_id,
                status=status,
                score=score,
                details=details if details else None
            )
            click.secho(f'✓ Employee status updated successfully!', fg='green')
            click.echo(f'  Status: {employee.status}')
            if employee.assessment_score:
                click.echo(f'  Score: {employee.assessment_score}')
        except ValueError as e:
            click.secho(f'✗ Error: {str(e)}', fg='red')

# ===================== DATABASE COMMANDS =====================

@cli.group()
def db():
    """Database management commands"""
    pass

@db.command()
def reset():
    """Reset database (CAUTION: Deletes all data)"""
    if click.confirm('⚠️  This will delete all data. Are you sure?', default=False):
        with app.app_context():
            from backend.database.db import reset_db
            reset_db(app)
            click.secho('✓ Database reset successfully!', fg='green')
    else:
        click.echo('Operation cancelled.')

if __name__ == '__main__':
    cli()

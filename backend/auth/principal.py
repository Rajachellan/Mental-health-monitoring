from flask_login import UserMixin


class Principal(UserMixin):
    """Flask-Login user: org admin, employee, or platform super admin."""

    def __init__(self, role, record):
        self.role = role
        self.record = record

    def get_id(self):
        return f'{self.role}:{self.record.id}'

    @property
    def org_id(self):
        if self.role == 'org':
            return self.record.id
        if self.role == 'employee':
            return self.record.organization_id
        return None

    @staticmethod
    def from_org(organization):
        if not organization:
            return None
        return Principal('org', organization)

    @staticmethod
    def from_employee(employee):
        if not employee:
            return None
        return Principal('employee', employee)

    @staticmethod
    def from_super(super_admin):
        if not super_admin:
            return None
        return Principal('super', super_admin)

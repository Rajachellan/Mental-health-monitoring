# Mental Health Monitoring System

A comprehensive tool to assess and monitor the mental health of employees in an organization.

## Features

- 🏢 **Organization Management** - Create and manage multiple organizations
- 👥 **Employee Management** - Register employees and bulk import
- 📊 **Assessment Tracking** - Track assessment status and scores
- 📈 **Statistics & Reporting** - View organization-wide and individual statistics
- 🔧 **REST API** - Full-featured REST API for integration
- 💻 **CLI Tool** - Easy-to-use command-line interface

## Project Structure

```
Mental Health Monitoring/
├── backend/
│   ├── models/              # Database models
│   │   ├── organization.py
│   │   ├── employee.py
│   │   └── assessment.py
│   ├── services/            # Business logic
│   │   ├── organization_service.py
│   │   ├── employee_service.py
│   │   └── assessment_service.py
│   ├── routes/              # API endpoints
│   │   ├── organization_routes.py
│   │   └── employee_routes.py
│   └── database/
│       └── db.py           # Database initialization
├── cli/                     # CLI commands
├── app.py                   # Flask app factory
├── cli.py                   # CLI entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Setup

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database**
   The database will be automatically created when you run the app or CLI for the first time.

## Usage

### Using the CLI Tool

#### Organization Commands

**Create a new organization:**

```bash
python cli.py org create
```

**List all organizations:**

```bash
python cli.py org list
```

**View organization details and statistics:**

```bash
python cli.py org view --org-id 1
```

#### Employee Commands

**Add an employee:**

```bash
python cli.py emp add --org-id 1
```

**List employees in an organization:**

```bash
python cli.py emp list-org-employees --org-id 1
```

**View employee details:**

```bash
python cli.py emp view --emp-id 1
```

**Update employee assessment status:**

```bash
python cli.py emp update-status --emp-id 1 --status completed --score 85
```

#### Database Commands

**Reset database (caution: deletes all data):**

```bash
python cli.py db reset
```

### Using the REST API

**Start the server:**

```bash
python app.py
```

The API will be available at `http://localhost:5000`

#### Organization Endpoints

**Create Organization**

```bash
POST /api/organizations
Content-Type: application/json

{
  "name": "Company A",
  "email": "contact@companya.com",
  "phone": "+91-9876543210",
  "address": "123 Business Street",
  "industry": "Technology"
}
```

**List Organizations**

```bash
GET /api/organizations
```

**Get Organization**

```bash
GET /api/organizations/{org_id}
```

**Get Organization Statistics**

```bash
GET /api/organizations/{org_id}/stats
```

**Update Organization**

```bash
PUT /api/organizations/{org_id}
Content-Type: application/json

{
  "phone": "+91-1234567890",
  "address": "New Address"
}
```

**Delete Organization**

```bash
DELETE /api/organizations/{org_id}
```

#### Employee Endpoints

**Add Employee**

```bash
POST /api/employees
Content-Type: application/json

{
  "organization_id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+91-9876543210",
  "employee_id": "EMP001",
  "department": "Engineering",
  "designation": "Software Engineer"
}
```

**Get Employee**

```bash
GET /api/employees/{employee_id}
```

**Get Employee Status**

```bash
GET /api/employees/{employee_id}/status
```

**Update Employee Status**

```bash
PUT /api/employees/{employee_id}/status
Content-Type: application/json

{
  "status": "completed",
  "score": 85.5,
  "details": "Good mental health indicators"
}
```

**Get Organization Employees**

```bash
GET /api/employees/organization/{org_id}
```

**Bulk Add Employees**

```bash
POST /api/employees/bulk-add
Content-Type: application/json

{
  "organization_id": 1,
  "employees": [
    {
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane@example.com",
      "phone": "+91-9876543211",
      "employee_id": "EMP002",
      "department": "HR"
    },
    {
      "first_name": "Bob",
      "last_name": "Johnson",
      "email": "bob@example.com",
      "phone": "+91-9876543212",
      "employee_id": "EMP003",
      "department": "Sales"
    }
  ]
}
```

**Delete Employee**

```bash
DELETE /api/employees/{employee_id}
```

## Database Schema

### Organizations Table

- `id`: Primary Key
- `name`: Organization name (unique)
- `email`: Contact email (unique)
- `phone`: Phone number
- `address`: Physical address
- `industry`: Industry type
- `total_employees`: Count of registered employees
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Employees Table

- `id`: Primary Key
- `organization_id`: Foreign Key to Organizations
- `first_name`: Employee's first name
- `last_name`: Employee's last name
- `email`: Employee email
- `phone`: Employee phone
- `department`: Department name
- `designation`: Job designation
- `employee_id`: Unique employee ID within organization
- `status`: Assessment status (pending, in_progress, completed, failed)
- `last_assessment_date`: Date of last assessment
- `assessment_score`: Latest assessment score (0-100)
- `assessment_status_details`: Additional assessment details
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Assessments Table

- `id`: Primary Key
- `employee_id`: Foreign Key to Employees
- `assessment_date`: When assessment was conducted
- `score`: Assessment score (0-100)
- `status`: Assessment result (good, fair, poor, critical)
- `summary`: Assessment summary
- `recommendations`: AI recommendations
- `call_duration`: Duration of AI call in seconds
- `call_status`: Status of the AI call
- `call_notes`: Notes from the call
- `created_at`: Creation timestamp

## Assessment Status Values

### Employee Status

- `pending`: Waiting for assessment
- `in_progress`: Currently being assessed
- `completed`: Assessment completed
- `failed`: Assessment failed

### Assessment Result Status

- `good`: Excellent mental health indicators
- `fair`: Moderate mental health indicators
- `poor`: Some concerning indicators
- `critical`: Serious mental health concerns

## Example Workflow

1. **Create Organization**

   ```bash
   python cli.py org create
   ```

   - Enter organization details
   - Receive organization ID (e.g., ID: 1)

2. **Add Employees**

   ```bash
   python cli.py emp add --org-id 1
   ```

   - Repeat for each employee or use bulk add endpoint

3. **View Status**

   ```bash
   python cli.py emp view --emp-id 1
   ```

   - Check initial status (should be "pending")

4. **AI Assessment** (via external system)
   - AI calling agent contacts employees
   - Updates status through API

5. **Update Assessment Results**

   ```bash
   python cli.py emp update-status --emp-id 1 --status completed --score 85
   ```

6. **View Statistics**
   ```bash
   python cli.py org view --org-id 1
   ```

   - See overall organization statistics

## Configuration

Default configuration uses SQLite database (`mental_health.db`) in the project root.

To use a different database, modify `app.py`:

```python
app = create_app(database_url='postgresql://user:password@localhost/dbname')
```

## Error Handling

The API provides meaningful error responses:

- `400 Bad Request`: Invalid input or missing required fields
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Example error response:

```json
{
  "error": "Organization 'Company A' already exists"
}
```

## Next Steps

1. Implement AI calling agent integration
2. Add authentication and authorization
3. Add email notifications
4. Create web dashboard
5. Add data export (CSV/PDF reports)
6. Implement assessment history tracking
7. Add bulk import from CSV

## Support

For issues or feature requests, please contact the development team.

## License

MIT License

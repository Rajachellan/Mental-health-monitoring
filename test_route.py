from backend.routes.web_routes import view_emps, VIEW_EMPLOYEES_PAGE
from flask import Response

# Call the function
result = view_emps()
print('Function returned:', type(result))
print('Response status:', result.status_code if hasattr(result, 'status_code') else 'N/A')
print('Content length:', len(result.data) if hasattr(result, 'data') else len(result))
print('Contains DOCTYPE:', b'DOCTYPE' in result.data if hasattr(result, 'data') else False)
print('VIEW_EMPLOYEES_PAGE length:', len(VIEW_EMPLOYEES_PAGE))

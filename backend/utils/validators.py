import re

def validate_email(email):
    if not email:
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    if not phone:
        return True
    pattern = r'^[\+\d\s\-\(\)]{8,20}$'
    return re.match(pattern, phone) is not None

def validate_name(name):
    """Supports Arabic, English, spaces, hyphens, dots"""
    if not name:
        return False
    # Arabic: \u0600-\u06FF, English: a-zA-Z, plus spaces, hyphens, dots
    pattern = r'^[a-zA-Z\u0600-\u06FF\s\-\.]{2,100}$'
    return re.match(pattern, name) is not None

def validate_password(password):
    """Password must be at least 8 chars, contain uppercase, lowercase, and number"""
    if not password:
        return False
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
    return re.match(pattern, password) is not None

def validate_task_data(data):
    if not data.get('title'):
        return False, 'Title is required'
    if len(data['title']) > 200:
        return False, 'Title too long'
    return True, None

def validate_expense_data(data):
    if not data.get('description'):
        return False, 'Description is required'
    if not data.get('amount') or float(data.get('amount', 0)) <= 0:
        return False, 'Valid amount is required'
    return True, None

def validate_event_data(data):
    if not data.get('title'):
        return False, 'Title is required'
    if not data.get('date'):
        return False, 'Date is required'
    return True, None
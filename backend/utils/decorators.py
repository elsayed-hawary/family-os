from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from backend import logger
from backend.models import db, User, Family

def require_family_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"User not found: {user_id}")
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        if not user.family_id:
            logger.warning(f"User {user_id} has no family")
            return jsonify({'success': False, 'message': 'No family found'}), 404
        
        family = Family.query.get(user.family_id)
        if not family:
            logger.warning(f"Family not found for user {user_id}")
            return jsonify({'success': False, 'message': 'Family not found'}), 404
        
        kwargs['user'] = user
        kwargs['family'] = family
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = kwargs.get('user')
            
            if not user:
                user_id = get_jwt_identity()
                user = User.query.get(user_id)
                kwargs['user'] = user
            
            if user.is_family_head:
                return f(*args, **kwargs)
            
            permissions = user.get_permissions()
            if permissions.get(permission, False):
                return f(*args, **kwargs)
            
            logger.warning(f"Permission denied for user {user.id}: {permission}")
            return jsonify({'success': False, 'message': f'Permission denied: {permission}'}), 403
        
        return decorated_function
    return decorator
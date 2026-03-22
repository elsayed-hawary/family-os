from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from backend import limiter, logger
from backend.models import db, User, Family, JoinRequest, FamilySettings
from backend.utils.validators import validate_email, validate_phone, validate_name, validate_password
from backend.services.notification_service import NotificationService
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("10 per minute")
def register():
    data = request.json
    logger.info(f"Registration attempt for {data.get('email')}")
    
    if not data.get('fullName'):
        return jsonify({'success': False, 'message': 'Full name is required'}), 400
    
    if not validate_name(data['fullName']):
        return jsonify({'success': False, 'message': 'Invalid name format'}), 400
    
    if data.get('email') and not validate_email(data['email']):
        return jsonify({'success': False, 'message': 'Invalid email format'}), 400
    
    if data.get('phone') and not validate_phone(data['phone']):
        return jsonify({'success': False, 'message': 'Invalid phone format'}), 400
    
    if data.get('password') and not validate_password(data['password']):
        return jsonify({'success': False, 'message': 'Password must be at least 8 chars with uppercase, lowercase and number'}), 400
    
    if data.get('email'):
        existing = User.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({'success': False, 'message': 'Email already registered'}), 409
    
    unique_id = User.generate_unique_id(data['fullName'])
    
    user = User(
        unique_id=unique_id,
        full_name=data['fullName'],
        email=data.get('email'),
        phone=data.get('phone'),
        role=data.get('role', 'member'),
        birth_date=datetime.fromisoformat(data['birthDate']) if data.get('birthDate') else None,
        bio=data.get('bio'),
        is_family_head=True
    )
    
    if data.get('password'):
        user.set_password(data['password'])
    
    db.session.add(user)
    db.session.flush()
    
    family = Family(
        family_code=Family.generate_family_code(),
        name=f"Семья {user.full_name}",
        created_by=user.id
    )
    db.session.add(family)
    db.session.flush()
    
    user.family_id = family.id
    
    settings = FamilySettings(family_id=family.id)
    db.session.add(settings)
    
    db.session.commit()
    user.update_last_login()
    
    access_token = create_access_token(identity=user.id)
    
    logger.info(f"User registered successfully: {unique_id}")
    
    return jsonify({
        'success': True,
        'token': access_token,
        'user': user.to_dict(include_permissions=True),
        'family': family.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.json
    identifier = data.get('identifier')
    password = data.get('password')
    
    logger.info(f"Login attempt for {identifier}")
    
    if not identifier or not password:
        return jsonify({'success': False, 'message': 'Identifier and password required'}), 400
    
    user = User.query.filter(
        (User.email == identifier) | (User.unique_id == identifier)
    ).first()
    
    if not user:
        logger.warning(f"Login failed: user not found - {identifier}")
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    if not user.check_password(password):
        logger.warning(f"Login failed: invalid password for {identifier}")
        return jsonify({'success': False, 'message': 'Invalid password'}), 401
    
    user.update_last_login()
    access_token = create_access_token(identity=user.id)
    
    logger.info(f"User logged in successfully: {user.unique_id}")
    
    return jsonify({
        'success': True,
        'token': access_token,
        'user': user.to_dict(include_permissions=True)
    })

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    return jsonify({'success': True, 'user': user.to_dict(include_permissions=True)})

@auth_bp.route('/join/<family_code>', methods=['GET'])
def get_join_info(family_code):
    family = Family.query.filter_by(family_code=family_code).first()
    
    if not family:
        return jsonify({'success': False, 'message': 'Family not found'}), 404
    
    return jsonify({
        'success': True,
        'family': {
            'name': family.name,
            'memberCount': family.member_count()
        }
    })

@auth_bp.route('/join/<family_code>', methods=['POST'])
@limiter.limit("3 per minute")
def join_family(family_code):
    data = request.json
    family = Family.query.filter_by(family_code=family_code).first()
    
    if not family:
        return jsonify({'success': False, 'message': 'Family not found'}), 404
    
    if not data.get('fullName'):
        return jsonify({'success': False, 'message': 'Full name required'}), 400
    
    if not validate_name(data['fullName']):
        return jsonify({'success': False, 'message': 'Invalid name format'}), 400
    
    if data.get('email') and not validate_email(data['email']):
        return jsonify({'success': False, 'message': 'Invalid email format'}), 400
    
    if data.get('email'):
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email:
            return jsonify({'success': False, 'message': 'Email already registered'}), 409
    
    existing = User.query.filter_by(email=data.get('email')).first()
    if existing and existing.family_id == family.id:
        return jsonify({'success': False, 'message': 'User already in this family'}), 409
    
    unique_id = User.generate_unique_id(data['fullName'])
    
    user = User(
        unique_id=unique_id,
        full_name=data['fullName'],
        email=data.get('email'),
        phone=data.get('phone'),
        role=data.get('role', 'member'),
        family_id=family.id,
        is_family_head=False
    )
    
    if data.get('password'):
        if not validate_password(data['password']):
            return jsonify({'success': False, 'message': 'Password must be at least 8 chars with uppercase, lowercase and number'}), 400
        user.set_password(data['password'])
    
    db.session.add(user)
    db.session.flush()
    
    join_request = JoinRequest(
        family_id=family.id,
        user_id=user.id,
        requested_role=data.get('role', 'member')
    )
    db.session.add(join_request)
    
    db.session.commit()
    
    family_head = User.query.get(family.created_by)
    if family_head:
        NotificationService.add_notification(
            user_id=family_head.id,
            title='👨‍👩‍👧 Новая заявка',
            message=f'{user.full_name} хочет присоединиться к семье',
            type='join_request',
            related_id=join_request.id
        )
    
    access_token = create_access_token(identity=user.id)
    
    logger.info(f"User joined family via link: {user.unique_id} -> {family.family_code}")
    
    return jsonify({
        'success': True,
        'token': access_token,
        'user': user.to_dict(),
        'pendingApproval': True
    })

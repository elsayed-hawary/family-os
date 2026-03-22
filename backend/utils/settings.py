from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import logger
from backend.models import db, User, Family, FamilySettings
from backend.utils.decorators import require_family_access, require_permission

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('', methods=['GET'])
@jwt_required()
@require_family_access
def get_settings(user, family):
    settings = family.settings
    if not settings:
        settings = FamilySettings(family_id=family.id)
        db.session.add(settings)
        db.session.commit()
    
    return jsonify({'success': True, 'settings': settings.to_dict()})

@settings_bp.route('', methods=['PUT'])
@jwt_required()
@require_family_access
@require_permission('can_manage_settings')
def update_settings(user, family):
    data = request.json
    settings = family.settings
    
    if not settings:
        settings = FamilySettings(family_id=family.id)
        db.session.add(settings)
    
    if 'currency' in data:
        settings.currency = data['currency']
    if 'homeAddress' in data:
        settings.home_address = data['homeAddress']
    if 'monthlyBudget' in data:
        settings.monthly_budget = data['monthlyBudget']
    
    db.session.commit()
    logger.info(f"Settings updated for family {family.id}")
    
    return jsonify({'success': True, 'settings': settings.to_dict()})

@settings_bp.route('/sections', methods=['PUT'])
@jwt_required()
@require_family_access
@require_permission('can_manage_settings')
def update_sections(user, family):
    data = request.json
    settings = family.settings
    
    if not settings:
        settings = FamilySettings(family_id=family.id)
        db.session.add(settings)
    
    if 'sections' in data:
        settings.sections_visibility = data['sections']
    
    db.session.commit()
    
    return jsonify({'success': True, 'sections': settings.sections_visibility})

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import logger
from backend.models import db, User, Notification
from backend.services.notification_service import NotificationService

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(50).all()
    
    return jsonify({'success': True, 'notifications': [n.to_dict() for n in notifications]})

@notifications_bp.route('/unread/count', methods=['GET'])
@jwt_required()
def get_unread_count():
    user_id = get_jwt_identity()
    count = NotificationService.get_unread_count(user_id)
    return jsonify({'success': True, 'count': count})

@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_read(notification_id):
    user_id = get_jwt_identity()
    success = NotificationService.mark_as_read(notification_id, user_id)
    return jsonify({'success': success})

@notifications_bp.route('/read-all', methods=['POST'])
@jwt_required()
def mark_all_read():
    user_id = get_jwt_identity()
    NotificationService.mark_all_read(user_id)
    return jsonify({'success': True})

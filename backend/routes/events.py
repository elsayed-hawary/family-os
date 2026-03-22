from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import logger
from backend.models import db, User, Event
from backend.utils.decorators import require_family_access, require_permission
from backend.utils.validators import validate_event_data
from datetime import datetime

events_bp = Blueprint('events', __name__)

@events_bp.route('', methods=['GET'])
@jwt_required()
@require_family_access
def get_events(user, family):
    events = Event.query.filter_by(family_id=family.id).order_by(Event.date.asc()).all()
    return jsonify({'success': True, 'events': [e.to_dict() for e in events]})

@events_bp.route('', methods=['POST'])
@jwt_required()
@require_family_access
@require_permission('can_manage_events')
def create_event(user, family):
    data = request.json
    logger.info(f"Creating event for family {family.id}")
    
    is_valid, error = validate_event_data(data)
    if not is_valid:
        return jsonify({'success': False, 'message': error}), 400
    
    event = Event(
        title=data['title'],
        description=data.get('description'),
        date=datetime.fromisoformat(data['date']),
        color=data.get('color', '#667eea'),
        reminder_type=data.get('reminderType', 'days_before'),
        reminder_days=data.get('reminderDays', 5),
        family_id=family.id,
        created_by=user.id
    )
    
    db.session.add(event)
    db.session.commit()
    
    logger.info(f"Event created: {event.id}")
    
    return jsonify({'success': True, 'event': event.to_dict()}), 201

@events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
@require_family_access
def delete_event(user, family, event_id):
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'success': False, 'message': 'Event not found'}), 404
    
    if event.family_id != family.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    if event.created_by != user.id and not user.is_family_head:
        return jsonify({'success': False, 'message': 'Only creator or family head can delete'}), 403
    
    db.session.delete(event)
    db.session.commit()
    logger.info(f"Event {event_id} deleted")
    
    return jsonify({'success': True})

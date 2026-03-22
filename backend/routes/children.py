from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import logger
from backend.models import db, User, Child, ChildTask, Reward
from backend.utils.decorators import require_family_access, require_permission
from datetime import datetime

children_bp = Blueprint('children', __name__)

@children_bp.route('', methods=['GET'])
@jwt_required()
@require_family_access
def get_children(user, family):
    children = Child.query.filter_by(family_id=family.id).all()
    return jsonify({'success': True, 'children': [c.to_dict() for c in children]})

@children_bp.route('', methods=['POST'])
@jwt_required()
@require_family_access
@require_permission('can_manage_children')
def create_child(user, family):
    data = request.json
    
    if not data.get('name'):
        return jsonify({'success': False, 'message': 'Name is required'}), 400
    
    child = Child(
        name=data['name'],
        birth_date=datetime.fromisoformat(data['birthDate']) if data.get('birthDate') else None,
        family_id=family.id,
        study_data=data.get('studyData', {}),
        health_data=data.get('healthData', {}),
        activities=data.get('activities', [])
    )
    
    db.session.add(child)
    db.session.commit()
    
    logger.info(f"Child created: {child.id}")
    
    return jsonify({'success': True, 'child': child.to_dict()}), 201

@children_bp.route('/<int:child_id>', methods=['PUT'])
@jwt_required()
@require_family_access
def update_child(user, family, child_id):
    child = Child.query.get(child_id)
    
    if not child or child.family_id != family.id:
        return jsonify({'success': False, 'message': 'Child not found'}), 404
    
    if not user.is_family_head:
        return jsonify({'success': False, 'message': 'Only family head can edit children'}), 403
    
    data = request.json
    
    for key in ['name', 'birth_date', 'study_data', 'health_data', 'activities']:
        if key in data:
            setattr(child, key, data[key])
    
    db.session.commit()
    
    return jsonify({'success': True, 'child': child.to_dict()})

@children_bp.route('/<int:child_id>', methods=['DELETE'])
@jwt_required()
@require_family_access
def delete_child(user, family, child_id):
    child = Child.query.get(child_id)
    
    if not child or child.family_id != family.id:
        return jsonify({'success': False, 'message': 'Child not found'}), 404
    
    if not user.is_family_head:
        return jsonify({'success': False, 'message': 'Only family head can delete children'}), 403
    
    db.session.delete(child)
    db.session.commit()
    
    return jsonify({'success': True})

# Child Tasks
@children_bp.route('/<int:child_id>/tasks', methods=['GET'])
@jwt_required()
@require_family_access
def get_child_tasks(user, family, child_id):
    child = Child.query.get(child_id)
    if not child or child.family_id != family.id:
        return jsonify({'success': False, 'message': 'Child not found'}), 404
    
    tasks = ChildTask.query.filter_by(child_id=child_id).all()
    return jsonify({'success': True, 'tasks': [t.to_dict() for t in tasks]})

@children_bp.route('/<int:child_id>/tasks', methods=['POST'])
@jwt_required()
@require_family_access
@require_permission('can_manage_children')
def create_child_task(user, family, child_id):
    child = Child.query.get(child_id)
    if not child or child.family_id != family.id:
        return jsonify({'success': False, 'message': 'Child not found'}), 404
    
    data = request.json
    
    if not data.get('title'):
        return jsonify({'success': False, 'message': 'Title is required'}), 400
    
    task = ChildTask(
        child_id=child_id,
        title=data['title'],
        description=data.get('description'),
        points=data.get('points', 10),
        due_date=datetime.fromisoformat(data['dueDate']) if data.get('dueDate') else None
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({'success': True, 'task': task.to_dict()}), 201

@children_bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
@jwt_required()
@require_family_access
def complete_child_task(user, family, task_id):
    task = ChildTask.query.get(task_id)
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'}), 404
    
    child = Child.query.get(task.child_id)
    if not child or child.family_id != family.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    if task.completed:
        return jsonify({'success': False, 'message': 'Task already completed'}), 400
    
    task.completed = True
    task.completed_at = datetime.utcnow()
    child.total_points += task.points
    
    db.session.commit()
    
    return jsonify({'success': True, 'task': task.to_dict(), 'totalPoints': child.total_points})

# Rewards
@children_bp.route('/<int:child_id>/rewards', methods=['GET'])
@jwt_required()
@require_family_access
def get_rewards(user, family, child_id):
    child = Child.query.get(child_id)
    if not child or child.family_id != family.id:
        return jsonify({'success': False, 'message': 'Child not found'}), 404
    
    rewards = Reward.query.filter_by(child_id=child_id).all()
    return jsonify({'success': True, 'rewards': [r.to_dict() for r in rewards]})

@children_bp.route('/<int:child_id>/rewards', methods=['POST'])
@jwt_required()
@require_family_access
@require_permission('can_manage_children')
def create_reward(user, family, child_id):
    child = Child.query.get(child_id)
    if not child or child.family_id != family.id:
        return jsonify({'success': False, 'message': 'Child not found'}), 404
    
    data = request.json
    
    if not data.get('title') or not data.get('pointsCost'):
        return jsonify({'success': False, 'message': 'Title and points cost required'}), 400
    
    reward = Reward(
        child_id=child_id,
        title=data['title'],
        points_cost=data['pointsCost']
    )
    
    db.session.add(reward)
    db.session.commit()
    
    return jsonify({'success': True, 'reward': reward.to_dict()}), 201

@children_bp.route('/rewards/<int:reward_id>/claim', methods=['POST'])
@jwt_required()
@require_family_access
def claim_reward(user, family, reward_id):
    reward = Reward.query.get(reward_id)
    if not reward:
        return jsonify({'success': False, 'message': 'Reward not found'}), 404
    
    child = Child.query.get(reward.child_id)
    if not child or child.family_id != family.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    if reward.claimed:
        return jsonify({'success': False, 'message': 'Reward already claimed'}), 400
    
    if child.total_points < reward.points_cost:
        return jsonify({'success': False, 'message': 'Not enough points'}), 400
    
    reward.claimed = True
    reward.claimed_at = datetime.utcnow()
    child.total_points -= reward.points_cost
    
    db.session.commit()
    
    return jsonify({'success': True, 'reward': reward.to_dict(), 'totalPoints': child.total_points})

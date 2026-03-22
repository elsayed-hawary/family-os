from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import logger
from backend.models import db, User, Task
from backend.services.notification_service import NotificationService
from backend.utils.decorators import require_family_access, require_permission
from backend.utils.validators import validate_task_data
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('', methods=['GET'])
@jwt_required()
@require_family_access
def get_tasks(user, family):
    tasks = Task.query.filter_by(family_id=family.id).order_by(Task.created_at.desc()).all()
    return jsonify({'success': True, 'tasks': [t.to_dict() for t in tasks]})

@tasks_bp.route('', methods=['POST'])
@jwt_required()
@require_family_access
@require_permission('can_manage_tasks')
def create_task(user, family):
    data = request.json
    logger.info(f"Creating task for family {family.id} by user {user.id}")
    
    is_valid, error = validate_task_data(data)
    if not is_valid:
        return jsonify({'success': False, 'message': error}), 400
    
    assignee_id = data.get('assigneeId')
    assignee = None
    if assignee_id:
        assignee = User.query.get(assignee_id)
        if not assignee or assignee.family_id != family.id:
            return jsonify({'success': False, 'message': 'Invalid assignee'}), 400
    
    task = Task(
        title=data['title'],
        description=data.get('description'),
        assignee_id=assignee_id,
        created_by=user.id,
        family_id=family.id,
        priority=data.get('priority', 'medium'),
        due_date=datetime.fromisoformat(data['dueDate']) if data.get('dueDate') else None
    )
    
    db.session.add(task)
    db.session.flush()
    
    if assignee_id and assignee_id != user.id:
        NotificationService.add_notification(
            user_id=assignee_id,
            title='📋 Новая задача',
            message=f'Вам назначена задача: {task.title}',
            type='task',
            related_id=task.id
        )
    
    db.session.commit()
    logger.info(f"Task created: {task.id}")
    
    return jsonify({'success': True, 'task': task.to_dict()}), 201

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
@require_family_access
def update_task(user, family, task_id):
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'}), 404
    
    if task.family_id != family.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    if task.created_by != user.id and not user.is_family_head:
        return jsonify({'success': False, 'message': 'Only creator or family head can edit'}), 403
    
    data = request.json
    logger.info(f"Updating task {task_id}")
    
    if data.get('status') == 'completed' and task.status != 'completed':
        task.complete()
        if task.created_by != user.id:
            NotificationService.add_notification(
                user_id=task.created_by,
                title='✅ Задача выполнена',
                message=f'Задача "{task.title}" выполнена',
                type='task',
                related_id=task.id
            )
    
    for key in ['title', 'description', 'priority']:
        if key in data:
            setattr(task, key, data[key])
    
    if 'assigneeId' in data:
        assignee_id = data['assigneeId']
        if assignee_id:
            assignee = User.query.get(assignee_id)
            if assignee and assignee.family_id == family.id:
                task.assignee_id = assignee_id
        else:
            task.assignee_id = None
    
    if 'dueDate' in data and data['dueDate']:
        task.due_date = datetime.fromisoformat(data['dueDate'])
    
    db.session.commit()
    logger.info(f"Task {task_id} updated")
    
    return jsonify({'success': True, 'task': task.to_dict()})

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
@require_family_access
def delete_task(user, family, task_id):
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'}), 404
    
    if task.family_id != family.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    if task.created_by != user.id and not user.is_family_head:
        return jsonify({'success': False, 'message': 'Only creator or family head can delete'}), 403
    
    db.session.delete(task)
    db.session.commit()
    logger.info(f"Task {task_id} deleted")
    
    return jsonify({'success': True})

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import logger
from backend.models import db, User, Expense
from backend.utils.decorators import require_family_access, require_permission
from backend.utils.validators import validate_expense_data
from datetime import datetime

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('', methods=['GET'])
@jwt_required()
@require_family_access
def get_expenses(user, family):
    expenses = Expense.query.filter_by(family_id=family.id).order_by(Expense.date.desc()).all()
    return jsonify({'success': True, 'expenses': [e.to_dict() for e in expenses]})

@expenses_bp.route('', methods=['POST'])
@jwt_required()
@require_family_access
@require_permission('can_manage_expenses')
def create_expense(user, family):
    data = request.json
    logger.info(f"Creating expense for family {family.id}")
    
    is_valid, error = validate_expense_data(data)
    if not is_valid:
        return jsonify({'success': False, 'message': error}), 400
    
    expense = Expense(
        description=data['description'],
        amount=data['amount'],
        category=data.get('category', 'Другое'),
        family_id=family.id,
        user_id=user.id,
        notes=data.get('notes'),
        date=datetime.fromisoformat(data['date']) if data.get('date') else datetime.utcnow()
    )
    
    db.session.add(expense)
    db.session.commit()
    
    logger.info(f"Expense created: {expense.id}")
    
    return jsonify({'success': True, 'expense': expense.to_dict()}), 201

@expenses_bp.route('/<int:expense_id>', methods=['DELETE'])
@jwt_required()
@require_family_access
def delete_expense(user, family, expense_id):
    expense = Expense.query.get(expense_id)
    
    if not expense:
        return jsonify({'success': False, 'message': 'Expense not found'}), 404
    
    if expense.family_id != family.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    if expense.user_id != user.id and not user.is_family_head:
        return jsonify({'success': False, 'message': 'Only creator or family head can delete'}), 403
    
    db.session.delete(expense)
    db.session.commit()
    logger.info(f"Expense {expense_id} deleted")
    
    return jsonify({'success': True})

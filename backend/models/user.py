# backend/models/user.py
from backend.models import db
from datetime import datetime
import bcrypt
import secrets
import logging

logger = logging.getLogger(__name__)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, index=True)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50), nullable=False, default='member')
    password_hash = db.Column(db.String(128))
    birth_date = db.Column(db.Date)
    bio = db.Column(db.Text)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), index=True)
    is_family_head = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    family = db.relationship('Family', back_populates='members', foreign_keys=[family_id])
    tasks_assigned = db.relationship('Task', foreign_keys='Task.assignee_id', back_populates='assignee_user')
    tasks_created = db.relationship('Task', foreign_keys='Task.created_by', back_populates='creator')
    expenses = db.relationship('Expense', back_populates='user')
    notifications = db.relationship('Notification', back_populates='user', lazy='dynamic')
    
    @staticmethod
    def generate_unique_id(name):
        prefix = name[:2].upper() if name else "US"
        suffix = secrets.token_hex(3).upper()
        return f"FAM-{prefix}{suffix}"
    
    def set_password(self, password):
        if not password:
            return
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        if not self.password_hash or not password:
            return False
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception:
            return False
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_permissions=False):
        result = {
            'id': self.id,
            'uniqueId': self.unique_id,
            'fullName': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'birthDate': self.birth_date.isoformat() if self.birth_date else None,
            'bio': self.bio,
            'familyId': self.family_id,
            'isFamilyHead': self.is_family_head,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'lastLogin': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_permissions:
            result['permissions'] = self.get_permissions()
        
        return result
    
    def get_permissions(self):
        if self.is_family_head:
            return {
                'can_manage_tasks': True, 'can_manage_expenses': True,
                'can_manage_events': True, 'can_manage_children': True,
                'can_manage_members': True, 'can_approve_requests': True,
                'can_manage_settings': True, 'can_view_all': True
            }
        return {
            'can_manage_tasks': True,
            'can_manage_expenses': True,
            'can_manage_events': True,
            'can_manage_children': False,
            'can_manage_members': False,
            'can_approve_requests': False,
            'can_manage_settings': False,
            'can_view_all': True
        }
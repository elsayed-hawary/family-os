from backend.models import db
from datetime import datetime
import secrets
import string

class Family(db.Model):
    __tablename__ = 'families'
    
    id = db.Column(db.Integer, primary_key=True)
    family_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('User', back_populates='family', foreign_keys='User.family_id', lazy='dynamic')
    tasks = db.relationship('Task', back_populates='family', lazy='dynamic')
    expenses = db.relationship('Expense', back_populates='family', lazy='dynamic')
    events = db.relationship('Event', back_populates='family', lazy='dynamic')
    children = db.relationship('Child', back_populates='family', lazy='dynamic')
    recurring_expenses = db.relationship('RecurringExpense', back_populates='family', lazy='dynamic')
    join_requests = db.relationship('JoinRequest', back_populates='family', lazy='dynamic')
    settings = db.relationship('FamilySettings', back_populates='family', uselist=False, lazy='joined')
    
    @staticmethod
    def generate_family_code():
        return 'FAMILY-' + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    
    def member_count(self):
        return self.members.count()
    
    def to_dict(self):
        return {
            'id': self.id,
            'familyCode': self.family_code,
            'name': self.name,
            'createdBy': self.created_by,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'memberCount': self.member_count()
        }
    
    def get_join_link(self, base_url):
        return f"{base_url}/join/{self.family_code}"

class JoinRequest(db.Model):
    __tablename__ = 'join_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    requested_role = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    family = db.relationship('Family', back_populates='join_requests')
    user = db.relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'familyId': self.family_id,
            'userId': self.user_id,
            'userName': self.user.full_name if self.user else None,
            'requestedRole': self.requested_role,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

class FamilySettings(db.Model):
    __tablename__ = 'family_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), unique=True, index=True)
    currency = db.Column(db.String(10), default='₽')
    home_address = db.Column(db.String(200))
    monthly_budget = db.Column(db.Float, default=0)
    sections_visibility = db.Column(db.JSON, default=lambda: {
        'tasks': True, 'shopping': True, 'expenses': True,
        'events': True, 'schedule': True, 'children': True,
        'recurring': True, 'chat': True, 'location': True
    })
    notification_settings = db.Column(db.JSON, default=lambda: {
        'task_reminders': True, 'event_reminders': True,
        'daily_reminders': True, 'expense_alerts': True
    })
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    family = db.relationship('Family', back_populates='settings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'familyId': self.family_id,
            'currency': self.currency,
            'homeAddress': self.home_address,
            'monthlyBudget': self.monthly_budget,
            'sectionsVisibility': self.sections_visibility,
            'notificationSettings': self.notification_settings
        }
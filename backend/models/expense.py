# backend/models/expense.py
from backend.models import db
from datetime import datetime

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    family = db.relationship('Family', back_populates='expenses')
    user = db.relationship('User', back_populates='expenses')
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'familyId': self.family_id,
            'userId': self.user_id,
            'userName': self.user.full_name if self.user else None,
            'date': self.date.isoformat() if self.date else None,
            'notes': self.notes
        }

class RecurringExpense(db.Model):
    __tablename__ = 'recurring_expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    frequency = db.Column(db.String(20))
    day_of_month = db.Column(db.Integer)
    day_of_week = db.Column(db.Integer)
    active = db.Column(db.Boolean, default=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    family = db.relationship('Family', back_populates='recurring_expenses')
# backend/models/child.py
from backend.models import db
from datetime import datetime

class Child(db.Model):
    __tablename__ = 'children'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'))
    study_data = db.Column(db.JSON, default={})
    health_data = db.Column(db.JSON, default={})
    activities = db.Column(db.JSON, default=[])
    total_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    family = db.relationship('Family', back_populates='children')
    daily_tasks = db.relationship('ChildTask', back_populates='child')
    rewards = db.relationship('Reward', back_populates='child')
    
    def to_dict(self):
        age = None
        if self.birth_date:
            today = datetime.now().date()
            age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        
        return {
            'id': self.id,
            'name': self.name,
            'birthDate': self.birth_date.isoformat() if self.birth_date else None,
            'age': age,
            'familyId': self.family_id,
            'studyData': self.study_data,
            'healthData': self.health_data,
            'activities': self.activities,
            'totalPoints': self.total_points
        }

class ChildTask(db.Model):
    __tablename__ = 'child_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    points = db.Column(db.Integer, default=10)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    child = db.relationship('Child', back_populates='daily_tasks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'childId': self.child_id,
            'title': self.title,
            'description': self.description,
            'points': self.points,
            'completed': self.completed,
            'dueDate': self.due_date.isoformat() if self.due_date else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None
        }

class Reward(db.Model):
    __tablename__ = 'rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'))
    title = db.Column(db.String(200), nullable=False)
    points_cost = db.Column(db.Integer, nullable=False)
    claimed = db.Column(db.Boolean, default=False)
    claimed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    child = db.relationship('Child', back_populates='rewards')
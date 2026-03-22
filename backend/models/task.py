from backend.models import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), index=True)
    status = db.Column(db.String(20), default='pending', index=True)
    priority = db.Column(db.String(10), default='medium')
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    assignee_user = db.relationship('User', foreign_keys=[assignee_id], back_populates='tasks_assigned')
    creator = db.relationship('User', foreign_keys=[created_by], back_populates='tasks_created')
    family = db.relationship('Family', back_populates='tasks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'assigneeId': self.assignee_id,
            'assigneeName': self.assignee_user.full_name if self.assignee_user else None,
            'createdBy': self.created_by,
            'creatorName': self.creator.full_name if self.creator else None,
            'familyId': self.family_id,
            'status': self.status,
            'priority': self.priority,
            'dueDate': self.due_date.isoformat() if self.due_date else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
    
    def complete(self):
        self.status = 'completed'
        self.completed_at = datetime.utcnow()

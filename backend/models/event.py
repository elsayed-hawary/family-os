from backend.models import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    color = db.Column(db.String(20), default='#667eea')
    reminder_type = db.Column(db.String(20), default='days_before')
    reminder_days = db.Column(db.Integer, default=5)
    reminder_sent = db.Column(db.Boolean, default=False)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    family = db.relationship('Family', back_populates='events')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'color': self.color,
            'reminderType': self.reminder_type,
            'reminderDays': self.reminder_days,
            'familyId': self.family_id,
            'createdBy': self.created_by,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index

db = SQLAlchemy()

# Import all models to ensure they are registered
from backend.models.user import User
from backend.models.family import Family, JoinRequest, FamilySettings
from backend.models.task import Task
from backend.models.expense import Expense, RecurringExpense
from backend.models.event import Event
from backend.models.child import Child, ChildTask, Reward
from backend.models.notification import Notification

# Create indexes for performance
Index('idx_user_email', User.email)
Index('idx_user_family_id', User.family_id)
Index('idx_task_family_id', Task.family_id)
Index('idx_expense_family_id', Expense.family_id)
Index('idx_event_family_id', Event.family_id)
Index('idx_notification_user_id', Notification.user_id)
Index('idx_notification_read', Notification.read)

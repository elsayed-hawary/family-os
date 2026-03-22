# backend/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models
from backend.models.user import User
from backend.models.family import Family, JoinRequest, FamilySettings
from backend.models.task import Task
from backend.models.expense import Expense, RecurringExpense
from backend.models.event import Event
from backend.models.child import Child, ChildTask, Reward
from backend.models.notification import Notification
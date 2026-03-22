# backend/services/notification_service.py
from backend.models import db, Notification
from backend.events.sse import send_notification
from backend import logger
import json
from datetime import datetime

class NotificationService:
    @staticmethod
    def add_notification(user_id, title, message, type='info', related_id=None):
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=type,
                related_id=related_id
            )
            db.session.add(notification)
            db.session.flush()
            
            notification_data = {
                'id': notification.id,
                'title': title,
                'message': message,
                'type': type,
                'relatedId': related_id,
                'createdAt': datetime.utcnow().isoformat()
            }
            
            send_notification(user_id, notification_data)
            logger.debug(f"Notification added for user {user_id}: {title}")
            
            return notification
        except Exception as e:
            logger.error(f"Failed to add notification: {e}")
            raise
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.read = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def mark_all_read(user_id):
        count = Notification.query.filter_by(user_id=user_id, read=False).update({'read': True})
        db.session.commit()
        return count
    
    @staticmethod
    def get_unread_count(user_id):
        return Notification.query.filter_by(user_id=user_id, read=False).count()
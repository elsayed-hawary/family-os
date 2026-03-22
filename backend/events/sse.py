from flask import Blueprint, Response, jsonify, stream_with_context, request
from flask_jwt_extended import decode_token
import queue
import logging
import json

logger = logging.getLogger(__name__)

sse_bp = Blueprint('sse', __name__)

# Store active connections: user_id -> queue
connections = {}

def event_stream(user_id):
    """Generate SSE events for a user"""
    if user_id not in connections:
        connections[user_id] = queue.Queue()
    
    user_queue = connections[user_id]
    logger.info(f"SSE connection established for user {user_id}")
    
    try:
        while True:
            try:
                event = user_queue.get(timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
            except queue.Empty:
                yield f": heartbeat\n\n"
    except GeneratorExit:
        logger.info(f"SSE connection closed for user {user_id}")
        if user_id in connections:
            del connections[user_id]

def send_notification(user_id, notification_data):
    """Send notification to a specific user"""
    if user_id in connections:
        connections[user_id].put(notification_data)
        logger.debug(f"Notification sent to user {user_id}")
    else:
        logger.debug(f"User {user_id} not connected")

@sse_bp.route('/stream')
def stream():
    """SSE endpoint - token passed as query parameter"""
    token = request.args.get('token')
    
    if not token:
        logger.warning("SSE connection attempt without token")
        return jsonify({'success': False, 'message': 'Missing token'}), 401
    
    try:
        decoded = decode_token(token)
        user_id = decoded['sub']
        logger.info(f"SSE connection authenticated for user {user_id}")
    except Exception as e:
        logger.error(f"Invalid token for SSE: {e}")
        return jsonify({'success': False, 'message': 'Invalid token'}), 401
    
    return Response(
        stream_with_context(event_stream(user_id)),
        mimetype="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )
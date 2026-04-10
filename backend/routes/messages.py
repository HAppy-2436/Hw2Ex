from flask import Blueprint, request, jsonify
from models import db, Conversation, Message

bp = Blueprint('messages', __name__, url_prefix='/api/ai/conversations')


@bp.route('/<int:conversation_id>/messages', methods=['GET'])
def get_conversation_messages(conversation_id):
    """获取对话消息"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    messages = conversation.messages.order_by(Message.created_at.asc()).all()
    return jsonify([msg.to_dict() for msg in messages])


@bp.route('/<int:conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    """发送消息"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    data = request.get_json()
    
    if 'role' not in data or 'content' not in data:
        return jsonify({'error': 'role and content are required'}), 400
    
    valid_roles = ['user', 'assistant', 'system']
    if data['role'] not in valid_roles:
        return jsonify({'error': f'role must be one of: {", ".join(valid_roles)}'}), 400
    
    message = Message(
        conversation_id=conversation_id,
        role=data['role'],
        content=data['content']
    )
    
    # 更新对话的 updated_at 时间戳
    conversation.updated_at = db.func.now()
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify(message.to_dict()), 201

from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, Conversation, KnowledgeNode, Message

bp = Blueprint('conversations', __name__, url_prefix='/api/ai/conversations')


@bp.route('', methods=['GET'])
def get_conversations():
    """获取对话历史（支持 node_id, type 过滤）"""
    node_id = request.args.get('node_id', type=int)
    conversation_type = request.args.get('type')
    
    query = Conversation.query
    
    if node_id:
        query = query.filter_by(node_id=node_id)
    
    if conversation_type:
        query = query.filter_by(conversation_type=conversation_type)
    
    conversations = query.order_by(Conversation.updated_at.desc()).all()
    return jsonify([conv.to_dict() for conv in conversations])


@bp.route('', methods=['POST'])
def create_conversation():
    """创建新对话"""
    data = request.get_json() or {}
    
    node_id = data.get('node_id')
    conversation_type = data.get('type', 'general')
    
    if node_id:
        node = KnowledgeNode.query.get(node_id)
        if not node:
            return jsonify({'error': 'Knowledge node not found'}), 404
    
    conversation = Conversation(
        node_id=node_id,
        conversation_type=conversation_type
    )
    
    db.session.add(conversation)
    db.session.commit()
    
    return jsonify(conversation.to_dict()), 201


@bp.route('/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """获取对话详情（包含消息列表）"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    result = conversation.to_dict()
    result['messages'] = [msg.to_dict() for msg in conversation.messages.order_by(Message.created_at.asc()).all()]
    
    return jsonify(result)


@bp.route('/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """删除对话"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    db.session.delete(conversation)
    db.session.commit()
    
    return jsonify({'message': 'Conversation deleted successfully'}), 200

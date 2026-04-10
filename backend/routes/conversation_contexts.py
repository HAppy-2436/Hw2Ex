from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models import db, ConversationContext
import uuid

bp = Blueprint('conversation_contexts', __name__, url_prefix='/api/ai')


def generate_session_id():
    """生成新的会话ID"""
    return f"sess_{uuid.uuid4().hex[:16]}"


def cleanup_expired_contexts():
    """清理过期上下文"""
    expired = ConversationContext.query.filter(
        ConversationContext.expires_at < datetime.utcnow()
    ).all()
    count = len(expired)
    for ctx in expired:
        db.session.delete(ctx)
    db.session.commit()
    return count


# 启动时清理过期上下文
@bp.before_app_request
def init_cleanup():
    """在请求前清理过期上下文（最多每10次请求清理一次）"""
    from flask import g
    if not hasattr(g, 'cleanup_done'):
        cleanup_expired_contexts()
        g.cleanup_done = True


@bp.route('/contexts', methods=['GET'])
def get_contexts():
    """
    获取对话上下文列表
    
    Query params:
        - user_id: int (optional)
        - conversation_type: str (optional)
        - include_expired: bool (default false)
    
    Returns: {
        "contexts": [ConversationContext]
    }
    """
    try:
        user_id = request.args.get('user_id', type=int)
        conversation_type = request.args.get('conversation_type')
        include_expired = request.args.get('include_expired', 'false').lower() == 'true'
        
        query = ConversationContext.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        if conversation_type:
            query = query.filter_by(conversation_type=conversation_type)
        if not include_expired:
            query = query.filter(ConversationContext.expires_at > datetime.utcnow())
        
        contexts = query.order_by(ConversationContext.updated_at.desc()).all()
        
        return jsonify({
            'contexts': [ctx.to_dict() for ctx in contexts],
            'total': len(contexts)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/contexts/<int:context_id>', methods=['GET'])
def get_context_detail(context_id):
    """
    获取上下文详情
    
    Returns: {
        "context": ConversationContext
    }
    """
    try:
        context = ConversationContext.query.get_or_404(context_id)
        return jsonify({'context': context.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/contexts', methods=['POST'])
def create_context():
    """
    创建对话上下文（新对话开始时调用）
    
    Body: {
        "user_id": int (optional),
        "conversation_type": str,  # learning/homework/review
        "scope_type": str,         # node/chapter/subject
        "scope_id": int,
        "context_summary": object,
        "explanation_depth_level": int (default 1)
    }
    
    Returns: {
        "context": ConversationContext,
        "session_id": str  # 新生成的会话ID
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400

        if 'conversation_type' not in data:
            return jsonify({'error': 'conversation_type 是必填参数'}), 400

        session_id = generate_session_id()
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        context = ConversationContext(
            user_id=data.get('user_id'),
            session_id=session_id,
            conversation_type=data['conversation_type'],
            scope_type=data.get('scope_type'),
            scope_id=data.get('scope_id'),
            context_summary=data.get('context_summary', {}),
            explanation_depth_level=data.get('explanation_depth_level', 1),
            expires_at=expires_at
        )
        
        db.session.add(context)
        db.session.commit()
        
        return jsonify({
            'context': context.to_dict(),
            'session_id': session_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/contexts/<int:context_id>', methods=['PUT'])
def update_context(context_id):
    """
    更新上下文（每次AI响应后调用）
    
    Body: {
        "context_summary": object,  # 更新后的摘要
        "understanding_check_passed": bool,
        "explanation_depth_level": int (optional)
    }
    
    Returns: {
        "context": ConversationContext
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400

        context = ConversationContext.query.get_or_404(context_id)
        
        if 'context_summary' in data:
            context.context_summary = data['context_summary']
        if 'understanding_check_passed' in data:
            context.understanding_check_passed = data['understanding_check_passed']
        if 'explanation_depth_level' in data:
            context.explanation_depth_level = data['explanation_depth_level']
        
        # 更新过期时间（延续7天）
        context.expires_at = datetime.utcnow() + timedelta(days=7)
        context.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'context': context.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/contexts/<int:context_id>', methods=['DELETE'])
def delete_context(context_id):
    """
    删除过期上下文
    
    Returns: {
        "message": str,
        "deleted": bool
    }
    """
    try:
        context = ConversationContext.query.get_or_404(context_id)
        
        # 检查是否真的过期了
        if context.expires_at > datetime.utcnow():
            return jsonify({
                'error': '上下文尚未过期，无法删除',
                'expires_at': context.expires_at.isoformat()
            }), 400
        
        db.session.delete(context)
        db.session.commit()
        
        return jsonify({
            'message': '上下文已删除',
            'deleted': True
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/contexts/cleanup', methods=['POST'])
def force_cleanup():
    """
    强制清理所有过期上下文
    
    Returns: {
        "message": str,
        "deleted_count": int
    }
    """
    try:
        count = cleanup_expired_contexts()
        return jsonify({
            'message': f'已清理 {count} 条过期上下文',
            'deleted_count': count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/contexts/session/<session_id>', methods=['GET'])
def get_context_by_session(session_id):
    """
    通过session_id获取上下文
    
    Returns: {
        "context": ConversationContext
    }
    """
    try:
        context = ConversationContext.query.filter_by(session_id=session_id).first()
        if not context:
            return jsonify({'error': '上下文不存在'}), 404
        
        return jsonify({'context': context.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

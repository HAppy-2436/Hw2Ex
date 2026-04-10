from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, LearningRecord, KnowledgeNode

bp = Blueprint('learning_records', __name__, url_prefix='/api/learn/records')


@bp.route('', methods=['GET'])
def get_learning_records():
    """获取学习记录（支持 node_id, date 过滤）"""
    node_id = request.args.get('node_id', type=int)
    date = request.args.get('date')  # format: YYYY-MM-DD
    
    query = LearningRecord.query
    
    if node_id:
        query = query.filter_by(node_id=node_id)
    
    if date:
        try:
            filter_date = datetime.strptime(date, '%Y-%m-%d').date()
            query = query.filter(
                db.func.date(LearningRecord.created_at) == filter_date
            )
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    records = query.order_by(LearningRecord.created_at.desc()).all()
    return jsonify([record.to_dict() for record in records])


@bp.route('', methods=['POST'])
def create_learning_record():
    """创建学习记录"""
    data = request.get_json()
    
    if 'node_id' not in data:
        return jsonify({'error': 'node_id is required'}), 400
    
    node = KnowledgeNode.query.get(data['node_id'])
    if not node:
        return jsonify({'error': 'Knowledge node not found'}), 404
    
    duration = data.get('duration', 0)
    notes = data.get('notes', '')
    self_rating = data.get('self_rating')
    
    if self_rating is not None and (self_rating < 1 or self_rating > 5):
        return jsonify({'error': 'self_rating must be between 1 and 5'}), 400
    
    record = LearningRecord(
        node_id=data['node_id'],
        duration=duration,
        notes=notes,
        self_rating=self_rating
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify(record.to_dict()), 201


@bp.route('/<int:record_id>', methods=['GET'])
def get_learning_record(record_id):
    """获取学习记录详情"""
    record = LearningRecord.query.get_or_404(record_id)
    return jsonify(record.to_dict())


@bp.route('/<int:record_id>', methods=['DELETE'])
def delete_learning_record(record_id):
    """删除学习记录"""
    record = LearningRecord.query.get_or_404(record_id)
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({'message': 'Learning record deleted successfully'}), 200

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models import db, LearningRecord, KnowledgeNode, Homework
from sqlalchemy import func

bp = Blueprint('learning', __name__, url_prefix='/api/learning')

@bp.route('/records', methods=['GET'])
def get_learning_records():
    node_id = request.args.get('node_id')
    status = request.args.get('status')
    
    query = LearningRecord.query
    
    if node_id:
        query = query.filter_by(node_id=node_id)
    if status:
        query = query.filter_by(status=status)
    
    records = query.all()
    return jsonify([record.to_dict() for record in records])

@bp.route('/records', methods=['POST'])
def create_learning_record():
    data = request.get_json()
    
    if 'node_id' not in data:
        return jsonify({'error': 'node_id is required'}), 400
    
    node = KnowledgeNode.query.get(data['node_id'])
    if not node:
        return jsonify({'error': 'Knowledge node not found'}), 404
    
    existing_record = LearningRecord.query.filter_by(node_id=data['node_id']).first()
    
    if existing_record:
        record = existing_record
        record.last_reviewed = datetime.utcnow()
        record.review_count += 1
    else:
        record = LearningRecord(
            node_id=data['node_id'],
            status=data.get('status', 'learning'),
            self_rating=data.get('self_rating')
        )
        db.session.add(record)
    
    db.session.commit()
    return jsonify(record.to_dict()), 201

@bp.route('/records/<int:record_id>', methods=['GET'])
def get_learning_record(record_id):
    record = LearningRecord.query.get_or_404(record_id)
    return jsonify(record.to_dict())

@bp.route('/records/<int:record_id>', methods=['PUT'])
def update_learning_record(record_id):
    record = LearningRecord.query.get_or_404(record_id)
    data = request.get_json()
    
    if 'status' in data:
        valid_statuses = ['learning', 'reviewing', 'mastered']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'status must be one of: {", ".join(valid_statuses)}'}), 400
        record.status = data['status']
    
    if 'self_rating' in data:
        rating = data['self_rating']
        if rating is not None and (rating < 1 or rating > 5):
            return jsonify({'error': 'self_rating must be between 1 and 5'}), 400
        record.self_rating = rating
    
    if 'correct_count' in data:
        record.correct_count = data['correct_count']
    if 'total_attempts' in data:
        record.total_attempts = data['total_attempts']
    
    record.last_reviewed = datetime.utcnow()
    
    db.session.commit()
    return jsonify(record.to_dict())

@bp.route('/records/<int:record_id>/practice', methods=['POST'])
def record_practice_result(record_id):
    record = LearningRecord.query.get_or_404(record_id)
    data = request.get_json()
    
    if 'is_correct' not in data:
        return jsonify({'error': 'is_correct is required'}), 400
    
    record.total_attempts += 1
    if data['is_correct']:
        record.correct_count += 1
    
    record.last_reviewed = datetime.utcnow()
    
    if record.total_attempts >= 3:
        accuracy = record.correct_count / record.total_attempts
        if accuracy >= 0.8:
            record.status = 'mastered'
        elif accuracy >= 0.5:
            record.status = 'reviewing'
        else:
            record.status = 'learning'
    
    db.session.commit()
    return jsonify(record.to_dict())

@bp.route('/nodes/<int:node_id>/status', methods=['GET'])
def get_node_learning_status(node_id):
    record = LearningRecord.query.filter_by(node_id=node_id).first()
    
    if not record:
        return jsonify({
            'node_id': node_id,
            'status': 'not_started',
            'review_count': 0,
            'correct_count': 0,
            'total_attempts': 0,
            'accuracy': 0
        })
    
    accuracy = record.correct_count / record.total_attempts if record.total_attempts > 0 else 0
    
    return jsonify({
        'node_id': node_id,
        'status': record.status,
        'review_count': record.review_count,
        'correct_count': record.correct_count,
        'total_attempts': record.total_attempts,
        'accuracy': accuracy,
        'self_rating': record.self_rating,
        'last_reviewed': record.last_reviewed.isoformat() if record.last_reviewed else None
    })

@bp.route('/review-plan', methods=['GET'])
def get_review_plan():
    days = int(request.args.get('days', 7))
    
    from datetime import timedelta
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    records = LearningRecord.query.filter(
        LearningRecord.last_reviewed < cutoff_date,
        LearningRecord.status.in_(['learning', 'reviewing'])
    ).order_by(LearningRecord.last_reviewed).limit(20).all()
    
    plan = []
    for record in records:
        node = KnowledgeNode.query.get(record.node_id)
        if node:
            plan.append({
                'record_id': record.id,
                'node_id': node.id,
                'node_title': node.title,
                'status': record.status,
                'days_since_review': (datetime.utcnow() - record.last_reviewed).days,
                'accuracy': record.correct_count / record.total_attempts if record.total_attempts > 0 else 0
            })
    
    return jsonify(plan)

@bp.route('/stats', methods=['GET'])
def get_learning_stats():
    """
    获取学习统计数据
    返回：总学习时长、本周学习时长、知识点学习数量、平均自评分
    """
    now = datetime.utcnow()
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 总学习时长
    total_duration = db.session.query(
        func.sum(LearningRecord.duration)
    ).scalar() or 0
    
    # 本周学习时长
    week_duration = db.session.query(
        func.sum(LearningRecord.duration)
    ).filter(
        LearningRecord.created_at >= week_start
    ).scalar() or 0
    
    # 知识点学习数量
    learned_nodes = db.session.query(
        func.count(func.distinct(LearningRecord.node_id))
    ).scalar() or 0
    
    # 平均自评分
    avg_rating = db.session.query(
        func.avg(LearningRecord.self_rating)
    ).filter(
        LearningRecord.self_rating.isnot(None)
    ).scalar() or 0
    
    return jsonify({
        'total_learning_duration_minutes': total_duration,
        'week_learning_duration_minutes': week_duration,
        'learned_nodes_count': learned_nodes,
        'average_self_rating': round(avg_rating, 2) if avg_rating else 0
    })
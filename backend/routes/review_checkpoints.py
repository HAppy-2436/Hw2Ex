from flask import Blueprint, request, jsonify
from models import db, ReviewPlan, ReviewCheckpoint, KnowledgeNode

bp = Blueprint('review_checkpoints', __name__, url_prefix='/api/review/plans')

VALID_LEARNING_STATUSES = ['not_started', 'learning', 'mastered']
VALID_MASTERY_LEVELS = range(0, 6)  # 0-5


@bp.route('/<int:plan_id>/checkpoints', methods=['GET'])
def get_checkpoints(plan_id):
    """获取复习计划的知识点清单"""
    plan = ReviewPlan.query.get_or_404(plan_id)
    
    checkpoints = ReviewCheckpoint.query.filter_by(plan_id=plan_id).all()
    return jsonify([cp.to_dict() for cp in checkpoints])


@bp.route('/<int:plan_id>/checkpoints', methods=['POST'])
def add_checkpoint(plan_id):
    """添加知识点到复习计划"""
    plan = ReviewPlan.query.get_or_404(plan_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    if 'knowledge_point_id' not in data:
        return jsonify({'error': 'knowledge_point_id is required'}), 400
    
    # Verify knowledge point exists
    node = KnowledgeNode.query.get(data['knowledge_point_id'])
    if not node:
        return jsonify({'error': 'Knowledge point not found'}), 404
    
    # Check if already exists in this plan
    existing = ReviewCheckpoint.query.filter_by(
        plan_id=plan_id,
        knowledge_point_id=data['knowledge_point_id']
    ).first()
    
    if existing:
        return jsonify({'error': 'Knowledge point already exists in this plan'}), 400
    
    checkpoint = ReviewCheckpoint(
        plan_id=plan_id,
        knowledge_point_id=data['knowledge_point_id'],
        learning_status=data.get('learning_status', 'not_started'),
        mastery_level=data.get('mastery_level', 0),
        notes=data.get('notes', '')
    )
    
    db.session.add(checkpoint)
    db.session.commit()
    
    return jsonify(checkpoint.to_dict()), 201


@bp.route('/<int:plan_id>/checkpoints/batch', methods=['POST'])
def batch_add_checkpoints(plan_id):
    """批量添加知识点到复习计划
    Body: { knowledge_point_ids: [1, 2, 3] }
    """
    plan = ReviewPlan.query.get_or_404(plan_id)
    data = request.get_json()
    
    if not data or 'knowledge_point_ids' not in data:
        return jsonify({'error': 'knowledge_point_ids is required'}), 400
    
    knowledge_point_ids = data['knowledge_point_ids']
    
    if not isinstance(knowledge_point_ids, list):
        return jsonify({'error': 'knowledge_point_ids must be a list'}), 400
    
    # Verify all knowledge points exist
    existing_nodes = KnowledgeNode.query.filter(
        KnowledgeNode.id.in_(knowledge_point_ids)
    ).all()
    
    existing_node_ids = {node.id for node in existing_nodes}
    missing_ids = set(knowledge_point_ids) - existing_node_ids
    
    if missing_ids:
        return jsonify({
            'error': f'Knowledge points not found: {list(missing_ids)}'
        }), 404
    
    # Get existing checkpoints to avoid duplicates
    existing_checkpoints = ReviewCheckpoint.query.filter(
        ReviewCheckpoint.plan_id == plan_id,
        ReviewCheckpoint.knowledge_point_id.in_(knowledge_point_ids)
    ).all()
    
    existing_cp_map = {cp.knowledge_point_id: cp for cp in existing_checkpoints}
    
    created = []
    skipped = []
    
    for node_id in knowledge_point_ids:
        if node_id in existing_cp_map:
            skipped.append(node_id)
        else:
            checkpoint = ReviewCheckpoint(
                plan_id=plan_id,
                knowledge_point_id=node_id,
                learning_status='not_started',
                mastery_level=0,
                notes=''
            )
            db.session.add(checkpoint)
            created.append(checkpoint)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Added {len(created)} checkpoints, skipped {len(skipped)} duplicates',
        'created_count': len(created),
        'skipped_count': len(skipped),
        'checkpoints': [cp.to_dict() for cp in created]
    }), 201


@bp.route('/<int:plan_id>/checkpoints/<int:cp_id>', methods=['PATCH'])
def update_checkpoint(plan_id, cp_id):
    """更新知识点复习状态"""
    checkpoint = ReviewCheckpoint.query.filter_by(
        id=cp_id,
        plan_id=plan_id
    ).first_or_404()
    
    data = request.get_json()
    
    if 'learning_status' in data:
        if data['learning_status'] not in VALID_LEARNING_STATUSES:
            return jsonify({
                'error': f'learning_status must be one of: {", ".join(VALID_LEARNING_STATUSES)}'
            }), 400
        checkpoint.learning_status = data['learning_status']
    
    if 'mastery_level' in data:
        if data['mastery_level'] not in VALID_MASTERY_LEVELS:
            return jsonify({'error': 'mastery_level must be between 0 and 5'}), 400
        checkpoint.mastery_level = data['mastery_level']
    
    if 'notes' in data:
        checkpoint.notes = data['notes']
    
    db.session.commit()
    return jsonify(checkpoint.to_dict())


@bp.route('/<int:plan_id>/checkpoints/<int:cp_id>', methods=['DELETE'])
def remove_checkpoint(plan_id, cp_id):
    """从复习计划移除知识点"""
    checkpoint = ReviewCheckpoint.query.filter_by(
        id=cp_id,
        plan_id=plan_id
    ).first_or_404()
    
    db.session.delete(checkpoint)
    db.session.commit()
    
    return jsonify({'message': 'Checkpoint removed successfully'})


@bp.route('/<int:plan_id>/progress', methods=['GET'])
def get_progress(plan_id):
    """获取复习进度统计"""
    plan = ReviewPlan.query.get_or_404(plan_id)
    
    checkpoints = ReviewCheckpoint.query.filter_by(plan_id=plan_id).all()
    
    total = len(checkpoints)
    reviewed = sum(1 for cp in checkpoints if cp.learning_status in ['learning', 'mastered'])
    mastered = sum(1 for cp in checkpoints if cp.learning_status == 'mastered')
    
    progress_percentage = (reviewed / total * 100) if total > 0 else 0
    
    return jsonify({
        'plan_id': plan_id,
        'total': total,
        'reviewed': reviewed,
        'mastered': mastered,
        'not_started': total - reviewed,
        'progress_percentage': round(progress_percentage, 1)
    })

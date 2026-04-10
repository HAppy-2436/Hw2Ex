from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, ReviewPlan, Subject

bp = Blueprint('review_plans', __name__, url_prefix='/api/review/plans')

VALID_STATUSES = ['planning', 'in_progress', 'completed']


@bp.route('', methods=['GET'])
def get_plans():
    """获取复习计划列表"""
    subject_id = request.args.get('subject_id')
    
    query = ReviewPlan.query
    
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    
    plans = query.order_by(ReviewPlan.exam_date.desc()).all()
    return jsonify([plan.to_dict() for plan in plans])


@bp.route('', methods=['POST'])
def create_plan():
    """创建复习计划
    Required: subject_id, exam_date
    Optional: scope
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    if 'subject_id' not in data:
        return jsonify({'error': 'subject_id is required'}), 400
    
    if 'exam_date' not in data:
        return jsonify({'error': 'exam_date is required'}), 400
    
    # Verify subject exists
    subject = Subject.query.get(data['subject_id'])
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404
    
    try:
        exam_date = datetime.strptime(data['exam_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'exam_date must be in YYYY-MM-DD format'}), 400
    
    plan = ReviewPlan(
        subject_id=data['subject_id'],
        exam_date=exam_date,
        scope=data.get('scope', ''),
        status=data.get('status', 'planning')
    )
    
    db.session.add(plan)
    db.session.commit()
    
    return jsonify(plan.to_dict()), 201


@bp.route('/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    """获取复习计划详情"""
    plan = ReviewPlan.query.get_or_404(plan_id)
    return jsonify(plan.to_dict())


@bp.route('/<int:plan_id>', methods=['PUT'])
def update_plan(plan_id):
    """更新复习计划"""
    plan = ReviewPlan.query.get_or_404(plan_id)
    data = request.get_json()
    
    if 'exam_date' in data:
        try:
            plan.exam_date = datetime.strptime(data['exam_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'exam_date must be in YYYY-MM-DD format'}), 400
    
    if 'scope' in data:
        plan.scope = data['scope']
    
    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return jsonify({'error': f'status must be one of: {", ".join(VALID_STATUSES)}'}), 400
        plan.status = data['status']
    
    if 'subject_id' in data:
        subject = Subject.query.get(data['subject_id'])
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        plan.subject_id = data['subject_id']
    
    db.session.commit()
    return jsonify(plan.to_dict())


@bp.route('/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    """删除复习计划"""
    plan = ReviewPlan.query.get_or_404(plan_id)
    
    db.session.delete(plan)
    db.session.commit()
    
    return jsonify({'message': 'Review plan deleted successfully'})


@bp.route('/<int:plan_id>/status', methods=['PATCH'])
def update_status(plan_id):
    """更新复习计划状态"""
    plan = ReviewPlan.query.get_or_404(plan_id)
    data = request.get_json()
    
    if 'status' not in data:
        return jsonify({'error': 'status is required'}), 400
    
    new_status = data['status']
    if new_status not in VALID_STATUSES:
        return jsonify({'error': f'status must be one of: {", ".join(VALID_STATUSES)}'}), 400
    
    plan.status = new_status
    db.session.commit()
    
    return jsonify(plan.to_dict())

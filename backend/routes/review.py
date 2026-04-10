"""
复习管理路由
基于遗忘曲线算法提供复习建议、计划生成和效果评估
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, case
from typing import List

from models import db, KnowledgeNode, Homework, LearningRecord, Book, Subject
from services.learning_algorithm import (
    calculate_review_priority,
    sort_nodes_by_priority,
    calculate_next_review_date,
    is_review_due,
    generate_review_plan,
    calculate_retention_rate,
    get_review_intervals,
    MEMORY_STRENGTH_MAP
)

bp = Blueprint('review', __name__, url_prefix='/api/review')


def get_node_mastery_level(node_id: int) -> int:
    """
    获取知识点的掌握度
    综合考虑关联的作业和复习记录
    """
    # 优先使用作业的掌握度
    homework = Homework.query.filter_by(primary_node_id=node_id).first()
    if homework and homework.mastery_level is not None:
        return homework.mastery_level
    
    # 其次使用学习记录的掌握度
    record = LearningRecord.query.filter_by(node_id=node_id).first()
    if record and record.self_rating is not None:
        return record.self_rating
    
    return 0  # 默认陌生


def get_node_last_reviewed(node_id: int) -> datetime:
    """
    获取知识点上次复习时间
    """
    record = LearningRecord.query.filter_by(node_id=node_id).order_by(
        LearningRecord.created_at.desc()
    ).first()
    
    return record.last_reviewed if record and record.last_reviewed else None


def build_node_review_data(node: KnowledgeNode) -> dict:
    """
    构建知识点的复习数据
    """
    mastery_level = get_node_mastery_level(node.id)
    last_reviewed = get_node_last_reviewed(node.id)
    priority = calculate_review_priority(node.id, last_reviewed, mastery_level)
    
    # 检查是否到期需要复习
    due, days_until = is_review_due(last_reviewed, mastery_level)
    
    # 获取关联作业
    homeworks = Homework.query.filter_by(primary_node_id=node.id).all()
    homework_data = [{
        'id': h.id,
        'title': h.title,
        'mastery_level': h.mastery_level,
        'status': h.status
    } for h in homeworks]
    
    # 获取复习记录
    records = LearningRecord.query.filter_by(node_id=node.id).all()
    review_count = len(records)
    
    return {
        'id': node.id,
        'node_id': node.id,
        'title': node.title,
        'book_id': node.book_id,
        'level': node.level,
        'mastery_level': mastery_level,
        'mastery_name': _get_mastery_name(mastery_level),
        'last_reviewed': last_reviewed.isoformat() if last_reviewed else None,
        'days_since_review': (datetime.utcnow() - last_reviewed).days if last_reviewed else 999,
        'priority': priority,
        'is_due': due,
        'days_until_review': days_until,
        'review_count': review_count,
        'homeworks': homework_data,
        'recommended_intervals': get_review_intervals(mastery_level),
        'next_review_date': calculate_next_review_date(
            last_reviewed, mastery_level, review_count
        ).isoformat()
    }


def _get_mastery_name(level: int) -> str:
    """获取掌握度名称"""
    names = {
        0: "陌生",
        1: "模糊",
        2: "模糊",
        3: "熟悉",
        4: "熟悉",
        5: "掌握"
    }
    return names.get(level, "未知")


@bp.route('/suggestions', methods=['GET'])
def get_review_suggestions():
    """
    获取复习建议（基于遗忘曲线）
    
    Query params:
        - subject_id: 科目ID（可选）
        - book_id: 书籍ID（可选）
        - days: 未来多少天内的复习建议（默认7）
        - limit: 返回数量限制（默认20）
        - include_mastered: 是否包含已掌握的（默认false）
    
    Returns:
        知识点列表，按复习优先级排序
    """
    subject_id = request.args.get('subject_id', type=int)
    book_id = request.args.get('book_id', type=int)
    days = request.args.get('days', default=7, type=int)
    limit = request.args.get('limit', default=20, type=int)
    include_mastered = request.args.get('include_mastered', default='false').lower() == 'true'
    
    # 构建查询
    query = KnowledgeNode.query
    
    if book_id:
        query = query.filter_by(book_id=book_id)
    elif subject_id:
        query = query.join(Book).filter(Book.subject_id == subject_id)
    
    nodes = query.all()
    
    # 构建复习数据
    review_data = []
    for node in nodes:
        data = build_node_review_data(node)
        
        # 过滤已掌握的（如果需要）
        if not include_mastered and data['mastery_level'] >= 5:
            continue
        
        # 只返回需要复习的（到期或即将到期）
        if data['is_due'] or data['days_until_review'] <= days:
            review_data.append(data)
    
    # 按优先级排序
    sorted_data = sorted(review_data, key=lambda x: x['priority'], reverse=True)
    
    # 限制返回数量
    sorted_data = sorted_data[:limit]
    
    # 统计信息
    stats = {
        'total_nodes_queried': len(nodes),
        'nodes_needing_review': len(review_data),
        'high_priority_count': len([d for d in review_data if d['priority'] >= 7]),
        'medium_priority_count': len([d for d in review_data if 4 <= d['priority'] < 7]),
        'low_priority_count': len([d for d in review_data if d['priority'] < 4])
    }
    
    return jsonify({
        'suggestions': sorted_data,
        'stats': stats,
        'query_params': {
            'subject_id': subject_id,
            'book_id': book_id,
            'days': days,
            'limit': limit
        }
    })


@bp.route('/plan/generate', methods=['POST'])
def create_review_plan():
    """
    生成复习计划
    
    Body:
        - subject_id: 科目ID（可选）
        - book_id: 书籍ID（可选）
        - exam_date: 考试日期（可选，格式: YYYY-MM-DD）
        - target_mastery: 目标掌握度（默认4）
        - max_daily_review: 每日最大复习量（默认10）
    
    Returns:
        复习计划，按最佳顺序排列
    """
    data = request.get_json() or {}
    
    subject_id = data.get('subject_id')
    book_id = data.get('book_id')
    exam_date_str = data.get('exam_date')
    target_mastery = data.get('target_mastery', 4)
    max_daily_review = data.get('max_daily_review', 10)
    
    # 解析考试日期
    exam_date = None
    if exam_date_str:
        try:
            exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid exam_date format. Use YYYY-MM-DD'}), 400
    
    # 构建查询
    query = KnowledgeNode.query
    
    if book_id:
        query = query.filter_by(book_id=book_id)
    elif subject_id:
        query = query.join(Book).filter(Book.subject_id == subject_id)
    
    nodes = query.all()
    
    if not nodes:
        return jsonify({'error': 'No knowledge nodes found for the given criteria'}), 404
    
    # 构建节点数据
    nodes_data = []
    for node in nodes:
        mastery_level = get_node_mastery_level(node.id)
        last_reviewed = get_node_last_reviewed(node.id)
        
        nodes_data.append({
            'id': node.id,
            'title': node.title,
            'level': node.level,
            'content': node.content,
            'mastery_level': mastery_level,
            'last_reviewed': last_reviewed
        })
    
    # 生成复习计划
    plan = generate_review_plan(
        nodes_data=nodes_data,
        exam_date=exam_date,
        target_mastery=target_mastery,
        max_daily_review=max_daily_review
    )
    
    # 计算计划统计
    days_until_exam = (exam_date - datetime.utcnow()).days if exam_date else None
    
    plan_stats = {
        'total_nodes': len(plan),
        'estimated_total_minutes': sum(p['estimated_time'] for p in plan),
        'days_until_exam': days_until_exam,
        'daily_average': len(plan) / days_until_exam if days_until_exam and days_until_exam > 0 else len(plan),
        'high_priority_nodes': len([p for p in plan if p['priority'] >= 7]),
        'target_mastery': target_mastery
    }
    
    return jsonify({
        'plan': plan,
        'stats': plan_stats,
        'params': {
            'subject_id': subject_id,
            'book_id': book_id,
            'exam_date': exam_date_str,
            'target_mastery': target_mastery,
            'max_daily_review': max_daily_review
        }
    })


@bp.route('/plan/<int:plan_id>/effectiveness', methods=['GET'])
def evaluate_plan_effectiveness(plan_id):
    """
    评估复习计划效果
    
    注意：此接口评估指定知识点ID作为"计划"的复习效果
    plan_id 实际对应一个 knowledge_node_id
    
    Returns:
        复习前后的掌握度变化和知识留存率
    """
    node_id = plan_id
    
    node = KnowledgeNode.query.get(node_id)
    if not node:
        return jsonify({'error': 'Knowledge node not found'}), 404
    
    # 获取复习记录
    records = LearningRecord.query.filter_by(node_id=node_id).order_by(
        LearningRecord.created_at
    ).all()
    
    if len(records) < 2:
        return jsonify({
            'error': 'Not enough review data to evaluate effectiveness',
            'node_id': node_id,
            'record_count': len(records),
            'message': 'Need at least 2 review records to evaluate effectiveness'
        }), 400
    
    # 获取作业（用于mastery_level）
    homeworks = Homework.query.filter_by(primary_node_id=node_id).all()
    
    # 计算效果指标
    first_record = records[0]
    latest_record = records[-1]
    
    # 初始和当前掌握度
    initial_mastery = first_record.self_rating or get_node_mastery_level(node_id)
    current_mastery = latest_record.self_rating or get_node_mastery_level(node_id)
    
    # 时间跨度
    days_elapsed = (datetime.utcnow() - first_record.created_at).days
    
    # 计算留存率
    retention_rate = calculate_retention_rate(
        initial_mastery=initial_mastery,
        current_mastery=current_mastery,
        days_elapsed=days_elapsed
    )
    
    # 掌握度变化
    mastery_change = current_mastery - initial_mastery
    
    # 复习频率
    total_reviews = len(records)
    avg_days_between_reviews = days_elapsed / (total_reviews - 1) if total_reviews > 1 else 0
    
    # 准确性（如果有练习数据）
    total_attempts = latest_record.total_attempts or 0
    correct_count = latest_record.correct_count or 0
    accuracy = correct_count / total_attempts if total_attempts > 0 else None
    
    # 趋势分析
    mastery_trend = []
    for i, record in enumerate(records):
        if record.self_rating is not None:
            mastery_trend.append({
                'review_number': i + 1,
                'date': record.created_at.isoformat(),
                'mastery': record.self_rating
            })
    
    # 效果评级
    if retention_rate >= 0.8 and mastery_change >= 1:
        effectiveness = 'excellent'
    elif retention_rate >= 0.6 and mastery_change >= 0:
        effectiveness = 'good'
    elif retention_rate >= 0.4:
        effectiveness = 'moderate'
    else:
        effectiveness = 'needs_improvement'
    
    return jsonify({
        'node_id': node_id,
        'node_title': node.title,
        'effectiveness': effectiveness,
        'metrics': {
            'initial_mastery': initial_mastery,
            'current_mastery': current_mastery,
            'mastery_change': mastery_change,
            'retention_rate': round(retention_rate * 100, 1),
            'days_elapsed': days_elapsed,
            'total_reviews': total_reviews,
            'average_days_between_reviews': round(avg_days_between_reviews, 1),
            'accuracy': round(accuracy * 100, 1) if accuracy is not None else None,
            'recommended_intervals': get_review_intervals(current_mastery)
        },
        'mastery_trend': mastery_trend,
        'recommendations': _get_effectiveness_recommendations(
            effectiveness, retention_rate, mastery_change, avg_days_between_reviews
        )
    })


def _get_effectiveness_recommendations(
    effectiveness: str,
    retention_rate: float,
    mastery_change: int,
    avg_days: float
) -> List[str]:
    """
    根据效果评估获取改进建议
    """
    recommendations = []
    
    if effectiveness == 'excellent':
        recommendations.append("复习效果优秀，继续保持当前复习节奏")
        return recommendations
    
    if retention_rate < 0.5:
        recommendations.append("知识留存率较低，建议增加复习频率")
    
    if mastery_change < 0:
        recommendations.append("掌握度下降，需要加强练习和复习")
    elif mastery_change == 0:
        recommendations.append("掌握度无明显变化，建议调整复习方法")
    
    # 根据当前复习间隔给出建议
    if avg_days > 14:
        recommendations.append("复习间隔过长，建议使用间隔递减法复习")
    elif avg_days < 1:
        recommendations.append("复习过于频繁，可适当拉长间隔")
    
    # 遗忘曲线相关的通用建议
    recommendations.append("遵循遗忘曲线规律：及时复习、间隔重复")
    recommendations.append("建议使用主动回忆而非被动阅读")
    
    return recommendations


@bp.route('/stats', methods=['GET'])
def get_review_stats():
    """
    获取复习统计数据
    """
    subject_id = request.args.get('subject_id', type=int)
    book_id = request.args.get('book_id', type=int)
    
    # 构建基础查询
    node_query = KnowledgeNode.query
    if book_id:
        node_query = node_query.filter_by(book_id=book_id)
    elif subject_id:
        node_query = node_query.join(Book).filter(Book.subject_id == subject_id)
    
    total_nodes = node_query.count()
    
    # 复习记录统计
    reviewed_nodes = db.session.query(
        func.count(func.distinct(LearningRecord.node_id))
    ).scalar() or 0
    
    # 掌握度分布
    mastery_distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    nodes = node_query.all()
    for node in nodes:
        mastery = get_node_mastery_level(node.id)
        if mastery in mastery_distribution:
            mastery_distribution[mastery] += 1
    
    # 到期复习数量
    due_count = 0
    for node in nodes:
        mastery = get_node_mastery_level(node.id)
        last_reviewed = get_node_last_reviewed(node.id)
        due, _ = is_review_due(last_reviewed, mastery)
        if due:
            due_count += 1
    
    return jsonify({
        'total_knowledge_nodes': total_nodes,
        'reviewed_nodes': reviewed_nodes,
        'review_coverage': round(reviewed_nodes / total_nodes * 100, 1) if total_nodes > 0 else 0,
        'mastery_distribution': mastery_distribution,
        'nodes_due_for_review': due_count,
        'query_params': {
            'subject_id': subject_id,
            'book_id': book_id
        }
    })


@bp.route('/intervals/<int:mastery_level>', methods=['GET'])
def get_intervals_by_mastery(mastery_level: int):
    """
    获取指定掌握度对应的复习间隔
    
    Args:
        mastery_level: 掌握度 (0-5)
    """
    if mastery_level < 0 or mastery_level > 5:
        return jsonify({'error': 'mastery_level must be between 0 and 5'}), 400
    
    intervals = get_review_intervals(mastery_level)
    mastery_names = {
        0: "陌生",
        1: "模糊",
        2: "模糊",
        3: "熟悉",
        4: "熟悉",
        5: "掌握"
    }
    
    return jsonify({
        'mastery_level': mastery_level,
        'mastery_name': mastery_names[mastery_level],
        'recommended_intervals': intervals,
        'description': f"对于{mastery_names[mastery_level]}程度的知识点，建议的复习间隔为: {intervals}"
    })

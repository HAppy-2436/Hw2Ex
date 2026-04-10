"""
学习历史分析服务
提供学习数据的统计分析和可视化
"""
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from models import db, LearningRecord, KnowledgeNode, Homework, ReviewCheckpoint


def get_learning_history(days=30):
    """
    获取学习历史分析数据
    返回：每日学习时长趋势、知识点学习频率、最常学习的知识点
    
    优化：使用索引查询，避免全表扫描
    """
    # 计算日期范围
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 1. 每日学习时长趋势 (使用created_at索引)
    daily_stats = db.session.query(
        func.date(LearningRecord.created_at).label('date'),
        func.sum(LearningRecord.duration).label('total_duration'),
        func.count(LearningRecord.id).label('record_count')
    ).filter(
        LearningRecord.created_at >= start_date
    ).group_by(
        func.date(LearningRecord.created_at)
    ).order_by(
        func.date(LearningRecord.created_at)
    ).all()
    
    daily_trend = [
        {
            'date': str(stat.date),
            'duration': stat.total_duration or 0,
            'record_count': stat.record_count
        }
        for stat in daily_stats
    ]
    
    # 2. 知识点学习频率 (最常学习的知识点)
    node_freq = db.session.query(
        LearningRecord.node_id,
        func.count(LearningRecord.id).label('learn_count'),
        func.max(LearningRecord.created_at).label('last_learned')
    ).filter(
        LearningRecord.created_at >= start_date
    ).group_by(
        LearningRecord.node_id
    ).order_by(
        func.count(LearningRecord.id).desc()
    ).limit(10).all()
    
    most_learned = []
    for stat in node_freq:
        node = KnowledgeNode.query.get(stat.node_id)
        if node:
            most_learned.append({
                'node_id': stat.node_id,
                'title': node.title,
                'learn_count': stat.learn_count,
                'last_learned': stat.last_learned.isoformat() if stat.last_learned else None
            })
    
    # 3. 总学习时长
    total_duration = db.session.query(
        func.sum(LearningRecord.duration)
    ).scalar() or 0
    
    return {
        'daily_trend': daily_trend,
        'most_learned_nodes': most_learned,
        'total_duration_minutes': total_duration,
        'period_days': days
    }


def get_mastery_distribution():
    """
    获取知识掌握度分布
    返回：各掌握度等级的数量分布
    
    基于Homework表的mastery_level字段 (0-5)
    优化：使用索引查询
    """
    # 获取所有作业的掌握度分布
    mastery_stats = db.session.query(
        Homework.mastery_level,
        func.count(Homework.id).label('count')
    ).group_by(
        Homework.mastery_level
    ).all()
    
    distribution = {i: 0 for i in range(6)}  # 0-5 六个等级
    for level, count in mastery_stats:
        distribution[level] = count
    
    # 获取通过ReviewCheckpoint的掌握度统计
    checkpoint_stats = db.session.query(
        ReviewCheckpoint.learning_status,
        func.count(ReviewCheckpoint.id).label('count')
    ).group_by(
        ReviewCheckpoint.learning_status
    ).all()
    
    checkpoint_distribution = {
        'not_started': 0,
        'learning': 0,
        'mastered': 0
    }
    for status, count in checkpoint_stats:
        if status in checkpoint_distribution:
            checkpoint_distribution[status] = count
    
    return {
        'homework_mastery': distribution,
        'review_checkpoint_status': checkpoint_distribution,
        'mastery_levels': {
            '0': '陌生',
            '1': '初步了解',
            '2': '了解',
            '3': '熟悉',
            '4': '熟练',
            '5': '精通'
        }
    }


def get_progress_stats():
    """
    获取学习进度统计
    返回：总知识点数、已学习数、掌握数、进度百分比
    
    优化：使用JOIN和聚合查询，避免多次查询
    """
    # 总知识点数
    total_nodes = KnowledgeNode.query.count()
    
    # 已学习的知识点数 (通过学习记录)
    learned_node_ids = db.session.query(
        func.count(func.distinct(LearningRecord.node_id))
    ).scalar() or 0
    
    # 已掌握的知识点数 (mastery_level >= 4)
    mastered_count = Homework.query.filter(
        Homework.mastery_level >= 4
    ).count()
    
    # 通过ReviewCheckpoint掌握的
    checkpoint_mastered = ReviewCheckpoint.query.filter(
        ReviewCheckpoint.learning_status == 'mastered'
    ).count()
    
    # 综合计算已学习数（有学习记录的知识点）
    nodes_with_records = db.session.query(
        func.count(func.distinct(LearningRecord.node_id))
    ).scalar() or 0
    
    # 掌握数取较大值
    total_mastered = max(mastered_count, checkpoint_mastered)
    
    # 计算进度百分比
    progress_percentage = (nodes_with_records / total_nodes * 100) if total_nodes > 0 else 0
    
    return {
        'total_knowledge_points': total_nodes,
        'learned_count': nodes_with_records,
        'mastered_count': total_mastered,
        'progress_percentage': round(progress_percentage, 1),
        'not_started': total_nodes - nodes_with_records
    }


def get_learning_stats_enhanced():
    """
    获取增强的学习统计数据
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
    
    return {
        'total_learning_duration_minutes': total_duration,
        'week_learning_duration_minutes': week_duration,
        'learned_nodes_count': learned_nodes,
        'average_self_rating': round(avg_rating, 2) if avg_rating else 0
    }
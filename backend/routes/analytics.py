"""
学习分析统计路由
提供学习历史、掌握度分布、进度统计等API
"""
from flask import Blueprint, jsonify
from services.analytics import (
    get_learning_history,
    get_mastery_distribution,
    get_progress_stats,
    get_learning_stats_enhanced
)

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


@bp.route('/learning-history', methods=['GET'])
def learning_history():
    """
    获取学习历史分析
    返回：每日学习时长趋势、知识点学习频率、最常学习的知识点
    """
    data = get_learning_history(days=30)
    return jsonify(data)


@bp.route('/mastery-distribution', methods=['GET'])
def mastery_distribution():
    """
    获取知识掌握度分布
    返回：各掌握度等级的数量分布
    """
    data = get_mastery_distribution()
    return jsonify(data)


@bp.route('/progress', methods=['GET'])
def progress():
    """
    获取学习进度统计
    返回：总知识点数、已学习数、掌握数、进度百分比
    """
    data = get_progress_stats()
    return jsonify(data)
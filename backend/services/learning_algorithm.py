"""
遗忘曲线算法服务
基于艾宾浩斯遗忘曲线理论，计算知识点复习优先级和最佳复习间隔
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


# 遗忘曲线参数
FORGETTING_CURVE_DECAY_RATE = 0.1  # 基础衰减率

# 记忆强度系数（基于 mastery_level）
# mastery_level 0-5 对应的记忆强度
MEMORY_STRENGTH_MAP = {
    0: 1.0,    # 陌生 - 极弱记忆强度
    1: 1.5,    # 模糊
    2: 2.0,    # 模糊
    3: 3.0,    # 熟悉
    4: 4.0,    # 熟悉
    5: 5.0,    # 掌握
}

# 复习间隔建议（天）- 基于 mastery_level
REVIEW_INTERVALS = {
    0: [1, 3],           # 陌生: 1天后 → 3天后
    1: [3, 7, 14],       # 模糊: 3天 → 7天 → 14天
    2: [3, 7, 14],
    3: [7, 21, 60],      # 熟悉: 7天 → 21天 → 60天
    4: [7, 21, 60],
    5: [30, 90],         # 掌握: 30天 → 90天
}

# 掌握度权重（用于优先级计算）
MASTERY_WEIGHT = {
    0: 1.0,    # 陌生 - 最高权重
    1: 0.9,
    2: 0.7,
    3: 0.5,
    4: 0.3,
    5: 0.1,    # 掌握 - 最低权重
}


def calculate_forgetting_degree(days_since_review: float, memory_strength: float) -> float:
    """
    计算遗忘程度
    基于遗忘曲线公式: y = e^(-t/S)
    
    Args:
        days_since_review: 距离上次复习的天数
        memory_strength: 记忆强度（基于 mastery_level）
    
    Returns:
        遗忘程度值 (0-1)，1 表示完全遗忘，0 表示没有遗忘
    """
    if days_since_review < 0:
        days_since_review = 0
    
    # 遗忘程度 = 1 - e^(-t/S)
    # 其中 S = memory_strength * FORGETTING_CURVE_DECAY_RATE
    S = memory_strength * FORGETTING_CURVE_DECAY_RATE
    if S <= 0:
        S = 0.01  # 防止除零
    
    forgetting_degree = 1 - math.exp(-days_since_review / S)
    
    # 限制在 0-1 范围内
    return max(0.0, min(1.0, forgetting_degree))


def calculate_review_priority(
    node_id: int,
    last_reviewed: Optional[datetime],
    mastery_level: int
) -> float:
    """
    根据遗忘曲线计算复习优先级
    
    优先级计算公式:
    priority = forgetting_degree * mastery_weight
    
    - 最近学习且掌握度高的优先级低
    - 很久没学习或掌握度低的优先级高
    
    Args:
        node_id: 知识点ID
        last_reviewed: 上次复习时间
        mastery_level: 掌握度 (0-5)
    
    Returns:
        优先级分数 (0-10)，越高越需要复习
    """
    # 获取记忆强度
    memory_strength = MEMORY_STRENGTH_MAP.get(mastery_level, 1.0)
    
    # 获取掌握度权重
    weight = MASTERY_WEIGHT.get(mastery_level, 0.5)
    
    # 计算天数差
    if last_reviewed is None:
        # 从未复习，立即需要复习
        days_since_review = 365  # 假设一年未复习
    else:
        days_since_review = (datetime.utcnow() - last_reviewed).total_seconds() / 86400
    
    # 计算遗忘程度
    forgetting_degree = calculate_forgetting_degree(days_since_review, memory_strength)
    
    # 计算优先级 (0-10)
    priority = forgetting_degree * weight * 10
    
    return round(priority, 2)


def get_review_intervals(mastery_level: int) -> List[int]:
    """
    根据掌握度获取建议复习间隔
    
    Args:
        mastery_level: 掌握度 (0-5)
    
    Returns:
        复习间隔天数列表
    """
    return REVIEW_INTERVALS.get(mastery_level, [1, 3, 7])


def calculate_next_review_date(
    last_reviewed: Optional[datetime],
    mastery_level: int,
    review_count: int = 0
) -> datetime:
    """
    计算下次复习日期
    
    Args:
        last_reviewed: 上次复习时间
        mastery_level: 掌握度 (0-5)
        review_count: 已复习次数
    
    Returns:
        下次复习日期
    """
    intervals = get_review_intervals(mastery_level)
    
    # 根据复习次数选择间隔
    interval_index = min(review_count, len(intervals) - 1)
    interval_days = intervals[interval_index]
    
    if last_reviewed is None:
        base_date = datetime.utcnow()
    else:
        base_date = last_reviewed
    
    return base_date + timedelta(days=interval_days)


def is_review_due(
    last_reviewed: Optional[datetime],
    mastery_level: int,
    review_count: int = 0
) -> Tuple[bool, int]:
    """
    检查是否需要复习
    
    Args:
        last_reviewed: 上次复习时间
        mastery_level: 掌握度 (0-5)
        review_count: 已复习次数
    
    Returns:
        (是否需要复习, 距离下次复习的天数，负数表示已过期)
    """
    next_review = calculate_next_review_date(last_reviewed, mastery_level, review_count)
    days_until_review = (next_review - datetime.utcnow()).total_seconds() / 86400
    
    is_due = days_until_review <= 0
    return is_due, int(days_until_review)


def sort_nodes_by_priority(nodes_data: List[Dict]) -> List[Dict]:
    """
    根据遗忘曲线优先级对知识点排序
    
    Args:
        nodes_data: 知识点列表，每项包含 id, last_reviewed, mastery_level
    
    Returns:
        按优先级排序的知识点列表（高优先级在前）
    """
    def get_priority(item):
        return calculate_review_priority(
            node_id=item.get('id', 0),
            last_reviewed=item.get('last_reviewed'),
            mastery_level=item.get('mastery_level', 0)
        )
    
    # 计算优先级并排序
    for item in nodes_data:
        item['priority'] = get_priority(item)
    
    sorted_nodes = sorted(nodes_data, key=lambda x: x['priority'], reverse=True)
    
    return sorted_nodes


def calculate_retention_rate(
    initial_mastery: int,
    current_mastery: int,
    days_elapsed: int
) -> float:
    """
    计算知识留存率
    
    基于遗忘曲线理论，留存率随时间下降
    公式: retention = e^(-t/S)
    
    Args:
        initial_mastery: 初始掌握度
        current_mastery: 当前掌握度
        days_elapsed: 经过的天数
    
    Returns:
        留存率 (0-1)
    """
    if days_elapsed <= 0:
        return 1.0 if current_mastery >= initial_mastery else 0.0
    
    # 记忆强度
    S = MEMORY_STRENGTH_MAP.get(initial_mastery, 1.0) * 10
    
    # 理论留存率
    theoretical_retention = math.exp(-days_elapsed / S)
    
    # 实际留存率（考虑掌握度变化）
    mastery_ratio = current_mastery / max(initial_mastery, 1)
    actual_retention = theoretical_retention * mastery_ratio
    
    return max(0.0, min(1.0, actual_retention))


def estimate_study_time(node_data: Dict) -> int:
    """
    估算学习时间（分钟）
    
    基于知识点的复杂度（通过level和content长度估算）
    
    Args:
        node_data: 知识点数据
    
    Returns:
        预估学习时间（分钟）
    """
    base_time = 10  # 基础学习时间
    
    # 根据层级调整
    level = node_data.get('level', 0)
    level_multiplier = 1 + (level * 0.2)
    
    # 根据内容长度调整
    content = node_data.get('content', '')
    content_length = len(content) if content else 0
    content_multiplier = 1 + (content_length / 1000)
    
    estimated_time = int(base_time * level_multiplier * content_multiplier)
    
    return max(5, min(estimated_time, 120))  # 限制在 5-120 分钟


def generate_review_plan(
    nodes_data: List[Dict],
    exam_date: Optional[datetime] = None,
    target_mastery: int = 4,
    max_daily_review: int = 10
) -> List[Dict]:
    """
    生成复习计划
    
    Args:
        nodes_data: 知识点列表
        exam_date: 考试日期（可选）
        target_mastery: 目标掌握度
        max_daily_review: 每日最大复习量
    
    Returns:
        复习计划列表
    """
    if not nodes_data:
        return []
    
    # 按优先级排序
    sorted_nodes = sort_nodes_by_priority(nodes_data)
    
    # 计算可用天数
    if exam_date:
        days_until_exam = (exam_date - datetime.utcnow()).days
        days_until_exam = max(1, days_until_exam)
    else:
        days_until_exam = 30  # 默认30天
    
    # 计算每天需要复习的知识点数量
    daily_quota = min(max_daily_review, math.ceil(len(sorted_nodes) / days_until_exam))
    
    # 生成计划
    plan = []
    current_date = datetime.utcnow().date()
    
    for i, node in enumerate(sorted_nodes):
        day_offset = i // daily_quota
        review_date = current_date + timedelta(days=day_offset)
        
        mastery_level = node.get('mastery_level', 0)
        intervals = get_review_intervals(mastery_level)
        
        plan.append({
            'node_id': node.get('id'),
            'node_title': node.get('title', 'Unknown'),
            'priority': node.get('priority', 0),
            'scheduled_date': review_date.isoformat(),
            'recommended_intervals': intervals,
            'target_mastery': target_mastery,
            'estimated_time': estimate_study_time(node),
            'mastery_level': mastery_level,
            'reason': _get_review_reason(mastery_level, node.get('last_reviewed'))
        })
    
    return plan


def _get_review_reason(mastery_level: int, last_reviewed: Optional[datetime]) -> str:
    """
    获取复习原因说明
    """
    reasons = {
        0: "知识点较陌生，需要尽快复习巩固",
        1: "记忆较模糊，需要定期强化",
        2: "有一定印象，需要进一步熟悉",
        3: "基本掌握，建议周期性回顾",
        4: "掌握较好，保持练习即可",
        5: "完全掌握，可减少复习频率"
    }
    
    base_reason = reasons.get(mastery_level, "根据遗忘曲线安排复习")
    
    if last_reviewed:
        days = (datetime.utcnow() - last_reviewed).days
        if days > 30:
            base_reason += f"（已{days}天未复习）"
    
    return base_reason

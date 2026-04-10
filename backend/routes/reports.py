"""
复习报告生成路由
提供复习计划的详细分析和报告
"""
from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func
from models import db, ReviewPlan, ReviewCheckpoint, KnowledgeNode, Book, Subject, Homework

bp = Blueprint('reports', __name__, url_prefix='/api/reports')


def get_weak_areas(plan_id):
    """
    分析复习计划中的薄弱知识点
    返回薄弱的章节/知识点列表
    """
    checkpoints = ReviewCheckpoint.query.filter_by(plan_id=plan_id).all()
    
    weak_chapters = {}
    for cp in checkpoints:
        if cp.learning_status != 'mastered' and cp.mastery_level < 3:
            node = cp.knowledge_point
            if node:
                # 获取章节信息（通过book的标题或父节点）
                book = Book.query.get(node.book_id)
                if book:
                    chapter_key = f"第{node.level + 1}章" if node.level == 0 else node.title
                    if chapter_key not in weak_chapters:
                        weak_chapters[chapter_key] = {
                            'chapter': chapter_key,
                            'unmastered_count': 0,
                            'avg_mastery': 0,
                            'total_count': 0
                        }
                    weak_chapters[chapter_key]['total_count'] += 1
                    if cp.learning_status != 'mastered':
                        weak_chapters[chapter_key]['unmastered_count'] += 1
    
    # 计算平均掌握度并排序
    for chapter in weak_chapters:
        data = weak_chapters[chapter]
        data['avg_mastery'] = round(
            (data['total_count'] - data['unmastered_count']) / data['total_count'] * 100
            if data['total_count'] > 0 else 0
        )
    
    # 返回最薄弱的章节（未掌握比例最高的）
    sorted_weak = sorted(
        weak_chapters.items(),
        key=lambda x: x[1]['unmastered_count'] / x[1]['total_count'] if x[1]['total_count'] > 0 else 0,
        reverse=True
    )
    
    return [chapter for chapter, _ in sorted_weak[:5]]  # 返回前5个薄弱章节


def generate_recommendations(plan_id, progress_data):
    """
    根据复习进度生成个性化建议
    """
    recommendations = []
    
    if progress_data['mastery_rate'] < 0.3:
        recommendations.append("加强对薄弱章节的练习，建议每天复习2小时以上")
    elif progress_data['mastery_rate'] < 0.6:
        recommendations.append("当前进度良好，建议保持每日复习习惯")
    else:
        recommendations.append("掌握情况不错，可适当减少复习时间，转向难题训练")
    
    # 根据薄弱章节给出建议
    weak_areas = progress_data.get('weak_areas', [])
    if weak_areas:
        recommendations.append(f"重点关注: {', '.join(weak_areas[:3])}")
    
    # 根据剩余时间给出建议
    days_until_exam = progress_data.get('days_until_exam', 0)
    if days_until_exam <= 7:
        recommendations.append("考前冲刺阶段，建议进行模拟测试和错题回顾")
    elif days_until_exam <= 14:
        recommendations.append("进入复习关键期，建议加强高频考点的练习")
    
    # 根据掌握度分布给出建议
    if progress_data.get('not_started', 0) > progress_data.get('total', 0) * 0.3:
        recommendations.append("未开始内容较多，建议优先学习核心知识点")
    
    return recommendations


def estimate_completion_date(plan_id, current_mastered, total_points, daily_review_capacity=5):
    """
    估算完成所有知识点复习的预计日期
    
    假设每天可以复习daily_review_capacity个知识点
    """
    remaining = total_points - current_mastered
    if remaining <= 0:
        return datetime.utcnow().strftime('%Y-%m-%d')
    
    days_needed = (remaining + daily_review_capacity - 1) // daily_review_capacity
    estimated_date = datetime.utcnow() + timedelta(days=days_needed)
    
    return estimated_date.strftime('%Y-%m-%d')


@bp.route('/review/<int:plan_id>', methods=['GET'])
def generate_review_report(plan_id):
    """
    生成复习报告
    
    返回：
    - plan_id: 计划ID
    - subject: 科目名称
    - exam_date: 考试日期
    - total_knowledge_points: 总知识点数
    - mastered: 已掌握数
    - learning: 学习中数
    - not_started: 未开始数
    - mastery_rate: 掌握率
    - estimated_completion_date: 预计完成日期
    - weak_areas: 薄弱区域
    - recommendations: 复习建议
    """
    # 获取复习计划
    plan = ReviewPlan.query.get_or_404(plan_id)
    subject = Subject.query.get(plan.subject_id)
    
    # 获取该计划下的所有知识点检查点
    checkpoints = ReviewCheckpoint.query.filter_by(plan_id=plan_id).all()
    
    total_knowledge_points = len(checkpoints)
    
    # 统计各状态数量
    mastered = sum(1 for cp in checkpoints if cp.learning_status == 'mastered')
    learning = sum(1 for cp in checkpoints if cp.learning_status == 'learning')
    not_started = sum(1 for cp in checkpoints if cp.learning_status == 'not_started')
    
    # 计算掌握率
    mastery_rate = mastered / total_knowledge_points if total_knowledge_points > 0 else 0
    
    # 获取薄弱区域
    weak_areas = get_weak_areas(plan_id)
    
    # 计算距考试天数
    days_until_exam = (plan.exam_date - datetime.utcnow().date()).days if plan.exam_date else 0
    
    # 准备进度数据
    progress_data = {
        'mastery_rate': mastery_rate,
        'weak_areas': weak_areas,
        'days_until_exam': days_until_exam,
        'not_started': not_started,
        'total': total_knowledge_points
    }
    
    # 生成建议
    recommendations = generate_recommendations(plan_id, progress_data)
    
    # 估算完成日期
    estimated_completion = estimate_completion_date(plan_id, mastered, total_knowledge_points)
    
    return jsonify({
        'plan_id': plan.id,
        'subject': subject.name if subject else '未知科目',
        'exam_date': plan.exam_date.isoformat() if plan.exam_date else None,
        'total_knowledge_points': total_knowledge_points,
        'mastered': mastered,
        'learning': learning,
        'not_started': not_started,
        'mastery_rate': round(mastery_rate, 2),
        'estimated_completion_date': estimated_completion,
        'weak_areas': weak_areas,
        'recommendations': recommendations,
        'days_until_exam': max(0, days_until_exam),
        'plan_status': plan.status
    })


@bp.route('/review/<int:plan_id>/detailed', methods=['GET'])
def generate_detailed_report(plan_id):
    """
    生成详细的复习报告，包含每个知识点的分析
    """
    plan = ReviewPlan.query.get_or_404(plan_id)
    subject = Subject.query.get(plan.subject_id)
    
    checkpoints = ReviewCheckpoint.query.filter_by(plan_id=plan_id).all()
    
    detailed_checkpoints = []
    for cp in checkpoints:
        node = cp.knowledge_point
        if node:
            # 获取关联的作业信息
            related_homework = Homework.query.filter_by(primary_node_id=node.id).first()
            
            detailed_checkpoints.append({
                'checkpoint_id': cp.id,
                'node_id': node.id,
                'title': node.title,
                'level': node.level,
                'learning_status': cp.learning_status,
                'mastery_level': cp.mastery_level,
                'notes': cp.notes,
                'related_homework_count': Homework.query.filter_by(primary_node_id=node.id).count(),
                'homework_mastery': related_homework.mastery_level if related_homework else None
            })
    
    return jsonify({
        'plan_id': plan.id,
        'subject': subject.name if subject else '未知科目',
        'exam_date': plan.exam_date.isoformat() if plan.exam_date else None,
        'total_checkpoints': len(checkpoints),
        'detailed_checkpoints': detailed_checkpoints
    })
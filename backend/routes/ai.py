from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from utils.ai_service import AIService
from models import db, KnowledgeNode, Homework

bp = Blueprint('ai', __name__, url_prefix='/api/ai')

ai_service = AIService()


@bp.route('/analyze', methods=['POST'])
def analyze_homework():
    """
    分析作业题目
    
    认知门控：必须先验证用户已提交思路（user_thought ≥ 20字）
    
    Body: {
        "homework_id": int,
        "user_thought": str  # 用户提交的解题思路
    }
    
    Returns: {
        "success": bool,
        "homework_id": int,
        "analysis": {
            "analysis": str,           # 对用户思路的分析评价
            "solution_steps": [],      # 解题步骤
            "knowledge_points": [],     # 关联知识点
            "similar_problems": [],     # 类似题目推荐
            "learning_tips": str,       # 学习建议
            "encouragement": str        # 鼓励评语
        },
        "source": str,
        "cached": bool
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    homework_id = data.get('homework_id')
    user_thought = data.get('user_thought', '')

    if not homework_id:
        return jsonify({'error': 'homework_id 是必填参数'}), 400

    if not user_thought:
        return jsonify({
            'success': False,
            'error': 'cognitive_gate_failed',
            'message': '认知门控未通过：请先提交你的解题思路（至少20字），这样AI分析才能更精准地帮助你学习。',
            'source': 'cognitive_gate'
        }), 403

    # 检查 homework 是否存在
    homework = Homework.query.get(homework_id)
    if not homework:
        return jsonify({'error': '作业题目不存在'}), 404

    response = ai_service.analyze_homework(homework_id, user_thought)

    if not response.get('success'):
        status_code = 400
        if response.get('error') == 'cognitive_gate_failed':
            status_code = 403
        elif response.get('error') == 'homework_not_found':
            status_code = 404
        return jsonify(response), status_code

    return jsonify(response)


@bp.route('/answer', methods=['POST'])
def get_answer():
    """
    获取答案（认知门控：必须先提交思路）
    
    Body: {
        "homework_id": int,
        "user_thought": str  # 用户提交的解题思路（至少20字）
    }
    
    Returns: {
        "success": bool,
        "homework_id": int,
        "answer": str,        # 格式化答案
        "source": str,
        "cached": bool
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    homework_id = data.get('homework_id')
    user_thought = data.get('user_thought', '')

    if not homework_id:
        return jsonify({'error': 'homework_id 是必填参数'}), 400

    if not user_thought:
        return jsonify({
            'success': False,
            'error': 'cognitive_gate_failed',
            'message': '认知门控未通过：请先提交你的解题思路（至少20字）才能获取答案。',
            'source': 'cognitive_gate'
        }), 403

    # 检查 homework 是否存在
    homework = Homework.query.get(homework_id)
    if not homework:
        return jsonify({'error': '作业题目不存在'}), 404

    response = ai_service.generate_answer(homework_id, user_thought)

    if not response.get('success'):
        status_code = 400
        if response.get('error') == 'cognitive_gate_failed':
            status_code = 403
        elif response.get('error') == 'homework_not_found':
            status_code = 404
        return jsonify(response), status_code

    return jsonify(response)


@bp.route('/ask', methods=['POST'])
def ask_question():
    """
    知识问答 - 基于知识点进行问答
    
    Body: {
        "node_id": int,       # 知识点ID（可选）
        "question": str,       # 问题
        "context": str        # 额外上下文（可选）
    }
    
    Returns: {
        "success": bool,
        "answer": str,
        "node_id": int,
        "source": str,
        "cached": bool
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    if 'question' not in data:
        return jsonify({'error': 'question 是必填参数'}), 400

    question = data['question']
    node_id = data.get('node_id')
    context = data.get('context')

    # 如果提供了 node_id，验证并获取知识点上下文
    if node_id:
        node = KnowledgeNode.query.get(node_id)
        if not node:
            return jsonify({'error': '知识点不存在'}), 404

    response = ai_service.ask_question(node_id, question, context)

    if not response.get('success'):
        return jsonify(response), 400

    return jsonify(response)


@bp.route('/knowledge-summary/<int:node_id>', methods=['POST'])
def generate_knowledge_summary(node_id):
    """生成知识点摘要"""
    node = KnowledgeNode.query.get_or_404(node_id)

    prompt = f"""请创建知识点的简洁摘要：

标题：{node.title}

内容：{node.content or '暂无内容'}

标签：{', '.join(node.tags) if node.tags else '无'}

请提供：
1. 简要定义/解释（2-3句话）
2. 关键概念（要点列表）
3. 常见应用或示例
4. 相关主题或先修知识
5. 常见错误或陷阱

使用清晰的markdown格式。"""

    response = ai_service.generate_answer_legacy(prompt)

    return jsonify(response)


@bp.route('/homework-answer/<int:homework_id>', methods=['POST'])
def generate_homework_answer(homework_id):
    """生成作业答案（兼容旧接口，不带认知门控）"""
    homework = Homework.query.get_or_404(homework_id)

    book = homework.book
    subject = book.subject if book else None

    response = ai_service.generate_answer_legacy(
        question=homework.content,
        context=f"学科：{subject.name if subject else '通用'}\n\n题目：{homework.content}"
    )

    if response['source'] != 'error':
        homework.answer = response.get('answer', '')
        db.session.commit()

    return jsonify(response)


@bp.route('/review-materials', methods=['POST'])
def generate_review_materials():
    """生成复习材料"""
    data = request.get_json()

    if 'topics' not in data:
        return jsonify({'error': 'topics 是必填参数'}), 400

    topics = data['topics']

    if not isinstance(topics, list):
        return jsonify({'error': 'topics 必须是列表'}), 400

    mastery_levels = []
    for topic in topics:
        if isinstance(topic, dict) and 'id' in topic and 'title' in topic and 'mastery' in topic:
            mastery_levels.append({
                'id': topic['id'],
                'title': topic['title'],
                'mastery': topic['mastery']
            })
        else:
            return jsonify({'error': '每个topic必须包含 id, title, mastery 字段'}), 400

    prompt = f"""请为以下主题生成个性化复习材料：

主题和掌握程度：
{json.dumps(mastery_levels, indent=2)}

要求：
1. 对于标记为"已掌握"的主题，提供具有挑战性的练习题
2. 对于标记为"复习中"的主题，提供概念摘要和中等难度题目
3. 对于标记为"学习中"的主题，提供详细解释和基础练习
4. 包含相关主题之间的联系
5. 根据掌握程度建议学习计划

使用清晰的markdown格式。"""

    response = ai_service.generate_answer_legacy(prompt)

    return jsonify(response)


@bp.route('/conversation', methods=['POST'])
def continue_conversation():
    """继续对话"""
    data = request.get_json()

    if 'messages' not in data or not isinstance(data['messages'], list):
        return jsonify({'error': 'messages 是必填参数且必须是列表'}), 400

    messages = data['messages']

    if len(messages) == 0:
        return jsonify({'error': 'messages 列表不能为空'}), 400

    if not all('role' in msg and 'content' in msg for msg in messages):
        return jsonify({'error': '每条消息必须包含 role 和 content 字段'}), 400

    result = ai_service._call_api_with_limit(messages, data.get('max_tokens', 1000))

    if 'error' in result:
        return jsonify({'error': result['error']}), 500

    try:
        answer = result['choices'][0]['message']['content']
        usage = result.get('usage', {})

        if usage:
            ai_service._record_token_usage(ai_service.model, usage)

        return jsonify({
            'answer': answer,
            'usage': usage
        })

    except Exception as e:
        current_app.logger.error(f"Conversation error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/cache/stats', methods=['GET'])
def get_cache_stats():
    """获取缓存统计"""
    try:
        conn = sqlite3.connect(ai_service.cache_db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM ai_cache')
        total = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM ai_cache WHERE expires_at > ?',
                      (datetime.now().isoformat(),))
        valid = cursor.fetchone()[0]

        cursor.execute('SELECT created_at FROM ai_cache ORDER BY created_at LIMIT 1')
        oldest = cursor.fetchone()

        conn.close()

        return jsonify({
            'total_entries': total,
            'valid_entries': valid,
            'oldest_entry': oldest[0] if oldest else None
        })

    except Exception as e:
        current_app.logger.error(f"Cache stats error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """清空缓存"""
    try:
        conn = sqlite3.connect(ai_service.cache_db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM ai_cache')
        deleted_count = cursor.rowcount

        conn.commit()
        conn.close()

        return jsonify({
            'message': '缓存清空成功',
            'deleted_entries': deleted_count
        })

    except Exception as e:
        current_app.logger.error(f"Cache clear error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/token-usage', methods=['GET'])
def get_token_usage():
    """获取Token使用统计"""
    try:
        from models import TokenUsage
        from datetime import datetime, timedelta

        date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        limit = request.args.get('limit', 24, type=int)

        records = TokenUsage.query.filter_by(date=date_str).order_by(
            TokenUsage.hour.desc()
        ).limit(limit).all()

        total_usage = {
            'date': date_str,
            'total_prompt_tokens': sum(r.prompt_tokens for r in records),
            'total_completion_tokens': sum(r.completion_tokens for r in records),
            'total_tokens': sum(r.total_tokens for r in records),
            'total_cost_usd': sum(r.cost_usd for r in records),
            'total_requests': sum(r.request_count for r in records),
            'records': [r.to_dict() for r in records]
        }

        return jsonify(total_usage)

    except Exception as e:
        current_app.logger.error(f"Token usage error: {e}")
        return jsonify({'error': str(e)}), 500


# 导入 sqlite3 用于缓存统计
import sqlite3
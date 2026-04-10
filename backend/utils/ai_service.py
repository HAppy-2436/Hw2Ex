import os
import json
import requests
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy import text
import hashlib
import sqlite3
import threading
import time

# 并发限制：最多3个并发AI请求
ai_semaphore = threading.Semaphore(3)
ai_lock = threading.Lock()

# DeepSeek API 配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
CACHE_TTL_DAYS = 7
MAX_RETRIES = 3
RETRY_DELAY = 1  # 秒


class AIService:
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.api_url = DEEPSEEK_API_URL
        self.model = DEEPSEEK_MODEL
        self.cache_db_path = '/home/i/Hw2Ex/data/ai_cache.db'
        self._init_cache_db()

    def _init_cache_db(self):
        """初始化缓存数据库"""
        os.makedirs('/home/i/Hw2Ex/data', exist_ok=True)
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_query_hash ON ai_cache(query_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON ai_cache(expires_at)')
        conn.commit()
        conn.close()

    def _get_cache_key(self, prompt, context=None):
        """生成缓存键"""
        content = prompt
        if context:
            content += json.dumps(context, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cached_response(self, cache_key):
        """获取缓存响应"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT response FROM ai_cache
                WHERE query_hash = ? AND expires_at > ?
            ''', (cache_key, datetime.now().isoformat()))

            result = cursor.fetchone()
            conn.close()

            if result:
                current_app.logger.info(f"Cache hit for query: {cache_key[:10]}...")
                return json.loads(result[0])

        except Exception as e:
            current_app.logger.error(f"Error reading cache: {e}")

        return None

    def _save_to_cache(self, cache_key, response):
        """保存响应到缓存"""
        try:
            expires_at = datetime.now() + timedelta(days=CACHE_TTL_DAYS)

            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO ai_cache (query_hash, response, expires_at)
                VALUES (?, ?, ?)
            ''', (cache_key, json.dumps(response), expires_at.isoformat()))

            conn.commit()
            conn.close()

            current_app.logger.info(f"Saved to cache: {cache_key[:10]}...")

        except Exception as e:
            current_app.logger.error(f"Error saving to cache: {e}")

    def _clean_expired_cache(self):
        """清理过期缓存"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM ai_cache WHERE expires_at <= ?',
                          (datetime.now().isoformat(),))

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted_count > 0:
                current_app.logger.info(f"Cleaned {deleted_count} expired cache entries")

        except Exception as e:
            current_app.logger.error(f"Error cleaning cache: {e}")

    def _record_token_usage(self, model, usage):
        """记录Token使用量到数据库"""
        try:
            from models import db, TokenUsage

            now = datetime.now()
            date_str = now.strftime('%Y-%m-%d')
            hour = now.hour

            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)

            # 估算成本 (DeepSeek $0.001/1K tokens for input, $0.002/1K tokens for output)
            cost_usd = (prompt_tokens * 0.001 / 1000) + (completion_tokens * 0.002 / 1000)

            # 查找或创建今天的记录
            record = TokenUsage.query.filter_by(
                date=date_str,
                hour=hour,
                model=model
            ).first()

            if record:
                record.prompt_tokens += prompt_tokens
                record.completion_tokens += completion_tokens
                record.total_tokens += total_tokens
                record.cost_usd += cost_usd
                record.request_count += 1
            else:
                record = TokenUsage(
                    date=date_str,
                    hour=hour,
                    model=model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    cost_usd=cost_usd,
                    request_count=1
                )
                db.session.add(record)

            db.session.commit()
            current_app.logger.info(f"Token usage recorded: {total_tokens} tokens, cost: ${cost_usd:.4f}")

        except Exception as e:
            current_app.logger.error(f"Error recording token usage: {e}")
            try:
                db.session.rollback()
            except:
                pass

    def _call_deepseek_api(self, messages, max_tokens=2000):
        """调用DeepSeek API（带重试机制）"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3
        }

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                last_error = e
                current_app.logger.warning(f"API request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))  # 指数退避

        # 所有重试都失败
        return {
            'error': f'API request failed after {MAX_RETRIES} attempts: {str(last_error)}'
        }

    def _call_api_with_limit(self, messages, max_tokens=2000):
        """带并发限制的API调用"""
        with ai_semaphore:
            return self._call_deepseek_api(messages, max_tokens)

    def _validate_cognitive_gate(self, user_thought):
        """
        验证认知门控：用户必须先提交自己的思路才能看AI答案
        要求：user_thought 长度 ≥ 20字
        """
        if not user_thought or len(user_thought.strip()) < 20:
            return False, "认知门控未通过：请先提交你的解题思路（至少20字），这样AI分析才能更精准地帮助你学习，而非直接给你答案。"
        return True, None

    def analyze_homework(self, homework_id, user_thought):
        """
        分析作业题目（认知门控：必须先验证用户已提交思路）

        输入：题目内容 + 用户提交的思路
        输出：AI 分析结果（解题思路、知识点关联、类似题目推荐）
        """
        # 认知门控检查
        is_valid, error_msg = self._validate_cognitive_gate(user_thought)
        if not is_valid:
            return {
                'success': False,
                'error': 'cognitive_gate_failed',
                'message': error_msg,
                'source': 'cognitive_gate'
            }

        from models import Homework

        homework = Homework.query.get(homework_id)
        if not homework:
            return {
                'success': False,
                'error': 'homework_not_found',
                'message': '作业题目不存在',
                'source': 'error'
            }

        # 构建上下文
        context = {
            'homework_id': homework.id,
            'homework_content': homework.content,
            'homework_title': homework.title,
            'book_id': homework.book_id,
            'user_thought': user_thought
        }

        # 构建缓存键
        cache_prompt = f"analyze_homework:{homework_id}:{user_thought[:100]}"
        cache_key = self._get_cache_key(cache_prompt, context)

        # 检查缓存
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            cached_response['cached'] = True
            return cached_response

        # 构建提示
        prompt = f"""你是学习助手，核心价值是"让作业成为学习的入口，而非学习的终点"。

请分析以下作业题目，结合用户的解题思路进行指导：

【作业题目】
{homework.content}

【用户提交的思路】
{user_thought}

请提供以下分析（格式化为JSON）：
{{
    "analysis": "对用户思路的分析评价，指出优点和需要改进的地方",
    "solution_steps": ["解题步骤1", "解题步骤2", ...],
    "knowledge_points": ["关联知识点1", "关联知识点2", ...],
    "similar_problems": ["类似题目推荐1", "类似题目推荐2", ...],
    "learning_tips": "学习建议和注意事项",
    "encouragement": "鼓励性评语，帮助用户建立信心"
}}

请确保：
1. 不要直接给出完整答案，而是引导用户思考
2. 知识点关联要准确，关联到用户的思路
3. 类似题目要真有可比性，不是随意推荐
4. 语言要温暖有耐心，体现"引导学习"而非"给出答案"的理念"""

        messages = [
            {"role": "system", "content": "你是一个的学习助手，帮助学生通过作业提升学习能力，而非简单地给出答案。"},
            {"role": "user", "content": prompt}
        ]

        # 调用API（带并发限制和重试）
        result = self._call_api_with_limit(messages, max_tokens=2000)

        if 'error' in result:
            return {
                'success': False,
                'error': 'api_error',
                'message': result['error'],
                'source': 'error',
                'cached': False
            }

        try:
            answer = result['choices'][0]['message']['content']
            usage = result.get('usage', {})

            # 记录Token使用
            if usage:
                self._record_token_usage(self.model, usage)

            # 清理markdown代码块
            if answer.strip().startswith('```'):
                lines = answer.split('\n')
                if lines[0].strip().startswith('```'):
                    lines = lines[1:]
                if lines and lines[-1].strip().startswith('```'):
                    lines = lines[:-1]
                answer = '\n'.join(lines)

            # 尝试解析JSON
            try:
                analysis_result = json.loads(answer)
            except json.JSONDecodeError:
                # 如果不是有效JSON，作为普通文本返回
                analysis_result = {
                    'analysis': answer,
                    'solution_steps': [],
                    'knowledge_points': [],
                    'similar_problems': [],
                    'learning_tips': '',
                    'encouragement': ''
                }

            response = {
                'success': True,
                'homework_id': homework_id,
                'analysis': analysis_result,
                'source': 'deepseek',
                'cached': False,
                'usage': usage
            }

            self._save_to_cache(cache_key, response)
            self._clean_expired_cache()

            return response

        except Exception as e:
            current_app.logger.error(f"Error processing analyze response: {e}")
            return {
                'success': False,
                'error': 'processing_error',
                'message': f'处理分析结果时出错: {str(e)}',
                'source': 'error',
                'cached': False
            }

    def generate_answer(self, homework_id, user_thought):
        """
        生成答案（认知门控：必须先验证用户已提交思路）

        返回格式化的答案
        """
        # 认知门控检查
        is_valid, error_msg = self._validate_cognitive_gate(user_thought)
        if not is_valid:
            return {
                'success': False,
                'error': 'cognitive_gate_failed',
                'message': error_msg,
                'source': 'cognitive_gate'
            }

        from models import Homework

        homework = Homework.query.get(homework_id)
        if not homework:
            return {
                'success': False,
                'error': 'homework_not_found',
                'message': '作业题目不存在',
                'source': 'error'
            }

        # 构建上下文
        context = {
            'homework_id': homework_id,
            'homework_content': homework.content,
            'homework_title': homework.title,
            'user_thought': user_thought
        }

        # 构建缓存键
        cache_prompt = f"generate_answer:{homework_id}:{user_thought[:100]}"
        cache_key = self._get_cache_key(cache_prompt, context)

        # 检查缓存
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            cached_response['cached'] = True
            return cached_response

        prompt = f"""你是学习助手，核心价值是"让作业成为学习的入口，而非学习的终点"。

【作业题目】
{homework.content}

【用户的解题思路】
{user_thought}

请提供详细解答，格式如下：
1. 先肯定用户的思路亮点
2. 指出思路中的小问题（如果有）
3. 给出完整解题步骤
4. 总结涉及的知识点

使用清晰的markdown格式，适当使用数学符号和代码块。"""

        messages = [
            {"role": "system", "content": "你是一个耐心的学习助手，帮助学生理解解题思路和方法。"},
            {"role": "user", "content": prompt}
        ]

        # 调用API（带并发限制和重试）
        result = self._call_api_with_limit(messages, max_tokens=2000)

        if 'error' in result:
            return {
                'success': False,
                'error': 'api_error',
                'message': result['error'],
                'source': 'error',
                'cached': False
            }

        try:
            answer = result['choices'][0]['message']['content']
            usage = result.get('usage', {})

            # 记录Token使用
            if usage:
                self._record_token_usage(self.model, usage)

            response = {
                'success': True,
                'homework_id': homework_id,
                'answer': answer,
                'source': 'deepseek',
                'cached': False,
                'usage': usage
            }

            self._save_to_cache(cache_key, response)
            self._clean_expired_cache()

            return response

        except Exception as e:
            current_app.logger.error(f"Error processing answer response: {e}")
            return {
                'success': False,
                'error': 'processing_error',
                'message': f'处理答案时出错: {str(e)}',
                'source': 'error',
                'cached': False
            }

    def ask_question(self, node_id, question, context=None):
        """
        知识问答 - 基于知识点进行问答
        """
        from models import KnowledgeNode

        if node_id:
            node = KnowledgeNode.query.get(node_id)
            if node:
                node_context = f"知识点：{node.title}\n\n内容：{node.content or '暂无内容'}"
                if context:
                    context = node_context + "\n\n" + context
                else:
                    context = node_context

        # 构建缓存键
        cache_key = self._get_cache_key(question, context)

        # 检查缓存
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            cached_response['cached'] = True
            return cached_response

        if context:
            system_message = f"""你是一个学习助手。请基于以下知识点回答用户的问题。

知识点上下文：
{context}

要求：
1. 回答要准确、清晰
2. 如果知识点不足以回答，说明情况
3. 可以适当拓展，但不要偏离知识点
4. 用markdown格式化回答"""
        else:
            system_message = "你是一个学习助手，请准确、清晰地回答问题。"

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
        ]

        # 调用API（带并发限制和重试）
        result = self._call_api_with_limit(messages, max_tokens=1500)

        if 'error' in result:
            return {
                'success': False,
                'error': 'api_error',
                'message': result['error'],
                'source': 'error',
                'cached': False
            }

        try:
            answer = result['choices'][0]['message']['content']
            usage = result.get('usage', {})

            # 记录Token使用
            if usage:
                self._record_token_usage(self.model, usage)

            response = {
                'success': True,
                'answer': answer,
                'node_id': node_id,
                'source': 'deepseek',
                'cached': False,
                'usage': usage
            }

            self._save_to_cache(cache_key, response)
            self._clean_expired_cache()

            return response

        except Exception as e:
            current_app.logger.error(f"Error processing ask response: {e}")
            return {
                'success': False,
                'error': 'processing_error',
                'message': f'处理问答时出错: {str(e)}',
                'source': 'error',
                'cached': False
            }

    # ==================== 保留原有方法（兼容） ====================

    def generate_answer_legacy(self, question, context=None, max_tokens=1000):
        """兼容旧接口"""
        if not self.api_key:
            return {
                'answer': 'DeepSeek API key not configured. Please set DEEPSEEK_API_KEY environment variable.',
                'source': 'error',
                'cached': False
            }

        cache_key = self._get_cache_key(question, context)
        cached_response = self._get_cached_response(cache_key)

        if cached_response:
            cached_response['cached'] = True
            return cached_response

        messages = []

        if context:
            system_message = f"""You are a helpful learning assistant. Use the following context to answer the question.

Context:
{context}

Instructions:
1. Answer based on the provided context
2. If the context doesn't contain enough information, say so
3. Provide clear, step-by-step explanations
4. Use examples when helpful
5. Format your answer with proper markdown"""
            messages.append({"role": "system", "content": system_message})
        else:
            messages.append({"role": "system", "content": "You are a helpful learning assistant for software engineering students. Provide clear, accurate answers with explanations."})

        messages.append({"role": "user", "content": question})

        result = self._call_api_with_limit(messages, max_tokens)

        if 'error' in result:
            return {
                'answer': f'Error calling AI service: {result["error"]}',
                'source': 'error',
                'cached': False
            }

        try:
            answer = result['choices'][0]['message']['content']
            usage = result.get('usage', {})

            if usage:
                self._record_token_usage(self.model, usage)

            ai_response = {
                'answer': answer,
                'source': 'deepseek',
                'cached': False,
                'usage': usage
            }

            self._save_to_cache(cache_key, ai_response)
            self._clean_expired_cache()

            return ai_response

        except Exception as e:
            current_app.logger.error(f"Unexpected error: {e}")
            return {
                'answer': f'Unexpected error: {str(e)}',
                'source': 'error',
                'cached': False
            }
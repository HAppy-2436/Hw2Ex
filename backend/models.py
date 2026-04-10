from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.sqlite import JSON

db = SQLAlchemy()

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    books = db.relationship('Book', backref='subject', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'book_count': len(self.books)
        }

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200))
    publisher = db.Column(db.String(200))
    year = db.Column(db.Integer)
    total_pages = db.Column(db.Integer)
    pdf_path = db.Column(db.String(500))
    extracted_text = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    knowledge_nodes = db.relationship('KnowledgeNode', backref='book', lazy=True, cascade='all, delete-orphan')
    homework = db.relationship('Homework', backref='book', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'year': self.year,
            'total_pages': self.total_pages,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class KnowledgeNode(db.Model):
    __tablename__ = 'knowledge_nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('knowledge_nodes.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    level = db.Column(db.Integer, default=0)
    order_index = db.Column(db.Integer, default=0)
    page_start = db.Column(db.Integer)
    page_end = db.Column(db.Integer)
    content = db.Column(db.Text)
    tags = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    parent = db.relationship('KnowledgeNode', remote_side=[id], backref='children')
    homework = db.relationship('Homework', backref='primary_knowledge', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'parent_id': self.parent_id,
            'title': self.title,
            'level': self.level,
            'order_index': self.order_index,
            'page_start': self.page_start,
            'page_end': self.page_end,
            'content': self.content,
            'tags': self.tags or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'child_count': len(self.children)
        }

class Homework(db.Model):
    __tablename__ = 'homework'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    primary_node_id = db.Column(db.Integer, db.ForeignKey('knowledge_nodes.id'), nullable=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    secondary_nodes = db.Column(JSON)
    status = db.Column(db.String(20), default='new')
    mastery_level = db.Column(db.Integer, default=0)  # 0-5: 0=陌生, 5=熟悉
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'primary_node_id': self.primary_node_id,
            'title': self.title,
            'content': self.content,
            'answer': self.answer,
            'secondary_nodes': self.secondary_nodes or [],
            'status': self.status,
            'mastery_level': self.mastery_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class LearningRecord(db.Model):
    __tablename__ = 'learning_records'
    
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('knowledge_nodes.id'), nullable=False)
    duration = db.Column(db.Integer, default=0)  # 学习时长（分钟）
    notes = db.Column(db.Text)  # 学习笔记
    self_rating = db.Column(db.Integer)  # 自我评分 1-5
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    knowledge_node = db.relationship('KnowledgeNode', backref='learning_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'node_id': self.node_id,
            'duration': self.duration,
            'notes': self.notes,
            'self_rating': self.self_rating,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('knowledge_nodes.id'), nullable=True)
    conversation_type = db.Column(db.String(50), default='general')  # 对话类型: general, homework_help, concept_explain, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    knowledge_node = db.relationship('KnowledgeNode', backref='conversations')
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'node_id': self.node_id,
            'conversation_type': self.conversation_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ReviewPlan(db.Model):
    """复习计划表"""
    __tablename__ = 'review_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)  # 考试日期
    scope = db.Column(db.Text)  # 考试范围描述
    status = db.Column(db.String(20), default='planning')  # planning/in_progress/completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    subject = db.relationship('Subject', backref='review_plans')
    checkpoints = db.relationship('ReviewCheckpoint', backref='plan', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'exam_date': self.exam_date.isoformat() if self.exam_date else None,
            'scope': self.scope,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'checkpoint_count': len(self.checkpoints)
        }


class ReviewCheckpoint(db.Model):
    """复习知识点勾选表"""
    __tablename__ = 'review_checkpoints'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('review_plans.id'), nullable=False)
    knowledge_point_id = db.Column(db.Integer, db.ForeignKey('knowledge_nodes.id'), nullable=False)
    learning_status = db.Column(db.String(20), default='not_started')  # not_started/learning/mastered
    mastery_level = db.Column(db.Integer, default=0)  # 0-5
    notes = db.Column(db.Text)  # 复习笔记
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    knowledge_point = db.relationship('KnowledgeNode', backref='review_checkpoints')
    
    def to_dict(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'knowledge_point_id': self.knowledge_point_id,
            'learning_status': self.learning_status,
            'mastery_level': self.mastery_level,
            'notes': self.notes,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'knowledge_point': self.knowledge_point.to_dict() if self.knowledge_point else None
        }


class TokenUsage(db.Model):
    """Token使用记录表 - 用于API成本控制"""
    __tablename__ = 'token_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    hour = db.Column(db.Integer, nullable=False)     # 0-23
    model = db.Column(db.String(50), nullable=False)
    prompt_tokens = db.Column(db.Integer, default=0)
    completion_tokens = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)
    cost_usd = db.Column(db.Float, default=0)
    request_count = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date,
            'hour': self.hour,
            'model': self.model,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'cost_usd': self.cost_usd,
            'request_count': self.request_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserProfile(db.Model):
    """用户画像表 - 存储用户学习信息和偏好"""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    grade = db.Column(db.String(50))           # 年级，如"大一"
    major = db.Column(db.String(200))         # 专业
    enrollment_year = db.Column(db.Integer)   # 入学年份
    learning_background = db.Column(JSON)     # 先验知识描述
    subject_preferences = db.Column(JSON)     # 学科偏好
    learning_habits = db.Column(JSON)         # 学习习惯
    persistent_weak_points = db.Column(JSON) # 持续跟踪的薄弱点
    current_learning_session = db.Column(JSON) # 当前学习上下文
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'grade': self.grade,
            'major': self.major,
            'enrollment_year': self.enrollment_year,
            'learning_background': self.learning_background or {},
            'subject_preferences': self.subject_preferences or {},
            'learning_habits': self.learning_habits or {},
            'persistent_weak_points': self.persistent_weak_points or [],
            'current_learning_session': self.current_learning_session or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ConversationContext(db.Model):
    """对话上下文表 - 管理AI对话的学习上下文"""
    __tablename__ = 'conversation_contexts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)   # 用户ID（可选，兼容访客）
    session_id = db.Column(db.String(100), nullable=False)  # 对话会话ID
    conversation_type = db.Column(db.String(50), default='learning')  # learning/homework/review
    scope_type = db.Column(db.String(50))            # node/chapter/subject
    scope_id = db.Column(db.Integer)                 # 关联的知识点/章节/学科ID
    context_summary = db.Column(JSON)                # 上下文摘要
    understanding_check_passed = db.Column(db.Boolean, default=False)  # AI是否验证了用户理解
    explanation_depth_level = db.Column(db.Integer, default=1)  # 讲解深度级别 1-3
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)  # 过期时间
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'conversation_type': self.conversation_type,
            'scope_type': self.scope_type,
            'scope_id': self.scope_id,
            'context_summary': self.context_summary or {},
            'understanding_check_passed': self.understanding_check_passed,
            'explanation_depth_level': self.explanation_depth_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': datetime.utcnow() > self.expires_at if self.expires_at else False
        }
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
    status = db.Column(db.String(20), default='learning')
    last_reviewed = db.Column(db.DateTime, default=datetime.utcnow)
    review_count = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    total_attempts = db.Column(db.Integer, default=0)
    self_rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    knowledge_node = db.relationship('KnowledgeNode', backref='learning_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'node_id': self.node_id,
            'status': self.status,
            'last_reviewed': self.last_reviewed.isoformat() if self.last_reviewed else None,
            'review_count': self.review_count,
            'correct_count': self.correct_count,
            'total_attempts': self.total_attempts,
            'self_rating': self.self_rating,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('knowledge_nodes.id'), nullable=True)
    key_moments = db.Column(JSON)
    summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    knowledge_node = db.relationship('KnowledgeNode', backref='conversations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'node_id': self.node_id,
            'key_moments': self.key_moments or [],
            'summary': self.summary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
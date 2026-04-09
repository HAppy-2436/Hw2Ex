# 学习复习作业管理助手 - 技术架构设计文档

## 1. 架构概览

### 1.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              客户端层 (Vue.js SPA)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   教材管理   │  │  知识结构   │  │  作业管理   │  │  学习/复习  │    │
│  │   组件      │  │   组件      │  │   组件      │  │   组件      │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │            │
│  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐   │
│  │                        Pinia 状态管理层                           │   │
│  │  subjectsStore | booksStore | nodesStore | homeworkStore | ...   │   │
│  └──────────────────────────────┬───────────────────────────────────┘   │
│                                  │                                      │
│  ┌──────────────────────────────┴───────────────────────────────────┐   │
│  │                     API 调用层 (Axios)                            │   │
│  │              /api/subjects | /api/books | /api/nodes | ...        │   │
│  └──────────────────────────────┬───────────────────────────────────┘   │
└──────────────────────────────────┼───────────────────────────────────────┘
                                   │ HTTP/REST
┌──────────────────────────────────┼───────────────────────────────────────┐
│                              服务层 │                                       │
│  ┌───────────────────────────────┴───────────────────────────────────┐ │
│  │                      Flask API 网关                                 │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │ │
│  │  │CORS中间件│  │认证中间件│  │限流中间件│  │错误处理  │  │请求日志 │  │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │ │
│  └───┬───────────┬───────────┬───────────┬───────────┬───────────────┘ │
│      │           │           │           │           │                 │
│  ┌───┴───┐   ┌───┴───┐   ┌───┴───┐   ┌───┴───┐   ┌───┴───┐             │
│  │subjects│   │ books │   │ nodes │   │homework│   │learning│  ...     │
│  │ 蓝图   │   │ 蓝图   │   │ 蓝图   │   │ 蓝图   │   │ 蓝图   │           │
│  └───┬───┘   └───┬───┘   └───┬───┘   └───┬───┘   └───┬───┘             │
│      │           │           │           │           │                 │
│  ┌───┴───────────┴───────────┴───────────┴───────────┴───────────────┐ │
│  │                         服务层 (Services)                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│ │
│  │  │ PDF解析服务  │  │ AI服务      │  │ 同步服务    │  │ 缓存服务    ││ │
│  │  │ (PyMuPDF)   │  │(DeepSeek)   │  │ (JSON)      │  │ (内存+SQLite)││ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘│ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                    │                                     │
│  ┌─────────────────────────────────┴─────────────────────────────────┐ │
│  │                      数据访问层 (SQLAlchemy ORM)                   │ │
│  │        Subject | Book | KnowledgeNode | Homework | LearningRecord  │ │
│  └─────────────────────────────────┬─────────────────────────────────┘ │
│                                    │                                     │
│  ┌─────────────────────────────────┴─────────────────────────────────┐ │
│  │                          SQLite 数据库                             │ │
│  │    subjects | books | knowledge_nodes | homework | learning_records│ │
│  │    conversations                                                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │        文件存储              │
                    │  /data/uploads (PDF文件)    │
                    │  /data/exports (导出JSON)   │
                    └─────────────────────────────┘
```

### 1.2 技术栈总结

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 前端框架 | Vue 3 + Composition API | 渐进式JS框架，组合式API更适合复杂状态 |
| 前端状态 | Pinia | Vue3官方推荐，轻量级状态管理 |
| 前端路由 | Vue Router 4 | SPA路由管理 |
| UI框架 | Element Plus | Vue3组件库，支持中文 |
| HTTP客户端 | Axios | Promise-based HTTP client |
| 后端框架 | Flask 3.0 | 轻量级Python Web框架 |
| ORM | Flask-SQLAlchemy | 数据库ORM映射 |
| PDF解析 | PyMuPDF (fitz) | 高效PDF解析，内存优化 |
| AI集成 | DeepSeek API | 本地个人使用，无需限流 |
| 数据库 | SQLite | 轻量级，适合1核1G服务器 |
| 缓存 | 内存缓存 + SQLite | LRU缓存热点数据 |

---

## 2. 后端架构设计

### 2.1 Flask应用结构

```
backend/
├── app.py                      # 应用入口，注册蓝图
├── extensions.py               # Flask扩展初始化
├── config.py                   # 配置文件
├── models.py                   # 数据模型（已存在）
├── routes/                     # API路由蓝图
│   ├── __init__.py             # 蓝图注册
│   ├── subjects.py             # 科目管理 (已完成)
│   ├── books.py                # 教材管理
│   ├── knowledge_nodes.py      # 知识节点管理
│   ├── homework.py             # 作业管理
│   ├── learning.py             # 学习/复习模式
│   ├── conversations.py         # AI对话
│   └── sync.py                 # 同步接口
├── services/                   # 业务逻辑服务层
│   ├── __init__.py
│   ├── pdf_service.py           # PDF解析服务
│   ├── ai_service.py           # AI服务（含对话缓存）
│   ├── sync_service.py         # 同步服务
│   └── cache_service.py         # 缓存服务
├── utils/                      # 工具函数
│   ├── __init__.py
│   ├── decorators.py           # 装饰器（认证、限流）
│   └── helpers.py               # 辅助函数
├── middleware/                 # 中间件
│   ├── __init__.py
│   ├── error_handler.py         # 全局错误处理
│   └── request_logger.py        # 请求日志
└── requirements.txt
```

### 2.2 蓝图划分与职责

| 蓝图 | 前缀 | 职责 |
|------|------|------|
| subjects | `/api/subjects` | 科目 CRUD |
| books | `/api/books` | 教材管理、PDF上传 |
| knowledge_nodes | `/api/nodes` | 知识节点树管理 |
| homework | `/api/homework` | 作业题目录入、答案生成 |
| learning | `/api/learning` | 学习/复习模式API |
| conversations | `/api/conversations` | AI对话管理 |
| sync | `/api/sync` | JSON导入/导出 |

### 2.3 API路由详细设计

#### 2.3.1 科目管理 (`/api/subjects`)

| 端点 | 方法 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/subjects` | GET | 获取所有科目 | - | `[{id, name, description, book_count}]` |
| `/api/subjects` | POST | 创建科目 | `{name, description?}` | `{id, name, ...}` |
| `/api/subjects/<id>` | GET | 获取单个科目 | - | `{id, name, ...}` |
| `/api/subjects/<id>` | PUT | 更新科目 | `{name?, description?}` | `{id, name, ...}` |
| `/api/subjects/<id>` | DELETE | 删除科目 | - | `{message}` |
| `/api/subjects/<id>/books` | GET | 获取科目下所有教材 | - | `[{id, title, ...}]` |

#### 2.3.2 教材管理 (`/api/books`)

| 端点 | 方法 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/books` | GET | 获取所有教材 | - | `[{id, title, subject_id, ...}]` |
| `/api/books` | POST | 创建教材（基础信息） | `{subject_id, title, author?, publisher?, year?}` | `{id, title, ...}` |
| `/api/books/<id>` | GET | 获取教材详情 | - | `{id, title, total_pages, ...}` |
| `/api/books/<id>` | PUT | 更新教材信息 | `{title?, author?, ...}` | `{id, title, ...}` |
| `/api/books/<id>` | DELETE | 删除教材 | - | `{message}` |
| `/api/books/<id>/pdf` | POST | 上传PDF文件 | `multipart/form-data: file` | `{id, pdf_path, total_pages}` |
| `/api/books/<id>/pdf` | GET | 下载PDF文件 | - | 文件流 |
| `/api/books/<id>/parse` | POST | 解析PDF提取章节 | `{strategy: "auto"|"manual"}` | `{nodes: [...]}` |
| `/api/books/<id>/text` | GET | 获取提取的文本 | `?page_start=1&page_end=10` | `{text: "...", page_count}` |

#### 2.3.3 知识节点管理 (`/api/nodes`)

| 端点 | 方法 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/nodes` | GET | 获取节点列表 | `?book_id=1&parent_id=null` | `[{id, title, level, ...}]` |
| `/api/nodes` | POST | 创建节点 | `{book_id, title, parent_id?, level?, content?, tags?}` | `{id, title, ...}` |
| `/api/nodes/<id>` | GET | 获取节点详情 | - | `{id, title, content, children, ...}` |
| `/api/nodes/<id>` | PUT | 更新节点 | `{title?, content?, tags?, page_start?, page_end?}` | `{id, title, ...}` |
| `/api/nodes/<id>` | DELETE | 删除节点（含子树） | - | `{message, deleted_count}` |
| `/api/nodes/<id>/children` | GET | 获取子节点 | - | `[{id, title, ...}]` |
| `/api/nodes/<id>/tree` | GET | 获取完整子树 | - | 递归树结构 |
| `/api/nodes/batch` | POST | 批量创建节点 | `{nodes: [{book_id, title, parent_id?, ...}, ...]}` | `{created: n}` |

#### 2.3.4 作业管理 (`/api/homework`)

| 端点 | 方法 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/homework` | GET | 获取作业列表 | `?book_id=1&status=pending` | `[{id, content, status, ...}]` |
| `/api/homework` | POST | 创建作业 | `{book_id, primary_node_id, location, content, secondary_nodes?}` | `{id, content, ...}` |
| `/api/homework/<id>` | GET | 获取作业详情 | - | `{id, content, answer, status, ...}` |
| `/api/homework/<id>` | PUT | 更新作业 | `{content?, answer?, status?}` | `{id, content, ...}` |
| `/api/homework/<id>` | DELETE | 删除作业 | - | `{message}` |
| `/api/homework/<id>/answer` | POST | **AI生成答案** | `{context?: "..."}` | `{answer: "...", confidence}` |
| `/api/homework/generate` | POST | **AI批量生成答案** | `{homework_ids: [1,2,3], book_id?}` | `{results: [...]}` |
| `/api/homework/import` | POST | CSV批量导入 | `multipart/form-data: file` | `{imported: n, failed: n}` |

#### 2.3.5 学习/复习模式 (`/api/learning`)

| 端点 | 方法 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/learning/mode` | GET | 获取当前模式 | - | `{mode: "learning"|"review"|"exam"}` |
| `/api/learning/mode` | POST | 切换模式 | `{mode: "learning"|"review"|"exam"}` | `{mode, settings}` |
| `/api/learning/study` | POST | 开始学习节点 | `{node_id}` | `{record_id, node, content}` |
| `/api/learning/review` | POST | 复习节点 | `{record_id, result}` | `{next_review, confidence}` |
| `/api/learning/records` | GET | 获取学习记录 | `?node_id=1&status=learning` | `[{id, status, review_count, ...}]` |
| `/api/learning/records/<id>` | PUT | 更新学习记录 | `{status?, self_rating?}` | `{id, status, ...}` |
| `/api/learning/dashboard` | GET | 获取学习仪表盘 | - | `{total_nodes, mastered, learning, ...}` |
| `/api/learning/due` | GET | 获取待复习节点 | - | `[{record_id, node, due_date, ...}]` |
| `/api/learning/exam/prepare` | POST | 准备考试范围 | `{book_id, exam_date?, topics?}` | `{coverage, weak_nodes, suggestions}` |
| `/api/learning/exam/question` | POST | 生成模拟题 | `{node_ids: [...], count?}` | `{questions: [...]}` |

#### 2.3.6 AI对话 (`/api/conversations`)

| 端点 | 方法 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/conversations` | GET | 获取对话列表 | `?node_id=1` | `[{id, summary, created_at, ...}]` |
| `/api/conversations` | POST | 创建对话/提问 | `{node_id?, question, context?}` | `{id, answer, key_moments}` |
| `/api/conversations/<id>` | GET | 获取对话详情 | - | `{id, messages, summary, ...}` |
| `/api/conversations/<id>` | DELETE | 删除对话 | - | `{message}` |
| `/api/conversations/<id>/messages` | GET | 获取对话消息 | - | `[{role, content, created_at}]` |
| `/api/conversations/<id>/continue` | POST | 继续对话 | `{question}` | `{answer, ...}` |

#### 2.3.7 同步接口 (`/api/sync`)

| 端点 | 方法 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/sync/export` | POST | 导出全部数据 | `{include_pdf?: false}` | JSON文件下载 |
| `/api/sync/export/<type>` | POST | 导出指定类型 | `{type: "subjects"|"books"|...}` | JSON文件下载 |
| `/api/sync/import` | POST | 导入数据 | `multipart/form-data: file` | `{imported: n, skipped: n}` |
| `/api/sync/backup` | POST | 创建备份 | - | `{backup_path, created_at}` |
| `/api/sync/restore` | POST | 恢复备份 | `{backup_path}` | `{restored: true}` |

### 2.4 服务层设计

#### 2.4.1 PDF解析服务 (`services/pdf_service.py`)

```python
# 核心功能
class PDFService:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
    
    def save_pdf(self, file, book_id: int) -> str:
        """保存上传的PDF文件"""
        
    def get_page_count(self, pdf_path: str) -> int:
        """获取PDF页数"""
        
    def extract_text(self, pdf_path: str, page_start: int = 1, page_end: int = None) -> str:
        """提取指定页面范围的文本"""
        
    def extract_chapters(self, pdf_path: str, strategy: str = "auto") -> List[Dict]:
        """自动或手动策略提取章节
        
        auto: 基于目录页、字号变化、关键词检测
        manual: 基于预定义的页面结构
        """
        
    def extract_page_text(self, pdf_path: str, page_num: int) -> str:
        """提取单页文本（内存优化）"""
        
    def search_in_pdf(self, pdf_path: str, keyword: str) -> List[Dict]:
        """在PDF中搜索关键词"""

# 内存优化策略
# 1. 分页读取：大文件不一次性加载
# 2. 流式处理：使用生成器逐页处理
# 3. 及时释放：使用上下文管理器
# 4. 缓存控制：限制缓存大小
```

#### 2.4.2 AI服务 (`services/ai_service.py`)

```python
# 核心功能
class AIService:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.client = DeepSeekClient(api_key, base_url)
        self.cache = LRUCache(max_size=1000)  # 对话缓存
        self.conversation_cache = LRUCache(max_size=100)  # 会话缓存
    
    def ask_question(self, question: str, context: Dict = None, node_id: int = None) -> Dict:
        """提问并获取回答（带缓存）"""
        # 1. 检查缓存
        # 2. 调用API
        # 3. 保存到缓存
        # 4. 记录conversation
        
    def generate_answer(self, homework_content: str, context: str = None) -> Dict:
        """为作业生成答案"""
        
    def generate_questions(self, node_ids: List[int], count: int = 5) -> List[Dict]:
        """基于知识点生成模拟题"""
        
    def summarize_conversation(self, messages: List[Dict]) -> str:
        """总结对话要点"""
        
    def analyze_knowledge_gaps(self, book_id: int) -> List[Dict]:
        """分析知识薄弱点"""

# 缓存策略
# - 问题+上下文hash作为key
# - TTL: 24小时
# - 相似问题合并
```

#### 2.4.3 同步服务 (`services/sync_service.py`)

```python
# 核心功能
class SyncService:
    def __init__(self, db_path: str, export_folder: str):
        self.db_path = db_path
        self.export_folder = export_folder
    
    def export_all(self, include_pdf: bool = False) -> Dict:
        """导出全部数据"""
        
    def export_by_type(self, data_type: str) -> Dict:
        """按类型导出"""
        
    def import_data(self, json_file: str, merge_strategy: str = "skip") -> Dict:
        """导入数据
        
        merge_strategy: skip | overwrite | merge
        """
        
    def create_backup(self) -> str:
        """创建数据库备份"""
        
    def restore_backup(self, backup_path: str) -> bool:
        """恢复备份"""
```

#### 2.4.4 缓存服务 (`services/cache_service.py`)

```python
from functools import wraps
from typing import Any, Callable
import hashlib
import json

class LRUCache:
    """简单的LRU缓存实现"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 86400):
        self.max_size = max_size
        self.ttl = ttl  # seconds
        self._cache = {}
    
    def get(self, key: str) -> Any:
        """获取缓存"""
        
    def set(self, key: str, value: Any) -> None:
        """设置缓存"""
        
    def delete(self, key: str) -> None:
        """删除缓存"""
        
    def clear(self) -> None:
        """清空缓存"""

def cached(key_prefix: str, ttl: int = 3600):
    """缓存装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存key
            key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
            cache_key = f"{key_prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"
            # 检查缓存...
            # 执行函数...
            # 保存缓存...
        return wrapper
    return decorator
```

### 2.5 中间件设计

#### 2.5.1 错误处理中间件 (`middleware/error_handler.py`)

```python
from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app: Flask):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad Request', 'message': str(e)}), 400
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not Found', 'message': str(e)}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({'error': e.name, 'message': e.description}), e.code
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        # 记录日志
        app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return jsonify({'error': 'Server Error', 'message': 'An unexpected error occurred'}), 500
```

#### 2.5.2 限流中间件 (`utils/decorators.py`)

```python
from functools import wraps
from flask import request, jsonify
import time

class RateLimiter:
    def __init__(self, max_requests: int = 100, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    
    def is_allowed(self, key: str) -> bool:
        """检查是否允许请求"""
        now = time.time()
        # 清理过期记录
        # 检查限制
        return True

rate_limiter = RateLimiter(max_requests=100, window=60)  # 1分钟100次

def rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        client_ip = request.remote_addr
        if not rate_limiter.is_allowed(client_ip):
            return jsonify({'error': 'Too Many Requests', 'message': 'Rate limit exceeded'}), 429
        return f(*args, **kwargs)
    return decorated
```

#### 2.5.3 请求日志中间件 (`middleware/request_logger.py`)

```python
from flask import request, g
import time
import logging

def register_request_logger(app: Flask):
    @app.before_request
    def before_request():
        g.start_time = time.time()
        app.logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            app.logger.info(f"Response: {response.status_code} in {elapsed:.3f}s")
        return response
```

### 2.6 app.py 蓝图注册

```python
# app.py 重构
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import os

from .extensions import db
from .config import config

def create_app(config_name: str = 'default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 修复代理头
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 初始化扩展
    db.init_app(app)
    
    # 注册中间件
    from .middleware.error_handler import register_error_handlers
    from .middleware.request_logger import register_request_logger
    register_error_handlers(app)
    register_request_logger(app)
    
    # 注册蓝图
    from .routes import register_blueprints
    register_blueprints(app)
    
    # 健康检查
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok'})
    
    # 创建数据库
    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app
```

```python
# routes/__init__.py
def register_blueprints(app):
    from .subjects import bp as subjects_bp
    from .books import bp as books_bp
    from .knowledge_nodes import bp as nodes_bp
    from .homework import bp as homework_bp
    from .learning import bp as learning_bp
    from .conversations import bp as conversations_bp
    from .sync import bp as sync_bp
    
    app.register_blueprint(subjects_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(nodes_bp)
    app.register_blueprint(homework_bp)
    app.register_blueprint(learning_bp)
    app.register_blueprint(conversations_bp)
    app.register_blueprint(sync_bp)
```

---

## 3. 前端架构设计

### 3.1 Vue.js 项目结构

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── main.js                    # 应用入口
│   ├── App.vue                    # 根组件
│   ├── api/                       # API 调用层
│   │   ├── index.js               # Axios 实例配置
│   │   ├── subjects.js            # 科目 API
│   │   ├── books.js               # 教材 API
│   │   ├── nodes.js               # 知识节点 API
│   │   ├── homework.js            # 作业 API
│   │   ├── learning.js            # 学习 API
│   │   ├── conversations.js       # 对话 API
│   │   └── sync.js                # 同步 API
│   ├── stores/                    # Pinia 状态管理
│   │   ├── index.js               # Store 入口
│   │   ├── subjects.js            # 科目状态
│   │   ├── books.js               # 教材状态
│   │   ├── nodes.js               # 知识节点状态
│   │   ├── homework.js            # 作业状态
│   │   ├── learning.js            # 学习状态
│   │   ├── conversations.js       # 对话状态
│   │   └── app.js                 # 全局应用状态
│   ├── views/                     # 页面视图
│   │   ├── DashboardView.vue      # 仪表盘
│   │   ├── subjects/
│   │   │   ├── SubjectList.vue    # 科目列表
│   │   │   └── SubjectDetail.vue   # 科目详情
│   │   ├── books/
│   │   │   ├── BookList.vue       # 教材列表
│   │   │   ├── BookDetail.vue     # 教材详情
│   │   │   └── BookUpload.vue     # PDF上传
│   │   ├── knowledge/
│   │   │   ├── KnowledgeTree.vue  # 知识树
│   │   │   └── NodeDetail.vue     # 节点详情
│   │   ├── homework/
│   │   │   ├── HomeworkList.vue   # 作业列表
│   │   │   ├── HomeworkDetail.vue # 作业详情
│   │   │   └── HomeworkImport.vue # 批量导入
│   │   ├── learning/
│   │   │   ├── LearningMode.vue   # 学习模式
│   │   │   ├── ReviewMode.vue     # 复习模式
│   │   │   └── ExamMode.vue       # 考试模式
│   │   ├── chat/
│   │   │   ├── ChatView.vue       # AI答疑主界面
│   │   │   └── ChatHistory.vue    # 对话历史
│   │   └── sync/
│   │       └── SyncView.vue       # 同步管理
│   ├── components/                # 可复用组件
│   │   ├── common/
│   │   │   ├── TreeList.vue       # 树形列表
│   │   │   ├── TreeNode.vue       # 树节点
│   │   │   ├── FileUpload.vue     # 文件上传
│   │   │   ├── MarkdownEditor.vue # Markdown编辑
│   │   │   └── Loading.vue        # 加载状态
│   │   ├── subject/
│   │   │   ├── SubjectCard.vue    # 科目卡片
│   │   │   └── SubjectForm.vue    # 科目表单
│   │   ├── book/
│   │   │   ├── BookCard.vue       # 教材卡片
│   │   │   └── BookViewer.vue     # PDF预览
│   │   ├── knowledge/
│   │   │   ├── NodeCard.vue       # 节点卡片
│   │   │   └── KnowledgeGraph.vue # 知识图谱
│   │   ├── homework/
│   │   │   ├── HomeworkCard.vue   # 作业卡片
│   │   │   └── AnswerDisplay.vue  # 答案展示
│   │   ├── learning/
│   │   │   ├── ProgressRing.vue   # 进度环
│   │   │   ├── StudyCard.vue      # 学习卡片
│   │   │   └── ReviewQueue.vue    # 复习队列
│   │   └── chat/
│   │       ├── ChatMessage.vue    # 聊天消息
│   │       └── ChatInput.vue      # 聊天输入
│   ├── router/
│   │   └── index.js               # 路由配置
│   ├── utils/
│   │   ├── index.js               # 工具函数
│   │   ├── storage.js             # 本地存储
│   │   └── format.js              # 格式化函数
│   └── styles/
│       ├── variables.scss         # 样式变量
│       ├── base.scss              # 基础样式
│       └── transition.scss        # 过渡动画
├── package.json
├── vite.config.js
└── .env
```

### 3.2 路由配置 (`router/index.js`)

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: '学习助手' }
  },
  {
    path: '/subjects',
    name: 'Subjects',
    component: () => import('@/views/subjects/SubjectList.vue'),
    meta: { title: '科目管理' }
  },
  {
    path: '/subjects/:id',
    name: 'SubjectDetail',
    component: () => import('@/views/subjects/SubjectDetail.vue'),
    meta: { title: '科目详情' }
  },
  {
    path: '/books',
    name: 'Books',
    component: () => import('@/views/books/BookList.vue'),
    meta: { title: '教材管理' }
  },
  {
    path: '/books/:id',
    name: 'BookDetail',
    component: () => import('@/views/books/BookDetail.vue'),
    meta: { title: '教材详情' }
  },
  {
    path: '/books/:id/upload',
    name: 'BookUpload',
    component: () => import('@/views/books/BookUpload.vue'),
    meta: { title: '上传教材' }
  },
  {
    path: '/knowledge',
    name: 'KnowledgeTree',
    component: () => import('@/views/knowledge/KnowledgeTree.vue'),
    meta: { title: '知识结构' }
  },
  {
    path: '/knowledge/:id',
    name: 'NodeDetail',
    component: () => import('@/views/knowledge/NodeDetail.vue'),
    meta: { title: '知识点详情' }
  },
  {
    path: '/homework',
    name: 'Homework',
    component: () => import('@/views/homework/HomeworkList.vue'),
    meta: { title: '作业管理' }
  },
  {
    path: '/homework/:id',
    name: 'HomeworkDetail',
    component: () => import('@/views/homework/HomeworkDetail.vue'),
    meta: { title: '作业详情' }
  },
  {
    path: '/homework/import',
    name: 'HomeworkImport',
    component: () => import('@/views/homework/HomeworkImport.vue'),
    meta: { title: '导入作业' }
  },
  {
    path: '/learning',
    name: 'Learning',
    component: () => import('@/views/learning/LearningMode.vue'),
    meta: { title: '学习模式' }
  },
  {
    path: '/review',
    name: 'Review',
    component: () => import('@/views/learning/ReviewMode.vue'),
    meta: { title: '复习模式' }
  },
  {
    path: '/exam',
    name: 'Exam',
    component: () => import('@/views/learning/ExamMode.vue'),
    meta: { title: '考试模式' }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/chat/ChatView.vue'),
    meta: { title: 'AI答疑' }
  },
  {
    path: '/chat/:id',
    name: 'ChatHistory',
    component: () => import('@/views/chat/ChatHistory.vue'),
    meta: { title: '对话历史' }
  },
  {
    path: '/sync',
    name: 'Sync',
    component: () => import('@/views/sync/SyncView.vue'),
    meta: { title: '数据同步' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 学习助手` : '学习助手'
  next()
})

export default router
```

### 3.3 Pinia Store 设计

#### 3.3.1 Store 入口 (`stores/index.js`)

```javascript
import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia

// 导出所有 store
export { useSubjectStore } from './subjects'
export { useBookStore } from './books'
export { useNodeStore } from './nodes'
export { useHomeworkStore } from './homework'
export { useLearningStore } from './learning'
export { useConversationStore } from './conversations'
export { useAppStore } from './app'
```

#### 3.3.2 科目 Store (`stores/subjects.js`)

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '@/api/subjects'

export const useSubjectStore = defineStore('subjects', () => {
  // 状态
  const subjects = ref([])
  const currentSubject = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // 计算属性
  const subjectCount = computed(() => subjects.value.length)
  const subjectMap = computed(() => 
    subjects.value.reduce((acc, s) => ({ ...acc, [s.id]: s }), {})
  )

  // Actions
  async function fetchSubjects() {
    loading.value = true
    error.value = null
    try {
      subjects.value = await api.getSubjects()
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createSubject(data) {
    const subject = await api.createSubject(data)
    subjects.value.push(subject)
    return subject
  }

  async function updateSubject(id, data) {
    const updated = await api.updateSubject(id, data)
    const index = subjects.value.findIndex(s => s.id === id)
    if (index !== -1) subjects.value[index] = updated
    return updated
  }

  async function deleteSubject(id) {
    await api.deleteSubject(id)
    subjects.value = subjects.value.filter(s => s.id !== id)
  }

  async function fetchSubject(id) {
    loading.value = true
    try {
      currentSubject.value = await api.getSubject(id)
      return currentSubject.value
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    subjects,
    currentSubject,
    loading,
    error,
    // 计算属性
    subjectCount,
    subjectMap,
    // Actions
    fetchSubjects,
    createSubject,
    updateSubject,
    deleteSubject,
    fetchSubject
  }
})
```

#### 3.3.3 学习 Store (`stores/learning.js`)

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '@/api/learning'

export const useLearningStore = defineStore('learning', () => {
  // 状态
  const mode = ref('learning')  // 'learning' | 'review' | 'exam'
  const currentRecord = ref(null)
  const records = ref([])
  const dashboard = ref(null)
  const dueReviews = ref([])
  const loading = ref(false)

  // 计算属性
  const masteredCount = computed(() => 
    records.value.filter(r => r.status === 'mastered').length
  )
  const learningCount = computed(() => 
    records.value.filter(r => r.status === 'learning').length
  )
  const progress = computed(() => {
    const total = records.value.length
    if (total === 0) return 0
    return Math.round((masteredCount.value / total) * 100)
  })

  // Actions
  async function setMode(newMode) {
    mode.value = newMode
    await api.setMode(newMode)
  }

  async function fetchDashboard() {
    loading.value = true
    try {
      dashboard.value = await api.getDashboard()
    } finally {
      loading.value = false
    }
  }

  async function fetchDueReviews() {
    dueReviews.value = await api.getDueReviews()
  }

  async function startStudy(nodeId) {
    const result = await api.startStudy(nodeId)
    currentRecord.value = result.record
    return result
  }

  async function recordReview(recordId, result) {
    const updated = await api.recordReview(recordId, result)
    const index = records.value.findIndex(r => r.id === recordId)
    if (index !== -1) records.value[index] = updated
    return updated
  }

  async function fetchRecords(filters = {}) {
    records.value = await api.getRecords(filters)
  }

  return {
    // 状态
    mode,
    currentRecord,
    records,
    dashboard,
    dueReviews,
    loading,
    // 计算属性
    masteredCount,
    learningCount,
    progress,
    // Actions
    setMode,
    fetchDashboard,
    fetchDueReviews,
    startStudy,
    recordReview,
    fetchRecords
  }
})
```

### 3.4 API 调用层 (`api/index.js`)

```javascript
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

// 创建 axios 实例
const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
client.interceptors.request.use(
  config => {
    // 添加 token（如果需要）
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
client.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        // 处理未授权
        console.error('Unauthorized')
      } else if (status === 429) {
        // 处理限流
        console.error('Rate limit exceeded')
      }
      return Promise.reject(new Error(data.message || 'Request failed'))
    }
    return Promise.reject(error)
  }
)

export default client
```

```javascript
// api/learning.js
import client from './index'

export const learningApi = {
  getMode: () => client.get('/learning/mode'),
  setMode: (mode) => client.post('/learning/mode', { mode }),
  getDashboard: () => client.get('/learning/dashboard'),
  getDueReviews: () => client.get('/learning/due'),
  getRecords: (params) => client.get('/learning/records', { params }),
  startStudy: (nodeId) => client.post('/learning/study', { node_id: nodeId }),
  recordReview: (recordId, result) => client.post(`/learning/review/${recordId}`, result),
  prepareExam: (data) => client.post('/learning/exam/prepare', data),
  generateQuestions: (data) => client.post('/learning/exam/question', data)
}
```

### 3.5 组件结构示例

#### 3.5.1 知识树组件 (`components/common/TreeList.vue`)

```vue
<template>
  <div class="tree-list">
    <TreeNode
      v-for="node in nodes"
      :key="node.id"
      :node="node"
      :selected-id="selectedId"
      @select="handleSelect"
      @toggle="handleToggle"
    />
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import TreeNode from './TreeNode.vue'

const props = defineProps({
  nodes: {
    type: Array,
    required: true
  },
  selectedId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['select', 'toggle'])

function handleSelect(node) {
  emit('select', node)
}

function handleToggle(node) {
  emit('toggle', node)
}
</script>
```

#### 3.5.2 知识节点组件 (`components/common/TreeNode.vue`)

```vue
<template>
  <div
    class="tree-node"
    :class="{ 'is-selected': selectedId === node.id, 'is-expanded': expanded }"
    :style="{ paddingLeft: `${level * 16 + 12}px` }"
    @click="handleClick"
  >
    <span v-if="hasChildren" class="toggle-icon" @click.stop="toggle">
      {{ expanded ? '▼' : '▶' }}
    </span>
    <span v-else class="toggle-placeholder"></span>
    
    <span class="node-title">{{ node.title }}</span>
    
    <span class="node-meta">{{ node.child_count || 0 }} 子节点</span>
  </div>
  
  <div v-if="expanded && hasChildren" class="tree-children">
    <TreeNode
      v-for="child in node.children"
      :key="child.id"
      :node="child"
      :selected-id="selectedId"
      :level="level + 1"
      @select="$emit('select', $event)"
      @toggle="$emit('toggle', $event)"
    />
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'

const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  selectedId: {
    type: Number,
    default: null
  },
  level: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['select', 'toggle'])

const expanded = ref(false)

const hasChildren = computed(() => 
  props.node.children && props.node.children.length > 0
)

function handleClick() {
  emit('select', props.node)
}

function toggle() {
  expanded.value = !expanded.value
  emit('toggle', props.node)
}
</script>
```

---

## 4. 数据流设计

### 4.1 PDF 上传和解析流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PDF 上传和解析流程                               │
└─────────────────────────────────────────────────────────────────────────┘

1. 前端上传阶段
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  用户选择PDF │ ──▶ │ 前端验证     │ ──▶ │ FormData上传  │
│    文件      │     │ (大小/类型)   │     │  到后端      │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
2. 后端接收阶段
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  验证请求    │ ──▶ │ 保存文件到    │ ──▶ │ 更新Book记录  │
│  (50MB限制)  │     │ /data/uploads │     │  (pdf_path)  │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
3. 解析阶段（可异步）
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  获取PDF     │ ──▶ │ 逐页提取     │ ──▶ │ 章节识别     │
│  文件路径    │     │ 文本(内存优化)│     │ (auto策略)   │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
                         ┌──────────────┐     ┌──────────────┐
                         │ 生成知识节点  │ ──▶ │ 返回解析结果  │
                         │ (树状结构)    │     │  给前端      │
                         └──────────────┘     └──────────────┘
```

**关键代码 - PDF解析服务内存优化**

```python
# services/pdf_service.py
import fitz  # PyMuPDF
from typing import Generator, List, Dict

class PDFService:
    """PDF解析服务 - 内存优化版本"""
    
    def __init__(self, upload_folder: str, cache_size: int = 5):
        self.upload_folder = upload_folder
        self._page_cache = {}  # LRU cache for pages
        self.cache_size = cache_size  # 限制缓存页数
    
    def extract_page_text(self, pdf_path: str, page_num: int) -> str:
        """提取单页文本（内存优化）"""
        # 使用生成器及时释放内存
        with fitz.open(pdf_path) as doc:
            if page_num < len(doc):
                page = doc.load_page(page_num)
                return page.get_text()
        return ""
    
    def extract_text_pages(self, pdf_path: str, start: int = 0, count: int = 10) -> Generator[str, None, None]:
        """分批提取文本（生成器）"""
        with fitz.open(pdf_path) as doc:
            for page_num in range(start, min(start + count, len(doc))):
                page = doc.load_page(page_num)
                yield page.get_text()
                # 显式删除page对象释放内存
                del page
    
    def extract_chapters_auto(self, pdf_path: str) -> List[Dict]:
        """自动识别章节"""
        chapters = []
        current_chapter = None
        
        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # 章节识别策略
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    # 检测章节标题特征
                    if self._is_chapter_title(line):
                        if current_chapter:
                            current_chapter['page_end'] = page_num
                            chapters.append(current_chapter)
                        
                        current_chapter = {
                            'title': line,
                            'level': self._detect_level(line),
                            'page_start': page_num,
                            'content': ''
                        }
                
                if current_chapter:
                    current_chapter['content'] += text + '\n'
                
                del page  # 释放内存
        
        if current_chapter:
            current_chapter['page_end'] = len(doc) - 1
            chapters.append(current_chapter)
        
        return chapters
    
    def _is_chapter_title(self, line: str) -> bool:
        """检测是否为章节标题"""
        # 常见章节标题模式
        patterns = [
            r'^第[一二三四五六七八九十\d]+[章节篇部]',
            r'^\d+\.\d+',  # 1.2, 1.2.3
            r'^[A-Z][A-Z\s]+$',  # 全大写标题
        ]
        import re
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        return False
```

### 4.2 AI 问答流程（带缓存）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI 问答流程（带缓存）                            │
└─────────────────────────────────────────────────────────────────────────┘

1. 问题处理
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  用户提问    │ ──▶ │ 构建上下文   │ ──▶ │ 检查缓存     │
│              │     │ (知识点+内容) │     │ (问题Hash)   │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                              ┌───────────────────┴───────────────────┐
                              │                                       │
                              ▼ 缓存命中                              ▼ 缓存未命中
                    ┌──────────────┐                         ┌──────────────┐
                    │ 直接返回     │                         │ 调用DeepSeek │
                    │ 缓存结果     │                         │ API          │
                    └──────────────┘                         └──────┬───────┘
                                                                        │
2. 结果处理                                                      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 保存对话    │ ◀── │ 返回回答    │ ◀── │ 保存到缓存   │ ◀── │ 获取响应     │
│ 到数据库    │     │ 给前端      │     │ (24h TTL)    │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

**关键代码 - AI服务带缓存**

```python
# services/ai_service.py
import hashlib
import json
import time
from typing import Dict, List, Optional

class AIService:
    """AI服务 - 带缓存优化"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.client = DeepSeekClient(api_key, base_url)
        self.cache = {}  # 问题hash -> {answer, timestamp}
        self.cache_ttl = 86400  # 24小时
        self.conversation_history = {}  # conversation_id -> messages
    
    def _generate_cache_key(self, question: str, context: Dict = None) -> str:
        """生成缓存key"""
        data = {
            'question': question,
            'context': context
        }
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """检查缓存是否有效"""
        return time.time() - cache_entry['timestamp'] < self.cache_ttl
    
    def ask_question(self, question: str, context: Dict = None, node_id: int = None) -> Dict:
        """提问（带缓存）"""
        # 1. 检查缓存
        cache_key = self._generate_cache_key(question, context)
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if self._is_cache_valid(cached):
                # 缓存命中，记录对话但跳过API调用
                return self._create_response(cached['answer'], cached=True)
        
        # 2. 调用API
        prompt = self._build_prompt(question, context)
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个学习助手，擅长解答学术问题。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        # 3. 保存到缓存
        self.cache[cache_key] = {
            'answer': answer,
            'timestamp': time.time()
        }
        
        # 4. 保存对话记录
        conversation = self._save_conversation(node_id, question, answer)
        
        return self._create_response(answer, cached=False, conversation=conversation)
    
    def _build_prompt(self, question: str, context: Dict = None) -> str:
        """构建prompt"""
        prompt = question
        if context:
            if 'node_content' in context:
                prompt = f"相关知识点内容：\n{context['node_content']}\n\n问题：{question}"
            if 'book_info' in context:
                prompt = f"教材信息：{context['book_info']}\n\n{prompt}"
        return prompt
    
    def generate_answer(self, homework_content: str, context: str = None) -> Dict:
        """为作业生成答案"""
        prompt = f"请解答以下作业题，给出详细答案和解题思路：\n\n{homework_content}"
        if context:
            prompt = f"参考内容：\n{context}\n\n{prompt}"
        
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # 降低随机性，更精准
            max_tokens=2000
        )
        
        return {
            'answer': response.choices[0].message.content,
            'confidence': 0.85  # 估算置信度
        }
```

### 4.3 学习/复习流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           学习模式流程                                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              学习模式                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. 选择知识点                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │ 浏览知识树   │ ──▶ │ 点击知识点   │ ──▶ │ 获取节点内容 │            │
│  │              │     │              │     │ 和学习记录   │            │
│  └──────────────┘     └──────────────┘     └──────┬───────┘            │
│                                                    │                     │
│  2. 开始学习                                       ▼                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │ 阅读内容    │ ◀── │ 展示知识内容 │ ◀── │ 创建/更新    │            │
│  │ 标记已掌握  │     │              │     │ 学习记录     │            │
│  └──────┬──────┘     └──────────────┘     └──────────────┘            │
│         │                                                                 │
│         ▼                                                                │
│  3. 完成学习                                     ┌──────────────┐        │
│  ┌──────────────┐     ┌──────────────┐          │ AI答疑入口   │        │
│  │ 更新掌握程度 │ ──▶ │ 记录学习时间 │ ────────▶│              │        │
│  │ self_rating  │     │ review_count │          └──────────────┘        │
│  └──────────────┘     └──────────────┘                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              复习模式                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. 获取待复习列表                                                       │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │ 访问复习页   │ ──▶ │ 调用/due API │ ──▶ │ 获取到期节点 │            │
│  │              │     │              │     │ 按遗忘曲线排序│           │
│  └──────────────┘     └──────────────┘     └──────┬───────┘            │
│                                                    │                     │
│  2. 复习流程                                       ▼                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │ 展示知识点   │ ──▶ │ 回忆回答    │ ──▶ │ 提交复习结果 │            │
│  │ (隐藏答案)   │     │ 验证掌握    │     │ (correct/incorrect)│     │
│  └──────────────┘     └──────────────┘     └──────┬───────┘            │
│                                                    │                     │
│  3. 更新记录                                       ▼                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │ 计算下次     │ ◀── │ 更新记录    │ ◀── │ 计算Ebbinghaus│           │
│  │ 复习时间     │     │ (SM2算法)   │     │ 曲线时间      │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**关键代码 - 复习间隔算法(SM2变体)**

```python
# services/learning_service.py
from datetime import datetime, timedelta
from math import ceil

class LearningService:
    """学习服务 - 含复习间隔算法"""
    
    def __init__(self):
        # 基础间隔（天）
        self.base_intervals = {
            0: 1,   # 新学习
            1: 3,   # 简单
            2: 7,   # 一般
            3: 14,  # 困难
            4: 30   # 已掌握
        }
    
    def calculate_next_review(self, record: 'LearningRecord', result: str) -> datetime:
        """SM2变体算法计算下次复习时间
        
        result: 'correct' | 'incorrect' | 'easy' | 'hard'
        """
        if result == 'incorrect':
            # 答错，回到间隔1天
            next_interval = 1
            new_status = 'learning'
        else:
            # 根据当前状态和结果计算间隔
            current_status = record.status
            difficulty = self._get_difficulty(current_status, result)
            next_interval = self.base_intervals[difficulty]
            
            if record.review_count > 0:
                # 指数增长，最大30天
                next_interval = min(ceil(next_interval * (1.5 ** record.review_count)), 30)
            
            new_status = 'mastered' if next_interval >= 14 else 'learning'
        
        return datetime.utcnow() + timedelta(days=next_interval)
    
    def _get_difficulty(self, status: str, result: str) -> int:
        """判断难度等级"""
        if result == 'easy':
            return 4 if status == 'mastered' else 2
        elif result == 'hard':
            return 1
        elif result == 'correct':
            return 2 if status == 'learning' else 3
        return 0
```

### 4.4 同步流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            数据同步流程                                  │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              导出流程                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. 触发导出                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │ 用户点击     │ ──▶ │ 后端查询     │ ──▶ │ 组装JSON    │            │
│  │ 导出按钮     │     │ 全部数据     │     │ 结构         │            │
│  └──────────────┘     └──────────────┘     └──────┬───────┘            │
│                                                    │                     │
│  2. 数据处理                                       ▼                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │ 生成下载    │ ◀── │ JSON序列化   │ ◀── │ 添加元数据   │            │
│  │ 文件流       │     │              │     │ (版本/时间)  │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              导入流程                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. 触发导入                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │ 选择JSON    │ ──▶ │ 验证文件     │ ──▶ │ 解析JSON    │            │
│  │ 文件        │     │ 格式/版本    │     │ 结构         │            │
│  └──────────────┘     └──────────────┘     └──────┬───────┘            │
│                                                    │                     │
│  2. 数据处理                                       ▼                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │ 按依赖顺序   │ ──▶ │ 合并策略处理 │ ──▶ │ 数据验证    │            │
│  │ 插入数据    │     │ skip/overwrite│     │              │            │
│  └──────┬──────┘     │ /merge       │     └──────┬───────┘            │
│         │             └──────────────┘            │                     │
│         ▼                                        ▼                     │
│  ┌──────────────┐                         ┌──────────────┐            │
│  │ subjects →  │                         │ 返回导入结果 │            │
│  │ books →      │                         │ (成功/失败数)│            │
│  │ nodes → ...  │                         │              │            │
│  └──────────────┘                         └──────────────┘            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. 性能优化方案

### 5.1 PDF 解析内存优化

| 策略 | 实现方式 | 效果 |
|------|----------|------|
| 分页读取 | 使用生成器逐页提取 | 内存峰值 < 50MB |
| 缓存控制 | LRU缓存限制5页 | 避免无限增长 |
| 及时释放 | 显式del和上下文管理 | 减少内存泄漏 |
| 异步处理 | 后台任务队列 | 不阻塞API |
| 流式响应 | 分块返回大文本 | 支持大文件 |

```python
# 内存优化示例
class PDFService:
    def __init__(self):
        self._page_cache = LRUCache(max_size=5)  # 只缓存5页
    
    def extract_text_optimized(self, pdf_path: str, pages: range):
        """优化后的文本提取"""
        with fitz.open(pdf_path) as doc:
            total_pages = len(doc)
            for page_num in pages:
                if page_num >= total_pages:
                    break
                
                # 检查缓存
                cache_key = f"{pdf_path}:{page_num}"
                if cache_key in self._page_cache:
                    yield self._page_cache.get(cache_key)
                    continue
                
                # 加载页面
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # 更新缓存
                self._page_cache.set(cache_key, text)
                
                # 显式释放
                del page
                
                yield text
```

### 5.2 数据库查询优化

| 优化点 | 实现方式 | 预期效果 |
|--------|----------|----------|
| 索引 | 为外键和常用查询字段添加索引 | 查询提升 10x |
| 懒加载 | 根据需要加载关联数据 | 减少数据传输 |
| 分页 | 默认分页 + 游标分页 | 大数据集支持 |
| 预加载 | joinedload 预加载关联 | 避免 N+1 问题 |
| 投影 | 只查询需要的字段 | 减少内存占用 |

```python
# 数据库优化示例

# 1. 添加索引
class KnowledgeNode(db.Model):
    __tablename__ = 'knowledge_nodes'
    __table_args__ = (
        db.Index('idx_book_parent', 'book_id', 'parent_id'),
        db.Index('idx_node_book', 'book_id'),
    )
    
# 2. 预加载避免 N+1
@bp.route('/nodes/tree/<int:book_id>')
def get_node_tree(book_id):
    # 使用 joinedload 预加载子节点
    nodes = KnowledgeNode.query.options(
        joinedload(KnowledgeNode.children)
    ).filter_by(book_id=book_id, parent_id=None).all()
    
# 3. 分页查询
@bp.route('/homework')
def get_homework():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = Homework.query.paginate(
        page=page, 
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'items': [h.to_dict() for h in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })
```

### 5.3 前端加载优化

| 策略 | 实现方式 | 效果 |
|------|----------|------|
| 路由懒加载 | `() => import()` | 首屏加载 < 200KB |
| 组件懒加载 | v-if 条件加载 | 按需加载 |
| 图片懒加载 | IntersectionObserver | 减少初始请求 |
| 虚拟滚动 | vue-virtual-scroller | 长列表优化 |
| 防抖节流 | 搜索输入防抖 | 减少 API 调用 |

```javascript
// 路由懒加载配置
// vite.config.js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'vendor': ['vue', 'vue-router', 'pinia']
        }
      }
    },
    // 启用 gzip 压缩
    compressOptions: {
      gzip: true
    }
  }
})
```

### 5.4 缓存策略

| 层级 | 内容 | TTL | 实现 |
|------|------|-----|------|
| 浏览器 | 静态资源 | 1年 | vite build hash |
| 内存 | API响应、树结构 | 会话 | Pinia |
| 本地存储 | 用户偏好、草稿 | 永久 | localStorage |
| 后端内存 | AI响应、PDF文本 | 24h | LRU Cache |
| 数据库 | 统计聚合数据 | 1h | SQLite |

```python
# 缓存服务实现
class CacheService:
    """多级缓存服务"""
    
    def __init__(self):
        self.memory_cache = LRUCache(max_size=500)
        self.db_cache_ttl = 3600  # 1小时
    
    def get_or_set(self, key: str, factory: callable, ttl: int = None):
        """获取缓存，不存在则调用工厂函数"""
        # 1. 检查内存缓存
        value = self.memory_cache.get(key)
        if value is not None:
            return value
        
        # 2. 检查数据库缓存
        cached = self._get_db_cache(key)
        if cached:
            self.memory_cache.set(key, cached)
            return cached
        
        # 3. 调用工厂函数
        value = factory()
        
        # 4. 存入缓存
        self.memory_cache.set(key, value)
        if ttl:
            self._set_db_cache(key, value, ttl)
        
        return value
```

---

## 6. 部署架构

### 6.1 目录结构

```
/home/i/Hw2Ex/
├── backend/                     # Flask后端
│   ├── app.py                   # 应用入口
│   ├── extensions.py            # Flask扩展
│   ├── config.py                # 配置
│   ├── models.py                # 数据模型
│   ├── routes/                  # API路由
│   ├── services/                # 业务服务
│   ├── utils/                   # 工具函数
│   ├── middleware/              # 中间件
│   └── requirements.txt         # Python依赖
│
├── frontend/                    # Vue.js前端
│   ├── dist/                    # 构建输出
│   ├── src/                     # 源代码
│   ├── package.json
│   └── vite.config.js
│
├── data/                        # 数据目录
│   ├── database.db              # SQLite数据库
│   ├── database.db.bak          # 数据库备份
│   ├── uploads/                  # 上传文件
│   │   ├── books/               # PDF教材
│   │   └── exports/            # 导出文件
│   └── backups/                 # 备份文件
│
├── scripts/                     # 运维脚本
│   ├── start.sh                 # 启动脚本
│   ├── backup.sh                # 备份脚本
│   └── restore.sh               # 恢复脚本
│
├── logs/                        # 日志目录
│   ├── app.log                  # 应用日志
│   └── error.log                # 错误日志
│
├── .env                         # 环境变量
├── .env.example                 # 环境变量示例
├── docker-compose.yml           # Docker部署（可选）
└── README.md
```

### 6.2 环境配置

```bash
# .env 文件
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///../data/database.db
UPLOAD_FOLDER=../data/uploads
MAX_CONTENT_LENGTH=52428800

# DeepSeek API
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 日志
LOG_LEVEL=INFO
LOG_FILE=../logs/app.log

# 性能
ENABLE_CACHE=true
CACHE_TTL=86400
MAX_UPLOAD_SIZE=52428800
```

### 6.3 启动脚本

```bash
#!/bin/bash
# scripts/start.sh

set -e

# 配置路径
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

# 创建必要目录
mkdir -p data/uploads data/exports data/backups logs

# 设置环境变量
export FLASK_ENV=production
export FLASK_DEBUG=0

# 启动后端
echo "Starting Flask backend..."
cd backend
python3 -m venv venv || true
source venv/bin/activate
pip install -r requirements.txt -q
nohup python app.py > ../logs/app.log 2>&1 &

echo "Backend started on http://localhost:5000"

# 如果需要构建前端
# cd ../frontend
# npm install
# npm run build
# 静态文件由 Nginx 或后端静态文件服务

echo "Application started successfully"
```

### 6.4 备份策略

```bash
#!/bin/bash
# scripts/backup.sh

set -e

BACKUP_DIR="/home/i/Hw2Ex/data/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份数据库
echo "Backing up database..."
cp /home/i/Hw2Ex/data/database.db "$BACKUP_DIR/database_$DATE.db"

# 备份上传文件（可选，太大可以注释）
# echo "Backing up uploads..."
# tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" /home/i/Hw2Ex/data/uploads

# 只保留最近10个备份
cd "$BACKUP_DIR"
ls -t database_*.db | tail -n +11 | xargs -r rm

echo "Backup completed: database_$DATE.db"

# 自动清理超过7天的备份
find "$BACKUP_DIR" -name "*.db" -mtime +7 -delete
```

---

## 7. 关键实现代码框架

### 7.1 后端 - 蓝图模板

```python
# routes/homework.py
from flask import Blueprint, request, jsonify, current_app
from ..models import db, Homework, Book, KnowledgeNode
from ..services.ai_service import AIService
from ..services.cache_service import cached
from ..utils.decorators import rate_limit

bp = Blueprint('homework', __name__, url_prefix='/api/homework')

@bp.route('', methods=['GET'])
def get_homework_list():
    """获取作业列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    book_id = request.args.get('book_id', type=int)
    status = request.args.get('status')
    
    query = Homework.query
    
    if book_id:
        query = query.filter_by(book_id=book_id)
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [h.to_dict() for h in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@bp.route('', methods=['POST'])
def create_homework():
    """创建作业"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required = ['book_id', 'location', 'content']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    homework = Homework(
        book_id=data['book_id'],
        primary_node_id=data.get('primary_node_id'),
        location=data['location'],
        content=data['content'],
        secondary_nodes=data.get('secondary_nodes', []),
        status='new'
    )
    
    db.session.add(homework)
    db.session.commit()
    
    return jsonify(homework.to_dict()), 201

@bp.route('/<int:homework_id>', methods=['GET'])
def get_homework(homework_id):
    """获取作业详情"""
    homework = Homework.query.get_or_404(homework_id)
    return jsonify(homework.to_dict())

@bp.route('/<int:homework_id>', methods=['PUT'])
def update_homework(homework_id):
    """更新作业"""
    homework = Homework.query.get_or_404(homework_id)
    data = request.get_json()
    
    updatable_fields = ['content', 'answer', 'secondary_nodes', 'status']
    for field in updatable_fields:
        if field in data:
            setattr(homework, field, data[field])
    
    db.session.commit()
    return jsonify(homework.to_dict())

@bp.route('/<int:homework_id>', methods=['DELETE'])
def delete_homework(homework_id):
    """删除作业"""
    homework = Homework.query.get_or_404(homework_id)
    db.session.delete(homework)
    db.session.commit()
    return jsonify({'message': 'Homework deleted successfully'})

@bp.route('/<int:homework_id>/answer', methods=['POST'])
@rate_limit
def generate_answer(homework_id):
    """AI生成答案"""
    homework = Homework.query.get_or_404(homework_id)
    data = request.get_json() or {}
    
    # 获取上下文
    context = None
    if homework.primary_node_id:
        node = KnowledgeNode.query.get(homework.primary_node_id)
        if node and node.content:
            context = node.content
    
    # 调用AI服务生成答案
    ai_service = AIService(
        api_key=current_app.config.get('DEEPSEEK_API_KEY')
    )
    
    result = ai_service.generate_answer(homework.content, context)
    
    # 保存答案
    homework.answer = result['answer']
    homework.status = 'answered'
    db.session.commit()
    
    return jsonify({
        'answer': result['answer'],
        'confidence': result.get('confidence', 0.8)
    })

@bp.route('/generate', methods=['POST'])
@rate_limit
def batch_generate_answers():
    """批量生成答案"""
    data = request.get_json()
    homework_ids = data.get('homework_ids', [])
    
    if not homework_ids:
        return jsonify({'error': 'No homework_ids provided'}), 400
    
    results = []
    for hw_id in homework_ids:
        homework = Homework.query.get(hw_id)
        if homework and not homework.answer:
            try:
                ai_service = AIService()
                result = ai_service.generate_answer(homework.content)
                homework.answer = result['answer']
                homework.status = 'answered'
                results.append({'id': hw_id, 'success': True})
            except Exception as e:
                results.append({'id': hw_id, 'success': False, 'error': str(e)})
    
    db.session.commit()
    
    return jsonify({
        'results': results,
        'total': len(results),
        'success_count': sum(1 for r in results if r['success'])
    })
```

### 7.2 前端 - 视图模板

```vue
<!-- views/learning/LearningMode.vue -->
<template>
  <div class="learning-mode">
    <div class="learning-header">
      <h2>学习模式</h2>
      <el-radio-group v-model="currentMode" @change="handleModeChange">
        <el-radio-button value="learning">学习中</el-radio-button>
        <el-radio-button value="review">待复习</el-radio-button>
        <el-radio-button value="exam">考试准备</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 学习模式 -->
    <div v-if="currentMode === 'learning'" class="learning-content">
      <el-row :gutter="20">
        <el-col :span="8">
          <knowledge-tree
            :nodes="knowledgeTree"
            :selected-id="currentNodeId"
            @select="handleNodeSelect"
          />
        </el-col>
        <el-col :span="16">
          <div v-if="currentNode" class="node-content">
            <h3>{{ currentNode.title }}</h3>
            <div class="node-body" v-html="renderMarkdown(currentNode.content)"></div>
            
            <div class="learning-actions">
              <el-button @click="startStudy" type="primary">
                开始学习
              </el-button>
              <el-button @click="openChat">
                提问AI
              </el-button>
            </div>
          </div>
          
          <div v-else class="placeholder">
            <p>请从左侧选择一个知识点开始学习</p>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 复习模式 -->
    <div v-if="currentMode === 'review'" class="review-content">
      <el-alert
        v-if="dueReviews.length === 0"
        title="太棒了！"
        type="success"
        description="目前没有需要复习的内容"
        show-icon
      />
      
      <div v-else class="review-list">
        <review-card
          v-for="record in dueReviews"
          :key="record.id"
          :record="record"
          @review="handleReview"
        />
      </div>
    </div>

    <!-- 考试模式 -->
    <div v-if="currentMode === 'exam'" class="exam-content">
      <el-card>
        <template #header>
          <span>考试准备</span>
        </template>
        <el-form :model="examForm" label-width="120px">
          <el-form-item label="选择教材">
            <el-select v-model="examForm.bookId" placeholder="请选择">
              <el-option
                v-for="book in books"
                :key="book.id"
                :label="book.title"
                :value="book.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="考试日期">
            <el-date-picker
              v-model="examForm.examDate"
              type="date"
              placeholder="选择日期"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="prepareExam">
              分析考试范围
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useLearningStore, useNodeStore, useBookStore } from '@/stores'
import KnowledgeTree from '@/components/common/TreeList.vue'
import ReviewCard from '@/components/learning/ReviewCard.vue'

const learningStore = useLearningStore()
const nodeStore = useNodeStore()
const bookStore = useBookStore()

const currentMode = ref('learning')
const currentNodeId = ref(null)
const currentNode = computed(() => 
  currentNodeId.value ? nodeStore.getNodeById(currentNodeId.value) : null
)

const examForm = reactive({
  bookId: null,
  examDate: null
})

onMounted(async () => {
  await Promise.all([
    nodeStore.fetchNodes(),
    bookStore.fetchBooks(),
    learningStore.fetchDueReviews()
  ])
})

function handleNodeSelect(node) {
  currentNodeId.value = node.id
}

async function startStudy() {
  if (!currentNodeId.value) return
  await learningStore.startStudy(currentNodeId.value)
}

function openChat() {
  // 打开AI答疑
}

async function handleReview({ recordId, result }) {
  await learningStore.recordReview(recordId, result)
  await learningStore.fetchDueReviews()
}

async function prepareExam() {
  // 调用考试准备API
}
</script>

<style scoped>
.learning-mode {
  padding: 20px;
}

.learning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.node-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
}

.node-body {
  margin: 20px 0;
  line-height: 1.8;
}

.learning-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
</style>
```

---

## 8. 数据库 Schema 完整定义

```sql
-- 科目表
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 教材表
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(200),
    publisher VARCHAR(200),
    year INTEGER,
    total_pages INTEGER,
    pdf_path VARCHAR(500),
    extracted_text JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- 知识节点表（树状结构）
CREATE TABLE knowledge_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    parent_id INTEGER,
    title VARCHAR(200) NOT NULL,
    level INTEGER DEFAULT 0,
    page_start INTEGER,
    page_end INTEGER,
    content TEXT,
    tags JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES knowledge_nodes(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_nodes_book ON knowledge_nodes(book_id);
CREATE INDEX idx_nodes_parent ON knowledge_nodes(parent_id);
CREATE INDEX idx_nodes_book_parent ON knowledge_nodes(book_id, parent_id);

-- 作业表
CREATE TABLE homework (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    primary_node_id INTEGER,
    location VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    answer TEXT,
    secondary_nodes JSON,
    status VARCHAR(20) DEFAULT 'new',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (primary_node_id) REFERENCES knowledge_nodes(id) ON DELETE SET NULL
);

CREATE INDEX idx_homework_book ON homework(book_id);
CREATE INDEX idx_homework_status ON homework(status);

-- 学习记录表
CREATE TABLE learning_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'learning',
    last_reviewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    next_review TIMESTAMP,
    review_count INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    total_attempts INTEGER DEFAULT 0,
    self_rating INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES knowledge_nodes(id) ON DELETE CASCADE
);

CREATE INDEX idx_record_node ON learning_records(node_id);
CREATE INDEX idx_record_status ON learning_records(status);
CREATE INDEX idx_record_next_review ON learning_records(next_review);

-- AI对话表
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id INTEGER,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES knowledge_nodes(id) ON DELETE SET NULL
);

-- 对话消息表
CREATE TABLE conversation_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'user' | 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conversation ON conversation_messages(conversation_id);
```

---

## 9. 附录

### 9.1 环境变量说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| FLASK_ENV | 运行环境 | development / production |
| SECRET_KEY | 应用密钥 | 随机字符串 |
| DATABASE_URL | 数据库路径 | sqlite:///../data/database.db |
| DEEPSEEK_API_KEY | AI API密钥 | sk-xxx |
| DEEPSEEK_BASE_URL | API地址 | https://api.deepseek.com |
| LOG_LEVEL | 日志级别 | DEBUG / INFO / WARNING |
| ENABLE_CACHE | 启用缓存 | true / false |
| MAX_UPLOAD_SIZE | 最大上传 | 52428800 (50MB) |

### 9.2 API 响应格式

```javascript
// 成功响应
{
  "data": { /* 实际数据 */ },
  "message": "操作成功",
  "code": 200
}

// 错误响应
{
  "error": "错误类型",
  "message": "详细错误信息",
  "code": 400
}

// 分页响应
{
  "items": [ /* 数据数组 */ ],
  "total": 100,
  "pages": 10,
  "current_page": 1,
  "per_page": 20
}
```

### 9.3 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

---

*文档版本：1.0*
*最后更新：2026-04-09*
*架构设计：基于项目企划文档*

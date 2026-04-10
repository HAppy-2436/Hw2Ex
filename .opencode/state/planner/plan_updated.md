# 学习复习作业管理助手 - 完整项目企划文档 (v2.0)

## Chapter 1: 项目概述与核心价值主张

### 1.1 项目愿景
- 项目名称: StudyMate - 学习复习作业管理助手
- 面向大一软件工程学生设计的智能知识管理和复习工具
- 通过AI辅助帮助学生高效管理教材、整理知识结构、管理作业任务

### 1.2 核心价值主张 - "让作业成为学习的入口，而非学习的终点"

传统模式: Learning → Homework (作业作为学习的终点/考核)
新模式: Homework → Learning (作业驱动的学习)

| 痛点 | 传统解决方案 | 本项目解决方案 |
|------|-------------|---------------|
| 初次学习和作业糅合 | 按部就班上课听讲 | 作业驱动学习，降低启动门槛 |
| 盲目套用范式不理解内核 | 重复刷题死记硬背 | AI讲解促进理解，建立知识连接 |
| 学习资源不匹配 | 被动接受统一教材 | 基于作业重点的精准学习材料 |

### 1.3 目标用户画像
- 年级/专业: 大一软件工程学生
- 核心需求: 课程知识整理、作业管理、考试复习
- 技术能力: 具备基础编程能力，能使用命令行
- 使用场景: 晚间复习、周末整理、考试周冲刺
- 痛点: 知识碎片化、复习无重点、作业遗忘

### 1.4 当前开发进度

| 模块 | 完成度 | 状态 |
|------|--------|------|
| 后端架构 | 80% | Flask + SQLAlchemy + SQLite，路由蓝图完整 |
| 数据模型 | 75% | 6张核心表已定义，缺少扩展表 |
| AI服务 | 70% | DeepSeek API + 缓存，对话上下文缺失 |
| 前端 | 15% | 仅有基础HTML壳，Vue.js未实现 |
| 多端同步 | 0% | 仅设计JSON导出/导入 |

## Chapter 2: 功能规格

### 2.1 功能模块划分

```
StudyMate
├── 教材管理模块 (Book Management)
│   ├── PDF上传与存储
│   ├── PDF解析与章节提取
│   └── 教材信息管理
│
├── 知识结构管理模块 (Knowledge Management)
│   ├── 树状知识结构 (父子节点)
│   ├── 标签系统
│   └── 知识点内容编辑
│
├── 作业管理模块 (Homework Management)
│   ├── 题目录入 (手动/CSV导入)
│   ├── 题目与知识点关联
│   ├── AI答案生成
│   ├── 认知门控 (Cognitive Gate) - 必须先提交自己的思路才能看AI答案
│   └── 掌握程度追踪
│
├── 学习模式模块 (Study Mode)
│   ├── 知识点学习
│   ├── AI答疑助手
│   ├── 学习记录追踪
│   └── 学习效果评估
│
├── 复习模式模块 (Review Mode)
│   ├── 考试范围分析
│   ├── 复习计划管理
│   ├── 知识点清单生成
│   └── 复习进度追踪
│
└── 同步与导出模块 (Sync & Export)
    ├── JSON数据导出
    ├── JSON数据导入
    └── 数据备份
```

### 2.2 核心功能详细描述

#### 2.2.1 认知门控 (Cognitive Gate) - 最重要的功能创新

| 特性 | 描述 |
|------|------|
| 定义 | 用户必须提交自己对题目的思考/解答思路后，才能查看AI提供的答案 |
| 目的 | 防止AI依赖症，确保用户真正思考后再参考AI解答 |
| 实现 | 解答查看前增加"我的思路"文本框提交步骤 |

#### 2.2.2 教材管理

| 功能 | 描述 | 优先级 |
|------|------|--------|
| PDF上传 | 支持拖拽上传，单文件≤10MB (1核1G服务器限制) | P0 |
| PDF解析 | 使用PyMuPDF提取文本和章节结构 | P0 |
| 章节提取 | 自动识别目录结构，生成知识节点 | P1 |
| 教材信息管理 | 编辑书名、作者、出版社等信息 | P1 |

#### 2.2.3 知识结构管理

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 树状结构 | 无限层级父子节点 | P0 |
| 节点CRUD | 创建/读取/更新/删除知识点 | P0 |
| 标签管理 | 为节点添加多个标签 | P1 |
| 内容编辑 | Markdown内容支持 | P1 |

#### 2.2.4 作业管理

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 题目录入 | 手动输入题目内容 | P0 |
| CSV批量导入 | 导入格式：题目,答案,关联知识点 | P0 |
| AI答案生成 | 调用DeepSeek生成答案(需通过认知门控) | P1 |
| 掌握程度 | 5档评级：陌生→熟悉 | P0 |
| 作业状态 | new/learning/reviewed/mastered | P0 |

#### 2.2.5 学习模式

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 知识点学习 | 查看知识点内容 + 相关作业 | P0 |
| AI答疑 | 基于当前知识点问答 | P1 |
| 学习记录 | 记录学习时长、提问次数 | P1 |
| 效果自评 | 学习后自我评分(1-5星) | P1 |

#### 2.2.6 复习模式

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 复习计划创建 | 确定复习范围，设置考试信息 | P0 |
| 复习清单生成 | 基于遗忘曲线排序 | P1 |
| 复习效果追踪 | 记录复习时长、对比复习前后状态 | P1 |

#### 2.2.7 同步功能

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 全量导出 | 导出所有数据为JSON | P1 |
| 全量导入 | 从JSON恢复数据 | P1 |
| 自动备份 | 每次修改前自动备份 | P2 |

## Chapter 3: 技术架构

### 3.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        客户端 (Vue.js 3 SPA)                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │教材管理 │  │知识管理 │  │作业管理 │  │学习模式 │  │复习模式 │     │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTP REST API
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Flask 后端服务 (1核1G优化)                        │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    API Routes (蓝图模块化)                       │    │
│  │  /api/subjects  /api/books  /api/nodes  /api/homework           │    │
│  │  /api/learn  /api/review  /api/ai  /api/sync                     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │PDF解析器 │  │ AI服务   │  │ 同步服务 │  │ 缓存服务 │           │
│  │(PyMuPDF) │  │(DeepSeek)│  │ (JSON)   │  │(SQLite)  │           │
│  │流式处理  │  │重试+降级 │  │导出/导入 │  │TTL过期   │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
               ┌─────────────────┴─────────────────┐
               ▼                                   ▼
┌─────────────────────────┐         ┌─────────────────────────┐
│      SQLite 数据库       │         │    文件存储 (data/)     │
│  - subjects             │         │  - /uploads (PDF)       │
│  - books                │         │  - /backups (JSON)      │
│  - knowledge_nodes      │         │  - /cache (AI响应)      │
│  - homework             │         │                         │
│  - learning_records     │         │                         │
│  - conversations        │         │                         │
│  - user_profiles (新增) │         │                         │
│  - conversation_contexts │         │                         │
│  - review_plans (新增)   │         │                         │
│  - review_checkpoints   │         │                         │
│  - token_usage (新增)   │         │                         │
│  - sync_log (新增)      │         │                         │
└─────────────────────────┘         └─────────────────────────┘
```

### 3.2 技术栈总结

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 前端框架 | Vue 3 + Composition API | 渐进式JS框架 |
| 前端状态 | Pinia | Vue3官方推荐状态管理 |
| 前端路由 | Vue Router 4 | SPA路由管理 |
| UI框架 | Element Plus | Vue3组件库，支持中文 |
| HTTP客户端 | Axios | Promise-based HTTP client |
| 后端框架 | Flask 3.0 | 轻量级Python Web框架 |
| ORM | Flask-SQLAlchemy | 数据库ORM映射 |
| PDF解析 | PyMuPDF (fitz) | 高效PDF解析，内存优化 |
| AI集成 | DeepSeek API | 本地个人使用 |
| 数据库 | SQLite | 轻量级，适合1核1G服务器 |
| 缓存 | 内存缓存 + SQLite | LRU缓存热点数据 |
| 部署 | Docker | 容器化部署 |

### 3.3 1核1G服务器性能优化策略

| 优化项 | 具体措施 | 预期效果 |
|--------|----------|----------|
| 内存限制 | 单文件上传≤10MB | 防止OOM |
| PDF流式处理 | 逐页读取，100页/次提交 | 内存峰值<100MB |
| SQLite配置 | WAL模式+64MB缓存 | 提升并发 |
| AI请求限流 | 并发≤3请求 | 防止API滥用 |
| 缓存TTL | AI响应缓存7天 | 减少API调用 |
| 进程管理 | Gunicorn 2 workers | 避免内存泄漏 |

## Chapter 4: 数据模型

### 4.1 扩展数据模型 (新增表)

#### 4.1.1 用户画像表 (user_profiles)
解决上下文反复交代问题

```sql
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50),
    grade VARCHAR(20),                    -- "大一"
    major VARCHAR(100),                   -- "软件工程"
    enrollment_year INTEGER,              -- 2024
    learning_background JSON,             -- 先验知识描述
    subject_preferences JSON,            -- 学科偏好
    learning_habits JSON,                 -- 学习习惯
    persistent_weak_points JSON,          -- 持续跟踪的薄弱点
    current_learning_session JSON,       -- 当前学习上下文
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.1.2 对话上下文表 (conversation_contexts)
多轮对话记忆

```sql
CREATE TABLE conversation_contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    session_id VARCHAR(100),              -- 对话会话ID
    conversation_type VARCHAR(20),       -- learning/homework/review
    scope_type VARCHAR(20),               -- node/chapter/subject
    scope_id INTEGER,
    context_summary JSON,                 -- 上下文摘要
    understanding_check_passed BOOLEAN,   -- AI是否验证了用户理解
    explanation_depth_level INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME                   -- 上下文过期时间
);
```

#### 4.1.3 复习计划表 (review_plans)

```sql
CREATE TABLE review_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    exam_date DATE,
    scope TEXT,                           -- 考试范围描述
    status VARCHAR(20) DEFAULT 'planning', -- planning/in_progress/completed
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);
```

#### 4.1.4 复习知识点勾选表 (review_checkpoints)

```sql
CREATE TABLE review_checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    knowledge_point_id INTEGER NOT NULL,
    learning_status VARCHAR(20) DEFAULT 'not_started', -- not_started/learning/mastered
    mastery_level INTEGER DEFAULT 0,      -- 0-5
    notes TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES review_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_nodes(id) ON DELETE CASCADE
);
```

#### 4.1.5 Token使用记录表 (token_usage)
API成本控制

```sql
CREATE TABLE token_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    hour INTEGER NOT NULL,
    model VARCHAR(50) NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0,
    request_count INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.1.6 操作日志表 (sync_log)
冲突检测和审计

```sql
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type VARCHAR(20) NOT NULL,
    entity_id INTEGER NOT NULL,
    operation VARCHAR(10) NOT NULL,       -- CREATE/UPDATE/DELETE
    old_value TEXT,
    new_value TEXT,
    device_id VARCHAR(100),
    synced BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 数据库索引优化

```sql
-- 为频繁查询字段添加索引
CREATE INDEX idx_knowledge_node_book ON knowledge_nodes(book_id);
CREATE INDEX idx_knowledge_node_parent ON knowledge_nodes(parent_id);
CREATE INDEX idx_homework_book ON homework(book_id);
CREATE INDEX idx_homework_status ON homework(status);
CREATE INDEX idx_learning_record_node ON learning_records(node_id);
CREATE INDEX idx_conversation_node ON conversations(node_id);
CREATE INDEX idx_ai_cache_hash ON ai_cache(query_hash);
CREATE INDEX idx_ai_cache_expires ON ai_cache(expires_at);
```

## Chapter 5: 开发计划 (四阶段)

### 5.1 阶段总览

```
┌──────────────────────────────────────────────────────────────────┐
│                     MVP阶段 (Week 1-2)                            │
│   学科管理 + 作业记录 + AI分析 (验证核心假设)                        │
├──────────────────────────────────────────────────────────────────┤
│  Week 1:                                                           │
│    - 完善Subjects/Books CRUD                        [backend]    │
│    - 完善KnowledgeNodes CRUD + 树状查询             [backend]    │
│    - 完善Homework CRUD                               [backend]    │
│    - 前端Vue.js项目初始化                            [frontend]   │
│                                                                   │
│  Week 2:                                                           │
│    - 核心页面开发(学科列表/知识树)                   [frontend]   │
│    - AI题目分析API                                     [backend]   │
│    - 认知门控功能实现                                 [frontend]   │
│    - 人工替代实验验证                                 [验证]       │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                     V1.0阶段 (Week 3-4)                           │
│   DeepSeek集成 + 知识点关联 + 复习模式                             │
├──────────────────────────────────────────────────────────────────┤
│  Week 3:                                                           │
│    - DeepSeek API完整集成                             [backend]   │
│    - 对话上下文管理                                   [backend]   │
│    - 用户画像表实现                                   [backend]   │
│    - AI多轮对话界面                                   [frontend]   │
│                                                                   │
│  Week 4:                                                           │
│    - 复习计划CRUD                                      [backend]   │
│    - 复习知识点勾选                                    [backend]   │
│    - 复习模式界面                                      [frontend]   │
│    - 遗忘曲线算法实现                                  [backend]   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                     V1.5阶段 (Week 5-6)                            │
│   Vue.js前端 + 多端适配 + JSON同步                                 │
├──────────────────────────────────────────────────────────────────┤
│  Week 5:                                                           │
│    - 完整Vue.js前端界面                             [frontend]   │
│    - 学习模式完整功能                                [frontend]   │
│    - 响应式布局适配                                  [frontend]   │
│                                                                   │
│  Week 6:                                                           │
│    - JSON导出/导入完整实现                           [backend]   │
│    - 数据备份功能                                    [backend]   │
│    - Token使用统计                                   [backend]   │
│    - 端到端测试                                      [testing]   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                     V2.0阶段 (Week 7-8)                            │
│   学习历史分析 + 进度可视化                                          │
├──────────────────────────────────────────────────────────────────┤
│  Week 7:                                                           │
│    - 学习历史记录分析                               [backend]   │
│    - 知识掌握度统计                                [backend]   │
│    - 学习仪表盘                                    [frontend]   │
│                                                                   │
│  Week 8:                                                           │
│    - 复习报告生成                                   [backend]   │
│    - 进度可视化图表                                [frontend]   │
│    - Docker部署配置                                 [devops]    │
│    - 性能优化与测试                                  [optimize]  │
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 MVP详细任务 (Week 1-2)

| 任务 | 描述 | 工时 | 依赖 | 负责 |
|------|------|------|------|------|
| T1.1 | 完善Subjects/Books CRUD | 4h | 无 | backend |
| T1.2 | 完善KnowledgeNodes CRUD + 树状查询 | 6h | T1.1 | backend |
| T1.3 | 完善Homework CRUD | 4h | 无 | backend |
| T1.4 | LearningRecords路由 | 4h | 无 | backend |
| T1.5 | Conversations路由 | 3h | 无 | backend |
| T1.6 | 前端Vue.js项目初始化 | 4h | 无 | frontend |
| T1.7 | 核心页面开发(学科列表/知识树) | 10h | T1.6 | frontend |
| T1.8 | AI题目分析API | 6h | T1.3 | backend |
| T1.9 | 认知门控功能 | 8h | T1.8 | frontend |
| T1.10 | 人工替代实验验证 | - | T1.8 | 验证 |

### 5.3 V1.0详细任务 (Week 3-4)

| 任务 | 描述 | 工时 | 依赖 |
|------|------|------|------|
| T2.1 | DeepSeek API完整集成 | 8h | T1.8 |
| T2.2 | 对话上下文管理 | 6h | T2.1 |
| T2.3 | 用户画像表实现 | 4h | T2.2 |
| T2.4 | AI多轮对话界面 | 10h | T2.2 |
| T2.5 | 复习计划CRUD | 6h | T1.2 |
| T2.6 | 复习知识点勾选 | 6h | T2.5 |
| T2.7 | 复习模式界面 | 10h | T2.6 |
| T2.8 | 遗忘曲线算法 | 8h | T2.5 |

### 5.4 V1.5详细任务 (Week 5-6)

| 任务 | 描述 | 工时 | 依赖 |
|------|------|------|------|
| T3.1 | 完整Vue.js前端界面 | 16h | T2.4 |
| T3.2 | 学习模式完整功能 | 12h | T3.1 |
| T3.3 | 响应式布局适配 | 8h | T3.1 |
| T3.4 | JSON导出/导入 | 8h | T3.1 |
| T3.5 | 数据备份功能 | 4h | T3.4 |
| T3.6 | Token使用统计 | 4h | T2.1 |
| T3.7 | 端到端测试 | 8h | T3.5 |

### 5.5 V2.0详细任务 (Week 7-8)

| 任务 | 描述 | 工时 | 依赖 |
|------|------|------|------|
| T4.1 | 学习历史记录分析 | 8h | T3.2 |
| T4.2 | 知识掌握度统计 | 6h | T4.1 |
| T4.3 | 学习仪表盘 | 10h | T4.2 |
| T4.4 | 复习报告生成 | 8h | T4.1 |
| T4.5 | 进度可视化图表 | 8h | T4.3 |
| T4.6 | Docker部署配置 | 6h | T4.5 |
| T4.7 | 性能优化与测试 | 8h | T4.6 |

## Chapter 6: 风险管理与AI依赖陷阱

### 6.1 高风险（必须应对）

| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|----------|
| **AI依赖陷阱** | 高 | 高 | 认知门控：先提交自己思路才能看AI解答 |
| **服务器容量不足** | 中 | 高 | 限流+内存监控+自动重启 |
| **DeepSeek API单点故障** | 中 | 高 | 三级降级：正常→缓存→提示 |
| **项目半途而废** | 高 | 中 | MVP验证，设定退出条件 |

### 6.2 AI依赖陷阱详解

#### 什么是AI依赖陷阱？
用户过度依赖AI解答，不愿意自己思考，长期导致独立解决问题能力下降。

#### 认知门控(Cognitive Gate)机制

```
┌─────────────────────────────────────────────────────────────────┐
│                     认知门控流程                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  用户请求查看AI答案                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────┐                                             │
│  │ 展示题目要求    │                                             │
│  │ 强制要求先思考  │                                             │
│  └────────┬────────┘                                             │
│           │                                                      │
│           ▼                                                        │
│  ┌─────────────────┐                                             │
│  │"我的解题思路"   │  ← 必填文本框                               │
│  │ 文本框 (≥20字) │                                             │
│  └────────┬────────┘                                             │
│           │                                                      │
│           ▼                                                        │
│     ┌─────┴─────┐                                                │
│     │  验证通过 │                                                │
│     │  (≥20字)  │                                                │
│     └─────┬─────┘                                                │
│           │                                                      │
│     ┌─────┴─────┐                                                │
│     │     是    │                                                │
│     └─────┬─────┘                                                │
│           │                                                      │
│           ▼                                                        │
│  ┌─────────────────┐                                             │
│  │ 展示AI答案     │ ← 用户必须先提交自己的思路                   │
│  │ + 对比提示    │   才能解锁AI提供的解答                        │
│  └─────────────────┘                                             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 核心假设验证方法

> **在写代码之前，先做2周人工替代实验**

```
目的：验证"AI答疑"是否真的比"自己查资料"更有效

方法：
1. 选取10道典型作业题
2. 前5道：自己查资料/问同学，不准用AI
3. 后5道：用DeepSeek API直接获取解答
4. 3天后闭卷做类似题目，测试两组正确率

判断标准：
- AI组正确率 > 自己查资料组 → AI答疑有价值
- 两组差不多 → AI只是节省时间
- AI组正确率更低 → AI答疑有害
```

### 6.4 中风险（建议应对）

| 风险 | 应对策略 |
|------|----------|
| JSON同步冲突复杂 | 先做JSON导出/导入，简化同步 |
| 数据丢失 | 每日自动备份到GitHub |
| Copilot技术债务 | 核心模块手写单元测试 |

### 6.5 应急响应

| 场景 | 响应措施 |
|------|----------|
| 服务宕机 | 自动重启脚本 + 监控告警 |
| 内存不足 | OOM自动重启 + 日志分析 |
| 数据库损坏 | JSON备份恢复 |
| API超时 | 重试机制 + 降级提示 |

## Chapter 7: 成功指标

### 7.1 核心指标

| 指标 | 测量方法 | 目标值 | 验收时间 |
|------|----------|--------|----------|
| **学习效率提升30%** | 记录首次vs再次学习同一知识点的时间 | -30% | 学期末 |
| **知识留存率>70%** | 7天后知识点仍保持mastered状态的比例 | >70% | 学期末 |
| **作业完成时间减少50%** | 使用AI辅助前后的完成时间对比 | -50% | 学期末 |

### 7.2 辅助指标（可量化）

| 指标 | 测量方法 | 目标 |
|------|----------|------|
| 周活跃天数 | 系统日志统计 | ≥4天/周 |
| 功能使用率 | 功能埋点 | >60% |
| API调用效率 | 每次作业分析的平均token | 优化20% |
| 认知门控通过率 | 提交思路长度≥20字的比例 | >80% |

### 7.3 质性指标

- **学习动力**：是否感觉学习更有条理？
- **焦虑缓解**：考试前是否更从容？
- **知识自信**：是否能清晰感知自己的知识边界？

### 7.4 阶段验收标准

| 阶段 | 标准 |
|------|------|
| MVP完成 | 能记录1门课的作业并获得AI分析，认知门控生效 |
| V1.0完成 | AI多轮对话可用，复习模式完整 |
| V1.5完成 | Vue.js界面完整，JSON同步可用 |
| V2.0完成 | 学习仪表盘可用，Docker部署完成 |

## Chapter 8: 测试策略

### 8.1 测试分层

```
┌─────────────────────────────────────┐
│         E2E 测试 (Playwright)        │  ← 用户行为验证
│   - 完整学习流程                     │
│   - 复习模式完整流程                 │
└─────────────────────────────────────┘
              ↑
┌─────────────────────────────────────┐
│       集成测试 (pytest)              │  ← API交互验证
│   - API端到端测试                    │
│   - 数据库操作测试                   │
└─────────────────────────────────────┘
              ↑
┌─────────────────────────────────────┐
│        单元测试 (pytest)             │  ← 核心逻辑验证
│   - 服务层测试                       │
│   - 工具函数测试                     │
│   - 模型序列化测试                   │
└─────────────────────────────────────┘
```

### 8.2 测试用例优先级

| 优先级 | 覆盖范围 | 目标 |
|--------|----------|------|
| P0 | 核心CRUD + 认知门控 + 复习算法 | 必须通过 |
| P1 | AI功能 + 同步功能 | 必须通过 |
| P2 | 边界情况 + 性能测试 | 应该通过 |

## Chapter 9: 砍掉的功能

| 功能 | 理由 | 后期可加 |
|------|------|----------|
| ~~多设备WebDAV实时同步~~ | 复杂度高，1核1G难以支撑 | V2考虑 |
| ~~PDF全文检索~~ | 大文件处理是性能噩梦 | 按需简化 |
| ~~智能学习路径规划~~ | AI依赖太重，效果难验证 | V2考虑 |
| ~~社交功能（论坛/讨论区）~~ | 维护成本高 | 永不加 |
| ~~成绩分析和可视化看板~~ | 数据量不够时无意义 | V2考虑 |
| ~~离线客户端App~~ | Web已覆盖所有设备 | 永不加 |

## Chapter 10: 部署架构

### 10.1 Docker配置

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - FLASK_ENV=production
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    restart: unless-stopped
    
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

### 10.2 目录结构

```
/home/i/Hw2Ex/
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── config.py
│   ├── requirements.txt
│   ├── routes/
│   ├── services/
│   └── utils/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── data/
│   ├── database.db
│   ├── uploads/
│   ├── backups/
│   └── cache/
├── scripts/
│   ├── start.sh
│   ├── backup.sh
│   └── restore.sh
├── docker-compose.yml
└── README.md
```

---

**文档版本**: 2.0
**创建日期**: 2026-04-09
**最后更新**: 2026-04-09
**基于**: 项目共识文档 v1.0 + 企划文档 v1.0 + 架构设计文档 v1.0
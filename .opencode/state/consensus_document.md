# 📄 项目共识文档

## 学习复习作业管理助手 - 项目共识文档

**项目名称**: StudyMate - 学习复习作业管理助手  
**版本**: 1.0.0  
**日期**: 2026-04-09  
**状态**: 讨论完成，待审核  
**文档类型**: 共识文档（核心输出）

---

## 一、项目现状评估

### 1.1 已有基础

| 组件 | 完成度 | 说明 |
|------|--------|------|
| 后端架构 | 80% | Flask + SQLAlchemy + SQLite，路由蓝图完整 |
| 数据模型 | 75% | 6张核心表已定义，缺少User Profile和Review Plan扩展 |
| AI服务 | 70% | DeepSeek API集成 + 缓存，但对话上下文管理缺失 |
| 前端 | 15% | 仅有基础HTML壳，Vue.js项目结构未实现 |
| 多端同步 | 0% | 仅设计JSON导出/导入，实时同步未规划 |

### 1.2 核心差距分析

**三位专家的共识判断：**

| 差距 | 优先级 | 建议 |
|------|--------|------|
| 前端Vue.js未集成 | P0 | 立即开始前端开发 |
| 对话上下文管理缺失 | P1 | 实现UserProfile和ConversationContext |
| 多端同步未实现 | P2 | 先做JSON导出/导入，WebDAV后期考虑 |
| 复习模式功能不完整 | P1 | 需要增加ReviewPlan和ReviewCheckpoint |

---

## 二、核心价值主张共识

### 2.1 项目的核心价值

> **"让作业成为学习的入口，而非学习的终点"**

| 痛点 | 传统解决方案 | 本项目解决方案 |
|------|-------------|---------------|
| 初次学习和作业糅合 | 按部就班上课听讲 | 作业驱动学习，降低启动门槛 |
| 盲目套用范式不理解内核 | 重复刷题死记硬背 | AI讲解促进理解，建立知识连接 |
| 学习资源不匹配 | 被动接受统一教材 | 基于作业重点的精准学习材料 |

### 2.2 三种模式的定位

```
┌─────────────────────────────────────────────────────────────────────┐
│                         学习复习作业管理助手                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│  │  学习模式   │    │  作业模式   │    │  复习模式   │            │
│  │             │    │             │    │             │            │
│  │ 知识点讲解  │    │ 作业记录    │    │ 复习计划    │            │
│  │ AI答疑     │    │ AI分析     │    │ 知识清单    │            │
│  │ 学习追踪   │    │ AI解答     │    │ 复习效果    │            │
│  │             │    │             │    │             │            │
│  │ [深度的    │    │ [效率的    │    │ [冲刺的    │            │
│  │  知识理解]  │    │  作业完成]  │    │  考试准备]  │            │
│  └─────────────┘    └─────────────┘    └─────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 三、用户工作流共识

### 3.1 学习模式工作流

```
用户操作                    系统响应                      AI交互
─────────                  ─────────                    ────────

[入口]
  │                            │                            │
  ▼                            │                            │
点击「学习模式」──────────────▶ 加载学习仪表盘 ◀─────────────┐│
  │                      (显示：待学知识点/进行中/已完成)     │
  │                            │                            │
  ▼                            │                            │
选择教材/学科 ───────────────▶ 展示知识树 ◀────────────────┤
  │                      (高亮：未学习/学习中/已掌握)          │
  │                            │                            │
  ▼                            │                            │
选择知识点 ─────────────────▶ 加载知识点内容                │
  │                      + 创建/更新LearningRecord          │
  │                            │                            │
  ▼                            │                            │
「开始学习」按钮 ────────────▶ 进入学习会话 ──────────────▶ 欢迎语+学习目标
  │                            │                      (如："我们来学习"
  │                            │                       "【循环链表】，学完后
  │                            │                       你将能够：...")
  ▼                            │                            │
用户提问/请求讲解 ──────────────────────────────────────▶ AI讲解
  │                            │                      (多轮对话，支持追问)
  │                            │                            │
  ▼                            │                            │
「标记已学完」───────────────▶ 记录学习完成 ◀──────────────┘
  │                      + 弹出自评对话框                    │
  ▼                            │                            │
自评(1-5星) ─────────────────▶ 更新LearningRecord          │
  │                      (status, self_rating)             │
  ▼                            ▼                            ▼
返回知识树              学习进度更新              推荐下一个知识点
```

### 3.2 作业模式工作流

```
题目导入 ─────────────────────────────────────────────────────────────────┐
    │                                                                      │
    ├── [方式1] 题号录入 ──────▶ 手动输入题号 ────▶ 系统展示题目位置提示    │
    │                              (例：第3章习题3.2)                         │
    │                                                                      │
    ├── [方式2] 拍照上传 ──────▶ OCR识别 ────────▶ 自动提取题目文本         │
    │                              (需对接OCR API或利用AI进行文字提取)       │
    │                                                                      │
    ├── [方式3] 手动录入 ──────▶ 粘贴/输入题目 ──▶ 直接进入分析             │
    │                                                                      │
    └── [方式4] CSV批量导入 ──▶ 解析CSV ─────────▶ 批量创建作业记录         │
                                                                            │
                              ▼                                            │
                    ┌─────────────────┐                                    │
                    │  AI分析题目     │                                    │
                    │  关联知识点     │ ◀─────────────────────────────────┘
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        [情况1]          [情况2]         [情况3]
      关联成功        需确认           无法关联
         │               │                │
         ▼               ▼                ▼
    显示关联的       展示候选       提示手动选择
    知识点列表       知识点列表       关联知识点
         │               │                │
         ▼               ▼                ▼
    ┌─────────────────────────────────────────┐
    │           查看答案和讲解                   │
    │  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
    │  │AI生成答案│  │关联知识 │  │解题思路 │   │
    │  │(可缓存) │  │点讲解   │  │步骤拆解 │   │
    │  └─────────┘  └─────────┘  └─────────┘   │
    └─────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ 作业状态更新    │
                    │ new→solved     │
                    │ →reviewing     │
                    │ →mastered     │
                    └─────────────────┘
```

### 3.3 复习模式工作流

```
[阶段1：复习计划创建]
         │
         ▼
┌─────────────────────┐
│ 确定复习范围        │
│ (按教材/按学科/自定义)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 设置考试信息(可选)   │
│ (考试日期/重点章节)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 生成知识清单        │ ◀── AI分析薄弱点+考试范围
│ (带学习状态标记)    │     生成优先级排序
└──────────┬──────────┘
           │
           ▼
    ┌──────┴──────┐
    │             │
    ▼             ▼
[开始复习]   [调整范围]
    │             │
    ▼             │
[阶段2：复习执行]    │
    │             │
    ├─▶ 勾选学习状态 ──▶ 未掌握/掌握/熟练
    │             │
    ├─▶ 查看讲解 ────▶ AI针对性讲解
    │             │
    ├─▶ 练习题目 ────▶ AI生成练习题
    │             │
    └─▶ 标记完成 ────▶ 更新状态
           │
           ▼
[阶段3：复习资料生成]
    │
    └─▶ 勾选完成后 ──▶ 一键生成复习资料
           │
           ▼
    ┌─────────────────┐
    │ 复习资料包含：   │
    │ - 知识网络图    │
    │ - 高频考点清单  │
    │ - 易错点整理    │
    │ - 典型例题      │
    └─────────────────┘
           │
           ▼
[阶段4：效果追踪]
    │
    ├─▶ 记录复习时长
    ├─▶ 对比复习前后状态
    └─▶ 生成复习报告
```

---

## 四、技术架构共识

### 4.1 技术栈确认

| 层级 | 当前 | 共识决策 | 理由 |
|------|------|----------|------|
| 后端 | Flask | **保持Flask** | 轻量、适合1核1G服务器，已有基础 |
| 数据库 | SQLite | **保持SQLite** | 无服务器运维成本 |
| 前端 | 静态HTML | **Vue.js 3 + Vite** | Copilot辅助开发效率高 |
| 缓存 | 内存/文件 | **保持文件缓存** | 1G服务器不推荐Redis |
| 同步 | JSON手动 | **保持JSON导出/导入** | 简化复杂度，后期考虑WebDAV |
| 部署 | 手动 | **Docker** | 简化部署 |

### 4.2 系统架构

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
│  - review_plans (新增)   │         │                         │
│  - token_usage (新增)   │         │                         │
└─────────────────────────┘         └─────────────────────────┘
```

### 4.3 1核1G服务器性能优化策略

| 优化项 | 具体措施 | 预期效果 |
|--------|----------|----------|
| **内存限制** | 单文件上传≤10MB | 防止OOM |
| **PDF流式处理** | 逐页读取，100页/次提交 | 内存峰值<100MB |
| **SQLite配置** | WAL模式+64MB缓存 | 提升并发 |
| **AI请求限流** | 并发≤3请求 | 防止API滥用 |
| **缓存TTL** | AI响应缓存7天 | 减少API调用 |
| **进程管理** | Gunicorn 2 workers | 避免内存泄漏 |

**预期承载能力：**

| 场景 | 预期并发 | 备注 |
|------|----------|------|
| 纯浏览/学习 | 50-100 | 受限于1核CPU |
| AI问答（带缓存命中） | 20-30 | 缓存命中时响应快 |
| AI问答（需调用API） | 5-10 | DeepSeek API延迟主导 |
| 文件上传 | 2-3 | 大文件处理慢 |

---

## 五、数据模型共识

### 5.1 扩展数据模型

在现有6张表基础上，增加以下表：

```sql
-- 用户画像表（解决上下文反复交代问题）
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50),
    grade VARCHAR(20),                    -- "大一"
    major VARCHAR(100),                  -- "软件工程"
    enrollment_year INTEGER,              -- 2024
    learning_background JSON,             -- 先验知识描述
    subject_preferences JSON,            -- 学科偏好
    learning_habits JSON,                 -- 学习习惯
    persistent_weak_points JSON,          -- 持续跟踪的薄弱点
    current_learning_session JSON,       -- 当前学习上下文
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 对话上下文表（多轮对话记忆）
CREATE TABLE conversation_contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    session_id VARCHAR(100),             -- 对话会话ID
    conversation_type VARCHAR(20),        -- learning/homework/review
    scope_type VARCHAR(20),             -- node/chapter/subject
    scope_id INTEGER,
    context_summary JSON,               -- 上下文摘要
    understanding_check_passed BOOLEAN,  -- AI是否验证了用户理解
    explanation_depth_level INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME                  -- 上下文过期时间
);

-- 复习计划表
CREATE TABLE review_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    exam_date DATE,
    scope TEXT,                          -- 考试范围描述
    status VARCHAR(20) DEFAULT 'planning', -- planning/in_progress/completed
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- 复习知识点勾选表
CREATE TABLE review_checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    knowledge_point_id INTEGER NOT NULL,
    learning_status VARCHAR(20) DEFAULT 'not_started', -- not_started/learning/mastered
    mastery_level INTEGER DEFAULT 0,     -- 0-5
    notes TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES review_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_nodes(id) ON DELETE CASCADE
);

-- Token使用记录表（API成本控制）
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

-- 操作日志表（冲突检测和审计）
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

### 5.2 现有表优化建议

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

---

## 六、DeepSeek API集成共识

### 6.1 API应用场景与提示词模板

| 场景 | 提示词类型 | 缓存TTL | 说明 |
|------|-----------|---------|------|
| 作业题目分析 | 知识点推测 | 72小时 | 作业题→知识点关联 |
| 知识点讲解 | 知识总结 | 168小时(7天) | 知识点内容解释 |
| 作业答案生成 | 详细解答 | 72小时 | 题目→答案 |
| 复习资料生成 | 复习清单 | 24小时 | 基于范围的复习计划 |
| 实时问答 | 一般QA | 48小时 | 用户追问 |

### 6.2 提示词模板

```python
# 作业题目分析
HOMEWORK_ANALYSIS_PROMPT = """
分析这道作业题，完成以下任务：
1. 【知识点识别】识别题目涉及的核心知识点
2. 【难度评估】评估题目难度（基础/中等/困难）
3. 【关联建议】从知识树中找到最相关的节点
4. 【解题思路】给出简要的解题方向

题目内容：{question}
知识树结构：{knowledge_tree_summary}

请以JSON格式返回分析结果"""

# 复习资料生成
REVIEW_MATERIALS_PROMPT = """
你是一位大学课程助教。用户是一名{grade}{major}学生，正在备考。

请根据以下信息生成复习知识清单：
考试范围：{exam_scope}
用户当前掌握情况：{user_mastery}
目标：{target_level}

请输出JSON格式：
{
  "knowledge_list": [...],
  "study_sequence": [...],
  "time_estimate": "..."
}"""
```

### 6.3 API调用策略

| 策略 | 实现 | 重要性 |
|------|------|--------|
| 请求缓存 | 基于query_hash，分类设置TTL | P0 |
| 超时重试 | 指数退避，最多3次 | P0 |
| 降级方案 | 超时→缓存答案，API失败→提示稍后重试 | P1 |
| 流式响应 | 提升用户体验 | P2 |
| Token监控 | 每日统计，月度预警 | P1 |

---

## 七、开发优先级共识

### 7.1 四阶段开发计划

| 阶段 | 周期 | 核心交付 | 价值产出 |
|------|------|----------|----------|
| **MVP** | Week 1-2 | 学科管理+作业记录+AI分析 | 验证核心假设 |
| **V1.0** | Week 3-4 | DeepSeek集成+知识点关联+复习模式 | 实现核心价值 |
| **V1.5** | Week 5-6 | Vue.js前端+多端适配+JSON同步 | 完整用户体验 |
| **V2.0** | Week 7-8 | 学习历史分析+进度可视化 | 长期价值追踪 |

### 7.2 MVP详细任务

| 任务 | 描述 | 工时 | 依赖 |
|------|------|------|------|
| T1 | 完善Subjects/Books CRUD | 4h | 无 |
| T2 | 完善KnowledgeNodes CRUD + 树状查询 | 6h | T1 |
| T3 | 完善Homework CRUD | 4h | 无 |
| T4 | LearningRecords路由 | 4h | 无 |
| T5 | Conversations路由 | 3h | 无 |
| T6 | 前端Vue.js项目初始化 | 4h | 无 |
| T7 | 核心页面开发(学科列表/知识树) | 10h | T6 |
| T8 | AI题目分析API | 6h | T3 |

### 7.3 砍掉的功能（共识决策）

| 功能 | 理由 | 后期可加 |
|------|------|----------|
| ~~多设备WebDAV实时同步~~ | 复杂度高，1核1G难以支撑 | V2考虑 |
| ~~PDF教材存储和检索~~ | 大文件处理是性能噩梦 | 按需简化 |
| ~~智能学习路径规划~~ | AI依赖太重，效果难验证 | V2考虑 |
| ~~社交功能（论坛/讨论区）~~ | 维护成本高 | 永不加 |
| ~~成绩分析和可视化看板~~ | 数据量不够时无意义 | V2考虑 |
| ~~离线客户端App~~ | Web已覆盖所有设备 | 永不加 |

---

## 八、风险识别与应对共识

### 8.1 高风险（必须应对）

| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|----------|
| **AI依赖陷阱** | 高 | 高 | 增加"认知门控"：先提交自己思路才能看AI解答 |
| **服务器容量不足** | 中 | 高 | 限流+内存监控+自动重启 |
| **DeepSeek API单点故障** | 中 | 高 | 三级降级：正常→缓存→提示 |
| **项目半途而废** | 高 | 中 | MVP验证，设定退出条件 |

### 8.2 中风险（建议应对）

| 风险 | 应对策略 |
|------|----------|
| WebDAV同步冲突复杂 | 先做JSON导出/导入，简化同步 |
| 数据丢失 | 每日自动备份到GitHub |
| Copilot技术债务 | 核心模块手写单元测试 |

### 8.3 验证核心假设的方法

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

---

## 九、成功指标共识

### 9.1 核心指标

| 指标 | 测量方法 | 目标值 | 验收时间 |
|------|----------|--------|----------|
| **学习效率提升30%** | 记录首次vs再次学习同一知识点的时间 | -30% | 学期末 |
| **知识留存率>70%** | 7天后知识点仍保持mastered状态的比例 | >70% | 学期末 |
| **作业完成时间减少50%** | 使用AI辅助前后的完成时间对比 | -50% | 学期末 |

### 9.2 辅助指标（可量化）

| 指标 | 测量方法 | 目标 |
|------|----------|------|
| 周活跃天数 | 系统日志统计 | ≥4天/周 |
| 功能使用率 | 功能埋点 | >60% |
| API调用效率 | 每次作业分析的平均token | 优化20% |

### 9.3 质性指标

- **学习动力**：是否感觉学习更有条理？
- **焦虑缓解**：考试前是否更从容？
- **知识自信**：是否能清晰感知自己的知识边界？

---

## 十、项目定位共识

### 10.1 定位声明

> **主要定位**："学习Node.js/Python开发的练手项目"  
> **次要定位**："个人学习管理工具"

| 定位 | 含义 | 影响 |
|------|------|------|
| 练手项目 | 不追求完美，允许失败和重构 | 降低预期压力 |
| 个人工具 | 单用户场景，不需要考虑扩展 | 简化权限和同步 |

### 10.2 成功标准

| 阶段 | 标准 |
|------|------|
| MVP完成 | 能记录1门课的作业并获得AI分析 |
| 核心价值实现 | 能从作业生成知识清单 |
| 完整使用 | 手机电脑能查看相同数据 |
| 稳定运行 | 连续3天无错误运行 |

---

## 十一、下一步行动

### 11.1 立即执行（本周）

| 任务 | 负责人 | 产出 |
|------|--------|------|
| 完成人工替代实验 | 用户 | 验证核心假设 |
| Vue.js项目初始化 | 后端 | 可运行的前端框架 |
| 数据模型扩展 | 后端 | 新增3张表 |

### 11.2 下周计划

| 任务 | 负责人 | 产出 |
|------|--------|------|
| 核心页面开发 | 前端 | 学科列表+知识树 |
| AI题目分析API完善 | 后端 | 支持题目→知识点关联 |
| 复习计划功能 | 后端 | ReviewPlan CRUD |

### 11.3 里程碑

| 里程碑 | 目标日期 | 交付物 |
|--------|----------|--------|
| M1: MVP Ready | Week 2 | 基础学习流程可用 |
| M2: AI功能上线 | Week 4 | AI问答和答案生成 |
| M3: 完整前端 | Week 6 | Vue.js完整界面 |
| M4: Release 1.0 | Week 8 | 稳定版本 |

---

## 十二、文档附录

### 12.1 术语表

| 术语 | 定义 |
|------|------|
| MVP | Minimum Viable Product，最小可行产品 |
| 认知门控 | 强制用户先独立思考才能获取AI帮助的机制 |
| 知识留存率 | 学习后一定时间内仍保持掌握状态的比例 |
| 上下文持久化 | 将用户背景信息持久化存储，避免重复交代 |

### 12.2 参考文档

- `.opencode/state/planner/plan.md` - 详细企划文档
- `.opencode/state/planner/architecture.md` - 技术架构文档

### 12.3 审核记录

| 版本 | 日期 | 审核人 | 状态 |
|------|------|--------|------|
| 1.0 | 2026-04-09 | - | 待审核 |

---

**文档版本**: 1.0  
**创建日期**: 2026-04-09  
**最后更新**: 2026-04-09  
**参与专家**: @questioner（需求细化）、@critic（风险评估）、@advisor（技术建议）  
**文档状态**: 待用户审核
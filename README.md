# 学习复习作业管理助手

面向大一软件工程学生的知识管理和复习工具，支持学习/作业/复习三种模式。

## 功能特性

### 核心功能
- 📚 **教材管理**：PDF教材上传、解析、章节提取
- 🌳 **知识结构**：树状+标签的知识点管理
- 📝 **作业管理**：题目录入、答案生成、掌握程度追踪
- 🧠 **学习模式**：知识点学习、AI答疑、学习记录
- 📊 **复习模式**：考试范围分析、知识点清单、智能推送
- 🔄 **多端同步**：JSON文件手动同步

### 技术栈
- **后端**：Flask + SQLite
- **前端**：Vue.js 单页应用
- **PDF解析**：PyMuPDF (fitz)
- **AI集成**：DeepSeek API
- **部署**：1核1G服务器

## 项目结构

```
Hw2Ex/
├── backend/           # Flask后端
│   ├── app.py        # 主应用
│   ├── models.py     # 数据模型
│   ├── routes/       # API路由
│   ├── utils/        # 工具函数
│   └── requirements.txt
├── frontend/         # Vue.js前端
│   ├── src/
│   ├── public/
│   └── package.json
├── data/             # 数据存储
│   ├── database.db   # SQLite数据库
│   └── uploads/      # 上传文件
├── docs/             # 文档
└── README.md
```

## 快速开始

### 后端设置
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### 前端设置
```bash
cd frontend
npm install
npm run serve
```

## 开发计划

### MVP版本（第1个月）
- [ ] 学科和教材管理
- [ ] PDF上传和解析
- [ ] 知识点树展示
- [ ] 学习模式基础流程
- [ ] 作业题目录入
- [ ] AI基础答疑

### 后续版本
- [ ] 作业答案生成
- [ ] 掌握程度追踪
- [ ] 复习模式
- [ ] 对话历史保存
- [ ] CSV批量导入

## 数据模型

### 核心表
- `Subject` - 学科
- `Book` - 教材
- `KnowledgeNode` - 知识点（树状）
- `Homework` - 作业题目
- `LearningRecord` - 学习记录
- `Conversation` - 对话历史

## 许可证

MIT License
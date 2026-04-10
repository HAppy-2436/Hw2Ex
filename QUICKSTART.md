# 学习助手 - 快速开始指南

## 🚀 一键启动

```bash
# 给启动脚本执行权限
chmod +x start.sh

# 启动系统
./start.sh
```

系统启动后，打开浏览器访问：http://localhost:8080

## 📋 系统要求

- Python 3.8+
- 网络连接（用于DeepSeek API）
- 1核1G内存（最低配置）

## 🔧 手动启动

### 后端API
```bash
cd backend
python3 app.py
```
后端运行在：http://localhost:5000

### 前端界面
```bash
cd frontend
# 使用Python
python3 -m http.server 8080
# 或直接打开 index.html 文件
```

## 🔑 配置DeepSeek API

1. 访问 https://platform.deepseek.com/api_keys 获取API密钥
2. 在前端管理页面输入API密钥
3. 保存后即可使用AI功能

## 📚 核心功能

### 1. 学习模式
- 输入问题或知识点
- 获取详细解答
- 支持上下文理解

### 2. 作业模式
- 输入作业题目
- 生成详细答案
- 支持多种科目

### 3. 复习模式
- 输入复习主题
- 根据掌握程度生成资料
- 提供个性化复习计划

### 4. 数据管理
- JSON数据导出/导入
- API缓存管理
- 系统状态监控

## 🗄️ API接口

### 健康检查
```
GET /api/health
```

### AI问答
```
POST /api/ai/ask
{
  "question": "你的问题",
  "context": "可选上下文"
}
```

### 作业答案
```
POST /api/ai/homework-answer
{
  "question": "作业题目",
  "subject": "科目"
}
```

### 复习资料
```
POST /api/ai/review-materials
{
  "topics": [
    {"id": 1, "title": "主题", "mastery": "learning"}
  ]
}
```

## 💾 数据存储

- 数据库：SQLite (`data/database.db`)
- 上传文件：`data/uploads/`
- AI缓存：`data/ai_cache.db`
- 本地配置：浏览器localStorage

## 🔄 多端同步

1. 在管理页面点击"导出数据"
2. 保存生成的JSON文件
3. 在其他设备导入该文件

## 🐛 故障排除

### API连接失败
1. 检查后端是否运行：`curl http://localhost:5000/api/health`
2. 检查端口是否被占用
3. 检查Python依赖是否安装

### AI功能不可用
1. 检查是否配置了DeepSeek API密钥
2. 检查网络连接
3. 查看浏览器控制台错误信息

### 文件上传失败
1. 检查`data/uploads`目录权限
2. 确保PDF文件小于50MB
3. 检查文件格式是否为PDF

## 📞 支持

如有问题，请检查：
1. 查看后端日志输出
2. 检查浏览器开发者工具
3. 确保满足系统要求

## 📄 许可证

MIT License - 仅供学习使用
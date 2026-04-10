#!/bin/bash

echo "🚀 启动学习助手系统"

echo "1. 检查Python依赖..."
cd backend
python3 -c "import flask, flask_cors, flask_sqlalchemy, fitz, pandas, openpyxl" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  正在安装Python依赖..."
    python3 -m pip install --break-system-packages flask flask-cors flask-sqlalchemy pymupdf python-dotenv requests pandas openpyxl
fi

echo "2. 启动后端API服务器..."
python3 app.py &
BACKEND_PID=$!
sleep 3

echo "3. 检查API状态..."
curl -s http://localhost:5000/api/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ 后端API运行正常"
else
    echo "❌ 后端API启动失败"
    exit 1
fi

echo "4. 启动前端服务..."
cd ../frontend
if command -v python3 &> /dev/null; then
    echo "使用Python启动HTTP服务器..."
    python3 -m http.server 8080 &
    FRONTEND_PID=$!
elif command -v php &> /dev/null; then
    echo "使用PHP启动HTTP服务器..."
    php -S localhost:8080 &
    FRONTEND_PID=$!
else
    echo "⚠️  请手动打开 frontend/index.html 文件"
    FRONTEND_PID=""
fi

echo ""
echo "========================================="
echo "🎉 学习助手系统已启动！"
echo ""
echo "🔗 前端界面: http://localhost:8080"
echo "🔗 后端API: http://localhost:5000"
echo "📚 API文档: http://localhost:5000/api/docs"
echo ""
echo "📝 使用说明:"
echo "1. 打开浏览器访问 http://localhost:8080"
echo "2. 在管理页面配置DeepSeek API密钥"
echo "3. 开始使用学习/作业/复习模式"
echo "========================================="
echo ""
echo "按 Ctrl+C 停止所有服务"

trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

wait
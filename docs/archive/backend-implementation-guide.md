# 智能客服系统后端实施指南 - 第一阶段Demo

## 分步实施指南

### 步骤1：创建项目结构
```bash
# 在项目根目录下创建后端目录
cd /home/ec2-user/work/ai-customer-service
mkdir backend
cd backend

# 创建项目结构
mkdir -p app/api app/services
touch app/__init__.py app/main.py app/models.py
touch app/api/__init__.py app/api/chat.py
touch app/services/__init__.py app/services/chat_service.py
touch requirements.txt Dockerfile docker-compose.yml
```

### 步骤2：创建依赖文件
创建 `requirements.txt`：
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
```

### 步骤3：创建数据模型
创建 `app/models.py`：
```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    type: str
    content: Dict[str, Any]
    timestamp: datetime
```

### 步骤4：创建聊天服务
创建 `app/services/chat_service.py`：
```python
import random
from datetime import datetime
from typing import Dict, Any

class ChatService:
    def __init__(self):
        self.demo_responses = {
            "text": [
                {"text": "您好！我是智能客服助手，很高兴为您服务！"},
                {"text": "感谢您的咨询，我会尽力帮助您解决问题。"},
                {"text": "这是一个演示回复，展示文本消息功能。"},
                {"text": "我正在学习中，请多多指教！"},
                {"text": "有什么其他问题需要帮助吗？"}
            ],
            "image": [
                {"picUrl": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgZmlsbD0iIzQyODVGNCIvPjx0ZXh0IHg9IjIwMCIgeT0iMTI1IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+QUkg5Zu+54mHPC90ZXh0Pjwvc3ZnPg=="},
                {"picUrl": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgZmlsbD0iIzRDQUY1MCIvPjx0ZXh0IHg9IjIwMCIgeT0iMTI1IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+5pm65oSP5a6i5pyNPC90ZXh0Pjwvc3ZnPg=="},
                {"picUrl": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgZmlsbD0iI0ZGOTgwMCIvPjx0ZXh0IHg9IjIwMCIgeT0iMTI1IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+5ryU56S65Zu+54mHPC90ZXh0Pjwvc3ZnPg=="}
            ],
            "card": [
                {
                    "title": "智能客服系统",
                    "desc": "基于AI技术的智能客服解决方案",
                    "img": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iIzQyODVGNCIvPjx0ZXh0IHg9IjE1MCIgeT0iNzUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5BSeWuouacjTwvdGV4dD48L3N2Zz4=",
                    "actions": [{"type": "url", "text": "了解更多", "url": "#"}]
                },
                {
                    "title": "产品介绍",
                    "desc": "全方位的客服解决方案",
                    "img": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iIzRDQUY1MCIvPjx0ZXh0IHg9IjE1MCIgeT0iNzUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7kuqflk4HkuIvnu40PC90ZXh0Pjwvc3ZnPg==",
                    "actions": [{"type": "url", "text": "查看详情", "url": "#"}]
                },
                {
                    "title": "技术支持",
                    "desc": "7x24小时技术支持服务",
                    "img": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iI0ZGOTgwMCIvPjx0ZXh0IHg9IjE1MCIgeT0iNzUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7mioDmnK/mlK/mjIE8L3RleHQ+PC9zdmc+",
                    "actions": [{"type": "url", "text": "联系我们", "url": "#"}]
                }
            ],
            "list": [
                {
                    "header": {"title": "系统功能"},
                    "items": [
                        {"title": "智能问答", "desc": "基于AI的自动问答", "icon": "🤖"},
                        {"title": "多轮对话", "desc": "支持上下文理解", "icon": "💬"},
                        {"title": "实时监控", "desc": "对话质量监控", "icon": "📊"}
                    ]
                },
                {
                    "header": {"title": "服务特色"},
                    "items": [
                        {"title": "24小时服务", "desc": "全天候在线服务", "icon": "⏰"},
                        {"title": "多语言支持", "desc": "支持多种语言", "icon": "🌍"},
                        {"title": "快速响应", "desc": "秒级响应速度", "icon": "⚡"}
                    ]
                }
            ]
        }
    
    def get_random_response(self) -> Dict[str, Any]:
        # 随机选择响应类型：30%文本，30%图片，20%卡片，20%列表
        response_type = random.choices(
            ["text", "image", "card", "list"],
            weights=[30, 30, 20, 20]
        )[0]
        
        content = random.choice(self.demo_responses[response_type])
        
        return {
            "type": response_type,
            "content": content,
            "timestamp": datetime.now()
        }
```

### 步骤5：创建API路由
创建 `app/api/chat.py`：
```python
from fastapi import APIRouter
from app.models import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response_data = chat_service.get_random_response()
    return ChatResponse(**response_data)
```

### 步骤6：创建主应用
创建 `app/main.py`：
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat

app = FastAPI(title="智能客服API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "智能客服API服务正在运行"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 步骤7：创建Docker配置
创建 `Dockerfile`：
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

创建 `docker-compose.yml`：
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=development
    volumes:
      - ./app:/app/app
```

### 步骤8：安装和运行
```bash
# 安装Python依赖
pip install -r requirements.txt

# 直接运行（开发模式）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用Docker运行
docker-compose up --build
```

### 步骤9：测试API
```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试聊天接口
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "你好"}'
```

### 步骤10：查看API文档
启动服务后访问：http://localhost:8000/docs

## 完成后的项目结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat.py
│   └── services/
│       ├── __init__.py
│       └── chat_service.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

执行完这些步骤后，你将拥有一个完整的后端API服务，可以接收前端消息并随机返回不同类型的演示内容。
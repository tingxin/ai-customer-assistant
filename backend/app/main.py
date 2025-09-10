from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat
from app.knowledge.api import knowledge_base

app = FastAPI(title="智能客服API", version="1.0.0")

# CORS配置 - 开发环境使用宽松设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=False,  # 设为False避免预检问题
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api")
app.include_router(knowledge_base.router, prefix="/api/knowledge")

@app.get("/")
async def root():
    return {"message": "智能客服API服务正在运行"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
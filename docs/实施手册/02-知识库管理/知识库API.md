# 知识库API实现

## 🎯 目标
基于开发文档的API设计规范，实现知识库管理的RESTful API接口。

## 📋 前置条件
- 知识库数据模型已创建
- FastAPI框架已配置

## 🔌 API接口设计

### 1. 创建知识库服务层

创建 `backend/app/services/knowledge_service.py`：
```python
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models.knowledge import KnowledgeBase, Document, KnowledgeBaseStatus
from app.schemas.knowledge import KnowledgeBaseCreate, KnowledgeBaseUpdate
import uuid

class KnowledgeBaseService:
    
    @staticmethod
    def create_knowledge_base(db: Session, kb_data: KnowledgeBaseCreate, owner_id: str) -> KnowledgeBase:
        """创建知识库"""
        kb = KnowledgeBase(
            name=kb_data.name,
            description=kb_data.description,
            owner_id=owner_id
        )
        db.add(kb)
        db.commit()
        db.refresh(kb)
        return kb
    
    @staticmethod
    def get_knowledge_bases(db: Session, owner_id: str, skip: int = 0, limit: int = 100) -> List[KnowledgeBase]:
        """获取知识库列表"""
        return db.query(KnowledgeBase).filter(
            and_(
                KnowledgeBase.owner_id == owner_id,
                KnowledgeBase.status != KnowledgeBaseStatus.DELETED
            )
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_knowledge_base(db: Session, kb_id: str, owner_id: str) -> Optional[KnowledgeBase]:
        """获取单个知识库"""
        return db.query(KnowledgeBase).filter(
            and_(
                KnowledgeBase.id == kb_id,
                KnowledgeBase.owner_id == owner_id,
                KnowledgeBase.status != KnowledgeBaseStatus.DELETED
            )
        ).first()
    
    @staticmethod
    def update_knowledge_base(db: Session, kb_id: str, kb_data: KnowledgeBaseUpdate, owner_id: str) -> Optional[KnowledgeBase]:
        """更新知识库"""
        kb = KnowledgeBaseService.get_knowledge_base(db, kb_id, owner_id)
        if not kb:
            return None
        
        update_data = kb_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(kb, field, value)
        
        db.commit()
        db.refresh(kb)
        return kb
    
    @staticmethod
    def delete_knowledge_base(db: Session, kb_id: str, owner_id: str, hard_delete: bool = False) -> bool:
        """删除知识库"""
        kb = KnowledgeBaseService.get_knowledge_base(db, kb_id, owner_id)
        if not kb:
            return False
        
        if hard_delete:
            db.delete(kb)
        else:
            kb.status = KnowledgeBaseStatus.DELETED
        
        db.commit()
        return True
    
    @staticmethod
    def update_document_count(db: Session, kb_id: str):
        """更新文档数量"""
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
        if kb:
            count = db.query(Document).filter(Document.knowledge_base_id == kb_id).count()
            kb.document_count = count
            db.commit()
```

### 2. 创建API路由

创建 `backend/app/api/v1/knowledge.py`：
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db
from app.services.knowledge_service import KnowledgeBaseService
from app.schemas.knowledge import (
    KnowledgeBaseCreate, 
    KnowledgeBaseUpdate, 
    KnowledgeBaseResponse
)

router = APIRouter()

# 临时用户ID，实际应从JWT token获取
TEMP_USER_ID = "temp-user-123"

@router.post("/bases", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    db: Session = Depends(get_db)
):
    """创建知识库"""
    try:
        kb = KnowledgeBaseService.create_knowledge_base(db, kb_data, TEMP_USER_ID)
        return kb
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建知识库失败: {str(e)}"
        )

@router.get("/bases", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取知识库列表"""
    try:
        kbs = KnowledgeBaseService.get_knowledge_bases(db, TEMP_USER_ID, skip, limit)
        return kbs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识库列表失败: {str(e)}"
        )

@router.get("/bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: str,
    db: Session = Depends(get_db)
):
    """获取知识库详情"""
    kb = KnowledgeBaseService.get_knowledge_base(db, kb_id, TEMP_USER_ID)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )
    return kb

@router.put("/bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: str,
    kb_data: KnowledgeBaseUpdate,
    db: Session = Depends(get_db)
):
    """更新知识库"""
    kb = KnowledgeBaseService.update_knowledge_base(db, kb_id, kb_data, TEMP_USER_ID)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )
    return kb

@router.delete("/bases/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    hard_delete: bool = False,
    db: Session = Depends(get_db)
):
    """删除知识库"""
    success = KnowledgeBaseService.delete_knowledge_base(db, kb_id, TEMP_USER_ID, hard_delete)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )
    
    return {
        "success": True,
        "message": "知识库删除成功" if not hard_delete else "知识库永久删除成功"
    }
```

### 3. 注册路由到主应用

更新 `backend/app/main.py`：
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import knowledge
from app.core.config import settings

app = FastAPI(
    title="智能客服系统API",
    description="基于RAG技术的智能客服系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册知识库路由
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])

@app.get("/")
async def root():
    return {"message": "智能客服系统API服务正在运行", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-customer-service"}
```

### 4. 创建统一响应格式

创建 `backend/app/schemas/response.py`：
```python
from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime

class StandardResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: str
    code: int
    timestamp: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

## ✅ 验证步骤

### 1. 启动API服务
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 测试API接口

#### 创建知识库
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/bases" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "产品知识库",
       "description": "产品相关文档和FAQ"
     }'
```

#### 获取知识库列表
```bash
curl "http://localhost:8000/api/v1/knowledge/bases"
```

#### 获取知识库详情
```bash
curl "http://localhost:8000/api/v1/knowledge/bases/{kb_id}"
```

#### 更新知识库
```bash
curl -X PUT "http://localhost:8000/api/v1/knowledge/bases/{kb_id}" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "更新后的知识库名称",
       "description": "更新后的描述"
     }'
```

#### 删除知识库
```bash
curl -X DELETE "http://localhost:8000/api/v1/knowledge/bases/{kb_id}"
```

### 3. 检查API文档
访问 http://localhost:8000/docs 查看自动生成的API文档

### 4. 验证数据库
```sql
-- 检查数据是否正确插入
SELECT * FROM knowledge_bases;
SELECT * FROM documents;
```

## 🚨 常见问题

### UUID格式错误
```python
# 确保UUID格式正确
import uuid
kb_id = str(uuid.uuid4())
```

### 数据库连接问题
```python
# 检查数据库连接配置
from app.core.config import settings
print(settings.DATABASE_URL)
```

### JSON序列化问题
```python
# 确保datetime正确序列化
from datetime import datetime
from pydantic import BaseModel

class Response(BaseModel):
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

## ➡️ 下一步
API实现完成后，继续 [文档处理服务](./文档处理服务.md)
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ..services.knowledge_base_service import KnowledgeBaseService
from ..schemas import KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse
from app.database import get_db

router = APIRouter()

@router.post("/bases", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(request: KnowledgeBaseCreate, db: AsyncSession = Depends(get_db)):
    """创建知识库"""
    try:
        kb_service = KnowledgeBaseService(db)
        return await kb_service.create_knowledge_base(
            name=request.name,
            description=request.description,
            owner_id="admin-001"  # TODO: 从认证中获取实际用户ID
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="创建知识库失败")

@router.get("/bases", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases(db: AsyncSession = Depends(get_db)):
    """获取知识库列表"""
    try:
        kb_service = KnowledgeBaseService(db)
        return await kb_service.get_knowledge_bases()
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取知识库列表失败")

@router.get("/bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(kb_id: str, db: AsyncSession = Depends(get_db)):
    """获取知识库详情"""
    try:
        kb_service = KnowledgeBaseService(db)
        kb = await kb_service.get_knowledge_base(kb_id)
        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")
        return kb
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取知识库失败")

@router.put("/bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(kb_id: str, request: KnowledgeBaseUpdate, db: AsyncSession = Depends(get_db)):
    """更新知识库"""
    try:
        kb_service = KnowledgeBaseService(db)
        kb = await kb_service.update_knowledge_base(
            kb_id=kb_id,
            name=request.name,
            description=request.description
        )
        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")
        return kb
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新知识库失败: {str(e)}")

@router.delete("/bases/{kb_id}")
async def delete_knowledge_base(kb_id: str, hard_delete: bool = False, db: AsyncSession = Depends(get_db)):
    """删除知识库"""
    try:
        kb_service = KnowledgeBaseService(db)
        success = await kb_service.delete_knowledge_base(kb_id, hard_delete=hard_delete)
        if not success:
            raise HTTPException(status_code=404, detail="知识库不存在")
        return {"message": "知识库删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="删除知识库失败")
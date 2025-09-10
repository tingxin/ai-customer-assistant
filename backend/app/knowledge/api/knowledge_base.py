from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..services.knowledge_base_service import KnowledgeBaseService
from ..models.knowledge_base import KnowledgeBase, KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseStatus

router = APIRouter()
kb_service = KnowledgeBaseService()

@router.post("/bases", response_model=KnowledgeBase)
async def create_knowledge_base(request: KnowledgeBaseCreate):
    """创建知识库"""
    try:
        return await kb_service.create_knowledge_base(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bases", response_model=List[KnowledgeBase])
async def list_knowledge_bases(
    status: Optional[KnowledgeBaseStatus] = Query(None, description="过滤状态")
):
    """列出知识库"""
    return await kb_service.list_knowledge_bases(status)

@router.get("/bases/{kb_id}", response_model=KnowledgeBase)
async def get_knowledge_base(kb_id: str):
    """获取知识库详情"""
    kb = await kb_service.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return kb

@router.put("/bases/{kb_id}", response_model=KnowledgeBase)
async def update_knowledge_base(kb_id: str, request: KnowledgeBaseUpdate):
    """更新知识库"""
    kb = await kb_service.update_knowledge_base(kb_id, request)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return kb

@router.delete("/bases/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    hard_delete: bool = Query(False, description="是否硬删除")
):
    """删除知识库"""
    success = await kb_service.delete_knowledge_base(kb_id, not hard_delete)
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return {"message": "Knowledge base deleted successfully"}
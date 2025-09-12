from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..services.document_service import DocumentService
from ..schemas import DocumentResponse
from app.database import get_db
from app.config import settings

router = APIRouter()

@router.post("/bases/{kb_id}/documents/upload", response_model=DocumentResponse)
async def upload_document(
    kb_id: str, 
    file: UploadFile = File(...), 
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """上传文档到知识库"""
    try:
        # 验证文件类型
        allowed_extensions = set(settings.allowed_extensions)
        file_extension = None
        if file.filename:
            file_extension = '.' + file.filename.split('.')[-1].lower()
        
        if not file_extension or file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件类型。支持的格式: {', '.join(allowed_extensions)}"
            )
        
        # 验证文件大小
        content = await file.read()
        if len(content) > settings.max_file_size:
            max_size_mb = settings.max_file_size / (1024 * 1024)
            raise HTTPException(status_code=400, detail=f"文件大小不能超过{max_size_mb:.0f}MB")
        
        # 重置文件指针
        await file.seek(0)
        
        doc_service = DocumentService(db)
        document = await doc_service.upload_document(kb_id, file, title, description)
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="文件上传失败")

@router.get("/bases/{kb_id}/documents", response_model=List[DocumentResponse])
async def get_documents(kb_id: str, db: AsyncSession = Depends(get_db)):
    """获取知识库的所有文档"""
    try:
        doc_service = DocumentService(db)
        return await doc_service.get_documents_by_kb(kb_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取文档列表失败")

@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    """获取单个文档详情"""
    try:
        doc_service = DocumentService(db)
        document = await doc_service.get_document(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取文档失败")

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    """删除文档"""
    try:
        doc_service = DocumentService(db)
        success = await doc_service.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="文档不存在")
        return {"message": "文档删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="删除文档失败")

@router.post("/documents/{doc_id}/process")
async def process_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    """处理文档（RAG解析和向量化）"""
    try:
        doc_service = DocumentService(db)
        success = await doc_service.process_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="文档不存在")
        return {"message": "文档处理已启动"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="文档处理启动失败")
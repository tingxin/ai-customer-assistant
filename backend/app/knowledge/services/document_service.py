import os
import uuid
import logging
from typing import List, Optional
from datetime import datetime, timezone
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from ..models.database_models import Document, DocumentStatus, KnowledgeBase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.database_models import Document as DocumentModel
else:
    DocumentModel = Document
from app.config import settings
import re

def secure_filename(filename):
    """Make a filename safe for use"""
    if not filename:
        return 'unnamed'
    # Remove path separators and dangerous characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    return filename or 'unnamed'

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _ensure_kb_directory(self, kb_id: str) -> Path:
        """确保知识库目录存在"""
        safe_kb_id = secure_filename(kb_id)
        kb_dir = Path(settings.upload_base_dir) / "knowledge_bases" / safe_kb_id
        documents_dir = kb_dir / "documents"
        
        try:
            documents_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create knowledge base directory: {e}")
            raise
        
        return documents_dir
    
    async def upload_document(self, kb_id: str, file: UploadFile, title: str = None, description: str = None) -> DocumentModel:
        """上传文档到知识库"""
        doc_id = str(uuid.uuid4())
        
        # 确保知识库文档目录存在
        kb_doc_dir = self._ensure_kb_directory(kb_id)
        
        # 安全处理文件名
        safe_filename_str = secure_filename(file.filename or "")
        file_extension = os.path.splitext(safe_filename_str)[1]
        file_name = f"{doc_id}{file_extension}"
        file_path = kb_doc_dir / file_name
        
        # 写入文件
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        except (IOError, OSError) as e:
            logger.error(f"Failed to save uploaded file: {e}")
            raise
        
        # 创建文档记录
        now = datetime.now(timezone.utc)
        document = Document(
            id=doc_id,
            title=title or file.filename or file_name,
            description=description,
            knowledge_base_id=kb_id,
            file_path=str(file_path),
            file_size=len(content),
            doc_type=file_extension.lower(),
            mime_type=file.content_type,
            status='uploaded',
            doc_metadata={},
            created_at=now,
            updated_at=now
        )
        
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document
    
    async def get_documents_by_kb(self, kb_id: str) -> List[DocumentModel]:
        """获取知识库的所有文档"""
        print(f"Querying documents for knowledge_base_id: {kb_id}")
        result = await self.db.execute(
            select(Document).where(Document.knowledge_base_id == kb_id)
        )
        documents = result.scalars().all()
        print(f"Query returned {len(documents)} documents")
        for doc in documents:
            print(f"Document: {doc.id}, title: {doc.title}, kb_id: {doc.knowledge_base_id}")
        return documents
    
    async def get_document(self, doc_id: str) -> Optional[DocumentModel]:
        """获取单个文档"""
        result = await self.db.execute(
            select(Document).where(Document.id == doc_id)
        )
        return result.scalar_one_or_none()
    
    async def update_document_status(self, doc_id: str, status: DocumentStatus, error_message: str = None) -> Optional[DocumentModel]:
        """更新文档状态"""
        update_data = {
            "status": status,
            "updated_at": datetime.now(timezone.utc)
        }
        
        if status == 'completed':
            update_data["processed_at"] = datetime.now(timezone.utc)
        
        if error_message:
            update_data["error_message"] = error_message
        
        stmt = update(Document).where(Document.id == doc_id).values(**update_data)
        result = await self.db.execute(stmt)
        
        if result.rowcount == 0:
            return None
        
        await self.db.commit()
        return await self.get_document(doc_id)
    
    async def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        document = await self.get_document(doc_id)
        if not document:
            return False
        
        # 删除文件
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to delete document file: {e}")
            # 继续删除数据库记录
        
        # 删除数据库记录
        await self.db.execute(delete(Document).where(Document.id == doc_id))
        await self.db.commit()
        return True
    
    async def process_document(self, doc_id: str) -> bool:
        """处理文档（RAG解析和向量化）"""
        document = await self.get_document(doc_id)
        if not document:
            return False
        
        # 检查文档状态
        if document.status != 'uploaded':
            return False
        
        # 更新状态为解析中
        await self.update_document_status(doc_id, 'parsing')
        
        # TODO: 这里将来集成RAG-Anything和LightRAG处理
        # 目前仅模拟状态变更
        
        return True
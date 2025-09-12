import os
import uuid
import logging
from typing import List, Optional
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from ..models.database_models import KnowledgeBase, KnowledgeBaseStatus, User
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.database_models import KnowledgeBase as KnowledgeBaseModel
else:
    KnowledgeBaseModel = KnowledgeBase
from app.config import settings
import shutil
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

class KnowledgeBaseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._ensure_base_directory()
    
    def _ensure_base_directory(self):
        """确保基础目录存在"""
        try:
            base_dir = Path(settings.upload_base_dir)
            base_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建知识库根目录
            kb_root = base_dir / "knowledge_bases"
            kb_root.mkdir(exist_ok=True)
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create base directory: {e}")
            raise

    async def create_knowledge_base(self, name: str, description: str = None, owner_id: str = "admin-001") -> KnowledgeBaseModel:
        """创建知识库"""
        kb_id = str(uuid.uuid4())
        
        # 安全地创建知识库目录
        safe_kb_id = secure_filename(kb_id)
        kb_dir = Path(settings.upload_base_dir) / "knowledge_bases" / safe_kb_id
        
        try:
            kb_dir.mkdir(parents=True, exist_ok=True)
            (kb_dir / "documents").mkdir(exist_ok=True)
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create knowledge base directory: {e}")
            raise
        
        now = datetime.now(timezone.utc)
        knowledge_base = KnowledgeBase(
            id=kb_id,
            name=name,
            description=description,
            owner_id=owner_id,
            status='active',
            created_at=now,
            updated_at=now
        )
        
        self.db.add(knowledge_base)
        await self.db.commit()
        await self.db.refresh(knowledge_base)
        return knowledge_base

    async def get_knowledge_bases(self) -> List[KnowledgeBaseModel]:
        """获取所有知识库（不包括已归档的）"""
        result = await self.db.execute(
            select(KnowledgeBase).where(KnowledgeBase.status != 'archived')
        )
        return result.scalars().all()

    async def get_knowledge_base(self, kb_id: str) -> Optional[KnowledgeBaseModel]:
        """获取单个知识库"""
        result = await self.db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
        return result.scalar_one_or_none()

    async def update_knowledge_base(self, kb_id: str, name: str = None, description: str = None) -> Optional[KnowledgeBaseModel]:
        """更新知识库"""
        stmt = update(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        update_data = {"updated_at": datetime.now(timezone.utc)}
        
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        
        stmt = stmt.values(**update_data)
        result = await self.db.execute(stmt)
        
        if result.rowcount == 0:
            return None
        
        await self.db.commit()
        return await self.get_knowledge_base(kb_id)

    async def delete_knowledge_base(self, kb_id: str, hard_delete: bool = False) -> bool:
        """删除知识库"""
        knowledge_base = await self.get_knowledge_base(kb_id)
        if not knowledge_base:
            return False
        
        try:
            if hard_delete:
                # 物理删除：先删除目录，再删除数据库记录
                safe_kb_id = secure_filename(kb_id)
                kb_dir = Path(settings.upload_base_dir) / "knowledge_bases" / safe_kb_id
                
                try:
                    if kb_dir.exists():
                        shutil.rmtree(kb_dir)
                except (OSError, PermissionError) as e:
                    logger.error(f"Failed to delete knowledge base directory: {e}")
                    # 继续删除数据库记录
                
                # 删除知识库（级联删除会自动删除相关文档）
                await self.db.execute(delete(KnowledgeBase).where(KnowledgeBase.id == kb_id))
            else:
                # 软删除：标记为已归档
                stmt = update(KnowledgeBase).where(KnowledgeBase.id == kb_id).values(
                    status='archived',
                    updated_at=datetime.now(timezone.utc)
                )
                await self.db.execute(stmt)
            
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise
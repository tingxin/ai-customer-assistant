from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import os
import shutil
from ..models.knowledge_base import KnowledgeBase, KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseStatus

class KnowledgeBaseService:
    def __init__(self, base_dir: str = "./knowledge_bases"):
        self.base_dir = base_dir
        self.knowledge_bases: Dict[str, KnowledgeBase] = {}
        os.makedirs(base_dir, exist_ok=True)
    
    async def create_knowledge_base(self, request: KnowledgeBaseCreate) -> KnowledgeBase:
        """创建知识库"""
        kb_id = str(uuid.uuid4())
        now = datetime.now()
        
        # 创建知识库目录
        kb_dir = os.path.join(self.base_dir, kb_id)
        os.makedirs(kb_dir, exist_ok=True)
        os.makedirs(os.path.join(kb_dir, "documents"), exist_ok=True)
        os.makedirs(os.path.join(kb_dir, "vectors"), exist_ok=True)
        
        knowledge_base = KnowledgeBase(
            id=kb_id,
            name=request.name,
            description=request.description,
            owner=request.owner,
            status=KnowledgeBaseStatus.ACTIVE,
            document_count=0,
            created_at=now,
            updated_at=now
        )
        
        self.knowledge_bases[kb_id] = knowledge_base
        return knowledge_base
    
    async def get_knowledge_base(self, kb_id: str) -> Optional[KnowledgeBase]:
        """获取知识库"""
        return self.knowledge_bases.get(kb_id)
    
    async def list_knowledge_bases(self, status: Optional[KnowledgeBaseStatus] = None) -> List[KnowledgeBase]:
        """列出知识库"""
        bases = list(self.knowledge_bases.values())
        if status:
            bases = [kb for kb in bases if kb.status == status]
        return sorted(bases, key=lambda x: x.created_at, reverse=True)
    
    async def update_knowledge_base(self, kb_id: str, request: KnowledgeBaseUpdate) -> Optional[KnowledgeBase]:
        """更新知识库"""
        if kb_id not in self.knowledge_bases:
            return None
        
        kb = self.knowledge_bases[kb_id]
        
        if request.name is not None:
            kb.name = request.name
        if request.description is not None:
            kb.description = request.description
        if request.owner is not None:
            kb.owner = request.owner
        if request.status is not None:
            kb.status = request.status
        
        kb.updated_at = datetime.now()
        return kb
    
    async def delete_knowledge_base(self, kb_id: str, soft_delete: bool = True) -> bool:
        """删除知识库"""
        if kb_id not in self.knowledge_bases:
            return False
        
        if soft_delete:
            # 软删除：只标记状态
            kb = self.knowledge_bases[kb_id]
            kb.status = KnowledgeBaseStatus.DELETED
            kb.updated_at = datetime.now()
        else:
            # 硬删除：删除文件和记录
            kb_dir = os.path.join(self.base_dir, kb_id)
            if os.path.exists(kb_dir):
                shutil.rmtree(kb_dir)
            del self.knowledge_bases[kb_id]
        
        return True
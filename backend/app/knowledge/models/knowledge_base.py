from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class KnowledgeBaseStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"

class KnowledgeBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    owner: str  # 新增字段
    status: KnowledgeBaseStatus = KnowledgeBaseStatus.ACTIVE
    document_count: int = 0
    created_at: datetime
    updated_at: datetime

class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    owner: str  # 新增字段

class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None  # 新增字段
    status: Optional[KnowledgeBaseStatus] = None
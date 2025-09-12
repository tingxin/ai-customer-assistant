from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class KnowledgeBaseStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    VECTORIZING = "vectorizing"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"

# Request schemas
class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    owner: str = "admin"

class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Response schemas
class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    status: KnowledgeBaseStatus
    document_count: int
    total_size: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    knowledge_base_id: str
    file_path: str
    file_size: int
    doc_type: str
    mime_type: Optional[str]
    status: DocumentStatus
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True
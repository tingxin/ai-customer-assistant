from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"

class DocumentCreate(BaseModel):
    title: str
    knowledge_base_id: str
    file_path: str
    file_size: int
    doc_type: str

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[DocumentStatus] = None

class Document(BaseModel):
    id: str
    title: str
    knowledge_base_id: str
    file_path: str
    file_size: int
    doc_type: str
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
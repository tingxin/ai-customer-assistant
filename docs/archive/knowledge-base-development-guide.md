# 知识库管理系统开发指南 - RAG-Anything + LightRAG

## 1. 技术架构设计

### 1.1 核心组件
```
知识库管理层
├── 文档处理模块 (RAG-Anything)
│   ├── 文档解析器 (PDF/Word/TXT/Markdown)
│   ├── 内容提取器
│   └── 格式标准化
├── 向量化处理模块 (LightRAG)
│   ├── 文本切片器
│   ├── 向量编码器
│   └── 索引构建器
├── 检索引擎
│   ├── 语义检索
│   ├── 关键词检索
│   └── 混合检索
└── 知识图谱
    ├── 实体识别
    ├── 关系抽取
    └── 图谱构建
```

### 1.2 数据流架构
```
文档上传 → RAG-Anything解析 → LightRAG向量化 → 向量存储
                                                    ↓
用户查询 ← 智能回复生成 ← 知识检索 ← 向量检索引擎
```

## 2. 环境搭建

### 2.1 依赖安装
```bash
# 创建知识库模块目录
mkdir -p backend/app/knowledge
cd backend

# 安装RAG-Anything
pip install rag-anything

# 安装LightRAG
pip install lightrag

# 安装向量数据库
pip install chromadb

# 安装文档处理依赖
pip install pypdf2 python-docx markdown beautifulsoup4

# 安装NLP依赖
pip install sentence-transformers transformers torch

# 更新requirements.txt
echo "rag-anything==0.1.0" >> requirements.txt
echo "lightrag==0.1.0" >> requirements.txt
echo "chromadb==0.4.15" >> requirements.txt
echo "pypdf2==3.0.1" >> requirements.txt
echo "python-docx==0.8.11" >> requirements.txt
echo "markdown==3.5.1" >> requirements.txt
echo "beautifulsoup4==4.12.2" >> requirements.txt
echo "sentence-transformers==2.2.2" >> requirements.txt
echo "transformers==4.35.0" >> requirements.txt
echo "torch==2.1.0" >> requirements.txt
```

### 2.2 项目结构
```
backend/app/knowledge/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── document.py          # 文档数据模型
│   ├── knowledge_base.py    # 知识库模型
│   └── vector_store.py      # 向量存储模型
├── services/
│   ├── __init__.py
│   ├── document_parser.py   # RAG-Anything文档解析
│   ├── vector_service.py    # LightRAG向量化服务
│   ├── retrieval_service.py # 检索服务
│   └── knowledge_service.py # 知识库管理服务
├── api/
│   ├── __init__.py
│   ├── knowledge.py         # 知识库管理API
│   └── retrieval.py         # 检索API
└── config/
    ├── __init__.py
    └── rag_config.py        # RAG配置
```

## 3. 核心功能实现

### 3.1 文档数据模型
```python
# backend/app/knowledge/models/document.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    PDF = "pdf"
    WORD = "word"
    TXT = "txt"
    MARKDOWN = "markdown"
    HTML = "html"

class DocumentStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"

class Document(BaseModel):
    id: str
    title: str
    content: str
    doc_type: DocumentType
    status: DocumentStatus
    file_path: str
    file_size: int
    upload_time: datetime
    process_time: Optional[datetime] = None
    tags: List[str] = []
    category: Optional[str] = None
    metadata: Dict[str, Any] = {}

class DocumentChunk(BaseModel):
    id: str
    document_id: str
    content: str
    chunk_index: int
    vector_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
```

### 3.2 RAG-Anything文档解析服务
```python
# backend/app/knowledge/services/document_parser.py
import os
from typing import List, Dict, Any
from rag_anything import DocumentParser, ContentExtractor
import PyPDF2
from docx import Document as DocxDocument
import markdown
from bs4 import BeautifulSoup

class DocumentParserService:
    def __init__(self):
        self.rag_parser = DocumentParser()
        self.content_extractor = ContentExtractor()
    
    async def parse_document(self, file_path: str, doc_type: str) -> Dict[str, Any]:
        """使用RAG-Anything解析文档"""
        try:
            if doc_type == "pdf":
                return await self._parse_pdf(file_path)
            elif doc_type == "word":
                return await self._parse_word(file_path)
            elif doc_type == "txt":
                return await self._parse_txt(file_path)
            elif doc_type == "markdown":
                return await self._parse_markdown(file_path)
            else:
                raise ValueError(f"Unsupported document type: {doc_type}")
        except Exception as e:
            raise Exception(f"Document parsing failed: {str(e)}")
    
    async def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """解析PDF文档"""
        # 使用RAG-Anything的PDF解析器
        result = self.rag_parser.parse_pdf(file_path)
        
        # 提取文本内容
        content = self.content_extractor.extract_text(result)
        
        # 提取元数据
        metadata = self.content_extractor.extract_metadata(result)
        
        return {
            "content": content,
            "metadata": metadata,
            "structure": result.get("structure", {}),
            "pages": result.get("pages", [])
        }
    
    async def _parse_word(self, file_path: str) -> Dict[str, Any]:
        """解析Word文档"""
        result = self.rag_parser.parse_docx(file_path)
        content = self.content_extractor.extract_text(result)
        metadata = self.content_extractor.extract_metadata(result)
        
        return {
            "content": content,
            "metadata": metadata,
            "structure": result.get("structure", {}),
            "paragraphs": result.get("paragraphs", [])
        }
    
    async def _parse_txt(self, file_path: str) -> Dict[str, Any]:
        """解析文本文档"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return {
            "content": content,
            "metadata": {"file_size": os.path.getsize(file_path)},
            "structure": {},
            "lines": content.split('\n')
        }
    
    async def _parse_markdown(self, file_path: str) -> Dict[str, Any]:
        """解析Markdown文档"""
        with open(file_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
        
        # 转换为HTML
        html = markdown.markdown(md_content)
        
        # 提取纯文本
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.get_text()
        
        return {
            "content": content,
            "metadata": {"original_format": "markdown"},
            "structure": {"html": html},
            "markdown": md_content
        }
```

### 3.3 LightRAG向量化服务
```python
# backend/app/knowledge/services/vector_service.py
from typing import List, Dict, Any, Optional
from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete, gpt_4o_complete
from lightrag.utils import EmbeddingFunc
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np

class VectorService:
    def __init__(self, working_dir: str = "./ragindex"):
        # 初始化LightRAG
        self.rag = LightRAG(
            working_dir=working_dir,
            llm_model_func=gpt_4o_mini_complete,
            llm_model_max_async=4,
            llm_model_kwargs={"api_key": "your-api-key"},
            embedding_func=EmbeddingFunc(
                embedding_dim=384,
                max_token_size=5000,
            ),
        )
        
        # 初始化向量数据库
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
        
        # 初始化嵌入模型
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def add_document(self, document_id: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """添加文档到知识库"""
        try:
            # 使用LightRAG插入文档
            await self.rag.ainsert(content)
            
            # 文档切片
            chunks = self._chunk_document(content)
            
            # 生成向量并存储
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{i}"
                embedding = self.embedding_model.encode(chunk)
                
                self.collection.add(
                    embeddings=[embedding.tolist()],
                    documents=[chunk],
                    metadatas=[{
                        "document_id": document_id,
                        "chunk_index": i,
                        **(metadata or {})
                    }],
                    ids=[chunk_id]
                )
            
            return True
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    def _chunk_document(self, content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """智能文档切片"""
        # 按段落分割
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """语义相似度搜索"""
        try:
            # 使用LightRAG进行检索
            rag_result = await self.rag.aquery(
                query, 
                param=QueryParam(mode="hybrid", top_k=top_k)
            )
            
            # 使用向量数据库进行补充检索
            query_embedding = self.embedding_model.encode(query)
            vector_results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )
            
            # 合并结果
            results = []
            
            # 添加LightRAG结果
            if rag_result:
                results.append({
                    "content": rag_result,
                    "source": "lightrag",
                    "score": 1.0
                })
            
            # 添加向量检索结果
            for i, (doc, metadata, distance) in enumerate(zip(
                vector_results['documents'][0],
                vector_results['metadatas'][0],
                vector_results['distances'][0]
            )):
                results.append({
                    "content": doc,
                    "metadata": metadata,
                    "score": 1 - distance,
                    "source": "vector_db"
                })
            
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    async def update_document(self, document_id: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """更新文档"""
        try:
            # 删除旧的chunks
            self.collection.delete(where={"document_id": document_id})
            
            # 重新添加
            return await self.add_document(document_id, content, metadata)
        except Exception as e:
            print(f"Error updating document: {e}")
            return False
    
    async def delete_document(self, document_id: str) -> bool:
        """删除文档"""
        try:
            self.collection.delete(where={"document_id": document_id})
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
```

### 3.4 知识库管理服务
```python
# backend/app/knowledge/services/knowledge_service.py
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import os
import aiofiles
from ..models.document import Document, DocumentType, DocumentStatus
from .document_parser import DocumentParserService
from .vector_service import VectorService

class KnowledgeService:
    def __init__(self, upload_dir: str = "./uploads", vector_dir: str = "./ragindex"):
        self.upload_dir = upload_dir
        self.parser_service = DocumentParserService()
        self.vector_service = VectorService(vector_dir)
        self.documents: Dict[str, Document] = {}
        
        # 确保上传目录存在
        os.makedirs(upload_dir, exist_ok=True)
    
    async def upload_document(self, file_content: bytes, filename: str, doc_type: str, 
                            category: Optional[str] = None, tags: List[str] = None) -> str:
        """上传并处理文档"""
        # 生成文档ID
        doc_id = str(uuid.uuid4())
        
        # 保存文件
        file_path = os.path.join(self.upload_dir, f"{doc_id}_{filename}")
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # 创建文档记录
        document = Document(
            id=doc_id,
            title=filename,
            content="",
            doc_type=DocumentType(doc_type),
            status=DocumentStatus.UPLOADING,
            file_path=file_path,
            file_size=len(file_content),
            upload_time=datetime.now(),
            tags=tags or [],
            category=category
        )
        
        self.documents[doc_id] = document
        
        # 异步处理文档
        await self._process_document(doc_id)
        
        return doc_id
    
    async def _process_document(self, doc_id: str):
        """处理文档：解析 + 向量化"""
        try:
            document = self.documents[doc_id]
            document.status = DocumentStatus.PROCESSING
            
            # 1. 使用RAG-Anything解析文档
            parsed_result = await self.parser_service.parse_document(
                document.file_path, 
                document.doc_type.value
            )
            
            # 2. 更新文档内容
            document.content = parsed_result["content"]
            document.metadata = parsed_result["metadata"]
            
            # 3. 使用LightRAG向量化
            success = await self.vector_service.add_document(
                doc_id, 
                document.content,
                {
                    "title": document.title,
                    "category": document.category,
                    "tags": document.tags,
                    "doc_type": document.doc_type.value
                }
            )
            
            if success:
                document.status = DocumentStatus.PROCESSED
                document.process_time = datetime.now()
            else:
                document.status = DocumentStatus.FAILED
                
        except Exception as e:
            print(f"Document processing failed: {e}")
            self.documents[doc_id].status = DocumentStatus.FAILED
    
    async def search_knowledge(self, query: str, top_k: int = 5, 
                             category: Optional[str] = None) -> List[Dict[str, Any]]:
        """搜索知识库"""
        results = await self.vector_service.search_similar(query, top_k)
        
        # 如果指定了分类，进行过滤
        if category:
            results = [r for r in results if r.get("metadata", {}).get("category") == category]
        
        return results
    
    async def get_document(self, doc_id: str) -> Optional[Document]:
        """获取文档信息"""
        return self.documents.get(doc_id)
    
    async def list_documents(self, category: Optional[str] = None, 
                           status: Optional[DocumentStatus] = None) -> List[Document]:
        """列出文档"""
        docs = list(self.documents.values())
        
        if category:
            docs = [d for d in docs if d.category == category]
        
        if status:
            docs = [d for d in docs if d.status == status]
        
        return docs
    
    async def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        if doc_id not in self.documents:
            return False
        
        try:
            # 从向量库删除
            await self.vector_service.delete_document(doc_id)
            
            # 删除文件
            document = self.documents[doc_id]
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # 从内存删除
            del self.documents[doc_id]
            
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    async def update_document_metadata(self, doc_id: str, title: Optional[str] = None,
                                     category: Optional[str] = None, 
                                     tags: Optional[List[str]] = None) -> bool:
        """更新文档元数据"""
        if doc_id not in self.documents:
            return False
        
        document = self.documents[doc_id]
        
        if title:
            document.title = title
        if category:
            document.category = category
        if tags is not None:
            document.tags = tags
        
        # 更新向量库中的元数据
        await self.vector_service.update_document(
            doc_id,
            document.content,
            {
                "title": document.title,
                "category": document.category,
                "tags": document.tags,
                "doc_type": document.doc_type.value
            }
        )
        
        return True
```

### 3.5 知识库管理API
```python
# backend/app/knowledge/api/knowledge.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from ..services.knowledge_service import KnowledgeService
from ..models.document import Document, DocumentStatus

router = APIRouter()
knowledge_service = KnowledgeService()

class DocumentUploadResponse(BaseModel):
    document_id: str
    message: str

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    category: Optional[str] = None

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Query(..., description="Document type: pdf, word, txt, markdown"),
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tags")
):
    """上传文档到知识库"""
    try:
        # 读取文件内容
        content = await file.read()
        
        # 解析标签
        tag_list = tags.split(",") if tags else []
        
        # 上传文档
        doc_id = await knowledge_service.upload_document(
            content, file.filename, doc_type, category, tag_list
        )
        
        return DocumentUploadResponse(
            document_id=doc_id,
            message="Document uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=List[Document])
async def list_documents(
    category: Optional[str] = Query(None),
    status: Optional[DocumentStatus] = Query(None)
):
    """列出所有文档"""
    return await knowledge_service.list_documents(category, status)

@router.get("/documents/{doc_id}", response_model=Document)
async def get_document(doc_id: str):
    """获取文档详情"""
    document = await knowledge_service.get_document(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.put("/documents/{doc_id}")
async def update_document(doc_id: str, request: DocumentUpdateRequest):
    """更新文档元数据"""
    success = await knowledge_service.update_document_metadata(
        doc_id, request.title, request.category, request.tags
    )
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document updated successfully"}

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """删除文档"""
    success = await knowledge_service.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}

@router.post("/search")
async def search_knowledge(request: SearchRequest):
    """搜索知识库"""
    results = await knowledge_service.search_knowledge(
        request.query, request.top_k, request.category
    )
    return {"results": results}
```

## 4. 集成到现有系统

### 4.1 更新主应用
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat
from app.knowledge.api import knowledge  # 新增

app = FastAPI(title="智能客服API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api/knowledge")  # 新增

@app.get("/")
async def root():
    return {"message": "智能客服API服务正在运行"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 4.2 更新聊天服务集成知识库
```python
# backend/app/services/chat_service.py
import random
from datetime import datetime
from typing import Dict, Any
from app.knowledge.services.knowledge_service import KnowledgeService

class ChatService:
    def __init__(self):
        self.knowledge_service = KnowledgeService()
        # 保留原有的demo_responses作为fallback
        self.demo_responses = {
            # ... 原有的demo数据
        }
    
    async def get_response(self, message: str) -> Dict[str, Any]:
        """获取回复 - 优先使用知识库，fallback到demo"""
        try:
            # 1. 先尝试从知识库搜索
            knowledge_results = await self.knowledge_service.search_knowledge(
                message, top_k=3
            )
            
            if knowledge_results and knowledge_results[0].get("score", 0) > 0.7:
                # 知识库有高质量匹配
                best_result = knowledge_results[0]
                return {
                    "type": "text",
                    "content": {"text": best_result["content"]},
                    "timestamp": datetime.now(),
                    "source": "knowledge_base"
                }
            else:
                # 2. fallback到原有的demo逻辑
                return self.get_random_response()
                
        except Exception as e:
            print(f"Knowledge search error: {e}")
            # 出错时使用demo响应
            return self.get_random_response()
    
    def get_random_response(self) -> Dict[str, Any]:
        """原有的随机响应逻辑"""
        response_type = random.choices(
            ["text", "image", "card", "list"],
            weights=[30, 30, 20, 20]
        )[0]
        
        content = random.choice(self.demo_responses[response_type])
        
        return {
            "type": response_type,
            "content": content,
            "timestamp": datetime.now(),
            "source": "demo"
        }
```

## 5. 测试和验证

### 5.1 功能测试
```bash
# 测试文档上传
curl -X POST "http://localhost:8000/api/knowledge/documents/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test.pdf" \
     -F "doc_type=pdf" \
     -F "category=产品说明"

# 测试知识搜索
curl -X POST "http://localhost:8000/api/knowledge/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "产品功能", "top_k": 5}'

# 测试聊天集成
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "产品有什么功能"}'
```

### 5.2 性能测试
- 文档解析速度测试
- 向量检索响应时间测试
- 并发处理能力测试

## 6. 部署和监控

### 6.1 Docker配置更新
```dockerfile
# 更新Dockerfile添加知识库依赖
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# 创建必要目录
RUN mkdir -p uploads ragindex

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 监控指标
- 文档处理成功率
- 知识库检索准确率
- 系统响应时间
- 存储空间使用情况

这个知识库管理系统基于RAG-Anything和LightRAG，提供了完整的文档处理、向量化、检索和管理功能，可以无缝集成到现有的智能客服系统中。
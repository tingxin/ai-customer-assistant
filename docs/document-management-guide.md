# 知识库文档管理开发手册

## 1. 技术架构

### 1.1 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                    文档管理系统架构                          │
├─────────────────────────────────────────────────────────────┤
│  前端层 (Frontend)                                          │
│  ├── 文档上传组件                                           │
│  ├── 文档列表管理                                           │
│  ├── 文档预览组件                                           │
│  └── 批量操作界面                                           │
├─────────────────────────────────────────────────────────────┤
│  API层 (Backend API)                                       │
│  ├── 文档上传API                                           │
│  ├── 文档管理API                                           │
│  ├── 文档处理状态API                                       │
│  └── 文档检索API                                           │
├─────────────────────────────────────────────────────────────┤
│  业务逻辑层 (Services)                                      │
│  ├── 文档解析服务 (RAG-Anything)                           │
│  ├── 向量化服务 (LightRAG)                                 │
│  ├── 文档存储服务                                           │
│  └── 文档索引服务                                           │
├─────────────────────────────────────────────────────────────┤
│  数据存储层 (Storage)                                       │
│  ├── 文件存储 (本地/云存储)                                 │
│  ├── 元数据存储 (PostgreSQL)                               │
│  ├── 向量存储 (ChromaDB)                                   │
│  └── 索引存储 (LightRAG)                                   │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 数据流架构
```
文档上传 → 格式验证 → 文件存储 → 解析队列
    ↓
RAG-Anything解析 → 内容提取 → 文本清洗
    ↓
LightRAG向量化 → 向量存储 → 索引构建
    ↓
元数据存储 → 状态更新 → 通知完成
```

## 2. 核心模块功能

### 2.1 文档上传模块
**功能职责**:
- 支持多种文档格式 (PDF, Word, TXT, Markdown, HTML)
- 文件格式验证和大小限制
- 批量上传和进度跟踪
- 文档去重检测

**核心组件**:
- `DocumentUploadService`: 文档上传处理
- `FileValidator`: 文件格式和内容验证
- `DuplicateDetector`: 文档去重检测
- `UploadProgressTracker`: 上传进度管理

### 2.2 文档解析模块
**功能职责**:
- 基于RAG-Anything的多格式文档解析
- 文档结构识别和内容提取
- 元数据提取和标准化
- 解析错误处理和重试机制

**核心组件**:
- `DocumentParser`: RAG-Anything解析器封装
- `ContentExtractor`: 内容提取器
- `MetadataExtractor`: 元数据提取器
- `StructureAnalyzer`: 文档结构分析器

### 2.3 向量化处理模块
**功能职责**:
- 基于LightRAG的文档向量化
- 智能文档切片和分块
- 向量嵌入生成和存储
- 知识图谱构建

**核心组件**:
- `VectorService`: LightRAG向量化服务
- `DocumentChunker`: 智能文档切片器
- `EmbeddingGenerator`: 向量嵌入生成器
- `KnowledgeGraphBuilder`: 知识图谱构建器

### 2.4 文档管理模块
**功能职责**:
- 文档CRUD操作
- 文档分类和标签管理
- 文档版本控制
- 文档状态跟踪

**核心组件**:
- `DocumentService`: 文档管理服务
- `CategoryManager`: 分类管理器
- `TagManager`: 标签管理器
- `VersionController`: 版本控制器

### 2.5 检索服务模块
**功能职责**:
- 语义检索和关键词检索
- 混合检索策略
- 检索结果排序和过滤
- 检索性能优化

**核心组件**:
- `RetrievalService`: 检索服务
- `SemanticSearcher`: 语义检索器
- `KeywordSearcher`: 关键词检索器
- `HybridSearcher`: 混合检索器

## 3. 模块关系图

### 3.1 模块依赖关系
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   文档上传模块   │───▶│   文档解析模块   │───▶│  向量化处理模块  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   文档管理模块   │◀───│   检索服务模块   │◀───│   存储管理模块   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 3.2 数据模型关系
```
KnowledgeBase (知识库)
    │
    ├── 1:N ──▶ Document (文档)
    │              │
    │              ├── 1:N ──▶ DocumentChunk (文档块)
    │              │              │
    │              │              └── 1:1 ──▶ VectorEmbedding (向量)
    │              │
    │              ├── 1:N ──▶ DocumentTag (标签)
    │              │
    │              └── 1:N ──▶ DocumentVersion (版本)
    │
    └── 1:N ──▶ Category (分类)
```

## 4. 接口设计

### 4.1 文档管理API
```
POST   /api/knowledge/{kb_id}/documents/upload     # 上传文档
GET    /api/knowledge/{kb_id}/documents           # 获取文档列表
GET    /api/knowledge/{kb_id}/documents/{doc_id}  # 获取文档详情
PUT    /api/knowledge/{kb_id}/documents/{doc_id}  # 更新文档信息
DELETE /api/knowledge/{kb_id}/documents/{doc_id}  # 删除文档
POST   /api/knowledge/{kb_id}/documents/batch     # 批量操作
```

### 4.2 文档处理API
```
GET    /api/knowledge/{kb_id}/documents/{doc_id}/status    # 获取处理状态
POST   /api/knowledge/{kb_id}/documents/{doc_id}/reprocess # 重新处理
GET    /api/knowledge/{kb_id}/documents/{doc_id}/chunks    # 获取文档块
GET    /api/knowledge/{kb_id}/documents/{doc_id}/preview   # 文档预览
```

### 4.3 检索API
```
POST   /api/knowledge/{kb_id}/search              # 文档检索
POST   /api/knowledge/{kb_id}/search/semantic     # 语义检索
POST   /api/knowledge/{kb_id}/search/keyword      # 关键词检索
POST   /api/knowledge/{kb_id}/search/hybrid       # 混合检索
```

## 5. 状态管理

### 5.1 文档处理状态流
```
UPLOADED → PARSING → VECTORIZING → INDEXING → COMPLETED
    │         │          │           │           │
    └─────────┴──────────┴───────────┴───────────┴─→ FAILED
```

### 5.2 状态转换规则
- `UPLOADED`: 文档已上传，等待解析
- `PARSING`: 正在使用RAG-Anything解析
- `VECTORIZING`: 正在使用LightRAG向量化
- `INDEXING`: 正在构建索引
- `COMPLETED`: 处理完成，可用于检索
- `FAILED`: 处理失败，需要重新处理

## 6. 性能考虑

### 6.1 异步处理
- 文档上传后立即返回，后台异步处理
- 使用消息队列管理处理任务
- 支持处理进度查询和状态通知

### 6.2 缓存策略
- 文档解析结果缓存
- 向量检索结果缓存
- 热点文档内容缓存

### 6.3 扩展性设计
- 支持分布式文档处理
- 向量存储水平扩展
- 检索服务负载均衡

## 7. 安全考虑

### 7.1 文件安全
- 文件类型白名单验证
- 文件内容安全扫描
- 恶意文件检测和隔离

### 7.2 访问控制
- 基于知识库的文档访问权限
- 文档操作审计日志
- 敏感信息脱敏处理

## 8. 监控和日志

### 8.1 处理监控
- 文档处理成功率监控
- 处理时间性能监控
- 错误率和失败原因统计

### 8.2 检索监控
- 检索响应时间监控
- 检索准确率评估
- 用户查询模式分析
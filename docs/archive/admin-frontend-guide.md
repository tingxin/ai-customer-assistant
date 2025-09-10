# 管理员前端界面开发指南 - 知识库管理

## 1. 整体架构设计

### 1.1 用户角色分离
```
智能客服系统
├── 用户端 (ChatUI界面)
│   ├── 聊天对话
│   ├── 历史记录
│   └── 用户反馈
└── 管理端 (Admin Dashboard)
    ├── 知识库管理
    ├── 对话监控
    ├── 系统配置
    └── 数据统计
```

### 1.2 前端路由设计
```
/                    # 用户聊天界面 (现有ChatUI)
/admin               # 管理员登录页
/admin/dashboard     # 管理员仪表板
/admin/knowledge     # 知识库管理
/admin/documents     # 文档管理
/admin/chat-monitor  # 对话监控
/admin/settings      # 系统设置
```

## 2. 管理员前端实现

### 2.1 项目结构扩展
```
frontend/src/
├── components/
│   ├── chat/           # 用户聊天组件 (现有)
│   └── admin/          # 管理员组件 (新增)
│       ├── Layout/
│       ├── Knowledge/
│       ├── Documents/
│       ├── Dashboard/
│       └── Settings/
├── pages/
│   ├── Chat.tsx        # 用户聊天页面 (现有)
│   └── admin/          # 管理员页面 (新增)
│       ├── Login.tsx
│       ├── Dashboard.tsx
│       ├── Knowledge.tsx
│       └── Documents.tsx
├── services/
│   ├── chatService.ts  # 聊天服务 (现有)
│   └── adminService.ts # 管理员服务 (新增)
└── utils/
    ├── auth.ts         # 认证工具
    └── api.ts          # API工具
```

### 2.2 安装管理界面依赖
```bash
cd frontend

# 安装路由和UI组件库
npm install react-router-dom @types/react-router-dom
npm install antd @ant-design/icons
npm install axios
npm install react-query

# 安装文件上传组件
npm install react-dropzone
```

### 2.3 API服务层
```typescript
// frontend/src/services/adminService.ts
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

// 知识库管理API
export class AdminService {
  // 文档管理
  static async uploadDocument(file: File, docType: string, category?: string, tags?: string[]) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);
    if (category) formData.append('category', category);
    if (tags) formData.append('tags', tags.join(','));

    const response = await axios.post(`${API_BASE}/knowledge/documents/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }

  static async getDocuments(category?: string, status?: string) {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (status) params.append('status', status);
    
    const response = await axios.get(`${API_BASE}/knowledge/documents?${params}`);
    return response.data;
  }

  static async getDocument(docId: string) {
    const response = await axios.get(`${API_BASE}/knowledge/documents/${docId}`);
    return response.data;
  }

  static async updateDocument(docId: string, data: any) {
    const response = await axios.put(`${API_BASE}/knowledge/documents/${docId}`, data);
    return response.data;
  }

  static async deleteDocument(docId: string) {
    const response = await axios.delete(`${API_BASE}/knowledge/documents/${docId}`);
    return response.data;
  }

  // 知识库搜索测试
  static async searchKnowledge(query: string, topK: number = 5, category?: string) {
    const response = await axios.post(`${API_BASE}/knowledge/search`, {
      query,
      top_k: topK,
      category
    });
    return response.data;
  }

  // 知识库管理
  static async createKnowledgeBase(name: string, description?: string) {
    const response = await axios.post(`${API_BASE}/knowledge/bases`, {
      name,
      description
    });
    return response.data;
  }

  static async getKnowledgeBases() {
    const response = await axios.get(`${API_BASE}/knowledge/bases`);
    return response.data;
  }

  static async deleteKnowledgeBase(baseId: string) {
    const response = await axios.delete(`${API_BASE}/knowledge/bases/${baseId}`);
    return response.data;
  }
}
```

### 2.4 路由配置
```typescript
// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ChatPage from './pages/Chat';
import AdminLogin from './pages/admin/Login';
import AdminDashboard from './pages/admin/Dashboard';
import KnowledgeManagement from './pages/admin/Knowledge';
import DocumentManagement from './pages/admin/Documents';
import { AuthProvider, useAuth } from './utils/auth';

// 路由保护组件
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/admin" />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* 用户端路由 */}
          <Route path="/" element={<ChatPage />} />
          
          {/* 管理员端路由 */}
          <Route path="/admin" element={<AdminLogin />} />
          <Route path="/admin/dashboard" element={
            <ProtectedRoute>
              <AdminDashboard />
            </ProtectedRoute>
          } />
          <Route path="/admin/knowledge" element={
            <ProtectedRoute>
              <KnowledgeManagement />
            </ProtectedRoute>
          } />
          <Route path="/admin/documents" element={
            <ProtectedRoute>
              <DocumentManagement />
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

### 2.5 知识库管理页面
```typescript
// frontend/src/pages/admin/Knowledge.tsx
import React, { useState, useEffect } from 'react';
import { 
  Layout, Card, Button, Table, Modal, Form, Input, Select, 
  Upload, message, Tag, Space, Popconfirm 
} from 'antd';
import { 
  PlusOutlined, UploadOutlined, DeleteOutlined, 
  EditOutlined, SearchOutlined 
} from '@ant-design/icons';
import { AdminService } from '../../services/adminService';

const { Header, Content } = Layout;
const { Option } = Select;

interface KnowledgeBase {
  id: string;
  name: string;
  description: string;
  document_count: number;
  created_at: string;
}

const KnowledgeManagement: React.FC = () => {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [loading, setLoading] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadKnowledgeBases();
  }, []);

  const loadKnowledgeBases = async () => {
    setLoading(true);
    try {
      const data = await AdminService.getKnowledgeBases();
      setKnowledgeBases(data);
    } catch (error) {
      message.error('加载知识库失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKnowledgeBase = async (values: any) => {
    try {
      await AdminService.createKnowledgeBase(values.name, values.description);
      message.success('知识库创建成功');
      setCreateModalVisible(false);
      form.resetFields();
      loadKnowledgeBases();
    } catch (error) {
      message.error('创建知识库失败');
    }
  };

  const handleDeleteKnowledgeBase = async (id: string) => {
    try {
      await AdminService.deleteKnowledgeBase(id);
      message.success('知识库删除成功');
      loadKnowledgeBases();
    } catch (error) {
      message.error('删除知识库失败');
    }
  };

  const columns = [
    {
      title: '知识库名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '文档数量',
      dataIndex: 'document_count',
      key: 'document_count',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (record: KnowledgeBase) => (
        <Space>
          <Button 
            type="primary" 
            icon={<EditOutlined />}
            onClick={() => {/* 跳转到文档管理 */}}
          >
            管理文档
          </Button>
          <Popconfirm
            title="确定要删除这个知识库吗？"
            onConfirm={() => handleDeleteKnowledgeBase(record.id)}
          >
            <Button danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px' }}>
        <h2>知识库管理</h2>
      </Header>
      <Content style={{ margin: '24px' }}>
        <Card>
          <div style={{ marginBottom: 16 }}>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              创建知识库
            </Button>
          </div>
          
          <Table
            columns={columns}
            dataSource={knowledgeBases}
            loading={loading}
            rowKey="id"
          />
        </Card>

        <Modal
          title="创建知识库"
          open={createModalVisible}
          onCancel={() => setCreateModalVisible(false)}
          onOk={() => form.submit()}
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={handleCreateKnowledgeBase}
          >
            <Form.Item
              name="name"
              label="知识库名称"
              rules={[{ required: true, message: '请输入知识库名称' }]}
            >
              <Input placeholder="输入知识库名称" />
            </Form.Item>
            <Form.Item
              name="description"
              label="描述"
            >
              <Input.TextArea placeholder="输入知识库描述" />
            </Form.Item>
          </Form>
        </Modal>
      </Content>
    </Layout>
  );
};

export default KnowledgeManagement;
```

### 2.6 文档管理页面
```typescript
// frontend/src/pages/admin/Documents.tsx
import React, { useState, useEffect } from 'react';
import { 
  Layout, Card, Button, Table, Modal, Form, Input, Select, 
  Upload, message, Tag, Space, Popconfirm, Progress 
} from 'antd';
import { 
  UploadOutlined, DeleteOutlined, EditOutlined, 
  EyeOutlined, SearchOutlined 
} from '@ant-design/icons';
import { useDropzone } from 'react-dropzone';
import { AdminService } from '../../services/adminService';

const { Header, Content } = Layout;
const { Option } = Select;

interface Document {
  id: string;
  title: string;
  doc_type: string;
  status: string;
  file_size: number;
  upload_time: string;
  tags: string[];
  category: string;
}

const DocumentManagement: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [searchModalVisible, setSearchModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await AdminService.getDocuments();
      setDocuments(data);
    } catch (error) {
      message.error('加载文档失败');
    } finally {
      setLoading(false);
    }
  };

  // 文件拖拽上传
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md']
    },
    onDrop: (acceptedFiles) => {
      handleFileUpload(acceptedFiles[0]);
    }
  });

  const handleFileUpload = async (file: File) => {
    const formData = form.getFieldsValue();
    try {
      const docType = getDocTypeFromFile(file);
      await AdminService.uploadDocument(
        file, 
        docType, 
        formData.category, 
        formData.tags?.split(',')
      );
      message.success('文档上传成功');
      setUploadModalVisible(false);
      form.resetFields();
      loadDocuments();
    } catch (error) {
      message.error('文档上传失败');
    }
  };

  const getDocTypeFromFile = (file: File): string => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf': return 'pdf';
      case 'doc':
      case 'docx': return 'word';
      case 'txt': return 'txt';
      case 'md': return 'markdown';
      default: return 'txt';
    }
  };

  const handleDeleteDocument = async (id: string) => {
    try {
      await AdminService.deleteDocument(id);
      message.success('文档删除成功');
      loadDocuments();
    } catch (error) {
      message.error('删除文档失败');
    }
  };

  const handleSearchKnowledge = async (values: any) => {
    try {
      const results = await AdminService.searchKnowledge(
        values.query, 
        values.topK || 5, 
        values.category
      );
      
      Modal.info({
        title: '搜索结果',
        width: 800,
        content: (
          <div>
            {results.results.map((result: any, index: number) => (
              <Card key={index} size="small" style={{ marginBottom: 8 }}>
                <p><strong>相关度:</strong> {(result.score * 100).toFixed(1)}%</p>
                <p><strong>内容:</strong> {result.content.substring(0, 200)}...</p>
                {result.metadata && (
                  <p><strong>来源:</strong> {result.metadata.title}</p>
                )}
              </Card>
            ))}
          </div>
        ),
      });
    } catch (error) {
      message.error('搜索失败');
    }
  };

  const columns = [
    {
      title: '文档名称',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '类型',
      dataIndex: 'doc_type',
      key: 'doc_type',
      render: (type: string) => <Tag color="blue">{type.toUpperCase()}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors = {
          'processed': 'green',
          'processing': 'orange',
          'failed': 'red',
          'uploading': 'blue'
        };
        return <Tag color={colors[status as keyof typeof colors]}>{status}</Tag>;
      },
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      render: (tags: string[]) => (
        <>
          {tags.map(tag => <Tag key={tag}>{tag}</Tag>)}
        </>
      ),
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size: number) => `${(size / 1024).toFixed(1)} KB`,
    },
    {
      title: '上传时间',
      dataIndex: 'upload_time',
      key: 'upload_time',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (record: Document) => (
        <Space>
          <Button icon={<EyeOutlined />} size="small">
            查看
          </Button>
          <Button icon={<EditOutlined />} size="small">
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个文档吗？"
            onConfirm={() => handleDeleteDocument(record.id)}
          >
            <Button danger icon={<DeleteOutlined />} size="small">
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px' }}>
        <h2>文档管理</h2>
      </Header>
      <Content style={{ margin: '24px' }}>
        <Card>
          <div style={{ marginBottom: 16 }}>
            <Space>
              <Button 
                type="primary" 
                icon={<UploadOutlined />}
                onClick={() => setUploadModalVisible(true)}
              >
                上传文档
              </Button>
              <Button 
                icon={<SearchOutlined />}
                onClick={() => setSearchModalVisible(true)}
              >
                测试搜索
              </Button>
            </Space>
          </div>
          
          <Table
            columns={columns}
            dataSource={documents}
            loading={loading}
            rowKey="id"
          />
        </Card>

        {/* 上传文档模态框 */}
        <Modal
          title="上传文档"
          open={uploadModalVisible}
          onCancel={() => setUploadModalVisible(false)}
          footer={null}
        >
          <Form form={form} layout="vertical">
            <Form.Item name="category" label="分类">
              <Select placeholder="选择分类">
                <Option value="产品说明">产品说明</Option>
                <Option value="技术文档">技术文档</Option>
                <Option value="FAQ">FAQ</Option>
                <Option value="其他">其他</Option>
              </Select>
            </Form.Item>
            <Form.Item name="tags" label="标签">
              <Input placeholder="输入标签，用逗号分隔" />
            </Form.Item>
          </Form>
          
          <div 
            {...getRootProps()} 
            style={{
              border: '2px dashed #d9d9d9',
              borderRadius: '6px',
              padding: '40px',
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: isDragActive ? '#f0f0f0' : '#fafafa'
            }}
          >
            <input {...getInputProps()} />
            <UploadOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
            <p>拖拽文件到此处，或点击选择文件</p>
            <p>支持 PDF, Word, TXT, Markdown 格式</p>
          </div>
        </Modal>

        {/* 搜索测试模态框 */}
        <Modal
          title="测试知识库搜索"
          open={searchModalVisible}
          onCancel={() => setSearchModalVisible(false)}
          onOk={() => searchForm.submit()}
        >
          <Form
            form={searchForm}
            layout="vertical"
            onFinish={handleSearchKnowledge}
          >
            <Form.Item
              name="query"
              label="搜索问题"
              rules={[{ required: true, message: '请输入搜索问题' }]}
            >
              <Input placeholder="输入要搜索的问题" />
            </Form.Item>
            <Form.Item name="category" label="限定分类">
              <Select placeholder="选择分类（可选）" allowClear>
                <Option value="产品说明">产品说明</Option>
                <Option value="技术文档">技术文档</Option>
                <Option value="FAQ">FAQ</Option>
              </Select>
            </Form.Item>
            <Form.Item name="topK" label="返回结果数量">
              <Select defaultValue={5}>
                <Option value={3}>3</Option>
                <Option value={5}>5</Option>
                <Option value={10}>10</Option>
              </Select>
            </Form.Item>
          </Form>
        </Modal>
      </Content>
    </Layout>
  );
};

export default DocumentManagement;
```

## 3. 后端API扩展

### 3.1 知识库管理API
```python
# backend/app/knowledge/api/knowledge_base.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()

class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeBase(BaseModel):
    id: str
    name: str
    description: Optional[str]
    document_count: int
    created_at: datetime

# 模拟数据存储
knowledge_bases = {}

@router.post("/bases", response_model=KnowledgeBase)
async def create_knowledge_base(request: KnowledgeBaseCreate):
    """创建知识库"""
    kb_id = str(uuid.uuid4())
    kb = KnowledgeBase(
        id=kb_id,
        name=request.name,
        description=request.description,
        document_count=0,
        created_at=datetime.now()
    )
    knowledge_bases[kb_id] = kb
    return kb

@router.get("/bases", response_model=List[KnowledgeBase])
async def list_knowledge_bases():
    """列出所有知识库"""
    return list(knowledge_bases.values())

@router.delete("/bases/{kb_id}")
async def delete_knowledge_base(kb_id: str):
    """删除知识库"""
    if kb_id not in knowledge_bases:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    del knowledge_bases[kb_id]
    return {"message": "Knowledge base deleted successfully"}
```

### 3.2 更新主应用路由
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat
from app.knowledge.api import knowledge, knowledge_base

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
app.include_router(knowledge.router, prefix="/api/knowledge")
app.include_router(knowledge_base.router, prefix="/api/knowledge")  # 新增

@app.get("/")
async def root():
    return {"message": "智能客服API服务正在运行"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## 4. 部署和使用

### 4.1 启动完整系统
```bash
# 启动后端
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端
cd frontend
npm start
```

### 4.2 访问地址
- 用户聊天界面：http://localhost:3000/
- 管理员界面：http://localhost:3000/admin

### 4.3 使用流程
1. 管理员登录后台
2. 创建知识库
3. 上传文档到知识库
4. 测试知识库搜索效果
5. 用户在前端聊天，自动调用知识库

这样就实现了完整的前后端集成，管理员可以通过Web界面管理知识库，用户通过ChatUI进行智能对话。
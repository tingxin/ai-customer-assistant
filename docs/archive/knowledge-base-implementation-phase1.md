# 知识库管理实施指南 - 第一阶段：知识库CRUD

## 1. 后端实现

### 1.1 知识库数据模型
```python
# backend/app/knowledge/models/knowledge_base.py
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
    status: KnowledgeBaseStatus = KnowledgeBaseStatus.ACTIVE
    document_count: int = 0
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[KnowledgeBaseStatus] = None
```

### 1.2 知识库服务层
```python
# backend/app/knowledge/services/knowledge_base_service.py
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
    
    async def create_knowledge_base(self, request: KnowledgeBaseCreate, created_by: Optional[str] = None) -> KnowledgeBase:
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
            status=KnowledgeBaseStatus.ACTIVE,
            document_count=0,
            created_at=now,
            updated_at=now,
            created_by=created_by
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
    
    async def get_knowledge_base_stats(self, kb_id: str) -> Optional[Dict[str, Any]]:
        """获取知识库统计信息"""
        if kb_id not in self.knowledge_bases:
            return None
        
        kb = self.knowledge_bases[kb_id]
        kb_dir = os.path.join(self.base_dir, kb_id)
        
        # 计算目录大小
        total_size = 0
        if os.path.exists(kb_dir):
            for dirpath, dirnames, filenames in os.walk(kb_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
        
        return {
            "id": kb.id,
            "name": kb.name,
            "document_count": kb.document_count,
            "total_size": total_size,
            "status": kb.status,
            "created_at": kb.created_at,
            "updated_at": kb.updated_at
        }
```

### 1.3 知识库API
```python
# backend/app/knowledge/api/knowledge_base.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..services.knowledge_base_service import KnowledgeBaseService
from ..models.knowledge_base import KnowledgeBase, KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseStatus

router = APIRouter()
kb_service = KnowledgeBaseService()

@router.post("/bases", response_model=KnowledgeBase)
async def create_knowledge_base(request: KnowledgeBaseCreate):
    """创建知识库"""
    try:
        return await kb_service.create_knowledge_base(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bases", response_model=List[KnowledgeBase])
async def list_knowledge_bases(
    status: Optional[KnowledgeBaseStatus] = Query(None, description="过滤状态")
):
    """列出知识库"""
    return await kb_service.list_knowledge_bases(status)

@router.get("/bases/{kb_id}", response_model=KnowledgeBase)
async def get_knowledge_base(kb_id: str):
    """获取知识库详情"""
    kb = await kb_service.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return kb

@router.put("/bases/{kb_id}", response_model=KnowledgeBase)
async def update_knowledge_base(kb_id: str, request: KnowledgeBaseUpdate):
    """更新知识库"""
    kb = await kb_service.update_knowledge_base(kb_id, request)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return kb

@router.delete("/bases/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    hard_delete: bool = Query(False, description="是否硬删除")
):
    """删除知识库"""
    success = await kb_service.delete_knowledge_base(kb_id, not hard_delete)
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return {"message": "Knowledge base deleted successfully"}

@router.get("/bases/{kb_id}/stats")
async def get_knowledge_base_stats(kb_id: str):
    """获取知识库统计信息"""
    stats = await kb_service.get_knowledge_base_stats(kb_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return stats
```

## 2. 前端实现

### 2.1 知识库服务
```typescript
// frontend/src/services/knowledgeBaseService.ts
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/knowledge';

export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'inactive' | 'deleted';
  document_count: number;
  created_at: string;
  updated_at: string;
  created_by?: string;
}

export interface CreateKnowledgeBaseRequest {
  name: string;
  description?: string;
}

export interface UpdateKnowledgeBaseRequest {
  name?: string;
  description?: string;
  status?: 'active' | 'inactive' | 'deleted';
}

export class KnowledgeBaseService {
  static async createKnowledgeBase(request: CreateKnowledgeBaseRequest): Promise<KnowledgeBase> {
    const response = await axios.post(`${API_BASE}/bases`, request);
    return response.data;
  }

  static async getKnowledgeBases(status?: string): Promise<KnowledgeBase[]> {
    const params = status ? { status } : {};
    const response = await axios.get(`${API_BASE}/bases`, { params });
    return response.data;
  }

  static async getKnowledgeBase(id: string): Promise<KnowledgeBase> {
    const response = await axios.get(`${API_BASE}/bases/${id}`);
    return response.data;
  }

  static async updateKnowledgeBase(id: string, request: UpdateKnowledgeBaseRequest): Promise<KnowledgeBase> {
    const response = await axios.put(`${API_BASE}/bases/${id}`, request);
    return response.data;
  }

  static async deleteKnowledgeBase(id: string, hardDelete: boolean = false): Promise<void> {
    await axios.delete(`${API_BASE}/bases/${id}`, {
      params: { hard_delete: hardDelete }
    });
  }

  static async getKnowledgeBaseStats(id: string): Promise<any> {
    const response = await axios.get(`${API_BASE}/bases/${id}/stats`);
    return response.data;
  }
}
```

### 2.2 知识库管理页面
```typescript
// frontend/src/pages/admin/KnowledgeBase.tsx
import React, { useState, useEffect } from 'react';
import {
  Layout, Card, Button, Table, Modal, Form, Input, Select,
  message, Tag, Space, Popconfirm, Tooltip, Typography
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined,
  InfoCircleOutlined, FolderOutlined
} from '@ant-design/icons';
import { KnowledgeBaseService, KnowledgeBase, CreateKnowledgeBaseRequest } from '../../services/knowledgeBaseService';

const { Header, Content } = Layout;
const { TextArea } = Input;
const { Title } = Typography;

const KnowledgeBaseManagement: React.FC = () => {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [loading, setLoading] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [currentKB, setCurrentKB] = useState<KnowledgeBase | null>(null);
  const [createForm] = Form.useForm();
  const [editForm] = Form.useForm();

  useEffect(() => {
    loadKnowledgeBases();
  }, []);

  const loadKnowledgeBases = async () => {
    setLoading(true);
    try {
      const data = await KnowledgeBaseService.getKnowledgeBases();
      setKnowledgeBases(data);
    } catch (error) {
      message.error('加载知识库失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKnowledgeBase = async (values: CreateKnowledgeBaseRequest) => {
    try {
      await KnowledgeBaseService.createKnowledgeBase(values);
      message.success('知识库创建成功');
      setCreateModalVisible(false);
      createForm.resetFields();
      loadKnowledgeBases();
    } catch (error) {
      message.error('创建知识库失败');
    }
  };

  const handleEditKnowledgeBase = async (values: any) => {
    if (!currentKB) return;
    
    try {
      await KnowledgeBaseService.updateKnowledgeBase(currentKB.id, values);
      message.success('知识库更新成功');
      setEditModalVisible(false);
      setCurrentKB(null);
      editForm.resetFields();
      loadKnowledgeBases();
    } catch (error) {
      message.error('更新知识库失败');
    }
  };

  const handleDeleteKnowledgeBase = async (id: string, hardDelete: boolean = false) => {
    try {
      await KnowledgeBaseService.deleteKnowledgeBase(id, hardDelete);
      message.success(hardDelete ? '知识库已永久删除' : '知识库已删除');
      loadKnowledgeBases();
    } catch (error) {
      message.error('删除知识库失败');
    }
  };

  const showEditModal = (kb: KnowledgeBase) => {
    setCurrentKB(kb);
    editForm.setFieldsValue({
      name: kb.name,
      description: kb.description,
      status: kb.status
    });
    setEditModalVisible(true);
  };

  const columns = [
    {
      title: '知识库名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: KnowledgeBase) => (
        <Space>
          <FolderOutlined />
          <strong>{name}</strong>
        </Space>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (desc: string) => desc || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors = {
          'active': 'green',
          'inactive': 'orange',
          'deleted': 'red'
        };
        const labels = {
          'active': '活跃',
          'inactive': '未激活',
          'deleted': '已删除'
        };
        return <Tag color={colors[status as keyof typeof colors]}>{labels[status as keyof typeof labels]}</Tag>;
      },
    },
    {
      title: '文档数量',
      dataIndex: 'document_count',
      key: 'document_count',
      render: (count: number) => count || 0,
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
          <Tooltip title="编辑知识库">
            <Button 
              icon={<EditOutlined />} 
              size="small"
              onClick={() => showEditModal(record)}
            />
          </Tooltip>
          <Tooltip title="查看统计">
            <Button 
              icon={<InfoCircleOutlined />} 
              size="small"
              onClick={() => {/* 显示统计信息 */}}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个知识库吗？"
            description="删除后可以在回收站中恢复"
            onConfirm={() => handleDeleteKnowledgeBase(record.id, false)}
          >
            <Button danger icon={<DeleteOutlined />} size="small" />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header style={{ background: '#fff', padding: '0 24px', boxShadow: '0 1px 4px rgba(0,21,41,.08)' }}>
        <Title level={3} style={{ margin: 0, lineHeight: '64px' }}>知识库管理</Title>
      </Header>
      <Content style={{ margin: '24px' }}>
        <Card>
          <div style={{ marginBottom: 16 }}>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
              size="large"
            >
              创建知识库
            </Button>
          </div>
          
          <Table
            columns={columns}
            dataSource={knowledgeBases}
            loading={loading}
            rowKey="id"
            pagination={{
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 个知识库`,
            }}
          />
        </Card>

        {/* 创建知识库模态框 */}
        <Modal
          title="创建知识库"
          open={createModalVisible}
          onCancel={() => setCreateModalVisible(false)}
          onOk={() => createForm.submit()}
          width={600}
        >
          <Form
            form={createForm}
            layout="vertical"
            onFinish={handleCreateKnowledgeBase}
          >
            <Form.Item
              name="name"
              label="知识库名称"
              rules={[
                { required: true, message: '请输入知识库名称' },
                { min: 2, max: 50, message: '名称长度应在2-50字符之间' }
              ]}
            >
              <Input placeholder="输入知识库名称" />
            </Form.Item>
            <Form.Item
              name="description"
              label="描述"
              rules={[
                { max: 200, message: '描述不能超过200字符' }
              ]}
            >
              <TextArea 
                placeholder="输入知识库描述（可选）" 
                rows={4}
                showCount
                maxLength={200}
              />
            </Form.Item>
          </Form>
        </Modal>

        {/* 编辑知识库模态框 */}
        <Modal
          title="编辑知识库"
          open={editModalVisible}
          onCancel={() => setEditModalVisible(false)}
          onOk={() => editForm.submit()}
          width={600}
        >
          <Form
            form={editForm}
            layout="vertical"
            onFinish={handleEditKnowledgeBase}
          >
            <Form.Item
              name="name"
              label="知识库名称"
              rules={[
                { required: true, message: '请输入知识库名称' },
                { min: 2, max: 50, message: '名称长度应在2-50字符之间' }
              ]}
            >
              <Input placeholder="输入知识库名称" />
            </Form.Item>
            <Form.Item
              name="description"
              label="描述"
              rules={[
                { max: 200, message: '描述不能超过200字符' }
              ]}
            >
              <TextArea 
                placeholder="输入知识库描述（可选）" 
                rows={4}
                showCount
                maxLength={200}
              />
            </Form.Item>
            <Form.Item
              name="status"
              label="状态"
            >
              <Select>
                <Select.Option value="active">活跃</Select.Option>
                <Select.Option value="inactive">未激活</Select.Option>
              </Select>
            </Form.Item>
          </Form>
        </Modal>
      </Content>
    </Layout>
  );
};

export default KnowledgeBaseManagement;
```

## 3. 集成到主应用

### 3.1 更新后端路由
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat
from app.knowledge.api import knowledge_base

app = FastAPI(title="智能客服API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(knowledge_base.router, prefix="/api/knowledge")

@app.get("/")
async def root():
    return {"message": "智能客服API服务正在运行"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 3.2 更新前端路由
```typescript
// frontend/src/App.tsx
import KnowledgeBaseManagement from './pages/admin/KnowledgeBase';

// 在Routes中添加
<Route path="/admin/knowledge-bases" element={
  <ProtectedRoute>
    <KnowledgeBaseManagement />
  </ProtectedRoute>
} />
```

## 4. 测试验证

### 4.1 API测试
```bash
# 创建知识库
curl -X POST "http://localhost:8000/api/knowledge/bases" \
     -H "Content-Type: application/json" \
     -d '{"name": "产品知识库", "description": "产品相关文档和FAQ"}'

# 获取知识库列表
curl "http://localhost:8000/api/knowledge/bases"

# 更新知识库
curl -X PUT "http://localhost:8000/api/knowledge/bases/{kb_id}" \
     -H "Content-Type: application/json" \
     -d '{"name": "更新后的名称"}'

# 删除知识库
curl -X DELETE "http://localhost:8000/api/knowledge/bases/{kb_id}"
```

### 4.2 前端测试
1. 启动前后端服务
2. 访问 http://localhost:3000/admin/knowledge-bases
3. 测试创建、编辑、删除知识库功能

这个第一阶段实现了完整的知识库CRUD功能，为后续的文档管理奠定了基础。
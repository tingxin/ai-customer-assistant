# 知识库管理实施指南 - 第一步：更新列表界面和数据模型

## 0. 技术选型

### 0.1 前端UI框架：Ant Design
**选择理由：**
- 企业级管理界面的标准选择
- 组件丰富完整（Table、Form、Layout、Upload等）
- TypeScript支持优秀
- 中文文档完善，适合国内开发
- GitHub Stars: 90k+，社区活跃

### 0.2 依赖安装
```bash
cd frontend

# 安装Ant Design
npm install antd @ant-design/icons

# 安装路由
npm install react-router-dom @types/react-router-dom

# 安装HTTP客户端
npm install axios

# 安装状态管理（可选）
npm install @tanstack/react-query
```

## 1. 实施目标

### 1.1 UI流程设计
```
知识库列表页面
├── "新建知识库"按钮 → 跳转到空的知识库编辑界面
├── 表格显示：名称、描述、创建时间、更新时间、owner、文档数量
├── 点击行选中 → 表头显示"编辑"按钮
└── 点击"编辑" → 跳转到知识库编辑界面（带数据）

知识库编辑界面（统一组件）
├── 新建模式：所有字段为空，文档列表为空
├── 编辑模式：显示现有数据和文档列表
├── 知识库信息编辑区（标题、描述、owner）
├── 文档列表表格（文档名、tokens、summary、状态）
├── "新增文档"按钮
└── 文档删除功能
```

### 1.2 本步骤实现范围
- 更新后端数据模型（添加owner字段）
- 更新前端知识库列表界面
- 添加表格行选中功能
- 实现路由跳转到编辑界面
- 创建知识库编辑界面框架

## 2. 后端实现

### 2.1 更新知识库数据模型
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
```

### 2.2 更新知识库服务
```python
# backend/app/knowledge/services/knowledge_base_service.py
# 在create_knowledge_base方法中添加owner处理
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
        owner=request.owner,  # 新增
        status=KnowledgeBaseStatus.ACTIVE,
        document_count=0,
        created_at=now,
        updated_at=now
    )
    
    self.knowledge_bases[kb_id] = knowledge_base
    return knowledge_base

# 在update_knowledge_base方法中添加owner更新
async def update_knowledge_base(self, kb_id: str, request: KnowledgeBaseUpdate) -> Optional[KnowledgeBase]:
    """更新知识库"""
    if kb_id not in self.knowledge_bases:
        return None
    
    kb = self.knowledge_bases[kb_id]
    
    if request.name is not None:
        kb.name = request.name
    if request.description is not None:
        kb.description = request.description
    if request.owner is not None:  # 新增
        kb.owner = request.owner
    if request.status is not None:
        kb.status = request.status
    
    kb.updated_at = datetime.now()
    return kb
```

### 2.3 更新API接口
```python
# backend/app/knowledge/api/knowledge_base.py
# API接口保持不变，因为Pydantic模型会自动处理新字段
```

## 3. 前端实现

### 3.1 导入Ant Design样式
```typescript
// frontend/src/App.tsx 或 frontend/src/index.tsx
import 'antd/dist/reset.css'; // Ant Design 5.x 样式
// 或者使用 4.x 版本：
// import 'antd/dist/antd.css';
```

### 3.2 更新知识库服务
```typescript
// frontend/src/services/knowledgeBaseService.ts
export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  owner: string;  // 新增字段
  status: 'active' | 'inactive' | 'deleted';
  document_count: number;
  created_at: string;
  updated_at: string;
}

export interface CreateKnowledgeBaseRequest {
  name: string;
  description?: string;
  owner: string;  // 新增字段
}

export interface UpdateKnowledgeBaseRequest {
  name?: string;
  description?: string;
  owner?: string;  // 新增字段
  status?: 'active' | 'inactive' | 'deleted';
}
```

### 3.3 更新知识库列表页面
```typescript
// frontend/src/pages/admin/KnowledgeBaseList.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Layout, Card, Button, Table, message, Tag, Space, Typography
} from 'antd';
import { PlusOutlined, EditOutlined, FolderOutlined } from '@ant-design/icons';
import { KnowledgeBaseService, KnowledgeBase } from '../../services/knowledgeBaseService';

const { Header, Content } = Layout;
const { Title } = Typography;

const KnowledgeBaseList: React.FC = () => {
  const navigate = useNavigate();
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);

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

  const handleCreateNew = () => {
    navigate('/admin/knowledge-base/new');
  };

  const handleEdit = () => {
    if (selectedRowKeys.length === 1) {
      navigate(`/admin/knowledge-base/${selectedRowKeys[0]}`);
    }
  };

  const columns = [
    {
      title: '知识库名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => (
        <Space>
          <FolderOutlined />
          <strong>{name}</strong>
        </Space>
      ),
    },
    {
      title: '详细描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (desc: string) => desc || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Owner',
      dataIndex: 'owner',
      key: 'owner',
    },
    {
      title: '文档数量',
      dataIndex: 'document_count',
      key: 'document_count',
      render: (count: number) => count || 0,
    },
  ];

  const rowSelection = {
    type: 'radio' as const,
    selectedRowKeys,
    onChange: (selectedKeys: React.Key[]) => {
      setSelectedRowKeys(selectedKeys as string[]);
    },
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header style={{ 
        background: '#fff', 
        padding: '0 24px', 
        boxShadow: '0 1px 4px rgba(0,21,41,.08)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Title level={3} style={{ margin: 0 }}>知识库管理</Title>
        {selectedRowKeys.length === 1 && (
          <Button 
            type="primary" 
            icon={<EditOutlined />}
            onClick={handleEdit}
          >
            编辑知识库
          </Button>
        )}
      </Header>
      <Content style={{ margin: '24px' }}>
        <Card>
          <div style={{ marginBottom: 16 }}>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={handleCreateNew}
              size="large"
            >
              新建知识库
            </Button>
          </div>
          
          <Table
            columns={columns}
            dataSource={knowledgeBases}
            loading={loading}
            rowKey="id"
            rowSelection={rowSelection}
            pagination={{
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 个知识库`,
            }}
          />
        </Card>
      </Content>
    </Layout>
  );
};

export default KnowledgeBaseList;
```

### 3.4 创建知识库编辑页面框架
```typescript
// frontend/src/pages/admin/KnowledgeBaseEdit.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Layout, Card, Button, Form, Input, message, Space, Table, Typography, Divider
} from 'antd';
import { ArrowLeftOutlined, SaveOutlined, PlusOutlined } from '@ant-design/icons';
import { KnowledgeBaseService, KnowledgeBase } from '../../services/knowledgeBaseService';

const { Header, Content } = Layout;
const { TextArea } = Input;
const { Title } = Typography;

const KnowledgeBaseEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(null);
  const [documents, setDocuments] = useState<any[]>([]); // 后续实现文档类型

  const isNewMode = id === 'new';

  useEffect(() => {
    if (!isNewMode && id) {
      loadKnowledgeBase(id);
    } else {
      // 新建模式，设置默认值
      form.setFieldsValue({
        owner: 'admin' // 临时默认值
      });
    }
  }, [id, isNewMode]);

  const loadKnowledgeBase = async (kbId: string) => {
    setLoading(true);
    try {
      const data = await KnowledgeBaseService.getKnowledgeBase(kbId);
      setKnowledgeBase(data);
      form.setFieldsValue({
        name: data.name,
        description: data.description,
        owner: data.owner
      });
      // TODO: 加载文档列表
    } catch (error) {
      message.error('加载知识库失败');
      navigate('/admin/knowledge-bases');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values: any) => {
    try {
      if (isNewMode) {
        await KnowledgeBaseService.createKnowledgeBase(values);
        message.success('知识库创建成功');
      } else if (id) {
        await KnowledgeBaseService.updateKnowledgeBase(id, values);
        message.success('知识库更新成功');
      }
      navigate('/admin/knowledge-bases');
    } catch (error) {
      message.error(isNewMode ? '创建知识库失败' : '更新知识库失败');
    }
  };

  const handleBack = () => {
    navigate('/admin/knowledge-bases');
  };

  // 临时文档列表列定义
  const documentColumns = [
    {
      title: '文档名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Tokens数',
      dataIndex: 'tokens',
      key: 'tokens',
      render: (tokens: number) => tokens || 0,
    },
    {
      title: 'Summary',
      dataIndex: 'summary',
      key: 'summary',
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header style={{ 
        background: '#fff', 
        padding: '0 24px', 
        boxShadow: '0 1px 4px rgba(0,21,41,.08)',
        display: 'flex',
        alignItems: 'center'
      }}>
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={handleBack}
            type="text"
          />
          <Title level={3} style={{ margin: 0 }}>
            {isNewMode ? '新建知识库' : `编辑知识库: ${knowledgeBase?.name || ''}`}
          </Title>
        </Space>
      </Header>
      <Content style={{ margin: '24px' }}>
        <Card title="基本信息" style={{ marginBottom: 24 }}>
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSave}
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
              label="详细描述"
              rules={[
                { max: 500, message: '描述不能超过500字符' }
              ]}
            >
              <TextArea 
                placeholder="输入知识库详细描述" 
                rows={4}
                showCount
                maxLength={500}
              />
            </Form.Item>
            <Form.Item
              name="owner"
              label="Owner"
              rules={[
                { required: true, message: '请输入Owner' }
              ]}
            >
              <Input placeholder="输入Owner" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
                {isNewMode ? '创建知识库' : '保存更改'}
              </Button>
            </Form.Item>
          </Form>
        </Card>

        <Card 
          title="文档管理" 
          extra={
            <Button type="primary" icon={<PlusOutlined />}>
              新增文档
            </Button>
          }
        >
          <Table
            columns={documentColumns}
            dataSource={documents}
            loading={loading}
            rowKey="id"
            locale={{ emptyText: isNewMode ? '请先保存知识库，然后添加文档' : '暂无文档' }}
          />
        </Card>
      </Content>
    </Layout>
  );
};

export default KnowledgeBaseEdit;
```

### 3.5 更新路由配置
```typescript
// frontend/src/App.tsx
import KnowledgeBaseList from './pages/admin/KnowledgeBaseList';
import KnowledgeBaseEdit from './pages/admin/KnowledgeBaseEdit';

// 在Routes中更新
<Route path="/admin/knowledge-bases" element={
  <ProtectedRoute>
    <KnowledgeBaseList />
  </ProtectedRoute>
} />
<Route path="/admin/knowledge-base/:id" element={
  <ProtectedRoute>
    <KnowledgeBaseEdit />
  </ProtectedRoute>
} />
```

## 4. 实施验证

### 4.1 功能测试清单
- [ ] 知识库列表显示所有字段（包括owner）
- [ ] 点击"新建知识库"跳转到编辑页面（新建模式）
- [ ] 表格行选中功能正常
- [ ] 选中行后表头显示"编辑"按钮
- [ ] 点击"编辑"跳转到编辑页面（编辑模式）
- [ ] 新建模式：所有字段为空
- [ ] 编辑模式：显示现有数据
- [ ] 保存功能正常
- [ ] 返回按钮正常

### 4.2 下一步准备
完成本步骤后，将具备：
- 完整的知识库列表和编辑界面
- 统一的编辑组件（支持新建和编辑模式）
- 为文档管理功能预留的界面框架

下一步将实现：
- 文档数据模型和API
- PDF上传功能
- 文档列表显示和管理

这个设计确认吗？
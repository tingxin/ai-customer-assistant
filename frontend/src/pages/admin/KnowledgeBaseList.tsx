import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Layout, Card, Button, Table, message, Space, Typography, Popconfirm
} from 'antd';
import { PlusOutlined, EditOutlined, FolderOutlined, DeleteOutlined } from '@ant-design/icons';
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

  const handleDelete = async () => {
    if (selectedRowKeys.length === 1) {
      try {
        console.log('Deleting knowledge base:', selectedRowKeys[0]);
        await KnowledgeBaseService.deleteKnowledgeBase(selectedRowKeys[0]);
        console.log('Delete API call successful');
        message.success('知识库删除成功');
        setSelectedRowKeys([]);
        // 延迟刷新列表确保数据库操作完成
        setTimeout(() => {
          loadKnowledgeBases();
        }, 500);
      } catch (error) {
        console.error('Delete failed:', error);
        message.error('删除知识库失败');
      }
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
          <Space>
            <Button 
              type="primary" 
              icon={<EditOutlined />}
              onClick={handleEdit}
            >
              编辑知识库
            </Button>
            <Popconfirm
              title="删除知识库"
              description="确定要删除这个知识库吗？删除后无法恢复。"
              onConfirm={handleDelete}
              okText="确定删除"
              cancelText="取消"
              okType="danger"
            >
              <Button 
                danger
                icon={<DeleteOutlined />}
              >
                删除知识库
              </Button>
            </Popconfirm>
          </Space>
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
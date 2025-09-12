import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card, Button, Form, Input, message, Space, Table, Typography, Popconfirm, Tag, Tooltip
} from 'antd';
import { ArrowLeftOutlined, SaveOutlined, PlusOutlined, DeleteOutlined, PlayCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import { KnowledgeBaseService, KnowledgeBase } from '../../services/knowledgeBaseService';
import { DocumentService, Document } from '../../services/documentService';
import DocumentUpload from '../../components/DocumentUpload';


const { TextArea } = Input;
const { Title } = Typography;

const KnowledgeBaseEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);

  const isNewMode = id === 'new';

  const loadKnowledgeBase = useCallback(async (kbId: string) => {
    setLoading(true);
    try {
      const data = await KnowledgeBaseService.getKnowledgeBase(kbId);
      setKnowledgeBase(data);
      form.setFieldsValue({
        name: data.name,
        description: data.description,
        owner: data.owner
      });
    } catch (error) {
      message.error('加载知识库失败');
      navigate('/admin/knowledge-bases');
    } finally {
      setLoading(false);
    }
  }, [form, navigate]);

  const loadDocuments = async (kbId: string) => {
    try {
      const docs = await DocumentService.getDocuments(kbId);
      setDocuments(Array.isArray(docs) ? docs : []);
    } catch (error: any) {
      console.error('加载文档列表失败:', error);
      message.error('加载文档列表失败');
      setDocuments([]);
    }
  };

  useEffect(() => {
    if (!isNewMode && id) {
      loadKnowledgeBase(id);
      loadDocuments(id);
    } else {
      form.setFieldsValue({
        owner: 'admin'
      });
    }
  }, [id, isNewMode, form, loadKnowledgeBase]);

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

  const handleDeleteDocument = async (docId: string) => {
    try {
      await DocumentService.deleteDocument(docId);
      message.success('文档删除成功');
      if (id) loadDocuments(id);
    } catch (error) {
      message.error('文档删除失败');
    }
  };

  const handleProcessDocument = async (docId: string) => {
    try {
      await DocumentService.processDocument(docId);
      message.success('文档处理已启动');
      if (id) loadDocuments(id);
    } catch (error) {
      message.error('文档处理启动失败');
    }
  };

  const documentColumns = [
    {
      title: '文档名称',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '文档描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (desc: string) => desc || '-',
      width: 200,
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (size: number) => {
        if (!size) return '-';
        if (size < 1024) return `${size} B`;
        if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
        return `${(size / (1024 * 1024)).toFixed(1)} MB`;
      },
    },
    {
      title: '文件类型',
      dataIndex: 'doc_type',
      key: 'doc_type',
      width: 80,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => {
        const statusConfig = {
          uploaded: { color: 'blue', text: '已上传', icon: null },
          parsing: { color: 'processing', text: '解析中', icon: <LoadingOutlined /> },
          vectorizing: { color: 'processing', text: '向量化中', icon: <LoadingOutlined /> },
          indexing: { color: 'processing', text: '索引中', icon: <LoadingOutlined /> },
          completed: { color: 'success', text: '已完成', icon: null },
          failed: { color: 'error', text: '处理失败', icon: null }
        };
        const config = statusConfig[status as keyof typeof statusConfig] || { color: 'default', text: status, icon: null };
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      },
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => date ? new Date(date).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right' as const,
      render: (_: any, record: Document) => (
        <Space size="small">
          {record.status === 'uploaded' && (
            <Tooltip title="开始处理文档">
              <Button 
                type="text" 
                icon={<PlayCircleOutlined />}
                size="small"
                onClick={() => handleProcessDocument(record.id)}
              >
                处理
              </Button>
            </Tooltip>
          )}
          <Popconfirm
            title="删除文档"
            description="确定要删除这个文档吗？"
            onConfirm={() => handleDeleteDocument(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button 
              type="text" 
              danger 
              icon={<DeleteOutlined />}
              size="small"
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ 
      background: '#f0f2f5',
      height: '100vh',
      overflow: 'auto',
      position: 'relative'
    }}>
      <div style={{ 
        background: '#fff', 
        padding: '0 24px', 
        boxShadow: '0 1px 4px rgba(0,21,41,.08)',
        display: 'flex',
        alignItems: 'center',
        height: '64px',
        position: 'sticky',
        top: 0,
        zIndex: 100
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
      </div>
      <div style={{ 
        padding: '24px',
        paddingBottom: '60px'
      }}>
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
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setUploadModalVisible(true)}
              disabled={isNewMode}
            >
              新增文档
            </Button>
          }
          style={{ marginBottom: '24px' }}
        >
          <Table
            columns={documentColumns}
            dataSource={documents}
            loading={loading}
            rowKey="id"
            locale={{ emptyText: isNewMode ? '请先保存知识库，然后添加文档' : '暂无文档' }}
            scroll={{ x: 800 }}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 个文档`,
            }}
            size="middle"
          />
        </Card>
        
        {!isNewMode && (
          <DocumentUpload
            visible={uploadModalVisible}
            onCancel={() => setUploadModalVisible(false)}
            onSuccess={() => {
              setUploadModalVisible(false);
              if (id) {
                setTimeout(() => loadDocuments(id), 1000);
              }
            }}
            knowledgeBaseId={id!}
          />
        )}
      </div>
    </div>
  );
};

export default KnowledgeBaseEdit;
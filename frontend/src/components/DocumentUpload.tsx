import React, { useState } from 'react';
import { Modal, Upload, message, Progress, Form, Input } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';

const { Dragger } = Upload;

interface DocumentUploadProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
  knowledgeBaseId: string;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  visible,
  onCancel,
  onSuccess,
  knowledgeBaseId
}) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [form] = Form.useForm();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleUpload = async () => {
    if (!selectedFile) {
      message.error('请选择要上传的文件');
      return;
    }

    try {
      const values = await form.validateFields();
      setUploading(true);
      
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (values.title) formData.append('title', values.title);
      if (values.description) formData.append('description', values.description);

      console.log('Uploading document:', {
        file: selectedFile.name,
        title: values.title,
        description: values.description,
        knowledgeBaseId
      });

      const response = await fetch(
        `http://localhost:8000/api/knowledge/bases/${knowledgeBaseId}/documents/upload`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (response.ok) {
        const result = await response.json();
        console.log('Upload response:', result);
        message.success('文档上传成功');
        form.resetFields();
        setSelectedFile(null);
        // 立即调用onSuccess，父组件会延迟刷新
        onSuccess();
      } else {
        const error = await response.json();
        console.error('Upload error:', error);
        message.error(error.detail || '文档上传失败');
      }
    } catch (error) {
      console.error('Upload exception:', error);
      message.error('文档上传失败');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const uploadProps: UploadProps = {
    beforeUpload: (file) => {
      const isValidType = ['.pdf', '.doc', '.docx', '.txt', '.md'].some(ext => 
        file.name.toLowerCase().endsWith(ext)
      );
      if (!isValidType) {
        message.error('只支持 PDF、Word、TXT、Markdown 格式文件');
        return false;
      }
      
      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('文件大小不能超过 10MB');
        return false;
      }
      
      setSelectedFile(file);
      form.setFieldsValue({ title: file.name.replace(/\.[^/.]+$/, '') });
      return false; // 阻止自动上传
    },
    fileList: selectedFile ? [{
      uid: '1',
      name: selectedFile.name,
      status: 'done',
    }] : [],
    onRemove: () => {
      setSelectedFile(null);
      form.resetFields();
    },
  };

  return (
    <Modal
      title="上传文档"
      open={visible}
      onCancel={uploading ? undefined : onCancel}
      onOk={handleUpload}
      okText="上传"
      cancelText="取消"
      confirmLoading={uploading}
      width={600}
      closable={!uploading}
      maskClosable={!uploading}
    >
      <div style={{ padding: '20px 0' }}>
        <Dragger {...uploadProps} disabled={uploading}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域选择</p>
          <p className="ant-upload-hint">
            支持格式：PDF、Word、TXT、Markdown，文件大小不超过10MB
          </p>
        </Dragger>
        
        {selectedFile && (
          <Form
            form={form}
            layout="vertical"
            style={{ marginTop: 16 }}
          >
            <Form.Item
              name="title"
              label="文档标题"
              rules={[{ required: true, message: '请输入文档标题' }]}
            >
              <Input placeholder="输入文档标题" />
            </Form.Item>
            
            <Form.Item
              name="description"
              label="文档描述"
            >
              <Input.TextArea 
                placeholder="输入文档描述（可选）" 
                rows={3}
                showCount
                maxLength={500}
              />
            </Form.Item>
          </Form>
        )}
        
        {uploading && (
          <div style={{ marginTop: 16 }}>
            <Progress percent={Math.round(uploadProgress)} />
            <p style={{ textAlign: 'center', marginTop: 8 }}>
              正在上传文档，请稍候...
            </p>
          </div>
        )}
      </div>
    </Modal>
  );
};

export default DocumentUpload;
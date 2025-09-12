import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Chat, { useMessages, Bubble } from '@chatui/core';
import '@chatui/core/dist/index.css';
import 'antd/dist/reset.css';
import KnowledgeBaseList from './pages/admin/KnowledgeBaseList';
import KnowledgeBaseEdit from './pages/admin/KnowledgeBaseEdit';
import botAvatar from './assets/images/bot.png';

// 聊天组件
const ChatPage: React.FC = () => {
  const { messages, appendMsg } = useMessages([]);

  // 添加欢迎消息
  useEffect(() => {
    appendMsg({
      type: 'text',
      content: { text: `您好！我是智能客服助手 🤖

欢迎体验我的AI服务！我会随机返回不同类型的消息：

• 文本消息
• 图片消息  
• 卡片消息
• 列表消息

请随意输入任何内容，或点击下方按钮开始体验！` },
      user: { avatar: botAvatar },
    });
  }, [appendMsg]);

  const handleSend = async (type: string, val: string) => {
    if (type === 'text') {
      // 添加用户消息
      appendMsg({
        type: 'text',
        content: { text: val },
        position: 'right',
      });
      
      try {
        // 调用后端API
        const response = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: val }),
        });
        
        if (response.ok) {
          const data = await response.json();
          // 添加后端返回的消息
          appendMsg({
            type: data.type,
            content: data.content,
            user: { avatar: botAvatar },
          });
        } else {
          // 错误处理
          appendMsg({
            type: 'text',
            content: { text: '抱歉，服务暂时不可用，请稍后再试。' },
            user: { avatar: botAvatar },
          });
        }
      } catch (error) {
        // 网络错误处理
        appendMsg({
          type: 'text',
          content: { text: '网络连接失败，请检查后端服务是否启动。' },
          user: { avatar: botAvatar },
        });
      }
    }
  };

  const renderMessageContent = (msg: any) => {
    const { type, content } = msg;
    
    // 使用ChatUI原生组件渲染不同类型的消息
    switch (type) {
      case 'card':
        return (
          <div style={{
            border: '1px solid #e0e0e0',
            borderRadius: '8px',
            padding: '16px',
            margin: '8px 0'
          }}>
            {content.img && (
              <img 
                src={content.img} 
                alt={content.title}
                style={{ width: '100%', borderRadius: '4px', marginBottom: '12px' }}
              />
            )}
            <div style={{ fontWeight: 'bold', fontSize: '16px', marginBottom: '8px' }}>
              {content.title}
            </div>
            <div style={{ color: '#666', fontSize: '14px', marginBottom: '12px' }}>
              {content.desc}
            </div>
            {content.actions && content.actions.map((action: any, index: number) => (
              <button
                key={index}
                onClick={() => action.url && window.open(action.url, '_blank')}
                style={{
                  background: '#1890ff',
                  color: 'white',
                  border: 'none',
                  padding: '8px 16px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  marginRight: '8px'
                }}
              >
                {action.text}
              </button>
            ))}
          </div>
        );
      
      case 'image':
        return (
          <img 
            src={content.picUrl} 
            alt="图片" 
            style={{ maxWidth: '100%', borderRadius: '8px' }}
          />
        );
      
      case 'list':
        return (
          <div style={{
            border: '1px solid #e0e0e0',
            borderRadius: '8px',
            padding: '16px',
            margin: '8px 0',
            background: '#fafafa'
          }}>
            <div style={{ 
              fontWeight: 'bold', 
              marginBottom: '12px',
              fontSize: '16px',
              color: '#333'
            }}>
              {content.header?.title}
            </div>
            {content.items?.map((item: any, index: number) => (
              <div key={index} style={{ 
                display: 'flex', 
                alignItems: 'flex-start', 
                padding: '12px 0',
                borderBottom: index < content.items.length - 1 ? '1px solid #e0e0e0' : 'none'
              }}>
                <span style={{ 
                  marginRight: '12px', 
                  fontSize: '20px',
                  marginTop: '2px'
                }}>
                  {item.icon}
                </span>
                <div style={{ flex: 1 }}>
                  <div style={{ 
                    fontWeight: '500', 
                    fontSize: '14px',
                    marginBottom: '4px',
                    color: '#333'
                  }}>
                    {item.title}
                  </div>
                  <div style={{ 
                    fontSize: '13px', 
                    color: '#666',
                    lineHeight: '1.4'
                  }}>
                    {item.desc}
                  </div>
                </div>
              </div>
            ))}
          </div>
        );
      
      case 'text':
      default:
        return <Bubble content={content.text || content} />;
    }
  };

  return (
    <div style={{ height: '100vh', position: 'relative' }}>
      <Chat
        navbar={{ 
          title: '智能客服 - ChatUI组件演示',
          rightContent: [
            {
              icon: 'settings',
              title: '管理员',
              onClick: () => window.location.href = '/admin/knowledge-bases'
            }
          ]
        }}
        messages={messages}
        onSend={handleSend}
        placeholder="输入任何内容体验AI回复..."
        quickReplies={[
          { name: '你好', isNew: false, isHighlight: false },
          { name: '显示卡片消息', isNew: false, isHighlight: false },
          { name: '显示列表消息', isNew: false, isHighlight: false },
          { name: '显示图片消息', isNew: false, isHighlight: false },
        ]}
        onQuickReplyClick={(item) => handleSend('text', item.name)}
        renderMessageContent={renderMessageContent}
      />
    </div>
  );
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<ChatPage />} />
        <Route path="/admin/knowledge-bases" element={<KnowledgeBaseList />} />
        <Route path="/admin/knowledge-base/:id" element={<KnowledgeBaseEdit />} />
      </Routes>
    </Router>
  );
}

export default App;

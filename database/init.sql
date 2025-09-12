-- 智能客服系统数据库初始化脚本
-- 数据库: ai_customer_service

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS ai_customer_service 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ai_customer_service;

-- 1. 用户表
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    role ENUM('admin', 'user', 'manager') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. 知识库表
CREATE TABLE knowledge_bases (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id VARCHAR(36) NOT NULL,
    status ENUM('active', 'inactive', 'archived') DEFAULT 'active',
    document_count INT DEFAULT 0,
    total_size BIGINT DEFAULT 0,
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_owner (owner_id),
    INDEX idx_status (status),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 文档表
CREATE TABLE documents (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    title VARCHAR(200) NOT NULL,
    knowledge_base_id VARCHAR(36) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    doc_type VARCHAR(20) NOT NULL,
    mime_type VARCHAR(100),
    status ENUM('uploaded', 'parsing', 'vectorizing', 'indexing', 'completed', 'failed') DEFAULT 'uploaded',
    error_message TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL,
    
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    INDEX idx_kb_id (knowledge_base_id),
    INDEX idx_status (status),
    INDEX idx_doc_type (doc_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. 文档块表
CREATE TABLE document_chunks (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    document_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    chunk_index INT NOT NULL,
    chunk_type ENUM('text', 'table', 'image', 'code') DEFAULT 'text',
    token_count INT,
    vector_id VARCHAR(100),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    INDEX idx_document_id (document_id),
    INDEX idx_chunk_index (chunk_index),
    INDEX idx_vector_id (vector_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. 分类表
CREATE TABLE categories (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    knowledge_base_id VARCHAR(36) NOT NULL,
    parent_id VARCHAR(36) NULL,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_kb_id (knowledge_base_id),
    INDEX idx_parent_id (parent_id),
    UNIQUE KEY uk_kb_name (knowledge_base_id, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. 标签表
CREATE TABLE tags (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#1890ff',
    knowledge_base_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    INDEX idx_kb_id (knowledge_base_id),
    UNIQUE KEY uk_kb_tag (knowledge_base_id, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. 文档标签关联表
CREATE TABLE document_tags (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    document_id VARCHAR(36) NOT NULL,
    tag_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE KEY uk_doc_tag (document_id, tag_id),
    INDEX idx_document_id (document_id),
    INDEX idx_tag_id (tag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. 文档分类关联表
CREATE TABLE document_categories (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    document_id VARCHAR(36) NOT NULL,
    category_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE KEY uk_doc_category (document_id, category_id),
    INDEX idx_document_id (document_id),
    INDEX idx_category_id (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. 会话表
CREATE TABLE sessions (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36),
    title VARCHAR(200),
    status ENUM('active', 'closed', 'archived') DEFAULT 'active',
    knowledge_base_id VARCHAR(36),
    context JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_kb_id (knowledge_base_id),
    INDEX idx_status (status),
    INDEX idx_last_activity (last_activity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. 消息表
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    session_id VARCHAR(36) NOT NULL,
    sender_type ENUM('user', 'ai', 'admin') NOT NULL,
    content TEXT NOT NULL,
    message_type ENUM('text', 'image', 'file', 'rich_text') DEFAULT 'text',
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_sender_type (sender_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. 处理任务表
CREATE TABLE processing_tasks (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    document_id VARCHAR(36) NOT NULL,
    task_type ENUM('parse', 'vectorize', 'index') NOT NULL,
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    progress INT DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    INDEX idx_document_id (document_id),
    INDEX idx_task_type (task_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. 系统配置表
CREATE TABLE system_configs (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSON NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_config_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入默认管理员用户
INSERT INTO users (id, username, email, role, password_hash) VALUES 
('admin-001', 'admin', 'admin@example.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5/Qe.');

-- 插入默认系统配置
INSERT INTO system_configs (config_key, config_value, description) VALUES 
('max_file_size', '10485760', '最大文件上传大小（字节）'),
('allowed_extensions', '[".pdf", ".doc", ".docx", ".txt", ".md", ".html"]', '允许的文件扩展名'),
('default_embedding_model', '"sentence-transformers/all-MiniLM-L6-v2"', '默认嵌入模型'),
('chunk_size', '1000', '文档分块大小'),
('chunk_overlap', '200', '文档分块重叠大小');

-- 创建触发器：更新知识库文档统计
DELIMITER $$

CREATE TRIGGER update_kb_stats_after_insert
AFTER INSERT ON documents
FOR EACH ROW
BEGIN
    UPDATE knowledge_bases 
    SET document_count = document_count + 1,
        total_size = total_size + NEW.file_size,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.knowledge_base_id;
END$$

CREATE TRIGGER update_kb_stats_after_delete
AFTER DELETE ON documents
FOR EACH ROW
BEGIN
    UPDATE knowledge_bases 
    SET document_count = document_count - 1,
        total_size = total_size - OLD.file_size,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.knowledge_base_id;
END$$

DELIMITER ;

-- 创建视图：文档详细信息
CREATE VIEW document_details AS
SELECT 
    d.id,
    d.title,
    d.knowledge_base_id,
    kb.name as knowledge_base_name,
    d.file_path,
    d.file_size,
    d.doc_type,
    d.status,
    d.created_at,
    d.updated_at,
    d.processed_at,
    COUNT(dc.id) as chunk_count,
    GROUP_CONCAT(DISTINCT t.name) as tags,
    GROUP_CONCAT(DISTINCT c.name) as categories
FROM documents d
LEFT JOIN knowledge_bases kb ON d.knowledge_base_id = kb.id
LEFT JOIN document_chunks dc ON d.id = dc.document_id
LEFT JOIN document_tags dt ON d.id = dt.document_id
LEFT JOIN tags t ON dt.tag_id = t.id
LEFT JOIN document_categories dcat ON d.id = dcat.document_id
LEFT JOIN categories c ON dcat.category_id = c.id
GROUP BY d.id;

-- 创建索引优化查询性能
CREATE INDEX idx_documents_composite ON documents(knowledge_base_id, status, created_at);
CREATE INDEX idx_chunks_composite ON document_chunks(document_id, chunk_index);
CREATE INDEX idx_sessions_composite ON sessions(user_id, status, last_activity);
CREATE INDEX idx_messages_composite ON messages(session_id, created_at);

-- 显示创建完成信息
SELECT 'Database initialization completed successfully!' as status;
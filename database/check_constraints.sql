-- 检查数据库约束和外键关系
USE ai_customer_service;

-- 1. 检查知识库表的外键约束
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME,
    DELETE_RULE,
    UPDATE_RULE
FROM 
    INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE 
    REFERENCED_TABLE_SCHEMA = 'ai_customer_service' 
    AND (TABLE_NAME = 'knowledge_bases' OR REFERENCED_TABLE_NAME = 'knowledge_bases');

-- 2. 检查是否有文档关联到知识库
SELECT kb.id, kb.name, COUNT(d.id) as document_count
FROM knowledge_bases kb
LEFT JOIN documents d ON kb.id = d.knowledge_base_id
GROUP BY kb.id, kb.name;

-- 3. 检查知识库状态
SELECT id, name, status, owner_id FROM knowledge_bases;

-- 4. 检查用户表中是否存在owner_id
SELECT id, username FROM users WHERE id = 'admin-001';
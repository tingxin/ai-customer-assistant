-- 修改数据库表中的metadata字段名以避免SQLAlchemy保留字冲突
-- 并为文档表添加描述字段
-- 执行前请备份数据库

USE ai_customer_service;

-- 1. 修改documents表的metadata字段为doc_metadata
ALTER TABLE documents CHANGE COLUMN metadata doc_metadata JSON;

-- 2. 为documents表添加description字段
ALTER TABLE documents ADD COLUMN description TEXT AFTER title;

-- 3. 修改document_chunks表的metadata字段为chunk_metadata  
ALTER TABLE document_chunks CHANGE COLUMN metadata chunk_metadata JSON;

-- 3. 重新创建视图以使用新的字段名
DROP VIEW IF EXISTS document_details;

CREATE VIEW document_details AS
SELECT 
    d.id,
    d.title,
    d.description,
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

-- 验证修改结果
DESCRIBE documents;
DESCRIBE document_chunks;
SHOW CREATE VIEW document_details;
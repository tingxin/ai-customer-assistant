# 数据库初始化指南

## 📋 数据库信息
- **数据库类型**: MySQL 8.0+
- **主机**: tx-db.cbore8wpy3mc.us-east-2.rds.amazonaws.com
- **端口**: 3306
- **用户**: demo
- **密码**: xxxxxx
- **数据库名**: ai_customer_service

## 🚀 初始化步骤

### 1. 连接到MySQL数据库
```bash
mysql -h tx-db.cbore8wpy3mc.us-east-2.rds.amazonaws.com -P 3306 -u demo -pDemo1234
```

### 2. 执行初始化脚本
```bash
mysql -h tx-db.cbore8wpy3mc.us-east-2.rds.amazonaws.com -P 3306 -u demo -pDemo1234 < init.sql
```

或者在MySQL客户端中：
```sql
source /path/to/init.sql;
```

## 📊 数据表结构

### 核心表
1. **users** - 用户表
2. **knowledge_bases** - 知识库表
3. **documents** - 文档表
4. **document_chunks** - 文档块表
5. **categories** - 分类表
6. **tags** - 标签表

### 关联表
7. **document_tags** - 文档标签关联
8. **document_categories** - 文档分类关联

### 业务表
9. **sessions** - 会话表
10. **messages** - 消息表
11. **processing_tasks** - 处理任务表
12. **system_configs** - 系统配置表

## 🔧 特殊功能

### 触发器
- `update_kb_stats_after_insert` - 文档插入后更新知识库统计
- `update_kb_stats_after_delete` - 文档删除后更新知识库统计

### 视图
- `document_details` - 文档详细信息视图（包含标签、分类等）

### 索引优化
- 复合索引优化查询性能
- 外键索引确保关联查询效率

## 📝 默认数据

### 管理员用户
- **用户名**: admin
- **邮箱**: admin@example.com
- **角色**: admin
- **密码**: 需要通过API设置

### 系统配置
- 最大文件大小: 10MB
- 允许的文件类型: PDF, Word, TXT, Markdown, HTML
- 默认分块大小: 1000 tokens
- 分块重叠: 200 tokens

## ⚠️ 注意事项

1. **字符集**: 使用 utf8mb4 支持完整的Unicode字符
2. **时区**: 所有时间戳使用服务器本地时区
3. **外键约束**: 启用级联删除，注意数据完整性
4. **索引**: 已优化常用查询的索引，定期监控性能

## 🔍 验证安装

执行以下查询验证安装：
```sql
-- 检查表是否创建成功
SHOW TABLES;

-- 检查默认用户
SELECT * FROM users WHERE username = 'admin';

-- 检查系统配置
SELECT * FROM system_configs;

-- 检查触发器
SHOW TRIGGERS;

-- 检查视图
SHOW FULL TABLES WHERE Table_type = 'VIEW';
```
-- 创建数据库
CREATE DATABASE IF NOT EXISTS shared_documents
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE shared_documents;

删除已存在的表（如果需要）
DROP TABLE IF EXISTS users;

-- 创建users表
CREATE TABLE users (
    -- 主键
    id INT NOT NULL AUTO_INCREMENT,
    
    -- 用户名字段
    username VARCHAR(80) NOT NULL,
    
    -- 邮箱字段
    email VARCHAR(120) NOT NULL,
    
    -- 密码哈希字段
    password_hash VARCHAR(128) NOT NULL,
    
    -- 创建时间字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 账户状态字段
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- 设置主键
    PRIMARY KEY (id),
    
    -- 设置唯一约束
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email),
    
    -- 添加索引
    KEY idx_username (username),
    KEY idx_email (email)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='用户表';

-- 查看表结构
DESCRIBE users;

-- 查看表信息
SHOW TABLE STATUS LIKE 'users';

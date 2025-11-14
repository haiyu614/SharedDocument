# 快速开始指南

## 🚀 5分钟快速启动

### 前置要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis（可选，用于会话管理）

---

## 第一步：后端设置

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env，修改数据库连接信息
# DATABASE_URL=mysql+mysqlconnector://root:your_password@localhost:3306/collab_doc
```

### 3. 创建数据库
```bash
mysql -u root -p
```
```sql
CREATE DATABASE collab_doc CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 4. 初始化数据库
```bash
# 如果还没有 Alembic，先初始化
alembic init alembic

# 执行迁移（需要先创建迁移文件，见 implementation-guide.md）
alembic upgrade head

# 初始化角色数据
python scripts/init_data.py
```

### 5. 启动后端服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

---

## 第二步：前端设置

### 1. 安装依赖
```bash
cd frontend
npm install
```

### 2. 配置环境变量
```bash
# 复制示例文件
cp .env.example .env

# 默认配置通常不需要修改
```

### 3. 启动开发服务器
```bash
npm run dev
```

访问 http://localhost:5173

---

## 第三步：测试登录

### 1. 注册用户
访问 http://localhost:5173/login，点击"注册"或直接调用 API：

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "123456",
    "email": "admin@example.com",
    "role_name": "admin"
  }'
```

### 2. 登录
使用注册的用户名密码登录

---

## 📋 开发顺序建议

按照以下顺序实现功能：

1. ✅ **环境搭建** - 完成上述步骤
2. ✅ **用户认证** - 登录/注册功能
3. ✅ **文档CRUD** - 创建/查看/编辑文档
4. ✅ **版本管理** - 保存版本/查看历史/对比
5. ✅ **实时协作** - WebSocket 多人编辑

详细步骤请参考 [implementation-guide.md](./implementation-guide.md)

---

## 🐛 常见问题

### 数据库连接失败
- 检查 MySQL 服务是否启动
- 检查 `.env` 中的 `DATABASE_URL` 是否正确
- 确认数据库用户有足够权限

### 前端无法连接后端
- 检查后端服务是否启动（http://localhost:8000/health）
- 检查 `.env` 中的 `VITE_API_BASE_URL` 是否正确
- 检查 CORS 配置

### 迁移失败
- 确认数据库已创建
- 检查数据库用户权限
- 查看 Alembic 日志错误信息

---

## 📚 下一步

- 阅读 [implementation-guide.md](./implementation-guide.md) 了解详细实现步骤
- 查看 [architecture-overview.md](./architecture/architecture-overview.md) 了解系统架构
- 查看 [rest-api.md](./api/rest-api.md) 了解 API 接口


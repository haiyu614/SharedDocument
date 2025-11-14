# 协同文档系统（MVP 框架）

本仓库提供共享编辑文档系统的最小可运行框架，包含前后端骨架与文档规范。适用于后续团队成员并行开发。

## 目录结构

```
backend/           # FastAPI 后端服务
frontend/          # Vue3 前端应用
docs/              # 架构、API、协同策略文档
```

### 后端（FastAPI）
- 入口：`backend/app/main.py`
- 路由：`backend/app/api/routes/`（auth / documents / versions / collab）
- 服务：`backend/app/services/` 封装业务逻辑
- 模型：`backend/app/models/` SQLAlchemy ORM
- 依赖：`backend/requirements.txt`

### 前端（Vue3 + Vite）
- 入口：`frontend/src/main.ts`
- 路由：`frontend/src/router/index.ts`
- 页面：`frontend/src/pages/`
- API 封装：`frontend/src/services/`
- 类型：`frontend/src/types/`
- 配置：`frontend/package.json`, `frontend/vite.config.ts`

## 快速启动（开发模式）

1. **后端**
   ```bash
   cd backend
   python -m venv .venv && .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
2. **前端**
   ```bash
    cd frontend
    npm install
    npm run dev
   ```
3. 打开浏览器访问 `http://localhost:5173`

## 📚 开发文档

### 开始开发
- **[快速开始指南](./docs/quick-start.md)** - 5分钟快速启动项目
- **[分步实现总结](./docs/step-by-step-summary.md)** - 清晰的实现步骤和任务清单
- **[详细实现指南](./docs/implementation-guide.md)** - 包含代码示例的完整指南

### 架构设计
- **[架构概览](./docs/architecture/architecture-overview.md)** - 系统整体架构
- **[数据库设计](./docs/architecture/database-schema.md)** - 表结构设计
- **[协同策略](./docs/architecture/collaboration-strategy.md)** - OT 算法说明

### API 文档
- **[REST API](./docs/api/rest-api.md)** - REST 接口规范
- **[WebSocket 协议](./docs/api/ws-protocol.md)** - WebSocket 消息格式

## 🚀 实现顺序

按照以下顺序逐步实现功能：

1. **环境搭建** → 数据库初始化、依赖安装
2. **用户认证** → 登录/注册、JWT Token
3. **文档CRUD** → 创建/查看/编辑文档
4. **版本管理** → 保存版本、查看历史、对比差异
5. **实时协作** → WebSocket 多人编辑

详细步骤请查看 [分步实现总结](./docs/step-by-step-summary.md)

## 后续工作指引

- 完善数据库迁移（Alembic）、业务逻辑与单元测试。
- 实现 `POST /documents/{id}/save` 等完整版本管理接口。
- 接入真正的 OT/CRDT 引擎，完善前端与后端消息协议。
- 补充 CI/CD、Docker Compose、Nginx 配置与监控告警。


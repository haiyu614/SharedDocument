# 协同文档系统架构概览

## 整体结构

- **前端**：`frontend/` 基于 Vue 3 + Vite，负责富文本编辑器、实时协作可视化、版本查看。
- **后端**：`backend/` 基于 FastAPI，提供 REST API 与 WebSocket 协作管道。
- **数据库**：MySQL 储存用户、文档、版本、权限、操作日志。
- **实时层**：WebSocket + 协同服务（可扩展接入 Redis 进行多实例广播）。
- **网关**：Nginx 统一提供 HTTPS、静态资源与反向代理。

```
Client (Vue3 SPA)
   ├── REST API  → FastAPI 应用 → MySQL
   └── WebSocket → 协同协调器  → Redis (可选)
```

## 关键模块

- `backend/app/api`: FastAPI 路由层，拆分 `auth`、`documents`、`versions`、`collab`。
- `backend/app/services`: 业务服务层，封装认证、文档、版本、协作逻辑。
- `backend/app/models`: SQLAlchemy ORM 模型，对应数据库实体。
- `frontend/src/pages`: 登录、编辑器、版本管理等页面。
- `docs/api`: Swagger/Markdown 格式的接口协议说明。

## 技术选型

- **协同算法**：MVP 先以 OT 为设计参考，后端留有 `CollaborationService` 扩展点，未来可接入 Yjs/ShareDB。
- **认证授权**：JWT + RBAC（角色：管理员、编辑者、查看者）。
- **版本管理**：保存完整内容 + diff 快照，提供 `GET /documents/{id}/compare` diff 接口。


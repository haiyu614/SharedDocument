# REST API 规范（MVP）

Base URL: `/api`

## Auth 模块

### `POST /auth/register`
- 描述：注册新用户，默认角色 `editor`。
- 请求体：
  ```json
  {
    "username": "alice",
    "password": "******",
    "email": "alice@example.com",
    "role_name": "editor"
  }
  ```
- 响应：`UserRead`

### `POST /auth/login`
- 描述：密码登录，返回 JWT。
- 请求：`application/x-www-form-urlencoded`
  ```
  username=alice&password=****** 
  ```
- 响应：
  ```json
  { "access_token": "...", "token_type": "bearer", "expires_at": "2025-11-12T12:00:00Z" }
  ```

### `GET /auth/me`
- 需 `Authorization: Bearer <token>`
- 返回当前用户信息。

### `GET /auth/users`
- 需管理员权限（后续在服务层限制）。

## Document 模块

### `GET /documents`
- 描述：文档列表，返回 `DocumentSummary[]`。

### `POST /documents`
- 描述：创建文档。
- 请求体：
  ```json
  { "title": "MVP 文档", "initial_content": "" }
  ```
- 响应：`DocumentRead`

### `GET /documents/{document_id}`
- 描述：获取文档详情。

### `PUT /documents/{document_id}`
- 描述：更新标题/归档状态。

## Version 模块

### `GET /documents/{document_id}/versions`
- 描述：版本列表。

### `GET /documents/{document_id}/versions/{version_id}`
- 描述：获取单个版本。

### `GET /documents/{document_id}/compare?from_version=1&to_version=2`
- 描述：对比两个版本，返回 diff 列表。

> 后续将补充 `POST /documents/{id}/save` 与 `POST /documents/{id}/restore/{version}` 等接口。


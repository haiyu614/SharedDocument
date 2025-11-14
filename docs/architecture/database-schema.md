# 数据库设计（MVP）

## 实体列表

### `roles`
- `id` (PK)
- `name` (`admin` / `editor` / `viewer`)
- `description`
- `created_at`

### `users`
- `id` (PK)
- `username`
- `email`
- `password_hash`
- `role_id` (FK → `roles.id`)
- `created_at`, `updated_at`

### `documents`
- `id` (PK)
- `title`
- `owner_id` (FK → `users.id`)
- `current_version_id` (FK → `document_versions.id`)
- `is_archived`
- `created_at`, `updated_at`

### `document_versions`
- `id` (PK)
- `document_id` (FK → `documents.id`)
- `version_number`
- `content` (LongText)
- `diff_snapshot` (JSON)
- `created_by` (FK → `users.id`)
- `created_at`

### `edit_logs`
- `id` (PK)
- `document_id`
- `version_id`
- `user_id`
- `operation` (JSON，记录 OT 操作)
- `cursor_position` (JSON)
- `timestamp`

### `permissions`（可选）
- `id`
- `role_id`
- `resource`
- `action`

## 关系说明

- `users` ↔ `roles`：多对一，角色定义权限集合。
- `documents` ↔ `users`：文档拥有者字段。
- `documents` ↔ `document_versions`：一对多，按 `version_number` 排序。
- `document_versions` ↔ `edit_logs`：一对多，版本对应若干操作日志。

> 可使用 MySQL Workbench 导出 ER 图（`docs/architecture/database-er.mwb/png` 占位），供团队确认字段/索引。


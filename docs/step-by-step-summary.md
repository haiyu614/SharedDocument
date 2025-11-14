# 分步实现总结

## 📌 实现顺序（按优先级）

```
第一步：环境搭建 → 第二步：用户认证 → 第三步：文档CRUD → 第四步：版本管理 → 第五步：实时协作
```

---

## 第一步：环境搭建与数据库初始化

### 后端任务清单

1. **创建数据库**
   ```sql
   CREATE DATABASE collab_doc CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **配置环境变量**
   - 创建 `backend/.env` 文件
   - 设置 `DATABASE_URL`、`SECRET_KEY` 等

3. **初始化 Alembic**
   ```bash
   cd backend
   alembic init alembic
   ```

4. **创建迁移文件**
   - 创建 `alembic/versions/001_initial.py`
   - 定义所有表结构（users, roles, documents, document_versions, edit_logs）

5. **执行迁移**
   ```bash
   alembic upgrade head
   ```

6. **初始化角色数据**
   ```bash
   python scripts/init_data.py
   ```

### 前端任务清单

1. **安装依赖**
   ```bash
   cd frontend
   npm install
   ```

2. **配置环境变量**
   - 创建 `frontend/.env` 文件
   - 设置 `VITE_API_BASE_URL`、`VITE_WS_BASE_URL`

3. **验证启动**
   ```bash
   npm run dev
   ```

---

## 第二步：用户认证系统

### 后端要做什么

✅ **已完成的基础代码：**
- `app/api/routes/auth.py` - 路由已定义
- `app/services/auth_service.py` - 服务层已实现
- `app/core/security.py` - JWT 和密码加密已实现

🔧 **需要测试和验证：**
1. 启动后端服务：`uvicorn app.main:app --reload`
2. 测试注册接口：`POST /api/auth/register`
3. 测试登录接口：`POST /api/auth/login`
4. 测试获取用户信息：`GET /api/auth/me`（需要 Token）

### 前端要做什么

1. **完善登录页面** (`frontend/src/pages/LoginPage.vue`)
   - [ ] 添加表单验证
   - [ ] 调用 `AuthService.login()`
   - [ ] 保存 Token 到 localStorage
   - [ ] 登录成功后跳转

2. **实现路由守卫** (`frontend/src/router/index.ts`)
   - [ ] 检查用户是否登录
   - [ ] 未登录跳转到登录页
   - [ ] 已登录访问登录页则跳转到首页

3. **完善认证 Store** (`frontend/src/store/index.ts`)
   - [ ] `login()` - 登录并保存 token
   - [ ] `logout()` - 登出并清除 token
   - [ ] `hydrateFromStorage()` - 从 localStorage 恢复状态
   - [ ] `getCurrentUser()` - 获取当前用户信息

4. **测试登录流程**
   - [ ] 注册新用户
   - [ ] 登录获取 Token
   - [ ] 刷新页面，Token 仍然有效
   - [ ] 登出后无法访问受保护页面

---

## 第三步：文档基础CRUD

### 后端要做什么

1. **完善文档服务层** (`backend/app/services/document_service.py`)

   实现以下方法：
   ```python
   async def create_document(owner_id, title, initial_content) -> Document
   async def list_documents(user_id, role_name) -> list[Document]
   async def get_document(document_id, user_id) -> Document
   async def update_document(document_id, user_id, title) -> Document
   async def delete_document(document_id, user_id) -> None
   ```

2. **完善文档路由** (`backend/app/api/routes/documents.py`)

   实现以下接口：
   ```python
   POST   /api/documents          # 创建文档
   GET    /api/documents          # 获取文档列表
   GET    /api/documents/{id}     # 获取文档详情
   PUT    /api/documents/{id}     # 更新文档
   DELETE /api/documents/{id}     # 删除文档
   ```

3. **实现权限检查**
   - admin: 可以查看/编辑所有文档
   - editor: 可以查看/编辑自己创建的文档
   - viewer: 只能查看文档

### 前端要做什么

1. **完善文档列表** (`frontend/src/pages/EditorPage.vue`)
   - [ ] 调用 `DocumentService.listDocuments()` 获取列表
   - [ ] 在侧边栏显示文档列表
   - [ ] 点击文档项，加载文档内容

2. **实现创建文档**
   - [ ] 点击"新建文档"按钮
   - [ ] 输入文档标题
   - [ ] 调用 `DocumentService.createDocument()`
   - [ ] 创建成功后自动选中

3. **实现文档选择**
   - [ ] 点击文档项
   - [ ] 调用 `DocumentService.getDocument(id)`
   - [ ] 将内容加载到 Quill 编辑器
   - [ ] 显示文档标题

4. **测试文档CRUD**
   - [ ] 创建文档 ✓
   - [ ] 查看文档列表 ✓
   - [ ] 选择文档查看内容 ✓
   - [ ] 更新文档标题 ✓
   - [ ] 删除文档 ✓

---

## 第四步：版本管理

### 后端要做什么

1. **完善版本服务层** (`backend/app/services/version_service.py`)

   实现以下方法：
   ```python
   async def save_version(document_id, user_id, content) -> DocumentVersion
   async def list_versions(document_id) -> list[DocumentVersion]
   async def get_version(version_id) -> DocumentVersion
   async def compare_versions(document_id, from_v, to_v) -> dict
   async def restore_version(document_id, version_id, user_id) -> DocumentVersion
   ```

2. **完善版本路由** (`backend/app/api/routes/versions.py`)

   实现以下接口：
   ```python
   POST /api/documents/{id}/save                    # 保存版本
   GET  /api/documents/{id}/versions                # 版本列表
   GET  /api/documents/{id}/versions/{version_id}   # 获取版本
   GET  /api/documents/{id}/compare                 # 对比版本
   POST /api/documents/{id}/restore/{version_id}    # 回滚版本
   ```

3. **实现版本对比算法**
   - 使用 Python `difflib` 库
   - 生成文本差异（增加/删除/修改）

### 前端要做什么

1. **实现保存版本** (`frontend/src/pages/EditorPage.vue`)
   - [ ] 点击工具栏"保存"按钮
   - [ ] 获取 Quill 编辑器内容
   - [ ] 调用 `DocumentService.saveVersion()`
   - [ ] 显示保存成功提示

2. **实现版本列表页面** (`frontend/src/pages/VersionsPage.vue`)
   - [ ] 调用 `DocumentService.listVersions()`
   - [ ] 显示版本列表（版本号、时间、创建者）
   - [ ] 点击版本项查看内容

3. **实现版本对比**
   - [ ] 选择两个版本
   - [ ] 调用 `DocumentService.compareVersions()`
   - [ ] 使用 `jsdiff` 库高亮显示差异
   - [ ] 显示增加/删除/修改的行

4. **实现版本回滚**
   - [ ] 在版本列表中点击"回滚"
   - [ ] 确认对话框
   - [ ] 调用 `DocumentService.restoreVersion()`
   - [ ] 回滚成功后刷新文档

5. **测试版本管理**
   - [ ] 创建文档并编辑内容
   - [ ] 多次保存版本
   - [ ] 查看版本列表
   - [ ] 对比不同版本
   - [ ] 回滚到旧版本

---

## 第五步：实时协作编辑

### 后端要做什么

1. **实现 WebSocket 端点** (`backend/app/api/routes/collab.py`)

   ```python
   @router.websocket("/ws/{document_id}")
   async def websocket_endpoint(websocket, document_id, token):
       # 1. 验证 token
       # 2. 接受连接
       # 3. 加入文档会话
       # 4. 广播用户加入
       # 5. 监听消息（编辑操作、光标更新）
       # 6. 处理操作（OT transform）
       # 7. 广播到其他客户端
       # 8. 处理断开连接
   ```

2. **实现协同服务** (`backend/app/services/collab_service.py`)

   ```python
   class CollaborationSession:
       def __init__(self, document_id):
           self.clients = {}  # client_id -> websocket
           self.document_state = ""
           self.version = 0
       
       def add_client(client_id, websocket, user)
       def remove_client(client_id)
       def apply_operation(operation, client_id)
       def broadcast(message, exclude_client_id)
   ```

3. **实现 OT 算法**
   - 简化版：基于文本位置的转换
   - 或使用现成库（如 `ot-text`）

### 前端要做什么

1. **实现 WebSocket 连接** (`frontend/src/pages/EditorPage.vue`)
   - [ ] 打开文档时建立连接
   - [ ] 连接参数：document_id, token
   - [ ] 处理连接成功/失败
   - [ ] 处理断开重连

2. **实现编辑操作同步**
   - [ ] 监听 Quill `text-change` 事件
   - [ ] 转换为 OT 格式
   - [ ] 发送到服务器
   - [ ] 接收服务器广播
   - [ ] 应用到编辑器（避免循环触发）

3. **实现光标同步**
   - [ ] 监听光标变化
   - [ ] 发送 `cursor_update` 消息
   - [ ] 接收其他用户光标
   - [ ] 在编辑器中显示（不同颜色）

4. **实现在线用户显示**
   - [ ] 接收 `user_joined` / `user_left`
   - [ ] 更新协作者列表
   - [ ] 显示在线用户头像

5. **测试实时协作**
   - [ ] 打开两个浏览器窗口
   - [ ] 登录不同账号
   - [ ] 打开同一文档
   - [ ] 在一个窗口编辑，观察另一个窗口同步
   - [ ] 观察光标同步

---

## 📊 进度跟踪

### 第一步：环境搭建
- [ ] 数据库创建
- [ ] Alembic 迁移
- [ ] 角色初始化
- [ ] 前端项目启动

### 第二步：用户认证
- [ ] 后端认证接口测试通过
- [ ] 前端登录页面完成
- [ ] 路由守卫生效
- [ ] Token 持久化

### 第三步：文档CRUD
- [ ] 创建文档
- [ ] 文档列表
- [ ] 文档详情
- [ ] 更新/删除文档

### 第四步：版本管理
- [ ] 保存版本
- [ ] 版本列表
- [ ] 版本对比
- [ ] 版本回滚

### 第五步：实时协作
- [ ] WebSocket 连接
- [ ] 编辑同步
- [ ] 光标同步
- [ ] 在线用户显示

---

## 🎯 每个步骤的验收标准

### 第一步验收
- ✅ 数据库表创建成功
- ✅ 可以执行查询操作
- ✅ 前端可以正常启动

### 第二步验收
- ✅ 可以注册用户
- ✅ 可以登录获取 Token
- ✅ 未登录无法访问受保护页面
- ✅ Token 过期后需要重新登录

### 第三步验收
- ✅ 可以创建文档
- ✅ 可以查看文档列表
- ✅ 可以编辑文档内容
- ✅ 权限控制正确（admin/editor/viewer）

### 第四步验收
- ✅ 每次保存生成新版本
- ✅ 可以查看所有版本
- ✅ 可以对比版本差异
- ✅ 可以回滚到旧版本

### 第五步验收
- ✅ 多用户可以同时编辑
- ✅ 编辑操作实时同步
- ✅ 光标位置同步显示
- ✅ 在线用户列表正确

---

## 💡 开发建议

1. **先完成后端接口，再实现前端**
   - 使用 Postman 测试所有 API
   - 确保接口返回正确的数据格式

2. **逐步测试，不要一次性实现所有功能**
   - 每完成一个小功能就测试
   - 确保当前功能正常再继续

3. **使用 Git 版本控制**
   - 每个步骤完成后提交一次
   - 方便回滚和协作

4. **遇到问题及时记录**
   - 记录错误信息和解决方案
   - 方便后续参考

---

## 📚 相关文档

- [详细实现指南](./implementation-guide.md) - 包含代码示例
- [快速开始指南](./quick-start.md) - 环境搭建步骤
- [架构概览](./architecture/architecture-overview.md) - 系统架构设计
- [API 文档](./api/rest-api.md) - REST API 接口规范
- [WebSocket 协议](./api/ws-protocol.md) - WebSocket 消息格式


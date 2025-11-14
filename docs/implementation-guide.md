# 分步实现指南

## 📋 总体实现顺序

按照依赖关系，建议按以下顺序实现：

1. **环境搭建与数据库初始化** → 基础环境
2. **用户认证系统** → 所有功能的基础
3. **文档基础CRUD** → 核心功能
4. **版本管理** → 基于文档CRUD
5. **实时协作编辑** → 最复杂的功能

---

## 第一步：环境搭建与数据库初始化

### 🎯 目标
- 配置开发环境
- 创建数据库表结构
- 初始化基础数据（角色）

### 后端要做的事

#### 1.1 创建数据库迁移脚本（Alembic）

```bash
# 在 backend 目录下执行
cd backend
alembic init alembic
```

创建初始化迁移文件 `alembic/versions/001_initial.py`：

```python
"""initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 创建 roles 表
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # 创建 users 表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # 创建 documents 表
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(150), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('current_version_id', sa.Integer(), nullable=True),
        sa.Column('is_archived', sa.Boolean(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建 document_versions 表
    op.create_table(
        'document_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id']),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_document_versions_document_id', 'document_versions', ['document_id'])
    
    # 创建 edit_logs 表
    op.create_table(
        'edit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('operation', sa.JSON(), nullable=True),
        sa.Column('cursor_position', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id']),
        sa.ForeignKeyConstraint(['version_id'], ['document_versions.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_edit_logs_document_id', 'edit_logs', ['document_id'])
    op.create_index('ix_edit_logs_user_id', 'edit_logs', ['user_id'])

def downgrade():
    op.drop_table('edit_logs')
    op.drop_table('document_versions')
    op.drop_table('documents')
    op.drop_table('users')
    op.drop_table('roles')
```

#### 1.2 创建初始化数据脚本

创建 `backend/scripts/init_data.py`：

```python
"""初始化基础数据：创建默认角色"""
from app.db.session import SessionLocal
from app.models.role import Role

def init_roles():
    db = SessionLocal()
    try:
        roles = [
            Role(name="admin", description="管理员，拥有所有权限"),
            Role(name="editor", description="编辑者，可以创建和编辑文档"),
            Role(name="viewer", description="查看者，只能查看文档"),
        ]
        for role in roles:
            existing = db.query(Role).filter(Role.name == role.name).first()
            if not existing:
                db.add(role)
        db.commit()
        print("✅ 角色初始化完成")
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_roles()
```

#### 1.3 配置 .env 文件

创建 `backend/.env`：

```env
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=mysql+mysqlconnector://root:password@localhost:3306/collab_doc
REDIS_URL=redis://localhost:6379/0
CORS_ALLOW_ORIGINS=["http://localhost:5173"]
```

#### 1.4 执行迁移

```bash
# 创建数据库（MySQL中手动创建）
mysql -u root -p
CREATE DATABASE collab_doc CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 执行迁移
alembic upgrade head

# 初始化角色数据
python scripts/init_data.py
```

### 前端要做的事

#### 1.1 安装依赖

```bash
cd frontend
npm install
```

#### 1.2 配置环境变量

创建 `frontend/.env`：

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000
```

#### 1.3 验证项目启动

```bash
npm run dev
```

---

## 第二步：用户认证系统

### 🎯 目标
- 用户注册
- 用户登录（JWT Token）
- 获取当前用户信息
- 前端路由守卫

### 后端要做的事

#### 2.1 完善认证路由（已完成基础结构）

检查 `backend/app/api/routes/auth.py`，确保：
- ✅ `/register` - 注册接口
- ✅ `/login` - 登录接口  
- ✅ `/me` - 获取当前用户
- ✅ Token 验证中间件

#### 2.2 测试认证接口

使用 Postman 或 curl 测试：

```bash
# 注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456","email":"test@example.com"}'

# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=123456"

# 获取用户信息
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 前端要做的事

#### 2.1 完善登录页面

在 `frontend/src/pages/LoginPage.vue` 中：
- ✅ 表单验证（用户名、密码必填）
- ✅ 调用登录 API
- ✅ 保存 Token 到 localStorage
- ✅ 登录成功后跳转到文档列表

#### 2.2 实现路由守卫

在 `frontend/src/router/index.ts` 中添加：

```typescript
import { useAuthStore } from "@/store";

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = !!authStore.token;
  
  if (to.name === "login") {
    if (isAuthenticated) {
      next({ name: "dashboard" });
    } else {
      next();
    }
  } else {
    if (isAuthenticated) {
      next();
    } else {
      next({ name: "login" });
    }
  }
});
```

#### 2.3 完善认证 Store

在 `frontend/src/store/index.ts` 中确保：
- ✅ `login()` - 调用登录API，保存token
- ✅ `logout()` - 清除token，跳转登录页
- ✅ `hydrateFromStorage()` - 从localStorage恢复token
- ✅ `getCurrentUser()` - 获取当前用户信息

#### 2.4 测试登录流程

1. 打开浏览器访问 `http://localhost:5173/login`
2. 输入用户名密码
3. 检查是否跳转到文档列表
4. 检查 localStorage 中是否有 token

---

## 第三步：文档基础CRUD

### 🎯 目标
- 创建文档
- 获取文档列表
- 获取单个文档详情
- 更新文档（标题）
- 删除文档（软删除）

### 后端要做的事

#### 3.1 完善文档服务层

在 `backend/app/services/document_service.py` 中实现：

```python
async def create_document(
    self, owner_id: int, title: str, initial_content: str = ""
) -> document_model.Document:
    """创建新文档，同时创建第一个版本"""
    # 1. 创建文档记录
    # 2. 创建初始版本（version_number=1）
    # 3. 关联文档的 current_version_id
    # 4. 返回文档对象
    pass

async def list_documents(
    self, user_id: int, role_name: str
) -> list[document_model.Document]:
    """根据用户权限返回文档列表"""
    # admin: 返回所有文档
    # editor/viewer: 返回自己创建的文档
    pass

async def get_document(
    self, document_id: int, user_id: int
) -> document_model.Document:
    """获取文档详情，检查权限"""
    # 检查用户是否有权限查看
    pass

async def update_document(
    self, document_id: int, user_id: int, title: str
) -> document_model.Document:
    """更新文档标题（只有owner或admin可以）"""
    pass

async def delete_document(
    self, document_id: int, user_id: int
) -> None:
    """软删除文档"""
    pass
```

#### 3.2 完善文档路由

在 `backend/app/api/routes/documents.py` 中实现：

```python
@router.post("/", response_model=DocumentDetail)
async def create_document(...):
    """创建文档"""
    pass

@router.get("/", response_model=list[DocumentSummary])
async def list_documents(...):
    """获取文档列表"""
    pass

@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(...):
    """获取文档详情"""
    pass

@router.put("/{document_id}", response_model=DocumentDetail)
async def update_document(...):
    """更新文档"""
    pass

@router.delete("/{document_id}")
async def delete_document(...):
    """删除文档"""
    pass
```

#### 3.3 测试文档接口

使用 Postman 测试所有 CRUD 操作。

### 前端要做的事

#### 3.1 完善文档列表页面

在 `frontend/src/pages/EditorPage.vue` 中：
- ✅ 调用 `DocumentService.listDocuments()` 获取列表
- ✅ 显示文档列表（侧边栏）
- ✅ 点击文档项，加载文档内容到编辑器

#### 3.2 实现创建文档功能

- ✅ 点击"新建文档"按钮
- ✅ 弹出输入框输入标题
- ✅ 调用 `DocumentService.createDocument()`
- ✅ 创建成功后自动选中新文档

#### 3.3 实现文档选择功能

- ✅ 点击侧边栏文档项
- ✅ 调用 `DocumentService.getDocument(id)` 获取详情
- ✅ 将文档内容加载到 Quill 编辑器
- ✅ 显示当前文档标题

#### 3.4 测试文档CRUD

1. 登录系统
2. 创建新文档
3. 查看文档列表
4. 选择文档，查看内容
5. 编辑文档标题

---

## 第四步：版本管理

### 🎯 目标
- 每次保存生成新版本
- 查看版本列表
- 查看历史版本内容
- 版本对比（diff）
- 回滚到指定版本

### 后端要做的事

#### 4.1 完善版本服务层

在 `backend/app/services/version_service.py` 中实现：

```python
async def save_version(
    self, document_id: int, user_id: int, content: str
) -> document_version_model.DocumentVersion:
    """保存当前内容为新版本"""
    # 1. 获取文档当前版本号
    # 2. 创建新版本（version_number + 1）
    # 3. 更新文档的 current_version_id
    # 4. 记录编辑日志
    pass

async def list_versions(
    self, document_id: int
) -> list[document_version_model.DocumentVersion]:
    """获取文档的所有版本"""
    pass

async def get_version(
    self, version_id: int
) -> document_version_model.DocumentVersion:
    """获取指定版本内容"""
    pass

async def compare_versions(
    self, document_id: int, from_version: int, to_version: int
) -> dict:
    """对比两个版本的差异"""
    # 使用 difflib 或类似库生成 diff
    pass

async def restore_version(
    self, document_id: int, version_id: int, user_id: int
) -> document_version_model.DocumentVersion:
    """回滚到指定版本（创建新版本）"""
    # 1. 获取指定版本的内容
    # 2. 创建新版本，内容为指定版本的内容
    # 3. 更新文档的 current_version_id
    pass
```

#### 4.2 完善版本路由

在 `backend/app/api/routes/versions.py` 中实现：

```python
@router.post("/{document_id}/save")
async def save_version(...):
    """保存当前内容为新版本"""
    pass

@router.get("/{document_id}/versions")
async def list_versions(...):
    """获取版本列表"""
    pass

@router.get("/{document_id}/versions/{version_id}")
async def get_version(...):
    """获取指定版本"""
    pass

@router.get("/{document_id}/compare")
async def compare_versions(...):
    """对比版本"""
    pass

@router.post("/{document_id}/restore/{version_id}")
async def restore_version(...):
    """回滚到指定版本"""
    pass
```

#### 4.3 实现版本对比算法

可以使用 Python 的 `difflib` 库：

```python
import difflib

def generate_diff(old_text: str, new_text: str) -> list[dict]:
    """生成文本差异"""
    diff = difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        lineterm=''
    )
    # 转换为结构化格式
    return [...]
```

### 前端要做的事

#### 4.1 实现保存版本功能

在 `frontend/src/pages/EditorPage.vue` 中：
- ✅ 点击工具栏"保存"按钮
- ✅ 获取编辑器内容
- ✅ 调用 `DocumentService.saveVersion(documentId, content)`
- ✅ 显示保存成功提示

#### 4.2 实现版本列表页面

在 `frontend/src/pages/VersionsPage.vue` 中：
- ✅ 调用 `DocumentService.listVersions(documentId)`
- ✅ 显示版本列表（版本号、创建时间、创建者）
- ✅ 点击版本项，查看该版本内容

#### 4.3 实现版本对比功能

- ✅ 选择两个版本进行对比
- ✅ 调用 `DocumentService.compareVersions(documentId, from, to)`
- ✅ 使用 `jsdiff` 库高亮显示差异
- ✅ 显示增加/删除/修改的内容

#### 4.4 实现版本回滚功能

- ✅ 在版本列表中点击"回滚"按钮
- ✅ 确认对话框
- ✅ 调用 `DocumentService.restoreVersion(documentId, versionId)`
- ✅ 回滚成功后刷新文档内容

#### 4.5 测试版本管理

1. 创建文档，编辑内容
2. 保存版本（多次保存）
3. 查看版本列表
4. 对比不同版本
5. 回滚到旧版本

---

## 第五步：实时协作编辑

### 🎯 目标
- WebSocket 连接管理
- 实时同步编辑操作
- 显示其他用户光标
- 显示在线用户列表

### 后端要做的事

#### 5.1 实现 WebSocket 端点

在 `backend/app/api/routes/collab.py` 中实现：

```python
@router.websocket("/ws/{document_id}")
async def websocket_endpoint(websocket: WebSocket, document_id: int, token: str):
    """WebSocket 连接处理"""
    # 1. 验证 token，获取用户信息
    # 2. 接受连接
    # 3. 将连接加入文档会话
    # 4. 广播用户加入消息
    # 5. 监听消息（编辑操作、光标更新）
    # 6. 处理操作（OT transform）
    # 7. 广播操作到其他客户端
    # 8. 处理断开连接
    pass
```

#### 5.2 实现协同服务

在 `backend/app/services/collab_service.py` 中实现：

```python
class CollaborationSession:
    """文档协作会话管理"""
    def __init__(self, document_id: int):
        self.document_id = document_id
        self.clients: dict[str, WebSocket] = {}  # client_id -> websocket
        self.document_state: str = ""  # 当前文档内容
        self.version: int = 0  # 当前版本号
    
    def add_client(self, client_id: str, websocket: WebSocket, user: User):
        """添加客户端"""
        pass
    
    def remove_client(self, client_id: str):
        """移除客户端"""
        pass
    
    def apply_operation(self, operation: dict, client_id: str):
        """应用编辑操作（OT transform）"""
        # 1. 获取操作
        # 2. 与服务器状态进行 transform
        # 3. 更新服务器状态
        # 4. 广播到其他客户端
        pass
    
    def broadcast(self, message: dict, exclude_client_id: str = None):
        """广播消息到所有客户端"""
        pass
```

#### 5.3 实现简单的 OT 算法

可以使用 `ot-text` 库或自己实现简单的文本操作转换：

```python
def transform_operation(op1: dict, op2: dict) -> dict:
    """OT transform：将 op1 转换为在 op2 之后执行的等效操作"""
    # 简化版：基于文本位置的转换
    pass
```

### 前端要做的事

#### 5.1 实现 WebSocket 连接

在 `frontend/src/pages/EditorPage.vue` 中：
- ✅ 打开文档时建立 WebSocket 连接
- ✅ 连接参数：document_id, token
- ✅ 处理连接成功/失败
- ✅ 处理断开重连

#### 5.2 实现编辑操作同步

- ✅ 监听 Quill 编辑器的 `text-change` 事件
- ✅ 将编辑操作转换为 OT 格式
- ✅ 通过 WebSocket 发送到服务器
- ✅ 接收服务器广播的操作
- ✅ 应用到本地编辑器（避免循环触发）

#### 5.3 实现光标同步

- ✅ 监听编辑器光标变化
- ✅ 发送 `cursor_update` 消息
- ✅ 接收其他用户的光标位置
- ✅ 在编辑器中显示其他用户光标（不同颜色）

#### 5.4 实现在线用户显示

- ✅ 接收 `user_joined` / `user_left` 消息
- ✅ 更新协作者列表
- ✅ 在界面上显示在线用户头像

#### 5.5 测试实时协作

1. 打开两个浏览器窗口
2. 都登录不同账号
3. 打开同一个文档
4. 在一个窗口编辑，观察另一个窗口是否同步
5. 观察光标是否同步显示

---

## 📝 检查清单

### 第一步：环境搭建
- [ ] 数据库创建成功
- [ ] Alembic 迁移执行成功
- [ ] 角色数据初始化成功
- [ ] 前端项目可以启动

### 第二步：用户认证
- [ ] 可以注册新用户
- [ ] 可以登录获取 Token
- [ ] 可以获取当前用户信息
- [ ] 前端路由守卫生效
- [ ] 未登录自动跳转到登录页

### 第三步：文档CRUD
- [ ] 可以创建文档
- [ ] 可以查看文档列表
- [ ] 可以查看文档详情
- [ ] 可以更新文档标题
- [ ] 可以删除文档

### 第四步：版本管理
- [ ] 可以保存版本
- [ ] 可以查看版本列表
- [ ] 可以查看历史版本
- [ ] 可以对比版本差异
- [ ] 可以回滚到旧版本

### 第五步：实时协作
- [ ] WebSocket 连接成功
- [ ] 编辑操作可以实时同步
- [ ] 光标位置可以同步
- [ ] 在线用户列表正确显示
- [ ] 多用户同时编辑不冲突

---

## 🚀 快速开始命令

### 后端
```bash
cd backend
# 安装依赖
pip install -r requirements.txt

# 配置 .env 文件
cp .env.example .env
# 编辑 .env 设置数据库连接

# 执行迁移
alembic upgrade head

# 初始化数据
python scripts/init_data.py

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端
```bash
cd frontend
# 安装依赖
npm install

# 配置环境变量
cp .env.example .env

# 启动开发服务器
npm run dev
```

---

## 📚 参考资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Vue 3 文档](https://vuejs.org/)
- [Quill 编辑器](https://quilljs.com/)
- [Operational Transformation 算法](https://en.wikipedia.org/wiki/Operational_transformation)
- [WebSocket 协议](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)


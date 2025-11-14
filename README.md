
# 共享文档系统

基于Flask的共享文档Web应用，使用JWT进行用户认证。

## 功能特点

- 用户注册和登录
- 基于JWT的身份认证
- 密码加密存储
- 令牌刷新机制
- 响应式UI设计
- RESTful API接口

## 技术栈

- Flask - 后端Web框架
- SQLAlchemy - 数据库ORM


## 安装与运行

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 运行应用：
   ```
   python app.py
   ```

3. 在浏览器中访问 `http://127.0.0.1:5000`

## API接口

### 认证相关

- `POST /auth/login` - 用户登录
  ```json
  {
    "username": "用户名",
    "password": "密码",
    "remember_me": "记住我"
  }
  ```

- `POST /auth/register` - 用户注册
  ```json
  {
    "username": "用户名",
    "email": "邮箱",
    "password1": "一次输入密码",
    "password2": "二次输入密码"
  }
  ```

- `POST /auth/refresh` - 刷新访问令牌
  - 需要在请求头中提供有效的刷新令牌

- `DELETE /auth/logout` - 用户登出
  - 需要在请求头中提供有效的访问令牌

## 项目结构

```
E:\Study\Shared-Document├── app.py              # 主应用文件
├── config.py           # 配置文件
├── models.py           # 数据模型
├── forms.py            # 表单处理
├── auth.py             # Web认证路由
├── api.py              # API认证路由
├── requirements.txt    # 依赖包列表
├── templates\          # HTML模板
│   ├── base.html       # 基础模板
│   ├── login.html      # 登录页面
│   ├── register.html   # 注册页面
│   └── index.html      # 首页
└── README.md           # 项目说明
```

## JWT认证说明

本应用使用JWT(JSON Web Token)进行用户认证，主要特点：

1. **无状态认证**：服务器不保存会话状态，所有必要信息存储在令牌中
2. **令牌过期机制**：访问令牌短期有效(1小时)，刷新令牌长期有效(30天)
3. **令牌刷新**：当访问令牌过期时，可以使用刷新令牌获取新的访问令牌
4. **令牌注销**：支持令牌黑名单机制，实现主动注销功能

## 下一步开发计划

- 文档上传功能
- 文档列表展示
- 文档搜索功能
- 文档分享与权限控制
- 用户个人资料管理

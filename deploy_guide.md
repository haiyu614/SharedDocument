# 部署指南 - 让其他人访问你的共享文档系统

## 方案一：部署到现有服务器（8.138.190.109）⭐推荐

### 1. 连接到服务器
```bash
ssh root@8.138.190.109
```

### 2. 安装必要软件
```bash
# 更新系统
apt update && apt upgrade -y  # Ubuntu/Debian
# 或
yum update -y  # CentOS

# 安装 Python 3 和 pip
apt install python3 python3-pip python3-venv -y

# 安装 Nginx（反向代理）
apt install nginx -y
```

### 3. 上传项目文件
在本地电脑执行：
```bash
# 方法1: 使用 scp
scp -r c:\Users\Administrator\Desktop\SharedDocument-tchen root@8.138.190.109:/var/www/

# 方法2: 使用 Git（推荐）
# 先在本地初始化 Git 仓库
cd c:\Users\Administrator\Desktop\SharedDocument-tchen
git init
git add .
git commit -m "Initial commit"
# 推送到 GitHub/Gitee
git remote add origin <你的仓库地址>
git push -u origin main

# 然后在服务器上克隆
ssh root@8.138.190.109
cd /var/www
git clone <你的仓库地址> SharedDocument-tchen
```

### 4. 在服务器上配置项目
```bash
cd /var/www/SharedDocument-tchen

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装生产环境服务器
pip install gunicorn
```

### 5. 修改配置文件
创建生产环境配置：
```bash
nano production_config.py
```

内容：
```python
import os
from datetime import timedelta

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-production-secret-key-change-this'
    
    # 数据库配置（使用本地连接，因为在同一服务器）
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/shared_documents'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # 文件上传配置
    UPLOAD_FOLDER = '/var/www/SharedDocument-tchen/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # JWT 配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-production-secret-key-change-this'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/'
    JWT_COOKIE_SECURE = True  # 生产环境启用 HTTPS
    JWT_COOKIE_SAMESITE = 'Lax'
    
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = True  # 生产环境启用 HTTPS
```

### 6. 创建 Gunicorn 启动脚本
```bash
nano start.sh
```

内容：
```bash
#!/bin/bash
cd /var/www/SharedDocument-tchen
source venv/bin/activate
gunicorn -k eventlet -w 1 --bind 127.0.0.1:5000 "app:create_app()"
```

赋予执行权限：
```bash
chmod +x start.sh
```

### 7. 配置 Systemd 服务（开机自启）
```bash
nano /etc/systemd/system/shareddoc.service
```

内容：
```ini
[Unit]
Description=Shared Document System
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/SharedDocument-tchen
Environment="PATH=/var/www/SharedDocument-tchen/venv/bin"
ExecStart=/var/www/SharedDocument-tchen/venv/bin/gunicorn -k eventlet -w 1 --bind 127.0.0.1:5000 "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
systemctl daemon-reload
systemctl start shareddoc
systemctl enable shareddoc
systemctl status shareddoc
```

### 8. 配置 Nginx 反向代理
```bash
nano /etc/nginx/sites-available/shareddoc
```

内容：
```nginx
server {
    listen 80;
    server_name 8.138.190.109;  # 或你的域名

    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_read_timeout 86400;
    }

    location /static {
        alias /var/www/SharedDocument-tchen/static;
    }
}
```

启用配置：
```bash
ln -s /etc/nginx/sites-available/shareddoc /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 9. 配置防火墙
```bash
# 开放 80 端口（HTTP）
ufw allow 80/tcp
# 开放 443 端口（HTTPS，如果配置了 SSL）
ufw allow 443/tcp
```

### 10. 访问应用
现在其他人可以通过以下地址访问：
```
http://8.138.190.109
```

---

## 方案二：使用内网穿透（快速测试）

如果只是临时让别人访问，可以使用内网穿透工具：

### 使用 ngrok
```bash
# 下载 ngrok: https://ngrok.com/download
# 注册账号获取 authtoken

# 启动穿透
ngrok http 5000
```

会得到一个公网地址，如：`https://abc123.ngrok.io`

### 使用 frp（免费开源）
1. 在有公网 IP 的服务器上部署 frps（服务端）
2. 在本地运行 frpc（客户端）
3. 配置端口映射

---

## 方案三：使用云平台部署

### 3.1 阿里云/腾讯云 ECS
1. 购买云服务器（最低配置即可）
2. 按照方案一的步骤部署

### 3.2 Heroku（国外，免费额度）
```bash
# 创建 Procfile
echo "web: gunicorn -k eventlet -w 1 app:create_app()" > Procfile

# 部署
heroku login
heroku create your-app-name
git push heroku main
```

### 3.3 Railway.app（推荐，简单）
1. 访问 https://railway.app
2. 连接 GitHub 仓库
3. 自动部署

---

## 配置域名（可选）

如果有域名，配置 DNS A 记录指向服务器 IP：
```
A记录: @ -> 8.138.190.109
A记录: www -> 8.138.190.109
```

然后修改 Nginx 配置中的 `server_name`。

---

## 配置 HTTPS（推荐）

使用 Let's Encrypt 免费证书：
```bash
# 安装 certbot
apt install certbot python3-certbot-nginx -y

# 自动配置 SSL
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期
certbot renew --dry-run
```

---

## 常见问题

### Q1: 其他人访问不了？
- 检查服务器防火墙是否开放 80 端口
- 检查云服务商的安全组规则
- 确认 Nginx 和 Gunicorn 都在运行

### Q2: WebSocket 连接失败？
- 确认 Nginx 配置了 WebSocket 支持
- 检查防火墙没有阻止 WebSocket 连接

### Q3: 文件上传失败？
- 确认 uploads 目录有写权限：`chmod 777 /var/www/SharedDocument-tchen/uploads`
- 检查 Nginx 的 `client_max_body_size` 配置

---

## 安全建议

1. **修改默认密钥**：更改 `SECRET_KEY` 和 `JWT_SECRET_KEY`
2. **启用 HTTPS**：使用 SSL 证书
3. **限制数据库访问**：只允许本地连接
4. **定期备份**：备份数据库和上传的文件
5. **更新依赖**：定期更新 Python 包

---

## 监控和维护

### 查看日志
```bash
# 应用日志
journalctl -u shareddoc -f

# Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 重启服务
```bash
systemctl restart shareddoc
systemctl restart nginx
```

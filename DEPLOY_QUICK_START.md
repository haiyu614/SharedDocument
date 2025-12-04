# 🚀 快速部署指南

## 最简单的方法：部署到你的服务器 8.138.190.109

### 前提条件
- 你已经有服务器：`8.138.190.109`
- 服务器上已经运行 MySQL
- 你有 SSH 访问权限

---

## 📋 部署步骤（复制粘贴即可）

### 第一步：连接服务器
```bash
ssh root@8.138.190.109
```

### 第二步：安装必要软件（一次性）
```bash
# 更新系统
apt update && apt upgrade -y

# 安装 Python 和工具
apt install python3 python3-pip python3-venv nginx git -y

# 创建项目目录
mkdir -p /var/www
cd /var/www
```

### 第三步：上传项目文件

**方法A：使用 Git（推荐）**
```bash
# 在本地电脑先初始化 Git
cd c:\Users\Administrator\Desktop\SharedDocument-tchen
git init
git add .
git commit -m "Initial commit"

# 推送到 GitHub/Gitee（需要先创建仓库）
git remote add origin https://github.com/你的用户名/SharedDocument-tchen.git
git push -u origin main

# 在服务器上克隆
cd /var/www
git clone https://github.com/你的用户名/SharedDocument-tchen.git
```

**方法B：使用 SCP 直接上传**

在本地 PowerShell 执行：
```powershell
# 压缩项目（排除不必要的文件）
Compress-Archive -Path "c:\Users\Administrator\Desktop\SharedDocument-tchen\*" `
  -DestinationPath "c:\Users\Administrator\Desktop\SharedDocument.zip" `
  -Force

# 上传到服务器
scp "c:\Users\Administrator\Desktop\SharedDocument.zip" root@8.138.190.109:/var/www/

# 在服务器上解压
ssh root@8.138.190.109
cd /var/www
apt install unzip -y
unzip SharedDocument.zip -d SharedDocument-tchen
```

### 第四步：配置项目环境
```bash
cd /var/www/SharedDocument-tchen

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建上传目录
mkdir -p uploads
chmod 755 uploads

# 初始化数据库（如果需要）
python3 init_db.py
```

### 第五步：配置 Systemd 服务
```bash
# 复制服务文件
cp shareddoc.service /etc/systemd/system/

# 启动服务
systemctl daemon-reload
systemctl start shareddoc
systemctl enable shareddoc

# 检查状态
systemctl status shareddoc
```

### 第六步：配置 Nginx
```bash
# 复制配置文件
cp nginx.conf /etc/nginx/sites-available/shareddoc

# 修改配置中的域名/IP
nano /etc/nginx/sites-available/shareddoc
# 将 server_name 改为: 8.138.190.109

# 启用配置
ln -s /etc/nginx/sites-available/shareddoc /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default  # 删除默认配置

# 测试配置
nginx -t

# 重启 Nginx
systemctl restart nginx
```

### 第七步：配置防火墙
```bash
# 开放 HTTP 端口
ufw allow 80/tcp
ufw allow 443/tcp

# 如果防火墙未启用
ufw enable
```

### 第八步：访问应用
在浏览器打开：
```
http://8.138.190.109
```

---

## ✅ 验证部署

### 检查服务状态
```bash
# 检查应用服务
systemctl status shareddoc

# 检查 Nginx
systemctl status nginx

# 查看应用日志
journalctl -u shareddoc -f

# 查看 Nginx 日志
tail -f /var/log/nginx/error.log
```

### 测试功能
1. 访问 `http://8.138.190.109`
2. 注册新用户
3. 登录系统
4. 上传文件
5. 分享文件给其他用户
6. 测试实时协作编辑

---

## 🔧 常见问题解决

### 问题1：无法访问网站
```bash
# 检查服务是否运行
systemctl status shareddoc
systemctl status nginx

# 检查端口是否监听
netstat -tlnp | grep 5000
netstat -tlnp | grep 80

# 检查防火墙
ufw status
```

### 问题2：应用启动失败
```bash
# 查看详细日志
journalctl -u shareddoc -n 50

# 手动启动测试
cd /var/www/SharedDocument-tchen
source venv/bin/activate
python3 wsgi.py
```

### 问题3：数据库连接失败
```bash
# 测试数据库连接
mysql -u root -p123456 -h localhost shared_documents

# 如果连接失败，修改配置
nano production_config.py
# 确认数据库地址、用户名、密码正确
```

### 问题4：WebSocket 不工作
```bash
# 检查 Nginx 配置是否包含 WebSocket 支持
nano /etc/nginx/sites-available/shareddoc
# 确认有这些行：
# proxy_set_header Upgrade $http_upgrade;
# proxy_set_header Connection "upgrade";

# 重启 Nginx
systemctl restart nginx
```

---

## 🔐 安全加固（重要！）

### 1. 修改密钥
```bash
nano /var/www/SharedDocument-tchen/production_config.py
```
修改这两行：
```python
SECRET_KEY = 'your-random-secret-key-here-change-this'
JWT_SECRET_KEY = 'your-jwt-secret-key-here-change-this'
```

生成随机密钥：
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. 配置 HTTPS（强烈推荐）
```bash
# 安装 certbot
apt install certbot python3-certbot-nginx -y

# 如果有域名，自动配置 SSL
certbot --nginx -d yourdomain.com

# 如果只有 IP，可以使用自签名证书（测试用）
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt
```

### 3. 限制数据库访问
```bash
# 修改 MySQL 配置，只允许本地访问
nano /etc/mysql/mysql.conf.d/mysqld.cnf
# 添加或修改：
# bind-address = 127.0.0.1

# 重启 MySQL
systemctl restart mysql
```

---

## 📱 告诉其他人如何访问

其他人只需要：
1. 在浏览器打开：`http://8.138.190.109`
2. 注册账号
3. 登录后即可使用

你可以分享文档给他们：
1. 上传文档
2. 点击"分享"按钮
3. 输入对方用户名
4. 选择权限（查看/编辑）
5. 对方在"与我共享"中查看

---

## 🔄 更新应用

当你修改代码后：
```bash
# 在服务器上
cd /var/www/SharedDocument-tchen
git pull  # 如果使用 Git

# 或重新上传文件
# scp ...

# 重启服务
systemctl restart shareddoc
```

---

## 📊 监控和维护

### 查看访问日志
```bash
tail -f /var/log/nginx/access.log
```

### 查看应用日志
```bash
journalctl -u shareddoc -f
```

### 备份数据
```bash
# 备份数据库
mysqldump -u root -p123456 shared_documents > backup_$(date +%Y%m%d).sql

# 备份上传的文件
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz /var/www/SharedDocument-tchen/uploads
```

---

## 💡 性能优化建议

1. **增加 Gunicorn worker 数量**（如果服务器配置好）
   ```bash
   nano /etc/systemd/system/shareddoc.service
   # 修改：-w 1 改为 -w 4
   ```

2. **启用 Nginx 缓存**
3. **使用 Redis 缓存会话**
4. **配置 CDN 加速静态资源**

---

## 🎉 完成！

现在你的共享文档系统已经部署成功，其他人可以通过公网访问了！

如有问题，查看日志或联系管理员。

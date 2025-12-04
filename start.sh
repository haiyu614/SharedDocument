#!/bin/bash

# 启动脚本

cd "$(dirname "$0")"

# 激活虚拟环境
source venv/bin/activate

# 设置环境变量
export FLASK_ENV=production

# 启动 Gunicorn
gunicorn -k eventlet -w 1 --bind 127.0.0.1:5000 wsgi:app

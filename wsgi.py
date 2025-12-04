"""
WSGI 入口文件
用于 Gunicorn 等 WSGI 服务器
"""
import os
from app import create_app, socketio

# 根据环境变量选择配置
env = os.environ.get('FLASK_ENV', 'development')

if env == 'production':
    from production_config import ProductionConfig
    app = create_app(ProductionConfig)
else:
    app = create_app()

if __name__ == '__main__':
    # 开发环境使用 socketio.run
    socketio.run(app, debug=True)

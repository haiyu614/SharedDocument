import os
from datetime import timedelta


class ProductionConfig:
    """生产环境配置"""
    
    # 基本配置 - 务必修改为随机字符串
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'CHANGE-THIS-TO-RANDOM-STRING-IN-PRODUCTION'
    
    # 数据库配置
    # 如果部署在同一服务器，使用 localhost
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:123456@localhost:3306/shared_documents'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = True  # 生产环境使用 HTTPS
    SESSION_COOKIE_HTTPONLY = True
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or \
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # JWT 配置 - 务必修改为随机字符串
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'CHANGE-THIS-JWT-SECRET-IN-PRODUCTION'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False  # 如需更高安全性可启用
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/'
    JWT_COOKIE_SECURE = True  # 生产环境使用 HTTPS
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_COOKIE_HTTPONLY = True

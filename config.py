
import os
from datetime import timedelta

class Config:
    SESSION_COOKIE_SAMESITE = None  # 或者 'Lax' 或 'Strict'

    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:123456@8.138.190.109:3306/shared_documents'    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # Extend token life to 1 hour
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False  # 简化开发，生产环境建议开启
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/'
    JWT_COOKIE_SECURE = False  # 开发环境设为False

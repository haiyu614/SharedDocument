
import os
from datetime import timedelta

class Config:
    SESSION_COOKIE_SAMESITE = None  # 或者 'Lax' 或 'Strict'

    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:@127.0.0.1:3306/shared_documents'    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

"""应用配置：从 .env 文件加载，支持 MySQL 和 SQLite 双模式"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

    # 数据库选择
    use_sqlite = os.getenv('DB_USE_SQLITE', 'false').lower() == 'true'

    if use_sqlite:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///boke_system.db'
    else:
        DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
        DB_PORT = os.getenv('DB_PORT', '3306')
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '123456')
        DB_NAME = os.getenv('DB_NAME', 'boke_system')
        DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')
        SQLALCHEMY_DATABASE_URI = (
            f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
            f'?charset={DB_CHARSET}'
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 上传配置
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'app', 'static', 'upload'
    )
    AVATAR_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'app', 'static', 'image'
    )

    # JWT / Token 过期时间（秒）
    JWT_EXPIRATION_SECONDS = 7 * 24 * 3600

    # 分页
    PER_PAGE = 10
    ADMIN_PER_PAGE = 15

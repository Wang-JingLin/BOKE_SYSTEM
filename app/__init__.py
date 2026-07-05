"""Flask 应用工厂"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录后再访问此页面'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 注册蓝图（article 已包含 / 根路由，不再额外注册）
    from app.routes.auth import auth_bp
    from app.routes.article import article_bp
    from app.routes.comment import comment_bp
    from app.routes.like_collect import like_collect_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(article_bp, url_prefix='/')
    app.register_blueprint(comment_bp, url_prefix='/comment')
    app.register_blueprint(like_collect_bp, url_prefix='/interact')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # 首次运行时自动建表（方便开发，生产环境建议用 flask db upgrade）
    with app.app_context():
        from app.models import User, Article, Category, Tag, Comment, Like, Favorite
        db.create_all()

    # 错误处理
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('errors/500.html'), 500

    return app

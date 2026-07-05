"""数据库模型：用户、分类、标签、文章、评论、点赞、收藏"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager


# ---------- 关联表 ----------
article_tags = db.Table(
    'article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
)


# ---------- 用户 ----------
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    avatar = db.Column(db.String(256), default='default_avatar.png')
    bio = db.Column(db.String(256), default='')
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关系
    articles = db.relationship('Article', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def article_count(self):
        return self.articles.count()

    @property
    def comment_count(self):
        return self.comments.count()

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------- 分类 ----------
class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(128), default='')
    created_at = db.Column(db.DateTime, default=datetime.now)

    articles = db.relationship('Article', backref='category', lazy='dynamic')

    @property
    def article_count(self):
        return self.articles.filter(Article.is_published == True).count()

    def __repr__(self):
        return f'<Category {self.name}>'


# ---------- 标签 ----------
class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    @property
    def article_count(self):
        return db.session.query(article_tags).filter_by(tag_id=self.id).count()

    def __repr__(self):
        return f'<Tag {self.name}>'


# ---------- 文章 ----------
class Article(db.Model):
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(256), default='')
    cover_image = db.Column(db.String(256), default='')
    is_published = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='SET NULL'), nullable=True)

    # 关系
    tags = db.relationship('Tag', secondary=article_tags, backref=db.backref('articles', lazy='dynamic'),
                           lazy='dynamic')
    comments = db.relationship('Comment', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='article', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.filter(Comment.is_deleted == False).count()

    @property
    def favorite_count(self):
        return self.favorites.count()

    @property
    def tag_list(self):
        return self.tags.all()

    def __repr__(self):
        return f'<Article {self.title}>'


# ---------- 评论 ----------
class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'), nullable=True)

    # 父评论（回复关系）
    parent = db.relationship('Comment', remote_side=[id], backref='replies')

    @property
    def reply_count(self):
        return Comment.query.filter_by(parent_id=self.id, is_deleted=False).count()

    def __repr__(self):
        return f'<Comment {self.id}>'


# ---------- 点赞 ----------
class Like(db.Model):
    __tablename__ = 'like'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'article_id', name='uq_user_article_like'),)

    def __repr__(self):
        return f'<Like user={self.user_id} article={self.article_id}>'


# ---------- 收藏 ----------
class Favorite(db.Model):
    __tablename__ = 'favorite'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'article_id', name='uq_user_article_favorite'),)

    def __repr__(self):
        return f'<Favorite user={self.user_id} article={self.article_id}>'

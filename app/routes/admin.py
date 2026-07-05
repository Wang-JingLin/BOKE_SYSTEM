"""后台管理路由：用户管理、文章管理、分类管理、标签管理"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import User, Article, Category, Tag, Comment
from app.utils import paginate

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """管理员装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """管理后台首页"""
    user_count = User.query.count()
    article_count = Article.query.count()
    comment_count = Comment.query.filter_by(is_deleted=False).count()
    category_count = Category.query.count()
    tag_count = Tag.query.count()

    recent_articles = Article.query.order_by(
        db.desc('created_at')
    ).limit(5).all()

    return render_template('admin/dashboard.html',
                           user_count=user_count,
                           article_count=article_count,
                           comment_count=comment_count,
                           category_count=category_count,
                           tag_count=tag_count,
                           recent_articles=recent_articles)


# ---------- 文章管理 ----------
@admin_bp.route('/articles')
@login_required
@admin_required
def article_list():
    """文章列表管理"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')

    query = Article.query
    if status == 'published':
        query = query.filter_by(is_published=True)
    elif status == 'draft':
        query = query.filter_by(is_published=False)

    query = query.order_by(db.desc('created_at'))
    result = paginate(query, page, per_page=15)
    return render_template('admin/articles.html', articles=result, status=status)


@admin_bp.route('/articles/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_article(id):
    """切换文章发布/草稿状态"""
    article = db.session.get(Article, id)
    if not article:
        abort(404)
    article.is_published = not article.is_published
    db.session.commit()
    flash(f'文章"{article.title}"状态已切换', 'success')
    return redirect(url_for('admin.article_list'))


# ---------- 分类管理 ----------
@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def category_list():
    """分类管理"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        desc = request.form.get('description', '').strip()
        if name:
            if Category.query.filter_by(name=name).first():
                flash('分类名称已存在', 'danger')
            else:
                category = Category(name=name, description=desc)
                db.session.add(category)
                db.session.commit()
                flash('分类创建成功', 'success')
        return redirect(url_for('admin.category_list'))

    categories = Category.query.order_by(db.asc('id')).all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_category(id):
    """编辑分类"""
    category = db.session.get(Category, id)
    if not category:
        abort(404)

    name = request.form.get('name', '').strip()
    desc = request.form.get('description', '').strip()
    if name:
        existing = Category.query.filter_by(name=name).first()
        if existing and existing.id != id:
            flash('分类名称已存在', 'danger')
        else:
            category.name = name
            category.description = desc
            db.session.commit()
            flash('分类已更新', 'success')

    return redirect(url_for('admin.category_list'))


@admin_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    """删除分类"""
    category = db.session.get(Category, id)
    if not category:
        abort(404)
    # 将属于此分类的文章设为未分类
    Article.query.filter_by(category_id=id).update({'category_id': None})
    db.session.delete(category)
    db.session.commit()
    flash('分类已删除', 'success')
    return redirect(url_for('admin.category_list'))


# ---------- 标签管理 ----------
@admin_bp.route('/tags', methods=['GET', 'POST'])
@login_required
@admin_required
def tag_list():
    """标签管理"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            if Tag.query.filter_by(name=name).first():
                flash('标签名称已存在', 'danger')
            else:
                tag = Tag(name=name)
                db.session.add(tag)
                db.session.commit()
                flash('标签创建成功', 'success')
        return redirect(url_for('admin.tag_list'))

    tags = Tag.query.order_by(db.asc('id')).all()
    return render_template('admin/tags.html', tags=tags)


@admin_bp.route('/tags/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_tag(id):
    """删除标签"""
    tag = db.session.get(Tag, id)
    if not tag:
        abort(404)
    db.session.delete(tag)
    db.session.commit()
    flash('标签已删除', 'success')
    return redirect(url_for('admin.tag_list'))


# ---------- 用户管理 ----------
@admin_bp.route('/users')
@login_required
@admin_required
def user_list():
    """用户列表"""
    page = request.args.get('page', 1, type=int)
    query = User.query.order_by(db.desc('created_at'))
    result = paginate(query, page, per_page=15)
    return render_template('admin/users.html', users=result)


@admin_bp.route('/users/<int:id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(id):
    """切换管理员状态"""
    user = db.session.get(User, id)
    if not user:
        abort(404)
    if user.id == current_user.id:
        flash('不能取消自己的管理员权限', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'用户"{user.username}"权限已更新', 'success')
    return redirect(url_for('admin.user_list'))


@admin_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    """删除用户"""
    user = db.session.get(User, id)
    if not user:
        abort(404)
    if user.id == current_user.id:
        flash('不能删除自己的账号', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'用户"{user.username}"已删除', 'success')
    return redirect(url_for('admin.user_list'))


# ---------- 评论管理 ----------
@admin_bp.route('/comments')
@login_required
@admin_required
def comment_list():
    """评论管理"""
    page = request.args.get('page', 1, type=int)
    query = Comment.query.order_by(db.desc('created_at'))
    result = paginate(query, page, per_page=15)
    return render_template('admin/comments.html', comments=result)


@admin_bp.route('/comments/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_comment(id):
    """管理员删除评论"""
    comment = db.session.get(Comment, id)
    if not comment:
        abort(404)
    comment.is_deleted = True
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect(url_for('admin.comment_list'))

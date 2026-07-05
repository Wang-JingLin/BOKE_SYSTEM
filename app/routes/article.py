"""文章路由：列表、详情、发布、编辑、删除、分类、标签、搜索"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Article, Category, Tag
from app.forms import ArticleForm
from app.utils import paginate, save_image

article_bp = Blueprint('article', __name__)


@article_bp.route('/index')
@article_bp.route('/')
def index():
    """文章首页"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', 0, type=int)
    tag_id = request.args.get('tag', 0, type=int)

    query = Article.query.filter_by(is_published=True)

    if category_id:
        query = query.filter_by(category_id=category_id)
    if tag_id:
        tag = db.session.get(Tag, tag_id)
        if tag:
            query = query.filter(Article.tags.contains(tag))

    query = query.order_by(db.desc('created_at'))
    result = paginate(query, page)

    categories = Category.query.all()
    tags = Tag.query.all()
    # 标签文章数统计（用于标签云字号）
    from app.models import article_tags
    tag_counts = dict(
        db.session.query(article_tags.c.tag_id, db.func.count(article_tags.c.article_id))
        .group_by(article_tags.c.tag_id).all()
    )

    hot_articles = Article.query.filter_by(is_published=True).order_by(
        db.desc('view_count')
    ).limit(5).all()

    return render_template('article/index.html',
                           articles=result,
                           categories=categories,
                           tags=tags,
                           tag_counts=tag_counts,
                           hot_articles=hot_articles,
                           current_category=category_id,
                           current_tag=tag_id)


@article_bp.route('/article/<int:id>')
def detail(id):
    """文章详情"""
    article = db.session.get(Article, id)
    if not article or not article.is_published:
        abort(404)

    # 增加浏览量
    article.view_count += 1
    db.session.commit()

    # 获取上一篇和下一篇
    prev_article = Article.query.filter(
        Article.is_published == True,
        Article.created_at < article.created_at
    ).order_by(db.desc('created_at')).first()

    next_article = Article.query.filter(
        Article.is_published == True,
        Article.created_at > article.created_at
    ).order_by(db.asc('created_at')).first()

    # 获取评论
    from app.models import Comment
    comments = Comment.query.filter_by(
        article_id=id, parent_id=None, is_deleted=False
    ).order_by(db.desc('created_at')).all()

    # 当前用户是否点赞/收藏
    user_liked = False
    user_favorited = False
    if current_user.is_authenticated:
        from app.models import Like, Favorite
        user_liked = Like.query.filter_by(
            user_id=current_user.id, article_id=id
        ).first() is not None
        user_favorited = Favorite.query.filter_by(
            user_id=current_user.id, article_id=id
        ).first() is not None

    return render_template('article/detail.html',
                           article=article,
                           prev_article=prev_article,
                           next_article=next_article,
                           comments=comments,
                           user_liked=user_liked,
                           user_favorited=user_favorited)


@article_bp.route('/article/new', methods=['GET', 'POST'])
@login_required
def create():
    """发布文章"""
    form = ArticleForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        article = Article(
            title=form.title.data,
            content=form.content.data,
            summary=form.summary.data or form.title.data,
            user_id=current_user.id,
            category_id=form.category_id.data,
            is_published=form.is_published.data
        )

        # 封面图片
        cover = request.files.get('cover_image')
        if cover and cover.filename:
            filename = save_image(cover)
            article.cover_image = filename

        # 处理标签
        tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
                db.session.add(tag)
            article.tags.append(tag)

        db.session.add(article)
        db.session.commit()
        flash('文章发布成功！', 'success')
        return redirect(url_for('article.detail', id=article.id))

    return render_template('article/create.html', form=form)


@article_bp.route('/article/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """编辑文章"""
    article = db.session.get(Article, id)
    if not article:
        abort(404)
    if article.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    form = ArticleForm(obj=article)
    # 修复 tags：SQLAlchemy 关系对象需转成逗号字符串
    if article.tags is not None:
        try:
            form.tags.data = ','.join([t.name for t in article.tags])
        except TypeError:
            pass  # 已经是字符串，保留原值
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        article.title = form.title.data
        article.content = form.content.data
        article.summary = form.summary.data
        article.category_id = form.category_id.data
        article.is_published = form.is_published.data

        # 封面图片
        cover = request.files.get('cover_image')
        if cover and cover.filename:
            filename = save_image(cover)
            article.cover_image = filename

        # 更新标签
        article.tags = []
        tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
                db.session.add(tag)
            article.tags.append(tag)

        db.session.commit()
        flash('文章已更新！', 'success')
        return redirect(url_for('article.detail', id=article.id))

    # 回填标签
    form.tags.data = ','.join([t.name for t in article.tags])
    return render_template('article/edit.html', form=form, article=article)


@article_bp.route('/article/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """删除文章"""
    article = db.session.get(Article, id)
    if not article:
        abort(404)
    if article.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    db.session.delete(article)
    db.session.commit()
    flash('文章已删除', 'success')
    return redirect(url_for('article.index'))


@article_bp.route('/search')
def search():
    """搜索文章"""
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    if not q:
        return redirect(url_for('article.index'))

    query = Article.query.filter(
        Article.is_published == True,
        db.or_(
            Article.title.like(f'%{q}%'),
            Article.content.like(f'%{q}%'),
            Article.summary.like(f'%{q}%')
        )
    ).order_by(db.desc('created_at'))

    result = paginate(query, page)
    return render_template('article/search.html', articles=result, keyword=q)

"""点赞与收藏路由"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Like, Favorite, Article

like_collect_bp = Blueprint('like_collect', __name__)


@like_collect_bp.route('/like/<int:article_id>', methods=['POST'])
@login_required
def toggle_like(article_id):
    """切换点赞状态"""
    article = db.session.get(Article, article_id)
    if not article:
        return jsonify({'error': '文章不存在'}), 404

    like = Like.query.filter_by(
        user_id=current_user.id,
        article_id=article_id
    ).first()

    if like:
        db.session.delete(like)
        liked = False
    else:
        like = Like(user_id=current_user.id, article_id=article_id)
        db.session.add(like)
        liked = True

    db.session.commit()
    count = Like.query.filter_by(article_id=article_id).count()

    return jsonify({'liked': liked, 'count': count})


@like_collect_bp.route('/favorite/<int:article_id>', methods=['POST'])
@login_required
def toggle_favorite(article_id):
    """切换收藏状态"""
    article = db.session.get(Article, article_id)
    if not article:
        return jsonify({'error': '文章不存在'}), 404

    fav = Favorite.query.filter_by(
        user_id=current_user.id,
        article_id=article_id
    ).first()

    if fav:
        db.session.delete(fav)
        favorited = False
    else:
        fav = Favorite(user_id=current_user.id, article_id=article_id)
        db.session.add(fav)
        favorited = True

    db.session.commit()
    count = Favorite.query.filter_by(article_id=article_id).count()

    return jsonify({'favorited': favorited, 'count': count})


@like_collect_bp.route('/favorites')
@login_required
def my_favorites():
    """我的收藏"""
    from flask import render_template
    from app.utils import paginate

    page = request.args.get('page', 1, type=int)
    query = Favorite.query.filter_by(user_id=current_user.id).order_by(
        db.desc(Favorite.created_at)
    )
    result = paginate(query, page)
    return render_template('auth/favorites.html', favorites=result)

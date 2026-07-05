"""评论路由：发表评论、回复、删除评论"""
from flask import Blueprint, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app import db
from app.models import Comment, Article

comment_bp = Blueprint('comment', __name__)


@comment_bp.route('/post/<int:article_id>', methods=['POST'])
@login_required
def post_comment(article_id):
    """发表评论"""
    article = db.session.get(Article, article_id)
    if not article or not article.is_published:
        abort(404)

    content = request.form.get('content', '').strip()
    if not content:
        flash('评论内容不能为空', 'danger')
        return redirect(url_for('article.detail', id=article_id))

    if len(content) > 1000:
        flash('评论内容不能超过1000字', 'danger')
        return redirect(url_for('article.detail', id=article_id))

    comment = Comment(
        content=content,
        user_id=current_user.id,
        article_id=article_id
    )
    db.session.add(comment)
    db.session.commit()
    flash('评论发表成功', 'success')
    return redirect(url_for('article.detail', id=article_id))


@comment_bp.route('/reply/<int:comment_id>', methods=['POST'])
@login_required
def reply_comment(comment_id):
    """回复评论"""
    parent = db.session.get(Comment, comment_id)
    if not parent or parent.is_deleted:
        abort(404)

    content = request.form.get('content', '').strip()
    if not content:
        flash('回复内容不能为空', 'danger')
        return redirect(url_for('article.detail', id=parent.article_id))

    if len(content) > 1000:
        flash('回复内容不能超过1000字', 'danger')
        return redirect(url_for('article.detail', id=parent.article_id))

    reply = Comment(
        content=content,
        user_id=current_user.id,
        article_id=parent.article_id,
        parent_id=parent.id
    )
    db.session.add(reply)
    db.session.commit()
    flash('回复成功', 'success')
    return redirect(url_for('article.detail', id=parent.article_id))


@comment_bp.route('/delete/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """删除评论（软删除）"""
    comment = db.session.get(Comment, comment_id)
    if not comment:
        abort(404)
    if comment.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    comment.is_deleted = True
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect(url_for('article.detail', id=comment.article_id))

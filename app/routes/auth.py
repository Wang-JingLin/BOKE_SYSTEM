"""认证路由：登录、注册、退出、个人中心"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegisterForm
from app.utils import save_image

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('article.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'欢迎回来，{user.username}！', 'success')
            return redirect(next_page or url_for('article.index'))
        flash('用户名或密码错误', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('article.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录！', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """退出登录"""
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('article.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """个人中心"""
    if request.method == 'POST':
        # 更新个人信息
        current_user.bio = request.form.get('bio', '')

        # 头像上传
        avatar_file = request.files.get('avatar')
        if avatar_file and avatar_file.filename:
            filename = save_image(avatar_file, sub_dir='image')
            current_user.avatar = filename

        db.session.commit()
        flash('个人信息已更新', 'success')
        return redirect(url_for('auth.profile'))

    # 获取用户的文章和收藏
    page = request.args.get('page', 1, type=int)
    from app.utils import paginate
    articles = paginate(
        current_user.articles.order_by(db.desc('created_at')),
        page, per_page=10
    )
    return render_template('auth/profile.html', articles=articles)

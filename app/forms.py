"""WTForms 表单：登录、注册、文章发布/编辑、评论"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('用户名', validators=[DataRequired('请输入用户名'), Length(1, 32)])
    password = PasswordField('密码', validators=[DataRequired('请输入密码')])
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    """注册表单"""
    username = StringField('用户名', validators=[
        DataRequired('请输入用户名'), Length(2, 32, '用户名长度2-32个字符')
    ])
    email = StringField('邮箱', validators=[
        DataRequired('请输入邮箱'), Email('邮箱格式不正确')
    ])
    password = PasswordField('密码', validators=[
        DataRequired('请输入密码'), Length(6, 128, '密码长度至少6位')
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired('请再次输入密码'), EqualTo('password', '两次密码不一致')
    ])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')


class ArticleForm(FlaskForm):
    """文章发布/编辑表单"""
    title = StringField('标题', validators=[
        DataRequired('请输入文章标题'), Length(1, 128, '标题长度1-128个字符')
    ])
    summary = StringField('摘要', validators=[Length(0, 256)])
    content = TextAreaField('内容', validators=[DataRequired('请输入文章内容')])
    category_id = SelectField('分类', coerce=int, validators=[DataRequired('请选择分类')])
    tags = StringField('标签（多个标签用逗号分隔）', validators=[Length(0, 128)])
    cover_image = FileField('封面图片')
    is_published = BooleanField('立即发布')
    submit = SubmitField('提交')


class CommentForm(FlaskForm):
    """评论表单"""
    content = TextAreaField('评论内容', validators=[
        DataRequired('请输入评论内容'), Length(1, 1000, '评论长度1-1000个字符')
    ])
    submit = SubmitField('发表评论')

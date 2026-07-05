"""工具函数：分页、图片压缩、Token、时间处理"""
import os
import secrets
from datetime import datetime, timedelta
from PIL import Image
from flask import current_app
from itsdangerous import URLSafeTimedSerializer


def save_image(file, sub_dir='upload'):
    """保存上传的图片并压缩，返回相对路径"""
    if sub_dir == 'upload':
        base_folder = current_app.config['UPLOAD_FOLDER']
    else:
        base_folder = current_app.config['AVATAR_FOLDER']

    # 生成安全文件名
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
    allowed = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    if ext not in allowed:
        ext = 'jpg'

    filename = f'{secrets.token_hex(16)}.{ext}'
    filepath = os.path.join(base_folder, filename)

    # 压缩图片
    img = Image.open(file)
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    if sub_dir == 'upload':
        # 文章封面：最大宽度 1200
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
    else:
        # 头像：裁剪为正方形 200x200
        size = min(img.width, img.height)
        left = (img.width - size) // 2
        top = (img.height - size) // 2
        img = img.crop((left, top, left + size, top + size))
        img = img.resize((200, 200), Image.LANCZOS)

    img.save(filepath, 'JPEG', quality=85, optimize=True)
    return filename


def paginate(query, page, per_page=10):
    """通用分页函数"""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = max(1, (total + per_page - 1) // per_page)

    return {
        'items': items,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page < total_pages else None,
    }


def generate_token(data, salt='default', expires_in=3600):
    """生成安全令牌"""
    s = URLSafeTimedSerializer(
        current_app.config['SECRET_KEY'],
        salt=salt
    )
    return s.dumps(data)


def verify_token(token, salt='default', max_age=3600):
    """验证令牌"""
    s = URLSafeTimedSerializer(
        current_app.config['SECRET_KEY'],
        salt=salt
    )
    try:
        return s.loads(token, max_age=max_age)
    except Exception:
        return None


def time_ago(dt):
    """人性化时间显示"""
    if dt is None:
        return ''

    now = datetime.now()
    diff = now - dt

    seconds = diff.total_seconds()
    if seconds < 0:
        return '刚刚'

    if seconds < 60:
        return '刚刚'
    minutes = seconds // 60
    if minutes < 60:
        return f'{int(minutes)}分钟前'
    hours = minutes // 60
    if hours < 24:
        return f'{int(hours)}小时前'
    days = hours // 24
    if days < 30:
        return f'{int(days)}天前'
    months = days // 30
    if months < 12:
        return f'{int(months)}个月前'
    years = months // 12
    return f'{int(years)}年前'


def markdown_to_html(text):
    """简单的 Markdown 转 HTML（纯文本换行处理）"""
    if not text:
        return ''
    import re
    # 转义 HTML
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # 代码块
    text = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code>\2</code></pre>', text, flags=re.DOTALL)
    # 行内代码
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # 粗体/斜体
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # 换行转段落
    paragraphs = text.split('\n\n')
    paragraphs = [f'<p>{p.strip().replace(chr(10), "<br>")}</p>' for p in paragraphs if p.strip()]
    return '\n'.join(paragraphs)

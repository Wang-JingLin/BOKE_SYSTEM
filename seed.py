"""
数据库测试数据填充脚本
用法：python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Category, Tag, Article, Comment, Like, Favorite
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    print('正在清空旧数据…')
    # 按外键顺序删除
    Favorite.query.delete()
    Like.query.delete()
    Comment.query.delete()
    db.session.execute(db.text('DELETE FROM article_tags'))
    Article.query.delete()
    Tag.query.delete()
    Category.query.delete()
    User.query.delete()
    db.session.commit()
    print('旧数据已清空\n')

    # ========================================================
    # 1. 用户
    # ========================================================
    print('创建用户…')

    admin = User(
        username='admin',
        email='admin@boke.com',
        bio='系统管理员',
        is_admin=True,
    )
    admin.set_password('123456')
    db.session.add(admin)

    users_data = [
        ('小明',   'xiaoming@test.com',  '热爱编程的小学生'),
        ('张三',   'zhangsan@test.com',  '后端开发工程师'),
        ('李四',   'lisi@test.com',      '前端开发爱好者'),
        ('小红',   'xiaohong@test.com',  '产品经理一枚'),
        ('王五',   'wangwu@test.com',    '自由职业者'),
    ]
    users = [admin]
    for uname, email, bio in users_data:
        u = User(username=uname, email=email, bio=bio)
        u.set_password('123456')
        db.session.add(u)
        users.append(u)
    db.session.commit()
    print(f'  ✓ 已创建 {len(users)} 个用户（admin / 123456，含普通用户）')

    # ========================================================
    # 2. 分类
    # ========================================================
    print('创建分类…')
    categories_data = [
        ('技术前沿',  '最新技术趋势与动态'),
        ('后端开发',  'Python、Go、Java 等后端技术'),
        ('前端开发',  'HTML、CSS、JavaScript 等前端技术'),
        ('人工智能',  'AI、机器学习、深度学习'),
        ('生活随笔',  '日常生活记录与感悟'),
        ('学习笔记',  '学习过程中的笔记整理'),
        ('项目实战',  '实际项目开发经验分享'),
    ]
    categories = []
    for name, desc in categories_data:
        c = Category(name=name, description=desc)
        db.session.add(c)
        categories.append(c)
    db.session.commit()
    print(f'  ✓ 已创建 {len(categories)} 个分类')

    # ========================================================
    # 3. 标签
    # ========================================================
    print('创建标签…')
    tag_names = [
        'Python', 'Flask', 'Django', 'JavaScript', 'TypeScript',
        'Vue.js', 'React', 'Node.js', 'Go', 'Docker',
        'Linux', '数据库', '算法', '设计模式', 'Git',
        'RESTful', 'WebSocket', 'Redis', 'Nginx', 'AI',
    ]
    tags = []
    for name in tag_names:
        t = Tag(name=name)
        db.session.add(t)
        tags.append(t)
    db.session.commit()
    print(f'  ✓ 已创建 {len(tags)} 个标签')

    # ========================================================
    # 4. 文章
    # ========================================================
    print('创建文章…')

    articles_data = [
        {
            'title': 'Flask 框架入门指南',
            'content': '''<h2>什么是 Flask？</h2>
<p>Flask 是一个轻量级的 Python Web 框架，由 Armin Ronacher 开发。它被称为"微框架"，因为它的核心非常简单，但可以通过扩展来添加各种功能。</p>
<h2>为什么选择 Flask？</h2>
<p>Flask 非常适合小型到中型的 Web 应用，它的设计理念是让开发者有更多的控制权。你可以选择使用哪些组件，而不被框架束缚。</p>
<h2>快速开始</h2>
<p>安装 Flask 非常简单，只需要一行命令：</p>
<pre><code>pip install flask</code></pre>
<p>然后创建一个简单的应用：</p>
<pre><code>from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'</code></pre>
<p>运行后访问 http://127.0.0.1:5000 就能看到结果。</p>
<h2>Flask 的核心特性</h2>
<ul>
<li>内置开发服务器和调试器</li>
<li>集成单元测试支持</li>
<li>RESTful 请求分发</li>
<li>支持 Jinja2 模板引擎</li>
<li>支持安全的 cookies（客户端会话）</li>
<li>基于 Unicode</li>
</ul>''',
            'summary': 'Flask 是一个轻量级的 Python Web 框架，本文带你快速入门。',
            'category': 0,  # 技术前沿
            'tags': [0, 1, 2],  # Python, Flask, Django
            'author': 0,  # admin
        },
        {
            'title': 'Python 异步编程从入门到实践',
            'content': '''<h2>异步编程概述</h2>
<p>异步编程是一种编程范式，它允许程序在等待 I/O 操作完成时执行其他任务，从而提高程序的整体效率。</p>
<h2>async/await 语法</h2>
<p>Python 3.5 引入了 <code>async</code> 和 <code>await</code> 关键字，使得异步编程变得更加直观。</p>
<pre><code>import asyncio

async def fetch_data(url):
    print(f"开始获取: {url}")
    await asyncio.sleep(1)  # 模拟网络请求
    return f"数据来自 {url}"

async def main():
    tasks = [
        fetch_data("https://api.example.com/1"),
        fetch_data("https://api.example.com/2"),
        fetch_data("https://api.example.com/3"),
    ]
    results = await asyncio.gather(*tasks)
    for r in results:
        print(r)

asyncio.run(main())</code></pre>
<h2>适用场景</h2>
<p>异步编程特别适合 I/O 密集型任务，如 Web 爬虫、API 调用、文件操作等。</p>''',
            'summary': '深入理解 Python 异步编程的核心概念与实践技巧。',
            'category': 1,  # 后端开发
            'tags': [0],  # Python
            'author': 0,  # admin
        },
        {
            'title': 'Vue3 + TypeScript 项目搭建实战',
            'content': '''<h2>前言</h2>
<p>Vue 3 带来了 Composition API 等重大更新，配合 TypeScript 可以获得更好的类型安全和开发体验。</p>
<h2>项目初始化</h2>
<pre><code>npm create vue@latest
cd my-project
npm install
npm run dev</code></pre>
<h2>Composition API 示例</h2>
<pre><code>import { ref, computed, onMounted } from 'vue'

export default {
  setup() {
    const count = ref(0)
    const doubled = computed(() => count.value * 2)

    onMounted(() => {
      console.log('组件已挂载')
    })

    function increment() {
      count.value++
    }

    return { count, doubled, increment }
  }
}</code></pre>
<h2>TypeScript 支持</h2>
<p>Vue 3 对 TypeScript 的支持非常完善，可以定义组件的 props、emits 的类型。</p>''',
            'summary': '使用 Vue3 + TypeScript 从零搭建一个现代化前端项目。',
            'category': 2,  # 前端开发
            'tags': [3, 4, 5],  # JavaScript, TypeScript, Vue.js
            'author': 2,  # 张三
        },
        {
            'title': 'Docker 容器化部署最佳实践',
            'content': '''<h2>为什么使用 Docker？</h2>
<p>Docker 解决了"在我机器上能跑"的问题，通过容器化技术让应用及其依赖打包在一起，确保在任何环境中都能一致运行。</p>
<h2>编写 Dockerfile</h2>
<pre><code>FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]</code></pre>
<h2>docker-compose.yml</h2>
<pre><code>version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - db
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: secret</code></pre>
<h2>常用命令</h2>
<ul>
<li><code>docker build -t myapp .</code> - 构建镜像</li>
<li><code>docker run -d -p 5000:5000 myapp</code> - 运行容器</li>
<li><code>docker-compose up -d</code> - 启动所有服务</li>
</ul>''',
            'summary': '掌握 Docker 容器化部署的核心技巧，让应用部署更轻松。',
            'category': 1,  # 后端开发
            'tags': [9, 10, 18],  # Docker, Linux, Nginx
            'author': 3,  # 李四
        },
        {
            'title': 'Git 工作流与团队协作指南',
            'content': '''<h2>Git Flow 工作流</h2>
<p>Git Flow 是一种经典的 Git 分支管理策略，适合有固定发布周期的项目。</p>
<h2>主要分支</h2>
<ul>
<li><strong>master</strong> - 生产分支</li>
<li><strong>develop</strong> - 开发分支</li>
<li><strong>feature/*</strong> - 功能分支</li>
<li><strong>release/*</strong> - 发布分支</li>
<li><strong>hotfix/*</strong> - 紧急修复分支</li>
</ul>
<h2>团队协作建议</h2>
<p>1. 保持提交信息清晰<br>
2. 经常推送和拉取<br>
3. 及时处理冲突<br>
4. 使用 Pull Request 进行代码审查</p>''',
            'summary': '学会使用 Git 工作流提升团队协作效率。',
            'category': 6,  # 项目实战
            'tags': [14],  # Git
            'author': 1,  # 小明
        },
        {
            'title': '深入理解 RESTful API 设计',
            'content': '''<h2>RESTful 设计原则</h2>
<p>REST（Representational State Transfer）是一种软件架构风格，用于设计网络应用程序。</p>
<h2>URL 设计规范</h2>
<pre><code>GET    /api/users        # 获取用户列表
POST   /api/users        # 创建用户
GET    /api/users/:id    # 获取单个用户
PUT    /api/users/:id    # 更新用户
DELETE /api/users/:id    # 删除用户</code></pre>
<h2>状态码使用</h2>
<ul>
<li>200 - 请求成功</li>
<li>201 - 创建成功</li>
<li>400 - 请求参数错误</li>
<li>401 - 未认证</li>
<li>404 - 资源不存在</li>
<li>500 - 服务器错误</li>
</ul>''',
            'summary': 'RESTful API 设计的最佳实践与规范。',
            'category': 1,  # 后端开发
            'tags': [15, 1],  # RESTful, Flask
            'author': 4,  # 小红
        },
        {
            'title': '算法竞赛入门：动态规划',
            'content': '''<h2>什么是动态规划？</h2>
<p>动态规划（Dynamic Programming, DP）是一种通过将复杂问题分解为更小的子问题来解决的算法思想。</p>
<h2>斐波那契数列</h2>
<pre><code>def fib(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]</code></pre>
<h2>背包问题</h2>
<p>0-1 背包问题是动态规划的经典问题，每个物品只能选择一次，在容量限制下最大化价值。</p>''',
            'summary': '动态规划是算法竞赛中的核心内容，本文带你入门。',
            'category': 0,  # 技术前沿
            'tags': [12],  # 算法
            'author': 5,  # 王五
        },
        {
            'title': '我的 2024 年度总结',
            'content': '''<h2>回顾这一年</h2>
<p>2024 年是不平凡的一年，我在技术、生活和工作中都有了不少收获。</p>
<h2>技术成长</h2>
<p>今年学习了 Flask 和 Vue.js 两个框架，独立完成了两个完整的项目。还深入学习了 Docker 和 Linux 运维知识。</p>
<h2>生活感悟</h2>
<p>编程不仅仅是写代码，更是解决问题的艺术。保持学习的热情，持续进步。</p>
<h2>2025 年目标</h2>
<ol>
<li>深入学习 Go 语言</li>
<li>参与开源项目</li>
<li>写至少 24 篇技术博客</li>
<li>锻炼身体，保持健康</li>
</ol>''',
            'summary': '回顾 2024 年的技术成长与生活感悟。',
            'category': 4,  # 生活随笔
            'tags': [0, 14],  # Python, Git
            'author': 1,  # 小明
        },
        {
            'title': 'MySQL 索引优化实战',
            'content': '''<h2>为什么需要索引？</h2>
<p>索引是数据库查询优化的核心手段，没有索引的查询就像在一本没有目录的书里找内容。</p>
<h2>索引类型</h2>
<ul>
<li><strong>主键索引</strong> - 唯一且非空</li>
<li><strong>唯一索引</strong> - 保证数据的唯一性</li>
<li><strong>普通索引</strong> - 加速查询</li>
<li><strong>联合索引</strong> - 多列组合索引</li>
<li><strong>全文索引</strong> - 文本搜索</li>
</ul>
<h2>最左前缀原则</h2>
<p>联合索引遵循最左前缀原则，查询条件必须从索引的最左侧开始匹配才能使用索引。</p>''',
            'summary': '深入理解 MySQL 索引原理，掌握查询优化技巧。',
            'category': 1,  # 后端开发
            'tags': [11, 16],  # 数据库, Redis (close enough)
            'author': 2,  # 张三
        },
        {
            'title': '前端性能优化清单',
            'content': '''<h2>加载性能</h2>
<ul>
<li>使用 CDN 加速静态资源</li>
<li>开启 Gzip 压缩</li>
<li>图片懒加载</li>
<li>代码分割（Code Splitting）</li>
</ul>
<h2>渲染性能</h2>
<ul>
<li>减少 DOM 操作</li>
<li>使用虚拟列表</li>
<li>避免强制回流</li>
<li>合理使用 requestAnimationFrame</li>
</ul>
<h2>缓存策略</h2>
<ul>
<li>强缓存与协商缓存</li>
<li>Service Worker 离线缓存</li>
<li>内存缓存（Redis）</li>
</ul>''',
            'summary': '一份实用的前端性能优化清单，涵盖加载、渲染和缓存。',
            'category': 2,  # 前端开发
            'tags': [3, 5, 6],  # JavaScript, Vue.js, React
            'author': 3,  # 李四
        },
    ]

    created_articles = []
    for i, ad in enumerate(articles_data):
        # 随机浏览量和创建时间
        view_count = random.randint(50, 2000)
        days_ago = random.randint(1, 60)
        created_at = datetime.now() - timedelta(days=days_ago)

        article = Article(
            title=ad['title'],
            content=ad['content'],
            summary=ad['summary'],
            user_id=users[ad['author']].id,
            category_id=categories[ad['category']].id,
            view_count=view_count,
            is_published=True,
            created_at=created_at,
            updated_at=created_at,
        )
        db.session.add(article)
        db.session.flush()  # 获取 article.id

        # 添加标签
        for tag_idx in ad['tags']:
            article.tags.append(tags[tag_idx])

        created_articles.append(article)

    db.session.commit()
    print(f'  ✓ 已创建 {len(created_articles)} 篇文章')

    # ========================================================
    # 5. 评论
    # ========================================================
    print('创建评论…')
    comments_data = [
        (1, 0, '写得很不错，初学者福音！'),
        (2, 0, '期待更多 Flask 教程'),
        (3, 0, '有没有关于 Flask 扩展的介绍？'),
        (0, 2, 'Vue3 确实好用，配合 TS 更香'),
        (4, 2, '有没有考虑用 Nuxt 3？'),
        (1, 3, 'Docker 部署真的很方便'),
        (0, 3, '建议补充 Docker 网络配置'),
        (3, 5, 'RESTful 设计写得很清楚！'),
        (2, 8, '索引优化很实用，收藏了'),
        (4, 9, '这清单太全了，已转发团队'),
        (1, 4, 'Git Flow 确实好用'),
        (5, 1, '异步编程讲得很透彻'),
    ]
    for user_idx, article_idx, content in comments_data:
        comment = Comment(
            content=content,
            user_id=users[user_idx].id,
            article_id=created_articles[article_idx].id,
        )
        db.session.add(comment)
    db.session.commit()
    print(f'  ✓ 已创建 {len(comments_data)} 条评论')

    # ========================================================
    # 6. 点赞 & 收藏
    # ========================================================
    print('创建点赞和收藏…')
    like_count = 0
    fav_count = 0
    for article in created_articles:
        # 每篇文章随机 1-5 个点赞
        for user in random.sample(users, random.randint(1, min(5, len(users)))):
            if not Like.query.filter_by(user_id=user.id, article_id=article.id).first():
                like = Like(user_id=user.id, article_id=article.id)
                db.session.add(like)
                like_count += 1

        # 每篇文章随机 0-3 个收藏
        for user in random.sample(users, random.randint(0, min(3, len(users)))):
            if not Favorite.query.filter_by(user_id=user.id, article_id=article.id).first():
                fav = Favorite(user_id=user.id, article_id=article.id)
                db.session.add(fav)
                fav_count += 1

    db.session.commit()
    print(f'  ✓ 已创建 {like_count} 个点赞、{fav_count} 个收藏')

    # ========================================================
    # 汇总
    # ========================================================
    print('\n' + '=' * 50)
    print('✅ 测试数据填充完成！')
    print('=' * 50)
    print(f'  用户：{User.query.count()} 人')
    print(f'  分类：{Category.query.count()} 个')
    print(f'  标签：{Tag.query.count()} 个')
    print(f'  文章：{Article.query.count()} 篇')
    print(f'  评论：{Comment.query.count()} 条')
    print(f'  点赞：{Like.query.count()} 个')
    print(f'  收藏：{Favorite.query.count()} 个')
    print('=' * 50)
    print('管理员账号：admin / 123456')
    print('普通用户口令均为：123456')

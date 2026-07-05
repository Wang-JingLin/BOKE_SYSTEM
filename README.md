# 📝 夜语书屋 - 个人博客系统

基于 **Flask + SQLAlchemy + MySQL/SQLite** 的个人博客系统，支持文章发布管理、富文本编辑、评论互动、收藏点赞等完整功能。

## ✨ 功能特性

### 📄 文章管理
- 文章发布、编辑、删除、草稿保存
- 富文本编辑器（支持标题、加粗、颜色、代码块、表格、图片等 20+ 格式工具）
- 文章分类与标签
- 文章阅读量统计
- 文章摘要自动生成

### 🎨 富文本编辑器
- 完全自定义的工具栏：撤销/重做、标题选择(H1-H6)、加粗、颜色、背景、列表、对齐、代码块、表格、图片、链接等
- 20 色颜色选择面板（文字色 / 背景色）
- 嵌入式代码编辑器（支持 50+ 编程语言标注）
- 表格网格选择器（可视化行列选择）
- 快捷键支持：Ctrl+B(加粗)、Ctrl+I(斜体)、Ctrl+U(下划线)、Ctrl+K(插入链接)、Ctrl+Z(撤销)
- 全屏编辑模式
- 编辑器工具栏按钮带悬浮提示，无文字标签

### 💬 互动系统
- 读者评论与回复
- 文章点赞
- 文章收藏（个人中心查看）

### 🔍 搜索与导航
- 全文搜索（标题/正文/摘要）
- 分类归档
- 标签云
- 文章目录自动生成

### 👤 用户系统
- 用户注册与登录（Flask-Login）
- 个人资料编辑（头像、昵称、签名）
- 个人中心（我的文章、我的收藏）
- 管理员后台管理

### 🎨 设计特点
- 浅灰白简约 UI，五区布局（导航、工具栏、侧边栏、编辑区、底部栏）
- 深浅色主题一键切换
- 全站响应式设计（适配手机/平板/PC）
- 沉浸式文章阅读模式 + 目录导航
- 无广告、无弹窗、阅读优先

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| **后端框架** | Python 3.11+ / Flask 3.0 |
| **ORM** | Flask-SQLAlchemy 3.1 |
| **数据库** | MySQL（推荐）/ SQLite（开发/测试） |
| **表单处理** | Flask-WTF / WTForms |
| **用户认证** | Flask-Login |
| **前端** | HTML5 + CSS3 + JavaScript（原生） |
| **富文本编辑器** | 自定义 contenteditable + execCommand |
| **数据库迁移** | Flask-Migrate (Alembic) |

## 📦 安装与运行

### 环境要求

- Python 3.11+
- MySQL 8.0+（可选，支持 SQLite 兜底）

### 快速启动

```bash
# 1. 克隆项目
git clone <repo-url> boke-system
cd boke-system

# 2. 创建虚拟环境
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 设置数据库等参数

# 5. 初始化数据库并填充测试数据
python seed.py

# 6. 启动服务
python run.py
```

访问 http://127.0.0.1:5000

### 默认管理员

| 用户名 | 密码 |
|--------|------|
| `admin` | `admin123` |

## ⚙️ 配置说明

创建 `.env` 文件（参考 `.env.example`）：

```env
SECRET_KEY=your-secret-key-here

# 使用 SQLite（开发用）
DB_USE_SQLITE=true

# 使用 MySQL（生产用）
# DB_HOST=127.0.0.1
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=your-password
# DB_NAME=boke_system
```

## 📁 项目结构

```
boke-system/
├── run.py                  # 应用启动入口
├── config.py               # 全局配置
├── seed.py                 # 测试数据填充
├── requirements.txt        # Python 依赖
├── .env                    # 环境变量配置
│
├── app/
│   ├── __init__.py         # 应用工厂（Flask 初始化）
│   ├── models.py           # 数据库模型（User, Article, Category, Tag, Comment, Like, Favorite）
│   ├── forms.py            # WTForms 表单定义
│   ├── utils.py            # 工具函数（分页、图片压缩、Token 等）
│   │
│   ├── routes/             # 蓝图路由
│   │   ├── __init__.py
│   │   ├── auth.py         # 登录、注册、退出、个人中心
│   │   ├── article.py      # 文章增删改查、分类、标签、搜索
│   │   ├── comment.py      # 评论、回复、删除
│   │   ├── like_collect.py # 点赞、收藏
│   │   └── admin.py        # 后台管理
│   │
│   ├── templates/          # Jinja2 模板
│   │   ├── base.html       # 基础布局
│   │   ├── auth/           # 登录、注册、个人中心
│   │   ├── article/        # 首页、文章详情、编辑、搜索
│   │   ├── admin/          # 后台管理
│   │   └── errors/         # 404, 500
│   │
│   ├── static/
│   │   ├── css/            # 样式文件
│   │   │   ├── base.css    # 全局样式 / 设计系统
│   │   │   ├── article.css # 文章列表/详情样式
│   │   │   ├── editor.css  # 编辑器样式
│   │   │   ├── auth.css    # 登录/注册样式
│   │   │   ├── admin.css   # 后台管理样式
│   │   │   ├── profile.css # 个人中心样式
│   │   │   └── errors.css  # 错误页面样式
│   │   ├── js/             # JavaScript
│   │   │   ├── base.js     # 基础交互
│   │   │   ├── editor.js   # 富文本编辑器（完整实现）
│   │   │   ├── article.js  # 文章详情交互
│   │   │   └── admin.js    # 后台管理交互
│   │   ├── upload/         # 上传图片目录
│   │   └── image/          # 用户头像目录
│   │
│   └── migrations/         # 数据库迁移文件（Alembic）
│
└── docs/
    └── 页面维护指南.md       # 页面维护说明
```

## 🧩 页面清单

| 页面 | 路由 | 说明 |
|------|------|------|
| 首页 | `/` | 博客文章列表、标签筛选、分页 |
| 文章详情 | `/article/<id>` | 沉浸式阅读、目录导航、评论区 |
| 写文章 | `/article/create` | 五区布局编辑器（工具栏+目录+编辑区+AI+底部栏） |
| 编辑文章 | `/article/<id>/edit` | 同上，预填已有内容 |
| 搜索 | `/search` | 全文搜索结果 |
| 登录 | `/auth/login` | 居中卡片表单 |
| 注册 | `/auth/register` | 居中卡片表单 |
| 个人中心 | `/auth/profile` | 个人资料、我的文章 |
| 我的收藏 | `/interact/favorites` | 收藏文章列表 |
| 后台概览 | `/admin/dashboard` | 统计卡片、文章/评论/分类管理 |
| 分类管理 | `/admin/categories` | 分类 CRUD |
| 标签管理 | `/admin/tags` | 标签 CRUD |
| 评论管理 | `/admin/comments` | 评论审核/删除 |
| 用户管理 | `/admin/users` | 用户列表（管理员） |

## 💻 开发

```bash
# 创建数据库迁移
flask db init
flask db migrate -m "描述"
flask db upgrade

# 填入测试数据
python seed.py

# 开发模式启动（热重载）
python run.py
```

## 📄 开源协议

MIT License

---

> **夜语书屋** — 用写作沉淀思考，用文字传递价值。

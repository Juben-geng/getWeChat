# WeChat Article Collector

一个功能完整的公众号文章收集和管理系统，支持微信公众号和任意网页文章的自动收集、智能分类、图片提取和飞书推送。

## ✨ 核心功能

- 🎯 **文章提取** - 完整提取微信公众号文章内容（标题、作者、正文、图片）
- 🤖 **智能分类** - 自动识别文章类型（技术、产品、运营等10+分类）并生成标签
- 📝 **摘要生成** - 自动生成200-500字文章摘要
- 🖼️ **图片提取** - 提取所有图片URL并存储到表格
- 📊 **飞书集成** - 自动推送到飞书表格和文档
- ⏰ **定时任务** - 创建定时收集和总结任务
- 📈 **报告生成** - 生成每日/每周报告
- 💬 **消息推送** - 发送飞书消息和邮件通知

## 🚀 快速开始

### 1. 安装依赖

```bash
# Node.js依赖
npm install

# Python依赖
pip3 install -r requirements.txt
```

### 2. 配置飞书凭证

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
nano .env
```

填入你的飞书凭证：
```bash
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
```

### 3. 开始使用

```bash
# 收集单篇文章
python3 collector_final.py --url "https://mp.weixin.qq.com/s/xxxxx"

# 批量收集
python3 collector_final.py --file urls.txt

# 仅创建表格
python3 collector_final.py --url "文章链接" --mode table

# 仅创建文档
python3 collector_final.py --url "文章链接" --mode doc
```

## 📋 功能详情

### 文章提取
- ✅ 支持微信公众号文章（完美支持）
- ✅ 支持任意网页链接
- ✅ 提取标题、作者、正文、发布时间
- ✅ 提取所有图片URL

### 智能分类
- ✅ 10+预设分类（技术、产品、运营、设计、商业、职场等）
- ✅ 基于关键词权重自动分类
- ✅ 自动生成5个相关标签

### 图片处理
- ✅ 自动提取所有图片URL
- ✅ 存储到表格（图片数、封面图、图片列表）
- ✅ 可点击查看图片

### 飞书集成
- ✅ 自动创建多维表格
- ✅ 自动创建文档
- ✅ 文档包含原文链接和摘要
- ✅ 表格包含完整图片信息

## 📊 输出示例

### 飞书表格

| 标题 | 作者 | 分类 | 图片数 | 封面图 | 收集时间 |
|------|------|------|--------|--------|----------|
| 文章标题 | 作者名 | 技术 | 5张 | [查看] | 2026-04-10 |

### 飞书文档

```
文章标题
作者: 作者名 | 来源: 公众号名 | 发布: 2026-04-10
分类: 技术 | 标签: AI, Python, 教程
────────────────────────────────
🔗 原文链接：https://mp.weixin.qq.com/s/xxxxx
📷 文章包含 5 张图片
────────────────────────────────
📌 内容摘要：
文章摘要内容...
────────────────────────────────
📖 正文片段：
正文内容...
```

## 🔧 高级功能

### 定时任务

```bash
# 创建每日收集任务
python3 scheduler.py create --type collect --time "09:00" --url-file urls.txt --repeat daily

# 创建每周报告任务
python3 scheduler.py create --type summarize --time "18:00" --days 7 --repeat weekly

# 查看任务列表
python3 scheduler.py list

# 启动调度器
python3 scheduler.py run
```

### 生成报告

```bash
# 生成周报并创建文档
python3 reporter.py --app-token xxx --days 7 --create-doc

# 生成报告并发送通知
python3 reporter.py --app-token xxx --days 7 --receive-id user@example.com
```

### 管理面板

```bash
# 启动交互式管理面板
bash manage.sh
```

## 📁 项目结构

```
article-collector/
├── collector_final.py      # 主程序（推荐使用）
├── extract.js             # 文章提取脚本
├── classifier.py          # 智能分类器
├── formatter.py           # 文档格式化器
├── image_processor.py     # 图片处理器
├── scheduler.py           # 定时任务调度器
├── summarizer.py          # 摘要生成器
├── notifier.py            # 消息推送器
├── reporter.py            # 报告生成器
├── manage.sh              # 管理面板脚本
├── .env.example          # 配置模板
├── package.json          # Node.js依赖
└── requirements.txt      # Python依赖
```

## 🔑 获取飞书凭证

### 步骤1：创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 点击「开发者后台」→「创建企业自建应用」
3. 填写应用名称（如：文章收集助手）

### 步骤2：获取凭证

在应用详情页找到：
- App ID
- App Secret

### 步骤3：配置权限

在「权限管理」添加以下权限：

| 权限名称 | 权限代码 | 用途 |
|---------|---------|------|
| 查看、评论、编辑和管理多维表格 | `bitable:app` | 创建和管理表格 |
| 查看、评论、编辑和管理文档 | `docx:document` | 创建文档 |
| 查看、评论、编辑和管理云空间中文件 | `drive:drive` | 文件操作 |

### 步骤4：发布应用

1. 进入「版本管理与发布」
2. 创建版本并提交审核
3. 审核通过后发布应用

## 💡 使用建议

1. 使用 `collector_final.py` 作为主程序
2. 文章会自动分类和生成摘要
3. 图片URL会自动提取和存储
4. 文档包含原文链接，方便回溯
5. 使用管理面板：`bash manage.sh` 获得交互式体验

## 🎯 使用场景

- **个人知识管理** - 收集优质文章，建立知识库
- **团队内容运营** - 监控行业动态，生成周报
- **Newsletter制作** - 自动汇总推送
- **竞品监控** - 定时收集竞品文章
- **学习笔记** - 整理教程文章系统化学习

## 📖 详细文档

- [SKILL.md](./SKILL.md) - 技能说明（符合 npx skills add 规范）
- [GUIDE.md](./GUIDE.md) - 快速开始指南
- [COMPLETE_GUIDE.md](./COMPLETE_GUIDE.md) - 完整使用文档
- [PERMISSION_GUIDE.md](./PERMISSION_GUIDE.md) - 权限配置指南

## 🎓 系统要求

- Node.js >= 14.0
- Python >= 3.7
- 飞书开放平台应用

## 📝 版本历史

### v1.0.0 (2026-04-10)
- ✅ 10个完整技能
- ✅ 文章提取、分类、摘要、图片处理
- ✅ 飞书表格和文档集成
- ✅ 定时任务和消息推送
- ✅ 文档包含原文链接和摘要内容

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**开始使用**: `npx skills add Juben-geng/getWeChat` 或直接克隆仓库使用 🚀

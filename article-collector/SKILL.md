---
name: wechat-article-collector
description: 公众号文章收集系统 - 自动提取微信公众号文章、智能分类、生成摘要、提取图片，并推送到飞书表格和文档。支持10个完整技能，包括文章提取、智能分类、文档格式化、图片处理、定时任务、摘要生成、消息推送、报告生成等。
---

# WeChat Article Collector

一个功能完整的公众号文章收集和管理系统，支持微信公众号和任意网页文章的自动收集、智能分类、图片提取和飞书推送。

## ✨ 核心功能

### 10个完整技能

| 技能 | 文件 | 功能 |
|------|------|------|
| 文章提取 | extract.js | 提取微信公众号完整内容和图片URL |
| 智能分类 | classifier.py | 自动识别文章类型（10+分类）和生成标签 |
| 文档格式化 | formatter.py | 三种格式风格（标准/卡片/Newsletter） |
| 图片处理 | image_processor.py | 提取图片URL和上传到飞书 |
| 定时任务 | scheduler.py | 创建定时收集和总结任务 |
| 摘要生成 | summarizer.py | 自动生成200-500字摘要 |
| 消息推送 | notifier.py | 发送飞书消息和邮件通知 |
| 报告生成 | reporter.py | 生成每日/每周报告 |
| 完整收集 | collector_final.py | 一键完成全流程（主程序） |
| 表格图片 | collector_table_image.py | 表格中展示图片信息 |

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
```
FEISHU_APP_ID=cli_xxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxx
```

### 3. 开始使用

```bash
# 完整收集（推荐）
python3 collector_final.py --url "https://mp.weixin.qq.com/s/xxxxx"

# 仅创建表格
python3 collector_final.py --url "文章链接" --mode table

# 仅创建文档
python3 collector_final.py --url "文章链接" --mode doc

# 批量收集
python3 collector_final.py --file urls.txt
```

## 📋 功能特点

### ✅ 文章提取
- 完整提取标题、作者、正文、发布时间
- 提取所有图片URL和元信息
- 支持微信公众号和任意网页

### ✅ 智能分类
- 10+预设分类（技术、产品、运营、设计等）
- 自动生成5个相关标签
- 基于关键词权重计算分类

### ✅ 图片处理
- 自动提取所有图片URL
- 存储到表格（图片数、封面图、图片列表）
- 可点击查看图片

### ✅ 飞书集成
- 自动创建多维表格
- 自动创建文档
- 文档包含原文链接和摘要
- 表格包含完整图片信息

### ✅ 定时任务
- 创建定时收集任务
- 支持每日/每周/每月重复
- 自动生成报告和推送

## 📊 输出示例

### 飞书表格
| 标题 | 作者 | 分类 | 图片数 | 封面图 |
|------|------|------|--------|--------|
| 文章1 | 作者1 | 技术 | 5张 | [查看] |

### 飞书文档
```
标题
作者 | 来源 | 发布时间
分类: 技术 | 标签: AI, Python
────────────────────
🔗 原文链接：https://...
📷 文章包含 5 张图片
────────────────────
📌 内容摘要：
摘要内容...
────────────────────
📖 正文片段：
正文内容...
```

## 🔧 高级功能

### 定时收集
```bash
# 创建每日收集任务
python3 scheduler.py create --type collect --time "09:00" --repeat daily

# 启动调度器
python3 scheduler.py run
```

### 生成报告
```bash
# 生成周报
python3 reporter.py --app-token xxx --days 7 --create-doc
```

## 📁 文件说明

```
article-collector/
├── collector_final.py      # 主程序（推荐）
├── extract.js             # 文章提取
├── classifier.py          # 智能分类
├── formatter.py           # 文档格式化
├── image_processor.py     # 图片处理
├── scheduler.py           # 定时任务
├── summarizer.py          # 摘要生成
├── notifier.py            # 消息推送
├── reporter.py            # 报告生成
├── .env.example          # 配置模板
├── package.json          # Node.js依赖
└── requirements.txt      # Python依赖
```

## 🔑 获取飞书凭证

1. 访问 https://open.feishu.cn/
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 添加权限：
   - `bitable:app` - 多维表格
   - `docx:document` - 文档
   - `drive:drive` - 云空间
5. 发布应用

## 💡 使用建议

1. 使用 `collector_final.py` 作为主程序
2. 文章会自动分类和生成摘要
3. 图片URL会自动提取和存储
4. 文档包含原文链接，方便回溯
5. 使用管理面板：`bash manage.sh`

## 🎯 系统要求

- Node.js >= 14.0
- Python >= 3.7
- 飞书开放平台应用

## 📝 版本

**v1.0** - 完整功能版本
- 10个完整技能
- 文章提取、分类、摘要、图片处理
- 飞书表格和文档集成
- 定时任务和消息推送
- 文档包含原文链接和摘要内容

---

**技能总数**: 10个  
**状态**: ✅ 生产可用  
**更新时间**: 2026-04-10

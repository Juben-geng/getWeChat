# 🚀 文章收集系统 - 完整版

一个功能完整的文章收集和管理系统，支持微信公众号和任意网页文章的自动收集、智能分类、定时总结和消息推送。

## ✨ 核心功能

### 1. 文章提取
- ✅ 支持微信公众号文章（完美支持）
- ✅ 支持任意网页链接
- ✅ 自动提取标题、作者、正文、封面图等
- ✅ 批量处理多篇文章

### 2. 智能分类 🆕
- ✅ 基于关键词的自动分类
- ✅ 支持10+预设分类（技术、产品、运营、设计等）
- ✅ 自动提取文章标签
- ✅ 可自定义分类规则

### 3. 文档排版 🆕
- ✅ 三种格式风格：
  - **标准格式** - 完整的文档结构
  - **卡片格式** - 适合快速浏览
  - **Newsletter格式** - 适合定期推送
- ✅ 自动格式化正文内容
- ✅ 生成精美报告文档

### 4. 定时总结 🆕
- ✅ 定时生成每日/每周报告
- ✅ 统计文章来源、标签、分类
- ✅ 自动提取精选文章
- ✅ 支持周期性重复任务

### 5. 消息推送 🆕
- ✅ 发送飞书消息通知
- ✅ 支持邮箱、OpenID等多种接收者类型
- ✅ 支持飞书Webhook
- ✅ 自动推送定期报告

## 📦 快速开始

### 第一步：配置飞书凭证

```bash
cd /workspace/article-collector

# 复制配置模板
cp .env.example .env

# 编辑配置文件
nano .env
```

填入你的飞书凭证：

```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxx
```

### 第二步：使用管理面板

```bash
# 运行管理面板
bash manage.sh
```

管理面板提供交互式菜单，包含所有功能。

### 第三步：开始收集

#### 方式一：交互式操作（推荐）

```bash
bash manage.sh
# 选择 "1) 收集单篇文章"
```

#### 方式二：命令行操作

```bash
# 收集单篇文章
python3 collector.py --url "https://mp.weixin.qq.com/s/xxxx"

# 批量收集
python3 collector.py --file urls.txt

# 选择文档风格
python3 collector.py --url "..." --doc-style card

# 仅创建表格
python3 collector.py --url "..." --mode table
```

## 📚 功能详解

### 智能分类

系统会自动识别文章类型并打标签：

| 分类 | 关键词示例 |
|------|-----------|
| 技术 | AI, Python, 编程, 前端, 后端 |
| 产品 | 产品经理, 用户体验, MVP |
| 运营 | 增长, 转化率, SEO, DAU |
| 设计 | UI, UX, Figma, 视觉设计 |
| 商业 | 创业, 融资, 商业模式 |
| 职场 | 面试, 薪资, 职业规划 |
| 金融 | 理财, 基金, 股票, 投资 |
| 教育 | 学习, 课程, 培训 |
| 生活 | 健康, 旅行, 美食 |

**自定义分类**：

编辑 `classifier.py` 添加你的分类规则：

```python
classifier.add_custom_category(
    name='区块链',
    keywords=['比特币', 'ETH', 'NFT', 'Web3'],
    weight=1.5
)
```

### 文档格式

#### 标准格式

```markdown
# 文章标题

---

**作者**: 张三 | **来源**: 公众号名称
**发布时间**: 2025-01-17 10:30 | **收集时间**: 2025-01-17 15:00

**标签**: `AI` `GPT` `人工智能`

---

## 📌 文章摘要
> 这是文章摘要...

## 📖 正文内容
文章正文内容...
```

#### 卡片格式

```
┌─────────────────────────────────────┐
│ **文章标题...**                      │
├─────────────────────────────────────┤
│ 📰 公众号名称                        │
│ ✍️  张三                             │
│ 🕒 2025-01-17 10:30                 │
├─────────────────────────────────────┤
│ 这是文章摘要...                      │
└─────────────────────────────────────┘

🏷️ `AI` `GPT` `技术`
🔗 [阅读原文](https://...)
```

#### Newsletter格式

```markdown
### 🔹 文章标题

*公众号名称 | 2025-01-17*

这是文章摘要...

🏷️ AI • GPT • 技术

[→ 阅读全文](https://...)

---
```

### 定时任务

#### 创建定时任务

```bash
# 定时收集
python3 scheduler.py create \
  --type collect \
  --time "2025-01-17 18:00" \
  --url-file urls.txt \
  --repeat daily

# 定时生成报告
python3 scheduler.py create \
  --type summarize \
  --time "2025-01-17 20:00" \
  --days 7 \
  --repeat weekly
```

#### 管理任务

```bash
# 查看任务列表
python3 scheduler.py list

# 查看待执行任务
python3 scheduler.py list --status pending

# 取消任务
python3 scheduler.py cancel task_id

# 启动调度器
python3 scheduler.py run
```

#### 定时任务类型

| 类型 | 说明 | 参数 |
|------|------|------|
| collect | 收集文章 | --url 或 --url-file |
| summarize | 生成摘要 | --days (统计天数) |
| report | 发送报告 | --app-token, --email |

### 报告生成

#### 快速生成报告

```bash
# 生成Markdown报告
python3 summarizer.py --days 7 --output report.md

# 创建飞书文档
python3 reporter.py --app-token xxx --days 7 --create-doc

# 发送到邮箱
python3 reporter.py --app-token xxx --receive-id user@example.com
```

#### 报告内容

报告包含以下部分：

1. **📊 数据概览**
   - 收集数量统计
   - 来源分布
   - 热门标签云
   - 每日收集趋势

2. **⭐ 精选文章**
   - 基于关键词权重自动筛选
   - 展示高质量文章

3. **📂 分类浏览**
   - 按分类分组展示
   - 快速定位感兴趣的内容

### 消息推送

#### 推送到飞书

```bash
# 发送文本消息
python3 notifier.py \
  --receive-id user@example.com \
  --message "报告已生成"

# 使用Webhook
python3 notifier.py \
  --webhook https://open.feishu.cn/... \
  --message "消息内容"
```

#### 编程方式调用

```python
from notifier import send_notification

# 发送通知
send_notification(
    receive_id='user@example.com',
    message='您的文章报告已生成',
    receive_type='email'
)
```

## 🔧 高级配置

### 环境变量

```bash
# 必需
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx

# 可选
FEISHU_FOLDER_TOKEN=fldcnxxx  # 默认文档文件夹
FEISHU_BITABLE_TOKEN=xxx      # 默认多维表格
```

### 自定义配置

#### 分类规则

编辑 `classifier.py`：

```python
# 添加新分类
self.categories['新分类'] = {
    'keywords': ['关键词1', '关键词2'],
    'weight': 1.0
}

# 调整权重（提高分类优先级）
self.categories['技术']['weight'] = 1.5
```

#### 报告模板

编辑 `summarizer.py` 中的 `create_summary_report()` 函数。

#### 定时任务

任务保存在 `tasks/scheduled_tasks.json`，可以手动编辑。

## 📁 文件结构

```
article-collector/
├── collector.py          # 主程序（增强版）
├── extract.js           # 文章提取脚本
├── classifier.py        # 智能分类器 🆕
├── formatter.py         # 文档格式化器 🆕
├── summarizer.py        # 摘要生成器 🆕
├── scheduler.py         # 定时任务调度器 🆕
├── notifier.py          # 消息推送器 🆕
├── reporter.py          # 报告生成器 🆕
├── manage.sh            # 管理面板脚本 🆕
├── package.json         # Node.js依赖
├── requirements.txt     # Python依赖
├── .env.example        # 环境变量模板
├── .env                # 环境变量配置
├── urls.txt            # 批量收集链接文件
├── tasks/              # 定时任务存储 🆕
├── README.md           # 基础文档
├── GUIDE.md            # 快速开始指南
└── COMPLETE_GUIDE.md   # 完整使用文档 🆕
```

## 🎯 使用场景

### 场景1：个人知识管理

```bash
# 每天收集看到的优质文章
python3 collector.py --url "..." --mode table

# 每周生成一次报告
python3 scheduler.py create \
  --type summarize \
  --time "2025-01-19 20:00" \
  --days 7 \
  --repeat weekly
```

### 场景2：团队内容运营

```bash
# 批量收集竞品文章
python3 collector.py --file competitor_urls.txt

# 生成并发送周报
python3 reporter.py \
  --app-token xxx \
  --days 7 \
  --receive-id team@company.com
```

### 场景3：自动化监控

```bash
# 创建定时收集任务
python3 scheduler.py create \
  --type collect \
  --time "09:00" \
  --url-file monitor_urls.txt \
  --repeat daily

# 启动调度器（后台运行）
nohup python3 scheduler.py run &
```

### 场景4：Newsletter制作

```bash
# 使用Newsletter格式收集
python3 collector.py \
  --file weekly_articles.txt \
  --mode doc \
  --doc-style newsletter

# 创建汇总文档
python3 reporter.py \
  --app-token xxx \
  --days 7 \
  --create-doc
```

## ⚡ 性能优化

- ✅ 文章内容限制在2000字符内，避免API超时
- ✅ 批量操作优先，减少API调用
- ✅ 本地缓存Token，避免重复认证
- ✅ 异步处理定时任务

## 🔒 安全建议

1. 不要将 `.env` 文件提交到Git
2. 定期更新飞书应用密钥
3. 限制应用权限范围
4. 使用Webhook时注意URL保密

## 🐛 故障排查

### 问题1：Token获取失败

**原因**：App ID或App Secret错误

**解决**：
```bash
# 检查配置
cat .env

# 确认应用已发布
# 确认权限已配置
```

### 问题2：分类不准确

**解决**：
```python
# 在 classifier.py 中调整关键词
# 或提高分类权重
self.categories['技术']['weight'] = 2.0
```

### 问题3：定时任务未执行

**解决**：
```bash
# 检查调度器是否运行
python3 scheduler.py list

# 手动启动调度器
python3 scheduler.py run
```

## 📝 更新日志

### v2.0.0 (2025-01-17) 🎉
- ✨ 新增智能分类功能
- ✨ 新增多种文档格式
- ✨ 新增定时任务调度
- ✨ 新增消息推送功能
- ✨ 新增报告生成器
- ✨ 新增管理面板
- 🎨 优化文档排版
- 🐛 修复若干bug

### v1.0.0 (2025-01-17)
- 基础文章收集功能
- 飞书表格和文档集成

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

---

**需要帮助？**

- 查看 [快速开始指南](GUIDE.md)
- 查看 [基础文档](README.md)
- 运行 `bash manage.sh` 使用管理面板

# WeChat Article Collector

微信公众号文章自动收集系统，支持智能分类、图片提取和飞书推送。

## 功能特点

| 功能 | 说明 |
|------|------|
| 文章提取 | 提取标题、作者、正文、发布时间、图片URL |
| 智能分类 | 自动识别10+类别（技术/产品/运营/设计等） |
| 摘要生成 | 自动生成200-500字摘要 |
| 图片收集 | 提取所有图片URL，记录封面和数量 |
| 飞书同步 | 自动推送到飞书多维表格和文档 |
| 定时任务 | 支持周期性采集和报告生成 |

## 安装使用

### 方式一：克隆仓库

```bash
# 克隆项目
git clone https://github.com/Juben-geng/getWeChat.git
cd getWeChat/article-collector

# 安装依赖
npm install
pip3 install -r requirements.txt

# 配置飞书凭证
cp .env.example .env
# 编辑 .env 文件，填入你的飞书 App ID 和 App Secret

# 运行
python3 collector_final.py --url "https://mp.weixin.qq.com/s/xxxxx"
```

### 方式二：作为技能安装

```bash
# 安装技能
npx skills add https://github.com/Juben-geng/getWeChat

# 使用技能
/wechat-article-collector "https://mp.weixin.qq.com/s/xxxxx"
```

## 配置说明

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 **App ID** 和 **App Secret**

### 2. 配置权限

在飞书应用中添加以下权限：

| 权限名称 | 权限代码 | 用途 |
|---------|---------|------|
| 多维表格 | `bitable:app` | 创建和管理表格 |
| 文档 | `docx:document` | 创建文档 |
| 云空间 | `drive:drive` | 文件操作 |

### 3. 发布应用

提交审核并发布应用后即可使用。

### 4. 创建配置文件

```bash
# 在项目目录创建 .env 文件
cat > .env << EOF
FEISHU_APP_ID=你的AppID
FEISHU_APP_SECRET=你的AppSecret
EOF
```

## 使用方法

### 收集单篇文章

```bash
python3 collector_final.py --url "https://mp.weixin.qq.com/s/xxxxx"
```

### 批量收集

```bash
# 创建链接文件
echo "https://mp.weixin.qq.com/s/xxx1" > urls.txt
echo "https://mp.weixin.qq.com/s/xxx2" >> urls.txt

# 批量处理
python3 collector_final.py --file urls.txt
```

### 仅创建表格

```bash
python3 collector_final.py --url "文章链接" --mode table
```

### 仅创建文档

```bash
python3 collector_final.py --url "文章链接" --mode doc
```

## 输出示例

### 飞书表格

| 标题 | 作者 | 来源 | 分类 | 标签 | 图片数 | 封面图 | 收集时间 |
|------|------|------|------|------|--------|--------|----------|
| 文章标题 | 作者名 | 公众号 | 技术 | AI, Python | 5 | [查看] | 2025-04-10 |

### 飞书文档

```
文章标题
━━━━━━━━━━━━━━━━━━━━
作者: 作者名 | 来源: 公众号名
分类: 技术 | 标签: AI, Python, 教程

🔗 原文链接：https://mp.weixin.qq.com/s/xxxxx
📷 文章包含 5 张图片

📌 内容摘要：
文章摘要内容...

📖 正文片段：
正文内容...
```

## 高级功能

### 定时任务

```bash
# 创建每日收集任务（每天9点）
python3 scheduler.py create --type collect --time "09:00" --repeat daily

# 创建每周报告任务（每周五18点）
python3 scheduler.py create --type summarize --time "18:00" --days 7 --repeat weekly

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

### 交互式管理

```bash
bash manage.sh
```

## 项目结构

```
article-collector/
├── collector_final.py      # 主程序（推荐使用）
├── extract.js              # 文章提取脚本
├── classifier.py           # 智能分类器
├── formatter.py            # 文档格式化器
├── image_processor.py      # 图片处理器
├── scheduler.py            # 定时任务调度器
├── summarizer.py           # 摘要生成器
├── notifier.py             # 消息推送器
├── reporter.py             # 报告生成器
├── manage.sh               # 管理面板脚本
├── .env.example            # 配置模板
├── package.json            # Node.js依赖
└── requirements.txt        # Python依赖
```

## 系统要求

- Node.js >= 14.0
- Python >= 3.7
- 飞书开放平台应用（需配置权限）

## 常见问题

### Q: 提示权限不足？
A: 确保飞书应用已添加所需权限并发布。

### Q: 文档创建成功但内容为空？
A: 检查飞书应用的文档权限是否正确配置。

### Q: 图片无法显示？
A: 微信图片URL有时效限制，建议及时保存。

## 许可证

MIT License

---

**仓库地址**: https://github.com/Juben-geng/getWeChat

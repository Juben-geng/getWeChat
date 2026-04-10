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

## 快速开始

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

## 配置说明

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret

### 2. 配置权限

| 权限名称 | 权限代码 | 用途 |
|---------|---------|------|
| 多维表格 | `bitable:app` | 创建和管理表格 |
| 文档 | `docx:document` | 创建文档 |
| 云空间 | `drive:drive` | 文件操作 |

### 3. 创建配置文件

```bash
cat > .env << EOF
FEISHU_APP_ID=你的AppID
FEISHU_APP_SECRET=你的AppSecret
EOF
```

## 使用方法

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

## 输出示例

### 飞书表格

| 标题 | 作者 | 分类 | 图片数 | 封面图 | 收集时间 |
|------|------|------|--------|--------|----------|
| 文章标题 | 作者名 | 技术 | 5 | [查看] | 2025-04-10 |

### 飞书文档

```
文章标题
━━━━━━━━━━━━━━━━━━━━
作者: 作者名 | 来源: 公众号名
分类: 技术 | 标签: AI, Python

🔗 原文链接：https://mp.weixin.qq.com/s/xxxxx
📷 文章包含 5 张图片

📌 内容摘要：
文章摘要内容...

📖 正文片段：
正文内容...
```

## 项目结构

```
article-collector/
├── collector_final.py      # 主程序
├── extract.js              # 文章提取
├── classifier.py           # 智能分类
├── formatter.py            # 文档格式化
├── scheduler.py            # 定时任务
├── .env.example            # 配置模板
├── package.json            # Node.js依赖
└── requirements.txt        # Python依赖
```

## 系统要求

- Node.js >= 14.0
- Python >= 3.7
- 飞书开放平台应用

## 许可证

MIT License

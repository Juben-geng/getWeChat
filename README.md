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

## 安装指南

### 一、GitHub 认证

#### 方式一：设备验证码登录

**第一步：启动登录**

```bash
gh auth login
```

选择：
- `GitHub.com`
- `HTTPS`
- `Login with a web browser`

**第二步：复制验证码**

终端显示类似：
```
! First copy your one-time code: 6DEC-102A
Press Enter to open github.com in your browser...
```

**第三步：打开浏览器**

访问：https://github.com/login/device

**第四步：输入验证码**

在浏览器页面输入验证码（如：`6DEC-102A`）

**第五步：授权应用**

点击 "Authorize" 完成授权

---

#### 方式二：Personal Access Token

**第一步：生成 Token**

访问：https://github.com/settings/tokens/new

**第二步：配置 Token**

| 设置项 | 值 |
|-------|-----|
| Note | `wechat-collector` |
| Expiration | `No expiration` 或选择期限 |
| Select scopes | 勾选 `repo`（完整仓库权限） |

**第三步：保存 Token**

点击 "Generate token"，复制生成的 Token（以 `ghp_` 开头）

**第四步：使用 Token 登录**

```bash
# 方式1：直接使用
git remote set-url origin https://YOUR_TOKEN@github.com/Juben-geng/getWeChat.git

# 方式2：配置 gh CLI
echo "YOUR_TOKEN" | gh auth login --with-token
```

---

### 二、飞书 CLI 安装

飞书 CLI 已开源：https://github.com/larksuite/cli/tree/main

#### 安装方式

**macOS / Linux:**

```bash
# 使用 Homebrew
brew install larksuite/tap/cli

# 或使用 curl
curl -sSL https://raw.githubusercontent.com/larksuite/cli/main/install.sh | sh
```

**Windows:**

```powershell
# 使用 scoop
scoop install larksuite/scoop/cli

# 或使用 PowerShell
irm https://raw.githubusercontent.com/larksuite/cli/main/install.ps1 | iex
```

**Go 安装:**

```bash
go install github.com/larksuite/cli/cmd/cli@latest
```

#### 飞书 CLI 常用命令

```bash
# 登录飞书
cli auth login

# 查看登录状态
cli auth status

# 创建多维表格
cli bitable create --name "文章收集"

# 推送数据到表格
cli bitable record add --app-token xxx --table-id xxx --data '{"标题":"测试文章"}'

# 查看帮助
cli --help
```

---

### 三、项目依赖安装

```bash
# 克隆项目
git clone https://github.com/Juben-geng/getWeChat.git
cd getWeChat/article-collector

# 安装 Node.js 依赖
npm install

# 安装 Python 依赖
pip3 install -r requirements.txt

# 配置飞书凭证
cp .env.example .env
# 编辑 .env 文件
```

---

## 飞书配置说明

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 点击「开发者后台」→「创建企业自建应用」
3. 填写应用名称（如：文章收集助手）

### 2. 获取凭证

在应用详情页找到：
- **App ID**：以 `cli_` 开头
- **App Secret**：随机字符串

### 3. 配置权限

在「权限管理」添加以下权限：

| 权限名称 | 权限代码 | 用途 |
|---------|---------|------|
| 查看、评论、编辑和管理多维表格 | `bitable:app` | 创建和管理表格 |
| 查看、评论、编辑和管理文档 | `docx:document` | 创建文档 |
| 查看、评论、编辑和管理云空间中文件 | `drive:drive` | 文件操作 |

### 4. 发布应用

1. 进入「版本管理与发布」
2. 创建版本并提交审核
3. 审核通过后发布应用

### 5. 创建配置文件

```bash
cat > .env << EOF
FEISHU_APP_ID=cli_xxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxx
EOF
```

---

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

---

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
分类: 技术 | 标签: AI, Python

🔗 原文链接：https://mp.weixin.qq.com/s/xxxxx
📷 文章包含 5 张图片

📌 内容摘要：
文章摘要内容...

📖 正文片段：
正文内容...
```

---

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

---

## 系统要求

- Node.js >= 14.0
- Python >= 3.7
- 飞书开放平台应用

---

## 相关链接

- **本项目**: https://github.com/Juben-geng/getWeChat
- **飞书开放平台**: https://open.feishu.cn/
- **飞书 CLI**: https://github.com/larksuite/cli/tree/main

---

## 许可证

MIT License

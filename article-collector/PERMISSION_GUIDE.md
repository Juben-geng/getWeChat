# 🔑 飞书权限配置指南

## 📋 需要的权限列表

### 当前已配置权限
- ✅ `bitable:app` - 多维表格操作（已配置）

### 需要添加的权限

#### 1. 文档权限（创建带图片的文档）
**权限名称**: 查看、评论、编辑和管理文档  
**权限代码**: `docx:document`

**快速添加链接**:  
https://open.feishu.cn/app/cli_a9b053829e789bd2/auth?q=docx:document,docx:document:create&op_from=openapi&token_type=tenant

#### 2. 云空间权限（上传图片）
**权限名称**: 查看、评论、编辑和管理云空间中文件  
**权限代码**: `drive:drive`

**快速添加链接**:  
https://open.feishu.cn/app/cli_a9b053829e789bd2/auth?q=drive:drive,drive:file:upload&op_from=openapi&token_type=tenant

## 🚀 快速配置步骤

### 方式一：一键添加所有权限

访问以下链接依次添加权限：

1. **文档权限**: [点击添加](https://open.feishu.cn/app/cli_a9b053829e789bd2/auth?q=docx:document,docx:document:create&op_from=openapi&token_type=tenant)
2. **云空间权限**: [点击添加](https://open.feishu.cn/app/cli_a9b053829e789bd2/auth?q=drive:drive,drive:file:upload&op_from=openapi&token_type=tenant)

### 方式二：手动添加

1. **打开应用管理页面**:  
   https://open.feishu.cn/app/cli_a9b053829e789bd2/

2. **进入权限管理**:
   - 点击左侧菜单「权限管理」
   - 点击「申请权限」

3. **搜索并添加以下权限**:
   - 搜索 "文档" → 添加「查看、评论、编辑和管理文档」
   - 搜索 "云空间" → 添加「查看、评论、编辑和管理云空间中文件」

4. **发布应用**:
   - 进入「版本管理与发布」
   - 创建新版本
   - 提交审核（企业内部应用通常立即生效）

## 🎯 功能说明

### 添加权限后可以做什么？

| 权限 | 功能 |
|------|------|
| `bitable:app` | ✅ 创建和管理多维表格 |
| `docx:document` | 📄 创建带图片的飞书文档 |
| `drive:drive` | 📷 上传图片到飞书云空间 |

### 权限添加后的效果

**文档视图展示**:
```
┌────────────────────────────────┐
│ 🦞 龙虾安全手册简版（个人版本）  │
│                                │
│ 作者: 郎瀚威 Will              │
│ 来源: 郎瀚威 Will              │
│ 分类: 技术 | 标签: AI, 安全    │
│                                │
│ ┌──────────────────────────┐ │
│ │      [封面图片]           │ │
│ └──────────────────────────┘ │
│                                │
│ 摘要：文章摘要内容...          │
│                                │
│ 正文段落1...                   │
│ 正文段落2...                   │
│                                │
│ 📷 文章配图：                  │
│ ┌────┐ ┌────┐ ┌────┐        │
│ │图1 │ │图2 │ │图3 │        │
│ └────┘ └────┘ └────┘        │
│                                │
│ 原文链接：https://...          │
└────────────────────────────────┘
```

**表格展示**:
```
┌──────────┬────────┬────────┬────────┐
│ 标题     │ 作者   │ 分类   │ 图片数 │
├──────────┼────────┼────────┼────────┤
│ 文章1    │ 作者1  │ 技术   │ 3张    │
│ 文章2    │ 作者2  │ 产品   │ 5张    │
└──────────┴────────┴────────┴────────┘
```

## ⏱️ 临时方案（无需额外权限）

如果暂时不想添加权限，可以使用以下方案：

### 方案一：仅使用表格（当前已可用）

```bash
python3 /workspace/article-collector/collector.py \
  --url "文章链接" \
  --mode table
```

### 方案二：图片URL存储到表格

图片URL已经存储在表格的"摘要"字段中，可以：
1. 在飞书表格中查看图片URL
2. 点击URL在新标签页打开图片

### 方案三：生成Markdown文档（本地）

```bash
python3 /workspace/article-collector/formatter.py > article.md
```

## 📝 权限配置检查

运行以下命令检查权限是否已配置：

```bash
python3 -c "
import sys
sys.path.insert(0, '/workspace/article-collector')
from dotenv import load_dotenv
load_dotenv('/workspace/article-collector/.env')
from collector import FeishuClient

feishu = FeishuClient()

print('正在检查权限...')
print()

# 测试表格权限
try:
    result = feishu.request('GET', '/bitable/v1/apps/PEeAb6xUPaL6umsbf2hc9wedn7d/tables')
    if result.get('code') == 0:
        print('✅ 多维表格权限: 已配置')
except:
    print('❌ 多维表格权限: 未配置')

# 测试文档权限
try:
    result = feishu.request('POST', '/docx/v1/documents', {'title': '测试'})
    if result.get('code') == 0:
        print('✅ 文档权限: 已配置')
        # 删除测试文档
    elif result.get('code') == 99991663:
        print('❌ 文档权限: 未配置')
except:
    print('❌ 文档权限: 未配置')

# 测试云空间权限
try:
    result = feishu.request('GET', '/drive/v1/files', params={'page_size': 1})
    if result.get('code') == 0:
        print('✅ 云空间权限: 已配置')
    elif result.get('code') == 99991663:
        print('❌ 云空间权限: 未配置')
except:
    print('❌ 云空间权限: 未配置')
"
```

## 🔗 相关链接

- **应用管理**: https://open.feishu.cn/app/cli_a9b053829e789bd2/
- **权限管理**: https://open.feishu.cn/app/cli_a9b053829e789bd2/auth
- **版本发布**: https://open.feishu.cn/app/cli_a9b053829e789bd2/release

---

**提示**: 权限添加后通常立即生效，无需重新配置系统。

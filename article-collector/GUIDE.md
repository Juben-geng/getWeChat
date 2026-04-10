# 快速开始指南

## 第一步：配置飞书凭证

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 点击「开发者后台」→「创建企业自建应用」
3. 填写应用名称（如：文章收集助手）
4. 点击「创建」

### 2. 获取凭证

1. 在应用详情页，找到「凭证与基础信息」
2. 复制 `App ID` 和 `App Secret`

### 3. 配置权限

在「权限管理」页面，添加以下权限：

| 权限名称 | 权限代码 | 用途 |
|---------|---------|------|
| 查看、评论、编辑和管理多维表格 | `bitable:app` | 创建和管理文章表格 |
| 查看、评论、编辑和管理文档 | `docx:document` | 创建文章文档 |
| 查看、评论、编辑和管理云空间中文件 | `drive:drive` | 文件夹操作 |

### 4. 配置环境变量

```bash
# 复制示例文件
cp .env.example .env

# 编辑配置文件
nano .env
```

填入你的凭证：

```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxx
```

### 5. 发布应用

1. 在应用详情页，点击「版本管理与发布」
2. 创建版本并提交审核
3. 审核通过后发布应用

## 第二步：测试系统

### 测试文章提取

```bash
# 测试提取微信文章（会输出JSON格式的内容）
node extract.js "https://mp.weixin.qq.com/s/你的文章链接"
```

成功输出示例：

```json
{
  "done": true,
  "code": 0,
  "data": {
    "msg_title": "文章标题",
    "msg_author": "作者",
    "account_name": "公众号名称",
    "msg_publish_time_str": "2025/01/17 10:30:00",
    "msg_content_text": "文章正文内容..."
  }
}
```

## 第三步：收集文章

### 方式一：收集单篇文章

```bash
# 同时创建文档和表格（默认）
python3 collector.py --url "https://mp.weixin.qq.com/s/xxxx"

# 仅创建表格
python3 collector.py --url "https://mp.weixin.qq.com/s/xxxx" --mode table

# 仅创建文档
python3 collector.py --url "https://mp.weixin.qq.com/s/xxxx" --mode doc
```

### 方式二：批量收集

创建一个文本文件 `urls.txt`，每行一个链接：

```
https://mp.weixin.qq.com/s/xxxx1
https://mp.weixin.qq.com/s/xxxx2
https://mp.weixin.qq.com/s/xxxx3
```

执行批量收集：

```bash
python3 collector.py --file urls.txt
```

### 方式三：追加到已有表格

如果你已经创建了多维表格，可以重复使用：

```bash
# 第一次运行会创建表格，输出 app_token 和 table_id
python3 collector.py --url "https://mp.weixin.qq.com/s/xxxx"

# 后续运行时指定已有的表格
python3 collector.py \
  --url "https://mp.weixin.qq.com/s/yyyy" \
  --app-token "你的app_token" \
  --table-id "你的table_id"
```

## 第四步：查看结果

### 查看表格

运行成功后，会输出表格链接：

```
✓ 表格已更新: https://feishu.cn/base/ABC123def
```

点击链接即可在飞书中查看收集的文章列表。

### 查看文档

运行成功后，会输出文档链接：

```
✓ 文档已创建: https://feishu.cn/docx/ABC123def
```

点击链接即可查看完整文章内容。

## 常见问题

### Q1: Token获取失败

**原因**: App ID 或 App Secret 配置错误

**解决**: 
1. 检查 `.env` 文件中的凭证是否正确
2. 确认应用已发布且权限已配置

### Q2: 文章提取失败

**原因**: 链接已过期或文章被删除

**解决**:
1. 确认链接可以正常访问
2. 微信文章链接有效期一般为几小时，请及时收集

### Q3: 写入飞书失败

**原因**: 应用权限不足

**解决**:
1. 确认已添加所需权限
2. 确认应用已发布

### Q4: 内容提取不完整

**原因**: 不同网站结构不同

**解决**:
1. 微信公众号文章支持最佳
2. 其他网站可能需要调整提取逻辑

## 进阶使用

### 定时自动收集

使用 cron 定时任务：

```bash
# 编辑 crontab
crontab -e

# 每小时执行一次
0 * * * * cd /workspace/article-collector && python3 collector.py --file /path/to/urls.txt
```

### 自定义字段

编辑 `collector.py` 中的 `add_article_fields` 方法：

```python
fields = [
    {'field_name': '标题', 'type': 1},
    {'field_name': '作者', 'type': 1},
    {'field_name': '标签', 'type': 4},  # 多选字段
    {'field_name': '重要性', 'type': 2},  # 数字字段
    # 添加更多自定义字段...
]
```

### 集成到工作流

可以将此系统集成到你的自动化工作流中：

1. 从微信群监控文章链接
2. 使用本系统自动收集
3. 发送飞书消息通知

## 技术支持

遇到问题？

1. 查看错误日志
2. 参考 [飞书开放平台文档](https://open.feishu.cn/document/)
3. 提交 Issue 到项目仓库

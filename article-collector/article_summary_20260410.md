# 📊 文章收集完成报告

## 📝 文章信息

**标题**: 🦞龙虾安全手册简版（个人版本）

**作者**: 郎瀚威 Will

**来源**: 郎瀚威 Will

**发布时间**: 2026/03/29 12:30:58

**原文链接**: [点击查看](https://mp.weixin.qq.com/s/H3CLBgeBUcs4cQvsh7zAMw)

## 🏷️ 智能分类结果

**主要分类**: 技术

**相关分类**: 技术, 科技资讯

**自动标签**: `代码` `GitHub` `AI` `电脑` `设计`

**分类得分**:
- 技术: 15.0 ⭐
- 科技资讯: 5.0
- 设计: 1.0

## 📋 文章摘要

这是一篇关于AI助手（龙虾）安全使用的实用指南。文章从环境隔离、账号权限、Skill安全检查、日常安全习惯四个维度，详细介绍了如何在使用AI助手时保护数据安全。

**核心要点**:
1. **环境隔离** - 龙虾装在单独机器上，切断与其他机器的通道
2. **账号隔离** - 为龙虾创建独立账号，不使用主账号
3. **安全检查** - 只从官方商店安装Skill，使用安全检测工具
4. **日常习惯** - 定期检查记忆文件，及时更新版本

## 📄 格式化预览

### 卡片格式
```
┌─────────────────────────────────────┐
│ **🦞龙虾安全手册简版（个人版本）**
├─────────────────────────────────────┤
│ 📰 郎瀚威 Will
│ ✍️  郎瀚威 Will
│ 🕒 2026/03/29 12:30:58
├─────────────────────────────────────┤
└─────────────────────────────────────┘

🏷️ `代码` `GitHub` `AI`

🔗 [阅读原文](https://mp.weixin.qq.com/s/H3CLBgeBUcs4cQvsh7zAMw)
```

### Newsletter格式
```markdown
### 🔹 🦞龙虾安全手册简版（个人版本）

*郎瀚威 Will | 2026/03/29*

🏷️ 代码 • GitHub • AI

[→ 阅读全文](https://mp.weixin.qq.com/s/H3CLBgeBUcs4cQvsh7zAMw)
```

## ✅ 收集状态

- ✅ 文章提取成功
- ✅ 智能分类完成
- ✅ 文档格式化完成
- ⏳ 飞书同步（待配置）

## 🚀 下一步操作

### 保存到飞书

如果你想将这篇文章保存到飞书表格和文档，请按以下步骤操作：

1. **配置飞书凭证**
   ```bash
   cd /workspace/article-collector
   cp .env.example .env
   nano .env  # 填入你的飞书 App ID 和 App Secret
   ```

2. **同步到飞书**
   ```bash
   # 同时创建表格和文档
   python3 collector.py --url "https://mp.weixin.qq.com/s/H3CLBgeBUcs4cQvsh7zAMw" --mode both --doc-style standard
   
   # 仅创建表格
   python3 collector.py --url "https://mp.weixin.qq.com/s/H3CLBgeBUcs4cQvsh7zAMw" --mode table
   
   # 仅创建文档
   python3 collector.py --url "https://mp.weixin.qq.com/s/H3CLBgeBUcs4cQvsh7zAMw" --mode doc --doc-style card
   ```

### 获取飞书凭证

1. 访问 https://open.feishu.cn/
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 添加权限：
   - `bitable:app` - 多维表格
   - `docx:document` - 文档
   - `drive:drive` - 云空间

---

**收集时间**: 2026-04-10 11:00:47

**系统版本**: Article Collector v2.0.0

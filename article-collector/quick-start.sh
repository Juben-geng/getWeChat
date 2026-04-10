#!/bin/bash

# 文章收集系统快速启动脚本

echo "===================================="
echo "  文章收集系统 - 快速启动"
echo "===================================="
echo ""

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "⚠️  检测到未配置飞书凭证"
    echo ""
    echo "请按照以下步骤配置："
    echo "1. 复制 .env.example 为 .env"
    echo "   cp .env.example .env"
    echo ""
    echo "2. 编辑 .env 文件，填入你的飞书应用凭证"
    echo "   FEISHU_APP_ID=your_app_id"
    echo "   FEISHU_APP_SECRET=your_app_secret"
    echo ""
    echo "获取飞书凭证的方法："
    echo "1. 访问 https://open.feishu.cn/"
    echo "2. 创建企业自建应用"
    echo "3. 获取 App ID 和 App Secret"
    echo "4. 添加应用权限：bitable:app, docx:document, drive:drive"
    echo ""
    exit 1
fi

# 显示使用说明
echo "✓ 配置文件已就绪"
echo ""
echo "使用方法："
echo ""
echo "1. 收集单篇文章："
echo "   python3 collector.py --url \"文章链接\""
echo ""
echo "2. 批量收集（从文件读取）："
echo "   python3 collector.py --file urls.txt"
echo ""
echo "3. 仅创建表格："
echo "   python3 collector.py --url \"文章链接\" --mode table"
echo ""
echo "4. 仅创建文档："
echo "   python3 collector.py --url \"文章链接\" --mode doc"
echo ""
echo "示例（测试提取功能）："
echo "   node extract.js \"https://mp.weixin.qq.com/s/xxxx\""
echo ""

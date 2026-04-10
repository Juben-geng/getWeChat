#!/bin/bash

# 公众号文章收集系统 - 一键安装脚本

echo "📦 开始安装公众号文章收集系统..."
echo ""

# 创建项目目录
PROJECT_DIR="$HOME/article-collector"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo "✓ 项目目录已创建: $PROJECT_DIR"

# 下载所有文件（使用curl）
echo ""
echo "⬇️  正在下载文件..."

# 主程序
curl -s -o collector_final.py "https://raw.githubusercontent.com/你的仓库/article-collector/main/collector_final.py" 2>/dev/null || {
    echo "提示: 请手动创建文件（见下方说明）"
}

echo ""
echo "✓ 安装完成！"
echo ""
echo "下一步："
echo "1. 安装依赖: npm install && pip3 install -r requirements.txt"
echo "2. 配置飞书: cp .env.example .env && nano .env"
echo "3. 开始使用: python3 collector_final.py --url '文章链接'"

#!/bin/bash
# 文章收集系统 - 演示脚本

echo "╔════════════════════════════════════════════╗"
echo "║    文章收集系统 - 功能演示                 ║"
echo "║    Article Collection System Demo          ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# 检查依赖
echo "1️⃣  检查依赖..."
echo "────────────────────────────────────────"

if ! command -v node &> /dev/null; then
    echo "✗ Node.js 未安装"
    exit 1
fi
echo "✓ Node.js: $(node --version)"

if ! command -v python3 &> /dev/null; then
    echo "✗ Python3 未安装"
    exit 1
fi
echo "✓ Python3: $(python3 --version)"

if [ -d "node_modules" ]; then
    echo "✓ Node.js 依赖已安装"
else
    echo "⚠ Node.js 依赖未安装，正在安装..."
    npm install
fi

echo ""

# 测试分类器
echo "2️⃣  测试智能分类器..."
echo "────────────────────────────────────────"
python3 classifier.py

echo ""
echo ""

# 测试格式化器
echo "3️⃣  测试文档格式化器..."
echo "────────────────────────────────────────"
python3 formatter.py

echo ""
echo ""

# 检查配置文件
echo "4️⃣  检查系统配置..."
echo "────────────────────────────────────────"

if [ -f ".env" ]; then
    if grep -q "FEISHU_APP_ID=cli_" .env 2>/dev/null; then
        echo "✓ 飞书凭证已配置"
        echo ""
        echo "系统已就绪，可以开始使用！"
    else
        echo "⚠ 飞书凭证未正确配置"
        echo ""
        echo "请编辑 .env 文件，填入正确的飞书凭证："
        echo "  FEISHU_APP_ID=cli_xxx"
        echo "  FEISHU_APP_SECRET=xxx"
    fi
else
    echo "⚠ 配置文件不存在"
    echo ""
    echo "请创建配置文件："
    echo "  cp .env.example .env"
    echo "  nano .env  # 填入飞书凭证"
fi

echo ""
echo ""

# 显示使用方法
echo "5️⃣  快速开始指南"
echo "────────────────────────────────────────"
echo ""
echo "方式一：使用管理面板（推荐）"
echo "  bash manage.sh"
echo ""
echo "方式二：命令行操作"
echo "  # 收集单篇文章"
echo "  python3 collector.py --url \"https://mp.weixin.qq.com/s/xxxx\""
echo ""
echo "  # 批量收集"
echo "  python3 collector.py --file urls.txt"
echo ""
echo "  # 生成报告"
echo "  python3 reporter.py --app-token xxx --days 7"
echo ""
echo "方式三：定时任务"
echo "  # 创建定时收集任务"
echo "  python3 scheduler.py create --type collect --time \"09:00\" --repeat daily"
echo ""
echo "  # 启动调度器"
echo "  python3 scheduler.py run"
echo ""

echo "════════════════════════════════════════════"
echo "🎉 演示完成！"
echo ""
echo "📚 详细文档："
echo "  - COMPLETE_GUIDE.md  完整使用文档"
echo "  - GUIDE.md          快速开始指南"
echo "  - README.md         项目说明"
echo ""
echo "🚀 立即开始："
echo "  bash manage.sh"
echo "════════════════════════════════════════════"

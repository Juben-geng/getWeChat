#!/bin/bash
# 文章收集系统 - 一键管理脚本

PROJECT_DIR="/workspace/article-collector"
cd "$PROJECT_DIR"

show_banner() {
    echo "╔══════════════════════════════════════════╗"
    echo "║      文章收集系统 - 管理面板             ║"
    echo "║  Article Collection System Manager       ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
}

check_config() {
    if [ ! -f ".env" ]; then
        echo "⚠️  检测到未配置飞书凭证"
        echo ""
        echo "请按照以下步骤配置："
        echo "1. cp .env.example .env"
        echo "2. 编辑 .env 文件，填入飞书凭证"
        echo ""
        return 1
    fi
    
    # 检查环境变量是否已设置
    if ! grep -q "FEISHU_APP_ID=cli_" .env 2>/dev/null; then
        echo "⚠️  请在 .env 文件中配置正确的飞书凭证"
        return 1
    fi
    
    return 0
}

collect_single() {
    echo "📝 收集单篇文章"
    echo "────────────────────────────"
    read -p "请输入文章链接: " url
    
    if [ -z "$url" ]; then
        echo "✗ 链接不能为空"
        return 1
    fi
    
    echo ""
    echo "选择汇总方式:"
    echo "  1) 同时创建表格和文档"
    echo "  2) 仅创建表格"
    echo "  3) 仅创建文档"
    read -p "请选择 (1-3): " mode_choice
    
    case $mode_choice in
        2) mode="table" ;;
        3) mode="doc" ;;
        *) mode="both" ;;
    esac
    
    echo ""
    echo "选择文档风格:"
    echo "  1) 标准格式"
    echo "  2) 卡片格式"
    echo "  3) Newsletter格式"
    read -p "请选择 (1-3): " style_choice
    
    case $style_choice in
        2) style="card" ;;
        3) style="newsletter" ;;
        *) style="standard" ;;
    esac
    
    echo ""
    python3 collector.py --url "$url" --mode "$mode" --doc-style "$style"
}

collect_batch() {
    echo "📚 批量收集文章"
    echo "────────────────────────────"
    
    if [ ! -f "urls.txt" ] || [ ! -s "urls.txt" ]; then
        echo "⚠️  urls.txt 文件不存在或为空"
        echo "请先在 urls.txt 中添加文章链接（每行一个）"
        return 1
    fi
    
    echo "已加载 urls.txt 中的链接"
    echo ""
    read -p "确认开始收集？(y/n): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        python3 collector.py --file urls.txt
    fi
}

create_schedule() {
    echo "⏰ 创建定时任务"
    echo "────────────────────────────"
    echo ""
    echo "任务类型:"
    echo "  1) 定时收集文章"
    echo "  2) 定时生成报告"
    read -p "请选择 (1-2): " task_type_choice
    
    case $task_type_choice in
        2) task_type="summarize" ;;
        *) task_type="collect" ;;
    esac
    
    echo ""
    read -p "执行时间 (格式: YYYY-MM-DD HH:MM): " schedule_time
    
    if [ "$task_type" = "collect" ]; then
        read -p "文章链接 (可选，留空则使用urls.txt): " url
        
        if [ -n "$url" ]; then
            params="--url $url"
        else
            params="--url-file $PROJECT_DIR/urls.txt"
        fi
    else
        read -p "统计天数 (默认7天): " days
        days=${days:-7}
        params="--days $days"
    fi
    
    echo ""
    echo "重复模式:"
    echo "  1) 仅执行一次"
    echo "  2) 每天"
    echo "  3) 每周"
    echo "  4) 每月"
    read -p "请选择 (1-4): " repeat_choice
    
    case $repeat_choice in
        2) repeat="daily" ;;
        3) repeat="weekly" ;;
        4) repeat="monthly" ;;
        *) repeat="once" ;;
    esac
    
    echo ""
    python3 scheduler.py create \
        --type "$task_type" \
        --time "$schedule_time" \
        --repeat "$repeat" \
        $params
}

list_tasks() {
    echo "📋 任务列表"
    echo "────────────────────────────"
    python3 scheduler.py list
}

start_scheduler() {
    echo "▶️  启动定时任务调度器"
    echo "────────────────────────────"
    echo "按 Ctrl+C 停止调度器"
    echo ""
    python3 scheduler.py run
}

generate_report() {
    echo "📊 生成报告"
    echo "────────────────────────────"
    
    if ! check_config; then
        return 1
    fi
    
    read -p "统计天数 (默认7天): " days
    days=${days:-7}
    
    echo ""
    echo "输出方式:"
    echo "  1) 保存为Markdown文件"
    echo "  2) 创建飞书文档"
    echo "  3) 发送飞书消息"
    read -p "请选择 (1-3): " output_choice
    
    case $output_choice in
        2)
            # 需要app_token
            read -p "请输入多维表格token: " app_token
            python3 reporter.py --app-token "$app_token" --days "$days" --create-doc
            ;;
        3)
            read -p "请输入多维表格token: " app_token
            read -p "接收者邮箱: " email
            python3 reporter.py --app-token "$app_token" --days "$days" --receive-id "$email"
            ;;
        *)
            output_file="report_$(date +%Y%m%d_%H%M%S).md"
            python3 summarizer.py --days "$days" --output "$output_file" --app-token "demo"
            ;;
    esac
}

test_extractor() {
    echo "🔍 测试文章提取"
    echo "────────────────────────────"
    read -p "请输入文章链接: " url
    
    if [ -z "$url" ]; then
        echo "✗ 链接不能为空"
        return 1
    fi
    
    echo ""
    node extract.js "$url"
}

show_help() {
    echo "📖 使用帮助"
    echo "────────────────────────────"
    echo ""
    echo "1. 快速开始"
    echo "   - 复制配置文件: cp .env.example .env"
    echo "   - 编辑配置: nano .env"
    echo "   - 填入飞书App ID和App Secret"
    echo ""
    echo "2. 收集文章"
    echo "   - 单篇文章: python3 collector.py --url \"链接\""
    echo "   - 批量收集: python3 collector.py --file urls.txt"
    echo ""
    echo "3. 定时任务"
    echo "   - 创建任务: python3 scheduler.py create ..."
    echo "   - 启动调度: python3 scheduler.py run"
    echo ""
    echo "4. 生成报告"
    echo "   - 快速报告: python3 summarizer.py --days 7"
    echo "   - 发送通知: python3 reporter.py --app-token xxx --receive-id email@example.com"
    echo ""
    echo "5. 详细文档"
    echo "   - 查看 README.md"
    echo "   - 查看 GUIDE.md"
    echo ""
}

# 主菜单
main() {
    show_banner
    
    while true; do
        echo ""
        echo "请选择操作:"
        echo "  1) 📝 收集单篇文章"
        echo "  2) 📚 批量收集文章"
        echo "  3) ⏰ 创建定时任务"
        echo "  4) 📋 查看任务列表"
        echo "  5) ▶️  启动调度器"
        echo "  6) 📊 生成报告"
        echo "  7) 🔍 测试提取功能"
        echo "  8) 📖 查看帮助"
        echo "  0) 🚪 退出"
        echo ""
        read -p "请输入选项 (0-8): " choice
        
        case $choice in
            1) collect_single ;;
            2) collect_batch ;;
            3) create_schedule ;;
            4) list_tasks ;;
            5) start_scheduler ;;
            6) generate_report ;;
            7) test_extractor ;;
            8) show_help ;;
            0) 
                echo ""
                echo "再见！"
                exit 0
                ;;
            *)
                echo "✗ 无效选项，请重新选择"
                ;;
        esac
        
        echo ""
        read -p "按回车键继续..."
    done
}

# 运行主菜单
main

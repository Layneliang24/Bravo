#!/bin/bash
# 新用户入职引导脚本
# 自动检测新团队成员并引导安装强制本地测试系统

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 配置文件
USER_CONFIG_FILE=".force_local_test_user_config"
ONBOARDING_LOG="logs/onboarding.log"

# 创建日志目录
mkdir -p "$(dirname "$ONBOARDING_LOG")"

# 日志函数
log_info() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" | tee -a "$ONBOARDING_LOG"
}

log_success() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $1" | tee -a "$ONBOARDING_LOG"
}

log_warning() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WARN] $1" | tee -a "$ONBOARDING_LOG"
}

# 显示欢迎横幅
show_welcome_banner() {
    echo ""
    echo "🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉"
    echo "🎊                 欢迎加入Bravo项目！                 🎊"
    echo "🛡️            检测到强制本地测试保护系统               🛡️"
    echo "🚀          让我们花5分钟设置您的开发环境！            🚀"
    echo "🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉"
    echo ""
}

# 检测是否为新用户
is_new_user() {
    # 检查用户配置文件
    if [[ -f "$USER_CONFIG_FILE" ]]; then
        local user_id="$(whoami)@$(hostname)"
        if grep -q "$user_id" "$USER_CONFIG_FILE"; then
            return 1  # 不是新用户
        fi
    fi

    # 检查是否已经安装过保护系统
    if [[ -f ".force_local_test_setup_done" ]]; then
        return 1  # 不是新用户
    fi

    # 检查便捷命令是否存在
    if [[ -f "test" && -f "passport" && -f "safe-push" ]]; then
        return 1  # 不是新用户
    fi

    return 0  # 是新用户
}

# 检测用户环境
detect_user_environment() {
    log_info "检测用户环境..."

    local env_info=""

    # 操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ -f "/proc/version" ]] && grep -q "Microsoft\|WSL" /proc/version; then
            env_info="WSL"
        else
            env_info="Linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        env_info="macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        env_info="Git_Bash"
    elif [[ "$OS" == "Windows_NT" ]]; then
        env_info="Windows"
    else
        env_info="Unknown"
    fi

    echo "🖥️ 运行环境: $env_info"
    echo "👤 用户: $(whoami)"
    echo "🏠 主机: $(hostname)"
    echo "📁 项目路径: $PROJECT_ROOT"
    echo ""

    # 保存环境信息
    cat > .user_environment_info << EOF
Environment: $env_info
User: $(whoami)
Hostname: $(hostname)
Project Path: $PROJECT_ROOT
Detection Time: $(date)
EOF

    return 0
}

# 检查系统依赖
check_system_dependencies() {
    echo "🔧 检查系统依赖..."
    echo ""

    local missing_deps=()
    local warnings=()

    # Python检查
    if command -v python3 &> /dev/null; then
        echo "✅ Python3: $(python3 --version)"
    elif command -v python &> /dev/null; then
        echo "✅ Python: $(python --version)"
    else
        missing_deps+=("Python (3.7+)")
    fi

    # Git检查
    if command -v git &> /dev/null; then
        echo "✅ Git: $(git --version)"
    else
        missing_deps+=("Git")
    fi

    # Docker检查
    if command -v docker &> /dev/null; then
        if docker info &> /dev/null 2>&1; then
            echo "✅ Docker: 服务运行中"
        else
            warnings+=("Docker已安装但服务未启动")
        fi
    else
        missing_deps+=("Docker Desktop")
    fi

    # docker-compose检查
    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose: $(docker-compose --version)"
    else
        warnings+=("docker-compose (通常包含在Docker Desktop中)")
    fi

    # act检查 (可选)
    if command -v act &> /dev/null; then
        echo "✅ act: $(act --version 2>&1 | head -1)"
    else
        warnings+=("act (可选，用于GitHub Actions本地测试)")
    fi

    echo ""

    # 显示缺失的依赖
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        echo "❌ 缺少必需依赖："
        for dep in "${missing_deps[@]}"; do
            echo "   • $dep"
        done
        echo ""
        show_installation_guide "${missing_deps[@]}"
        return 1
    fi

    # 显示警告
    if [[ ${#warnings[@]} -gt 0 ]]; then
        echo "⚠️ 建议安装以获得完整功能："
        for warning in "${warnings[@]}"; do
            echo "   • $warning"
        done
        echo ""
    fi

    return 0
}

# 显示安装指南
show_installation_guide() {
    local missing_deps=("$@")

    echo "📋 安装指南："
    echo ""

    for dep in "${missing_deps[@]}"; do
        case "$dep" in
            "Python (3.7+)")
                echo "🐍 Python 安装："
                echo "   Windows: https://python.org/downloads/"
                echo "   macOS: brew install python3"
                echo "   Ubuntu: sudo apt install python3 python3-pip"
                echo ""
                ;;
            "Git")
                echo "📦 Git 安装："
                echo "   Windows: https://git-scm.com/download/win"
                echo "   macOS: brew install git"
                echo "   Ubuntu: sudo apt install git"
                echo ""
                ;;
            "Docker Desktop")
                echo "🐳 Docker 安装："
                echo "   Windows/macOS: https://www.docker.com/products/docker-desktop"
                echo "   Ubuntu: https://docs.docker.com/engine/install/ubuntu/"
                echo ""
                ;;
        esac
    done

    echo "💡 安装完成后请重新运行此脚本"
}

# 交互式安装向导
interactive_installation_wizard() {
    echo "🧙‍♂️ 安装向导"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    echo "🎯 这个系统的作用："
    echo "   • 阻止Cursor AI跳过本地测试直接推送代码"
    echo "   • 强制执行四层验证：语法→环境→功能→差异"
    echo "   • 生成1小时有效期的推送通行证"
    echo "   • 确保代码质量和CI/CD流程的稳定性"
    echo ""

    echo "⏱️ 安装预计需要：5-10分钟"
    echo "📖 详细文档：docs/CURSOR_PROTECTION_GUIDE.md"
    echo ""

    # 询问是否继续安装
    while true; do
        read -p "🚀 是否现在安装强制本地测试系统？(Y/n): " response
        case $response in
            [Yy]* | "")
                echo ""
                echo "✅ 开始安装..."
                return 0
                ;;
            [Nn]*)
                echo ""
                echo "⏸️ 跳过安装。您可以稍后运行以下命令进行安装："
                echo "   bash scripts/setup_cursor_protection.sh"
                echo ""
                return 1
                ;;
            *)
                echo "请输入 Y 或 n"
                ;;
        esac
    done
}

# 执行安装
perform_installation() {
    echo "🔧 正在安装强制本地测试系统..."
    echo ""

    # 检查安装脚本
    if [[ ! -f "scripts/setup_cursor_protection.sh" ]]; then
        log_warning "安装脚本不存在，可能需要更新代码库"
        echo "❌ 找不到安装脚本: scripts/setup_cursor_protection.sh"
        echo ""
        echo "💡 请尝试："
        echo "   git pull origin main"
        echo "   git checkout HEAD -- scripts/"
        return 1
    fi

    # 设置执行权限
    chmod +x scripts/setup_cursor_protection.sh

    # 执行安装
    if bash scripts/setup_cursor_protection.sh --new-user; then
        log_success "保护系统安装成功"
        return 0
    else
        log_warning "保护系统安装失败"
        return 1
    fi
}

# 创建用户配置
create_user_config() {
    local user_id="$(whoami)@$(hostname)"
    local install_time="$(date '+%Y-%m-%d %H:%M:%S')"

    # 添加用户记录
    echo "$user_id:$install_time:installed" >> "$USER_CONFIG_FILE"

    # 创建完成标记
    echo "$install_time: 新用户 $user_id 安装完成" > .force_local_test_setup_done

    log_info "用户配置创建完成: $user_id"
}

# 显示后续步骤
show_next_steps() {
    echo ""
    echo "🎉 安装完成！接下来您可以："
    echo ""
    echo "📋 基本命令："
    echo "   make test         # 运行完整本地测试"
    echo "   make test-quick   # 快速测试（推荐日常使用）"
    echo "   make passport     # 检查通行证状态"
    echo "   make safe-push    # 安全推送代码"
    echo ""
    echo "🎯 典型工作流程："
    echo "   1. 修改代码"
    echo "   2. 运行 make test-quick"
    echo "   3. 获得通行证后推送: git push origin your-branch"
    echo ""
    echo "📖 详细文档："
    echo "   • docs/CURSOR_PROTECTION_GUIDE.md  (用户指南)"
    echo "   • docs/force_local_test/FAQ.md     (常见问题)"
    echo ""
    echo "🔧 在Cursor中使用："
    echo "   按 Ctrl+Shift+P → 搜索 \"Tasks: Run Task\" → 选择测试任务"
    echo ""
    echo "💡 提示：第一次运行测试可能需要下载Docker镜像，请耐心等待"
    echo ""
}

# 快速验证安装
quick_verification() {
    echo "🔍 快速验证安装..."
    echo ""

    # 检查便捷命令
    local commands=("test" "passport" "safe-push")
    for cmd in "${commands[@]}"; do
        if [[ -f "$cmd" && -x "$cmd" ]]; then
            echo "✅ $cmd 命令可用"
        else
            echo "❌ $cmd 命令缺失"
            return 1
        fi
    done

    # 检查通行证脚本
    if python3 scripts/local_test_passport.py --check &> /dev/null; then
        echo "✅ 通行证系统正常"
    elif python scripts/local_test_passport.py --check &> /dev/null; then
        echo "✅ 通行证系统正常"
    else
        echo "⚠️ 通行证系统检查异常（可能是首次运行）"
    fi

    echo ""
    echo "🎊 系统验证完成！"
    return 0
}

# 主函数
main() {
    log_info "==================== 新用户入职检查开始 ===================="

    # 检查是否为新用户
    if ! is_new_user; then
        log_info "检测到已有用户配置，跳过新用户入职流程"
        return 0
    fi

    # 显示欢迎信息
    show_welcome_banner

    # 检测环境
    detect_user_environment

    # 检查依赖
    if ! check_system_dependencies; then
        echo "❌ 系统依赖检查失败，请安装缺失的工具后重新运行"
        return 1
    fi

    # 交互式安装向导
    if ! interactive_installation_wizard; then
        echo "⏸️ 用户选择跳过安装"
        return 0
    fi

    # 执行安装
    if perform_installation; then
        echo "✅ 安装成功！"

        # 创建用户配置
        create_user_config

        # 快速验证
        quick_verification

        # 显示后续步骤
        show_next_steps

        log_success "新用户入职完成"
        log_info "==================== 新用户入职成功 ===================="

    else
        echo "❌ 安装失败"
        echo ""
        echo "🔧 故障排除："
        echo "   1. 检查网络连接"
        echo "   2. 确保有足够的磁盘空间"
        echo "   3. 查看安装日志: $ONBOARDING_LOG"
        echo "   4. 手动运行: bash scripts/setup_cursor_protection.sh"
        echo ""
        echo "📞 获取帮助："
        echo "   • docs/force_local_test/FAQ.md"
        echo "   • docs/force_local_test/DEBUG_GUIDE.md"

        log_warning "新用户入职失败"
        return 1
    fi
}

# 命令行参数处理
case "${1:-}" in
    --check)
        if is_new_user; then
            echo "检测到新用户"
            exit 0
        else
            echo "已配置用户"
            exit 1
        fi
        ;;
    --force)
        log_info "强制执行新用户入职流程"
        rm -f "$USER_CONFIG_FILE" .force_local_test_setup_done
        main
        ;;
    --help|-h)
        echo "新用户入职脚本"
        echo ""
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --check    检查是否为新用户"
        echo "  --force    强制执行入职流程"
        echo "  --help     显示帮助信息"
        ;;
    *)
        main "$@"
        ;;
esac

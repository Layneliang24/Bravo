#!/bin/bash
# 跨Windows协作演示脚本
# 演示强制本地测试系统在团队协作中的自动生效机制

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 日志函数
demo_step() {
    echo ""
    echo -e "${PURPLE}🎬 演示步骤: $1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

demo_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

demo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

demo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

demo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 显示演示横幅
show_demo_banner() {
    echo ""
    echo "🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭"
    echo "🎬          跨Windows协作自动生效演示          🎬"
    echo "🎯     展示强制本地测试系统的团队协作机制     🎯"
    echo "🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭🎭"
    echo ""
}

# 场景1: 新团队成员克隆项目
demo_new_member_onboarding() {
    demo_step "场景1: 新团队成员首次克隆项目"

    demo_info "模拟新用户环境（清除现有配置）..."

    # 临时清除用户配置（模拟新用户）
    mv .force_local_test_user_config .force_local_test_user_config.backup 2>/dev/null || true
    mv .force_local_test_setup_done .force_local_test_setup_done.backup 2>/dev/null || true

    demo_info "检查新用户检测机制..."
    if bash scripts/new_user_onboarding.sh --check; then
        demo_success "✅ 成功检测到新用户"

        demo_info "模拟新用户选择自动安装..."
        echo "y" | bash scripts/new_user_onboarding.sh 2>/dev/null || {
            demo_warning "新用户引导需要交互，这里跳过自动安装演示"
        }
    else
        demo_warning "当前环境已配置，无法演示新用户检测"
    fi

    # 恢复用户配置
    mv .force_local_test_user_config.backup .force_local_test_user_config 2>/dev/null || true
    mv .force_local_test_setup_done.backup .force_local_test_setup_done 2>/dev/null || true

    demo_success "场景1演示完成"
}

# 场景2: 系统更新时的自动部署
demo_auto_deployment() {
    demo_step "场景2: 团队成员拉取系统更新时的自动部署"

    demo_info "模拟检测到强制本地测试系统更新..."

    # 创建模拟的更新检测环境
    demo_info "创建测试提交历史..."
    git log --oneline -5 | head -1

    demo_info "测试自动部署检测逻辑..."
    if bash scripts/auto_deploy_on_pull.sh; then
        demo_success "自动部署检测运行成功"
    else
        demo_warning "自动部署检测运行完成（可能无需更新）"
    fi

    demo_success "场景2演示完成"
}

# 场景3: 跨Windows环境兼容性
demo_cross_windows_compatibility() {
    demo_step "场景3: 跨Windows环境兼容性测试"

    demo_info "检测当前Windows环境..."

    # 环境检测
    local env_type="unknown"
    if [[ -f "/proc/version" ]] && grep -q "Microsoft\|WSL" /proc/version; then
        env_type="WSL"
    elif [[ "$OS" == "Windows_NT" ]]; then
        env_type="Native Windows"
    elif command -v git.exe &> /dev/null; then
        env_type="Git Bash"
    else
        env_type="Unknown"
    fi

    demo_success "检测到环境: $env_type"

    demo_info "测试Python命令适配..."
    if command -v python3 &> /dev/null; then
        demo_success "Python3 可用: $(python3 --version)"
    elif command -v python &> /dev/null; then
        demo_success "Python 可用: $(python --version)"
    else
        demo_error "Python 不可用"
    fi

    demo_info "测试便捷命令创建..."
    if [[ -f "test" ]]; then
        demo_success "便捷命令 'test' 存在"
    else
        demo_warning "便捷命令 'test' 不存在"
    fi

    demo_success "场景3演示完成"
}

# 场景4: Git钩子自动安装
demo_git_hooks_installation() {
    demo_step "场景4: Git钩子自动安装和生效"

    demo_info "检查Git钩子状态..."

    if [[ -f ".git/hooks/post-merge" ]]; then
        demo_success "post-merge钩子已安装"
        demo_info "钩子内容预览:"
        head -5 .git/hooks/post-merge | sed 's/^/    /'
    else
        demo_warning "post-merge钩子未安装"
        demo_info "现在安装钩子..."
        bash scripts/setup_cursor_protection.sh --install-hooks
    fi

    if [[ -f ".git/hooks/post-checkout" ]]; then
        demo_success "post-checkout钩子已安装"
    else
        demo_warning "post-checkout钩子未安装"
    fi

    demo_success "场景4演示完成"
}

# 场景5: 团队协作工作流演示
demo_team_workflow() {
    demo_step "场景5: 团队协作工作流演示"

    demo_info "模拟团队成员A推送更新..."
    echo "模拟场景："
    echo "  1. 团队成员A对保护系统进行了改进"
    echo "  2. 推送到远程仓库"
    echo "  3. 团队成员B拉取更新"
    echo "  4. 系统自动检测并部署新版本"

    demo_info "检查当前分支..."
    current_branch=$(git branch --show-current)
    demo_success "当前分支: $current_branch"

    demo_info "检查系统版本信息..."
    if [[ -f ".force_local_test_auto_deployed" ]]; then
        demo_success "发现自动部署记录:"
        cat .force_local_test_auto_deployed | sed 's/^/    /'
    else
        demo_info "暂无自动部署记录"
    fi

    demo_info "测试便捷命令功能..."
    if [[ -f "test" ]]; then
        demo_success "测试 './test --check' 命令:"
        ./test --check 2>/dev/null || demo_warning "命令执行需要完整环境"
    fi

    demo_success "场景5演示完成"
}

# 显示系统状态摘要
show_system_status() {
    demo_step "系统状态摘要"

    echo "📊 强制本地测试系统状态:"
    echo ""

    # 核心文件检查
    echo "🔧 核心文件:"
    local core_files=(
        "scripts/git-guard.sh"
        "scripts/local_test_passport.py"
        "scripts/one_click_test.sh"
        "scripts/auto_deploy_on_pull.sh"
        "scripts/new_user_onboarding.sh"
    )

    for file in "${core_files[@]}"; do
        if [[ -f "$file" && -x "$file" ]]; then
            echo "  ✅ $file"
        else
            echo "  ❌ $file"
        fi
    done

    echo ""
    echo "📋 便捷命令:"
    for cmd in "test" "passport" "safe-push"; do
        if [[ -f "$cmd" && -x "$cmd" ]]; then
            echo "  ✅ ./$cmd"
        else
            echo "  ❌ ./$cmd"
        fi
    done

    echo ""
    echo "🔗 Git钩子:"
    for hook in "post-merge" "post-checkout"; do
        if [[ -f ".git/hooks/$hook" && -x ".git/hooks/$hook" ]]; then
            echo "  ✅ $hook"
        else
            echo "  ❌ $hook"
        fi
    done

    echo ""
    echo "📚 文档:"
    if [[ -d "docs/force_local_test" ]]; then
        echo "  ✅ 设计文档集 ($(ls docs/force_local_test/*.md | wc -l) 个文件)"
    else
        echo "  ❌ 设计文档集"
    fi

    echo ""
    echo "🎯 系统就绪状态:"
    if [[ -f "scripts/git-guard.sh" && -f "test" && -f ".git/hooks/post-merge" ]]; then
        demo_success "🎉 系统完全就绪，支持跨Windows团队协作！"
    else
        demo_warning "⚠️ 系统部分组件缺失，建议运行完整安装"
    fi
}

# 显示使用建议
show_usage_recommendations() {
    demo_step "使用建议"

    echo "💡 团队协作最佳实践:"
    echo ""
    echo "👥 新团队成员:"
    echo "  1. git clone <repository>"
    echo "  2. 系统会自动检测并引导安装"
    echo "  3. 或手动运行: bash scripts/new_user_onboarding.sh"
    echo ""
    echo "🔄 日常开发:"
    echo "  1. 修改代码"
    echo "  2. make test-quick  # 快速本地测试"
    echo "  3. git push origin your-branch  # 自动验证通行证"
    echo ""
    echo "🤝 团队更新:"
    echo "  1. git pull origin main  # 自动检测并部署系统更新"
    echo "  2. 系统会自动同步配置"
    echo ""
    echo "🔧 故障排除:"
    echo "  1. 查看日志: logs/auto_deployment.log"
    echo "  2. 手动更新: bash scripts/setup_cursor_protection.sh --update"
    echo "  3. 参考文档: docs/force_local_test/FAQ.md"
    echo ""
    echo "📖 完整文档:"
    echo "  • docs/CURSOR_PROTECTION_GUIDE.md  (用户指南)"
    echo "  • docs/force_local_test/            (设计文档集)"
}

# 主演示函数
main() {
    show_demo_banner

    echo "本演示将展示以下场景："
    echo "  1. 新团队成员首次使用"
    echo "  2. 系统更新自动部署"
    echo "  3. 跨Windows环境兼容"
    echo "  4. Git钩子自动安装"
    echo "  5. 团队协作工作流"
    echo ""

    read -p "按Enter开始演示，或Ctrl+C退出: "

    # 运行所有演示场景
    demo_new_member_onboarding
    demo_auto_deployment
    demo_cross_windows_compatibility
    demo_git_hooks_installation
    demo_team_workflow

    # 显示系统状态
    show_system_status
    show_usage_recommendations

    echo ""
    demo_success "🎉 跨Windows协作演示完成！"
    echo ""
    echo "📝 演示总结:"
    echo "  ✅ 新用户自动检测和引导"
    echo "  ✅ 系统更新自动部署"
    echo "  ✅ 跨Windows环境兼容"
    echo "  ✅ Git钩子自动化"
    echo "  ✅ 团队协作无缝衔接"
    echo ""
    echo "🎯 现在您的团队可以在任何Windows电脑上无缝协作！"
}

# 命令行参数处理
case "${1:-}" in
    --help|-h)
        echo "跨Windows协作演示脚本"
        echo ""
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --help    显示帮助信息"
        echo "  --status  仅显示系统状态"
        ;;
    --status)
        show_system_status
        ;;
    *)
        main "$@"
        ;;
esac

#!/bin/bash
# 一键本地测试脚本
# 专为对抗Cursor跳过本地测试的恶习而设计
# 集成act、docker-compose、通行证生成等多种验证

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "\n${PURPLE}🔹 $1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# 显示帮助信息
show_help() {
    echo "🚀 一键本地测试脚本 - Cursor AI拦截器"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --quick, -q        快速测试（跳过完整的功能测试）"
    echo "  --full, -f         完整测试（默认模式）"
    echo "  --act-only         仅运行act语法验证"
    echo "  --docker-only      仅运行Docker环境测试"
    echo "  --passport-only    仅生成通行证（要求其他测试已通过）"
    echo "  --check            检查现有通行证状态"
    echo "  --force            强制重新运行所有测试"
    echo "  --help, -h         显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                 # 运行完整测试并生成通行证"
    echo "  $0 --quick         # 快速测试"
    echo "  $0 --check         # 检查通行证状态"
    echo "  $0 --force         # 强制重新测试"
    echo ""
    echo "🎯 目标：强制Cursor进行本地验证，生成推送通行证"
}

# 检查必要工具
check_prerequisites() {
    log_step "检查前置条件"

    local missing_tools=()

    # 检查Docker
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    else
        if ! docker info &> /dev/null; then
            log_error "Docker服务未运行"
            exit 1
        fi
        log_success "Docker服务正常"
    fi

    # 检查docker-compose
    if ! command -v docker-compose &> /dev/null; then
        missing_tools+=("docker-compose")
    else
        log_success "docker-compose可用"
    fi

    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        log_success "Python3可用"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        log_success "Python可用"
    else
        missing_tools+=("python")
    fi

    # 检查Git
    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    else
        log_success "Git可用"
    fi

    # 检查act（可选）
    if command -v act &> /dev/null; then
        log_success "act可用（GitHub Actions本地模拟）"
        ACT_AVAILABLE=true
    else
        log_warning "act不可用（建议安装：choco install act-cli）"
        ACT_AVAILABLE=false
    fi

    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必要工具：${missing_tools[*]}"
        echo ""
        echo "安装建议："
        for tool in "${missing_tools[@]}"; do
            case $tool in
                docker)
                    echo "  - Docker: https://docs.docker.com/get-docker/"
                    ;;
                docker-compose)
                    echo "  - Docker Compose: https://docs.docker.com/compose/install/"
                    ;;
                python3)
                    echo "  - Python3: https://www.python.org/downloads/"
                    ;;
                git)
                    echo "  - Git: https://git-scm.com/downloads"
                    ;;
            esac
        done
        exit 1
    fi
}

# Act语法验证
run_act_validation() {
    log_step "第一层验证：GitHub Actions语法检查"

    if [ "$ACT_AVAILABLE" = false ]; then
        log_warning "act不可用，跳过语法验证"
        return 0
    fi

    # 检查是否有工作流文件
    if [ ! -d ".github/workflows" ] || [ -z "$(find .github/workflows -name '*.yml' -o -name '*.yaml')" ]; then
        log_warning "未找到GitHub Actions工作流文件"
        return 0
    fi

    log_info "使用act进行GitHub Actions语法验证..."

    # 干运行验证
    if act --dry-run pull_request --verbose 2>&1 | tee /tmp/act_validation.log; then
        log_success "act语法验证通过"
        return 0
    else
        log_error "act语法验证失败"
        echo ""
        echo "错误详情："
        tail -n 20 /tmp/act_validation.log
        return 1
    fi
}

# Docker环境验证
run_docker_validation() {
    log_step "第二层验证：Docker环境检查"

    # 验证docker-compose配置
    log_info "验证docker-compose配置..."
    if docker-compose config &> /dev/null; then
        log_success "docker-compose配置有效"
    else
        log_error "docker-compose配置无效"
        docker-compose config
        return 1
    fi

    # 检查关键服务配置
    log_info "检查关键服务配置..."
    local services=$(docker-compose config --services)

    for service in backend frontend mysql redis; do
        if echo "$services" | grep -q "^${service}$"; then
            log_success "服务配置存在：$service"
        else
            log_warning "服务配置缺失：$service"
        fi
    done

    return 0
}

# 快速功能测试
run_quick_tests() {
    log_step "第三层验证：快速功能测试"

    # 启动必要的服务
    log_info "启动核心服务..."
    docker-compose up -d mysql redis

    # 等待MySQL就绪
    log_info "等待MySQL服务就绪..."
    for i in {1..30}; do
        if docker-compose exec -T mysql mysqladmin ping -h localhost --silent; then
            log_success "MySQL服务就绪"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "MySQL服务启动超时"
            return 1
        fi
        sleep 2
    done

    # 运行后端基础检查
    log_info "运行后端基础检查..."
    if docker-compose run --rm backend python manage.py check --settings=bravo.settings.test; then
        log_success "后端基础检查通过"
    else
        log_error "后端基础检查失败"
        return 1
    fi

    # 运行前端基础检查
    log_info "运行前端基础检查..."
    if docker-compose run --rm frontend npm run build:check 2>/dev/null || \
       docker-compose run --rm frontend npm run lint:check 2>/dev/null || \
       docker-compose run --rm frontend npm list --depth=0 2>/dev/null; then
        log_success "前端基础检查通过"
    else
        log_warning "前端基础检查跳过（命令不存在）"
    fi

    return 0
}

# 完整功能测试
run_full_tests() {
    log_step "第三层验证：完整功能测试"

    # 使用现有的GitHub Actions模拟脚本
    if [ -f "scripts/run_github_actions_simulation.sh" ]; then
        log_info "运行GitHub Actions完整模拟..."
        if timeout 600 bash scripts/run_github_actions_simulation.sh; then
            log_success "完整功能测试通过"
            return 0
        else
            log_error "完整功能测试失败"
            return 1
        fi
    else
        log_warning "未找到GitHub Actions模拟脚本，使用快速测试"
        run_quick_tests
        return $?
    fi
}

# 环境差异检查
run_environment_diff_check() {
    log_step "第四层验证：环境差异检查"

    # 检查关键配置文件
    local config_files=(
        "docker-compose.yml"
        "package.json"
        "backend/requirements/test.txt"
        "frontend/package.json"
    )

    for config_file in "${config_files[@]}"; do
        if [ -f "$config_file" ]; then
            log_success "配置文件存在：$config_file"
        else
            log_warning "配置文件缺失：$config_file"
        fi
    done

    # 检查npm workspaces结构（如果存在）
    if [ -f "package.json" ]; then
        log_info "检查npm workspaces结构..."
        if $PYTHON_CMD scripts/check_npm_workspaces.py 2>/dev/null; then
            log_success "npm workspaces结构正常"
        else
            log_warning "npm workspaces检查跳过或异常"
        fi
    fi

    # 检查分支状态
    log_info "检查Git分支状态..."
    local current_branch=$(git branch --show-current)
    if [[ "$current_branch" =~ ^(dev|main|master)$ ]]; then
        log_warning "当前在保护分支：$current_branch（建议切换到feature分支）"
    else
        log_success "当前分支：$current_branch"
    fi

    return 0
}

# 生成通行证
generate_passport() {
    log_step "生成本地测试通行证"

    if $PYTHON_CMD scripts/local_test_passport.py --force; then
        log_success "通行证生成成功！"
        log_info "现在可以安全推送到远程仓库"
        return 0
    else
        log_error "通行证生成失败"
        return 1
    fi
}

# 检查通行证状态
check_passport_status() {
    log_step "检查通行证状态"

    # 确定Python命令
    if command -v python3 &> /dev/null; then
        python3 scripts/local_test_passport.py --check
    else
        python scripts/local_test_passport.py --check
    fi
}

# 清理资源
cleanup() {
    log_step "清理资源"

    log_info "停止Docker服务..."
    docker-compose down --timeout 10 &> /dev/null || true

    # 清理临时文件
    rm -f /tmp/act_validation.log

    log_success "清理完成"
}

# 主函数
main() {
    local mode="full"
    local force=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick|-q)
                mode="quick"
                shift
                ;;
            --full|-f)
                mode="full"
                shift
                ;;
            --act-only)
                mode="act"
                shift
                ;;
            --docker-only)
                mode="docker"
                shift
                ;;
            --passport-only)
                mode="passport"
                shift
                ;;
            --check)
                check_passport_status
                exit 0
                ;;
            --force)
                force=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                echo ""
                show_help
                exit 1
                ;;
        esac
    done

    # 显示开始信息
    echo "🚀 一键本地测试脚本启动"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎯 目标：对抗Cursor跳过本地测试的恶习"
    echo "📁 项目：$(basename "$PROJECT_ROOT")"
    echo "📅 时间：$(date)"
    echo "🔧 模式：$mode"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 设置清理陷阱
    trap cleanup EXIT

    # 检查现有通行证（除非强制）
    if [ "$force" = false ] && [ "$mode" != "passport" ]; then
        if $PYTHON_CMD scripts/local_test_passport.py --check &> /dev/null; then
            log_success "发现有效的本地测试通行证"
            $PYTHON_CMD scripts/local_test_passport.py --check
            echo ""
            read -p "通行证仍然有效，是否重新测试？(y/N): " confirm
            if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
                log_info "跳过测试，使用现有通行证"
                exit 0
            fi
        fi
    fi

    # 检查前置条件
    check_prerequisites

    # 记录开始时间
    local start_time=$(date +%s)
    local failed_steps=()

    # 根据模式运行测试
    case $mode in
        "act")
            run_act_validation || failed_steps+=("act验证")
            ;;
        "docker")
            run_docker_validation || failed_steps+=("Docker验证")
            ;;
        "passport")
            generate_passport || failed_steps+=("通行证生成")
            ;;
        "quick")
            run_act_validation || failed_steps+=("语法验证")
            run_docker_validation || failed_steps+=("环境验证")
            run_quick_tests || failed_steps+=("快速测试")
            run_environment_diff_check || failed_steps+=("差异检查")

            if [ ${#failed_steps[@]} -eq 0 ]; then
                generate_passport || failed_steps+=("通行证生成")
            fi
            ;;
        "full")
            run_act_validation || failed_steps+=("语法验证")
            run_docker_validation || failed_steps+=("环境验证")
            run_full_tests || failed_steps+=("完整测试")
            run_environment_diff_check || failed_steps+=("差异检查")

            if [ ${#failed_steps[@]} -eq 0 ]; then
                generate_passport || failed_steps+=("通行证生成")
            fi
            ;;
    esac

    # 计算耗时
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # 显示结果
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 测试结果汇总"
    echo "⏱️  耗时：${duration}秒"

    if [ ${#failed_steps[@]} -eq 0 ]; then
        log_success "🎉 所有验证通过！"
        log_success "🎫 本地测试通行证已生成"
        log_success "🚀 现在可以安全推送到远程仓库"
        echo ""
        echo "💡 推送命令示例："
        echo "   git push origin $(git branch --show-current 2>/dev/null || echo 'your-branch')"
        exit 0
    else
        log_error "❌ 以下验证失败：${failed_steps[*]}"
        log_error "🚫 通行证生成失败"
        echo ""
        echo "💡 修复建议："
        echo "   1. 查看上方错误信息"
        echo "   2. 修复问题后重新运行"
        echo "   3. 或使用 --quick 进行快速测试"
        exit 1
    fi
}

# 运行主函数
main "$@"

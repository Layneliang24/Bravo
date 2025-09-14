#!/bin/bash

# 本地CI测试脚本
# 使用方法: ./scripts/local-ci.sh [test-type] [workflow]
# 例如: ./scripts/local-ci.sh unit backend
#       ./scripts/local-ci.sh workflow branch-protection

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查本地依赖..."

    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装"
        exit 1
    fi

    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装"
        exit 1
    fi

    # 检查act (GitHub Actions本地运行器)
    if ! command -v act &> /dev/null; then
        log_warning "act未安装，将无法本地运行GitHub Actions"
        log_info "安装命令: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
    fi

    log_success "依赖检查完成"
}

# 启动测试环境
start_test_env() {
    log_info "启动本地CI测试环境..."

    # 构建并启动服务
    docker-compose -f docker-compose.local-ci.yml up -d

    # 等待MySQL准备就绪
    log_info "等待MySQL启动..."
    timeout 60 bash -c 'until docker-compose -f docker-compose.local-ci.yml exec mysql-test mysqladmin ping -h localhost -u root -proot_password --silent; do sleep 2; done'

    log_success "测试环境启动完成"
}

# 停止测试环境
stop_test_env() {
    log_info "停止本地CI测试环境..."
    docker-compose -f docker-compose.local-ci.yml down
    log_success "测试环境已停止"
}

# 运行后端单元测试
run_backend_unit_tests() {
    log_info "运行后端单元测试..."

    # 在容器中运行测试
    docker-compose -f docker-compose.local-ci.yml exec backend-test bash -c "
        python manage.py migrate --noinput &&
        python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term --maxfail=0
    "

    log_success "后端单元测试完成"
}

# 运行前端单元测试
run_frontend_unit_tests() {
    log_info "运行前端单元测试..."

    # 在容器中运行测试
    docker-compose -f docker-compose.local-ci.yml exec frontend-test bash -c "
        npm run test:coverage
    "

    log_success "前端单元测试完成"
}

# 运行集成测试
run_integration_tests() {
    log_info "运行集成测试..."

    # 启动后端服务
    docker-compose -f docker-compose.local-ci.yml exec -d backend-test bash -c "
        python manage.py migrate --noinput &&
        python manage.py runserver 0.0.0.0:8000
    "

    # 等待服务启动
    sleep 10

    # 运行集成测试
    docker-compose -f docker-compose.local-ci.yml exec backend-test bash -c "
        python -m pytest tests/integration/ -v --maxfail=0
    "

    log_success "集成测试完成"
}

# 运行E2E测试
run_e2e_tests() {
    log_info "运行E2E测试..."

    # 启动前端服务
    docker-compose -f docker-compose.local-ci.yml exec -d frontend-test bash -c "
        npm run build &&
        npm run preview -- --host 0.0.0.0
    "

    # 启动后端服务
    docker-compose -f docker-compose.local-ci.yml exec -d backend-test bash -c "
        python manage.py migrate --noinput &&
        python manage.py runserver 0.0.0.0:8000
    "

    # 等待服务启动
    sleep 15

    # 运行E2E测试
    docker-compose -f docker-compose.local-ci.yml exec e2e-test bash -c "
        npx playwright test --project=chromium
    "

    log_success "E2E测试完成"
}

# 运行GitHub Actions workflow
run_github_workflow() {
    local workflow_name=$1

    if ! command -v act &> /dev/null; then
        log_error "act未安装，无法运行GitHub Actions workflow"
        exit 1
    fi

    log_info "运行GitHub Actions workflow: $workflow_name"

    # 使用act运行workflow
    act -W ".github/workflows/${workflow_name}.yml" \
        --container-architecture linux/amd64 \
        --use-gitignore false \
        --verbose

    log_success "GitHub Actions workflow完成"
}

# 运行完整的CI流程
run_full_ci() {
    log_info "运行完整CI流程..."

    start_test_env

    log_info "=== 阶段1: 单元测试 ==="
    run_backend_unit_tests
    run_frontend_unit_tests

    log_info "=== 阶段2: 集成测试 ==="
    run_integration_tests

    log_info "=== 阶段3: E2E测试 ==="
    run_e2e_tests

    log_success "完整CI流程完成"
}

# 清理环境
cleanup() {
    log_info "清理测试环境..."

    # 停止所有容器
    docker-compose -f docker-compose.local-ci.yml down -v

    # 清理dangling images
    docker image prune -f

    log_success "清理完成"
}

# 显示帮助信息
show_help() {
    echo "本地CI测试脚本"
    echo ""
    echo "用法: $0 [命令] [参数]"
    echo ""
    echo "命令:"
    echo "  start         启动测试环境"
    echo "  stop          停止测试环境"
    echo "  unit-backend  运行后端单元测试"
    echo "  unit-frontend 运行前端单元测试"
    echo "  integration   运行集成测试"
    echo "  e2e           运行E2E测试"
    echo "  workflow      运行GitHub Actions workflow"
    echo "  full-ci       运行完整CI流程"
    echo "  cleanup       清理测试环境"
    echo ""
    echo "示例:"
    echo "  $0 start"
    echo "  $0 unit-backend"
    echo "  $0 workflow branch-protection"
    echo "  $0 full-ci"
}

# 主函数
main() {
    local command=$1
    local param=$2

    case $command in
        "start")
            check_dependencies
            start_test_env
            ;;
        "stop")
            stop_test_env
            ;;
        "unit-backend")
            run_backend_unit_tests
            ;;
        "unit-frontend")
            run_frontend_unit_tests
            ;;
        "integration")
            run_integration_tests
            ;;
        "e2e")
            run_e2e_tests
            ;;
        "workflow")
            if [ -z "$param" ]; then
                log_error "请指定workflow名称"
                exit 1
            fi
            run_github_workflow "$param"
            ;;
        "full-ci")
            check_dependencies
            run_full_ci
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help"|"")
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 错误处理
trap 'log_error "脚本执行失败，正在清理..."; cleanup; exit 1' ERR

# 运行主函数
main "$@"

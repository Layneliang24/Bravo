#!/bin/bash

# 回归测试快速启动脚本
# 用于本地开发环境快速运行回归测试

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
    log_info "检查依赖..."
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi
    
    # 检查Python
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        log_error "Python 未安装"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    # 检查后端服务
    if curl -f http://localhost:8000/api/health &> /dev/null; then
        log_success "后端服务运行中 (http://localhost:8000)"
        BACKEND_RUNNING=true
    else
        log_warning "后端服务未运行"
        BACKEND_RUNNING=false
    fi
    
    # 检查前端服务
    if curl -f http://localhost:3000 &> /dev/null; then
        log_success "前端服务运行中 (http://localhost:3000)"
        FRONTEND_RUNNING=true
    else
        log_warning "前端服务未运行"
        FRONTEND_RUNNING=false
    fi
}

# 启动服务
start_services() {
    log_info "启动必要的服务..."
    
    # 启动后端服务
    if [ "$BACKEND_RUNNING" = false ]; then
        log_info "启动后端服务..."
        cd ../../backend
        if [ -f "manage.py" ]; then
            python manage.py runserver 8000 &
            BACKEND_PID=$!
            log_info "后端服务启动中 (PID: $BACKEND_PID)"
            sleep 5
        else
            log_error "未找到 Django manage.py 文件"
            exit 1
        fi
        cd ../tests/regression
    fi
    
    # 启动前端服务
    if [ "$FRONTEND_RUNNING" = false ]; then
        log_info "启动前端服务..."
        cd ../../frontend
        if [ -f "package.json" ]; then
            npm run dev &
            FRONTEND_PID=$!
            log_info "前端服务启动中 (PID: $FRONTEND_PID)"
            sleep 5
        else
            log_error "未找到前端 package.json 文件"
            exit 1
        fi
        cd ../tests/regression
    fi
    
    # 等待服务就绪
    log_info "等待服务就绪..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/api/health &> /dev/null; do sleep 2; done' || {
        log_error "后端服务启动超时"
        cleanup
        exit 1
    }
    
    timeout 60 bash -c 'until curl -f http://localhost:3000 &> /dev/null; do sleep 2; done' || {
        log_error "前端服务启动超时"
        cleanup
        exit 1
    }
    
    log_success "所有服务已就绪"
}

# 清理函数
cleanup() {
    log_info "清理进程..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        log_info "后端服务已停止"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        log_info "前端服务已停止"
    fi
}

# 运行回归测试
run_regression_tests() {
    local test_type="$1"
    local update_snapshots="$2"
    
    log_info "运行回归测试 (类型: $test_type)..."
    
    local command="node run-regression.js"
    
    case $test_type in
        "api")
            command="$command --api-only"
            ;;
        "ui")
            command="$command --ui-only"
            ;;
        "db")
            command="$command --db-only"
            ;;
        "all")
            # 默认运行所有测试
            ;;
        *)
            log_warning "未知的测试类型: $test_type，运行所有测试"
            ;;
    esac
    
    if [ "$update_snapshots" = "true" ]; then
        command="$command --update-snapshots"
    fi
    
    log_info "执行命令: $command"
    
    if eval $command; then
        log_success "回归测试完成"
        return 0
    else
        log_error "回归测试失败"
        return 1
    fi
}

# 显示帮助信息
show_help() {
    echo "回归测试快速启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -t, --type TYPE        测试类型 (all|api|ui|db) [默认: all]"
    echo "  -u, --update-snapshots 更新快照基线"
    echo "  -s, --skip-services    跳过服务启动检查"
    echo "  -c, --cleanup-only     仅执行清理操作"
    echo "  -h, --help            显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                     # 运行所有回归测试"
    echo "  $0 -t api              # 仅运行API回归测试"
    echo "  $0 -t ui -u            # 运行UI测试并更新快照"
    echo "  $0 -s                  # 跳过服务检查直接运行测试"
    echo "  $0 -c                  # 仅清理进程"
}

# 主函数
main() {
    local test_type="all"
    local update_snapshots="false"
    local skip_services="false"
    local cleanup_only="false"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--type)
                test_type="$2"
                shift 2
                ;;
            -u|--update-snapshots)
                update_snapshots="true"
                shift
                ;;
            -s|--skip-services)
                skip_services="true"
                shift
                ;;
            -c|--cleanup-only)
                cleanup_only="true"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 设置信号处理
    trap cleanup EXIT INT TERM
    
    # 仅清理模式
    if [ "$cleanup_only" = "true" ]; then
        cleanup
        exit 0
    fi
    
    log_info "🚀 启动回归测试..."
    log_info "测试类型: $test_type"
    log_info "更新快照: $update_snapshots"
    log_info "跳过服务检查: $skip_services"
    
    # 检查依赖
    check_dependencies
    
    # 检查和启动服务
    if [ "$skip_services" = "false" ]; then
        check_services
        start_services
    fi
    
    # 运行回归测试
    if run_regression_tests "$test_type" "$update_snapshots"; then
        log_success "🎉 回归测试成功完成！"
        
        # 显示报告位置
        if [ -f "reports/regression-report.html" ]; then
            log_info "📊 HTML报告: $(pwd)/reports/regression-report.html"
        fi
        
        if [ -f "reports/regression-report.json" ]; then
            log_info "📄 JSON报告: $(pwd)/reports/regression-report.json"
        fi
        
        exit 0
    else
        log_error "❌ 回归测试失败"
        
        # 显示失败报告
        if [ -f "reports/regression-report.json" ]; then
            log_info "查看详细报告: $(pwd)/reports/regression-report.json"
        fi
        
        exit 1
    fi
}

# 检查是否在正确的目录中
if [ ! -f "run-regression.js" ]; then
    log_error "请在 tests/regression 目录中运行此脚本"
    exit 1
fi

# 运行主函数
main "$@"
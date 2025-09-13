#!/bin/bash

# 本地GitHub Actions工作流测试脚本
# 自动化触发本地容器测试环境

set -e

echo "🎯 Bravo项目 - 本地GitHub Actions工作流测试"
echo "================================================================"

# 检查依赖
check_dependencies() {
    echo "🔍 检查运行依赖..."

    if ! command -v docker &> /dev/null; then
        echo "❌ Docker未安装，请先安装Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi

    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3未安装，请先安装Python3"
        exit 1
    fi

    echo "✅ 依赖检查通过"
}

# 清理旧环境
cleanup_old_environment() {
    echo "🧹 清理旧的测试环境..."

    docker-compose -f docker-compose.github-actions.yml down -v --remove-orphans 2>/dev/null || true
    docker system prune -f --volumes 2>/dev/null || true

    echo "✅ 环境清理完成"
}

# 设置测试环境
setup_test_environment() {
    echo "⚙️ 设置测试环境..."

    # 确保脚本有执行权限
    chmod +x scripts/local_github_actions.py

    # 创建必要目录
    mkdir -p .github/workflows
    mkdir -p logs

    echo "✅ 测试环境设置完成"
}

# 运行工作流测试
run_workflow_test() {
    local test_type=${1:-"full"}

    echo "🚀 运行工作流测试: $test_type"
    echo "----------------------------------------------------------------"

    case $test_type in
        "quick")
            echo "⚡ 运行快速测试..."
            python3 scripts/local_github_actions.py --job smart-dependencies
            ;;
        "frontend")
            echo "🌐 运行前端测试..."
            python3 scripts/local_github_actions.py --job frontend-tests
            ;;
        "backend")
            echo "🖥️ 运行后端测试..."
            python3 scripts/local_github_actions.py --job backend-tests
            ;;
        "e2e")
            echo "🧪 运行E2E测试..."
            python3 scripts/local_github_actions.py --job e2e-tests
            ;;
        "security")
            echo "🔒 运行安全测试..."
            python3 scripts/local_github_actions.py --job security-validation
            ;;
        "quality")
            echo "🚀 运行质量门控..."
            python3 scripts/local_github_actions.py --job quality-gates
            ;;
        "full"|*)
            echo "🎯 运行完整工作流测试..."
            python3 scripts/local_github_actions.py
            ;;
    esac
}

# 生成测试报告
generate_test_report() {
    echo "📊 生成测试报告..."

    local report_file="logs/workflow_test_report_$(date +%Y%m%d_%H%M%S).md"

    cat > "$report_file" << EOF
# GitHub Actions 本地测试报告

## 测试信息
- **测试时间**: $(date)
- **Git分支**: $(git branch --show-current)
- **Git提交**: $(git rev-parse --short HEAD)
- **测试类型**: $1

## 测试环境
- **Docker版本**: $(docker --version)
- **Docker Compose版本**: $(docker-compose --version)
- **Python版本**: $(python3 --version)

## 测试结果
测试结果已记录在上述输出中。

## 清理状态
环境已自动清理完成。

---
报告生成时间: $(date)
EOF

    echo "✅ 测试报告已生成: $report_file"
}

# 主函数
main() {
    local test_type=${1:-"full"}

    echo "开始时间: $(date)"
    echo ""

    # 执行测试流程
    check_dependencies
    cleanup_old_environment
    setup_test_environment

    # 运行测试并记录结果
    if run_workflow_test "$test_type"; then
        echo ""
        echo "🎉 测试执行完成!"
        generate_test_report "$test_type"
    else
        echo ""
        echo "❌ 测试执行失败!"
        exit 1
    fi

    echo ""
    echo "结束时间: $(date)"
    echo "================================================================"
}

# 显示帮助信息
show_help() {
    cat << EOF
用法: $0 [测试类型]

测试类型:
  quick     - 快速依赖测试
  frontend  - 前端测试
  backend   - 后端测试
  e2e       - E2E测试
  security  - 安全测试
  quality   - 质量门控
  full      - 完整工作流测试 (默认)

示例:
  $0              # 运行完整测试
  $0 quick        # 快速测试
  $0 frontend     # 只测试前端
  $0 backend      # 只测试后端

EOF
}

# 处理命令行参数
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac

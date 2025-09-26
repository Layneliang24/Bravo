#!/bin/bash
# 宿主机依赖安装拦截器
# 这个脚本拦截所有危险的宿主机依赖安装命令

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/logs/dependency-violations.log"
mkdir -p "$(dirname "$LOG_FILE")"

# 获取真实的命令名（从脚本名或第一个参数）
REAL_COMMAND="$(basename "$0")"
if [[ "$REAL_COMMAND" == "dependency-guard.sh" ]]; then
    REAL_COMMAND="$1"
    shift
fi

# 🚨 宿主机依赖安装警告函数
show_host_dependency_warning() {
    local command_full="$1"
    local violation_type="$2"

    echo "🚨🚨🚨 检测到严重违规：$violation_type 🚨🚨🚨"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ 绝对禁止在宿主机安装依赖！"
    echo "📋 违规命令：$command_full"
    echo ""
    echo "⚠️  基于30轮修复血泪教训，宿主机依赖安装会导致："
    echo "   • npm workspaces依赖结构破坏"
    echo "   • Docker容器环境不一致性"
    echo "   • CI/CD流水线执行差异"
    echo "   • 版本冲突和依赖漂移"
    echo "   • 开发环境污染和不可重现"
    echo "   • 噗你阿母，在宿主机装依赖试试！！！"
    echo ""
    echo "🐳 正确的纯Docker开发流程："
    echo "   1. 使用docker-compose up启动服务"
    echo "   2. 进入容器执行依赖操作："
    echo "      docker-compose exec frontend npm install [package]"
    echo "      docker-compose exec backend pip install [package]"
    echo "   3. 或者修改Dockerfile重新构建镜像"
    echo "   4. 所有工具都应该在容器内运行"
    echo ""
    echo "🔧 快速修复命令："
    local container_name=""
    case "$command_full" in
        npm*|yarn*|pnpm*|node*) container_name="frontend" ;;
        pip*|python*) container_name="backend" ;;
        *) container_name="适当的" ;;
    esac
    echo "   docker-compose exec $container_name $command_full"
    echo ""
    echo "⚠️  紧急情况绕过（极度不推荐）："
    echo "   export ALLOW_HOST_DEPENDENCY_INSTALL=true"
    echo "   或输入紧急确认码：DOCKER_NATIVE_BYPASS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 记录违规尝试
    echo "$(date '+%Y-%m-%d %H:%M:%S') | HOST_DEPENDENCY | $violation_type | $command_full" >> "$LOG_FILE"

    # 检查环境变量绕过
    if [[ "$ALLOW_HOST_DEPENDENCY_INSTALL" == "true" ]]; then
        echo "🟡 检测到环境变量绕过，允许宿主机依赖安装"
        echo "$(date '+%Y-%m-%d %H:%M:%S') | HOST_DEPENDENCY_BYPASS_ENV | $command_full" >> "$LOG_FILE"
        return 0
    fi

    # 询问紧急确认码
    echo ""
    read -p "紧急确认码: " response
    if [[ "$response" == "DOCKER_NATIVE_BYPASS" ]]; then
        echo "🟡 紧急绕过确认，允许宿主机依赖安装"
        echo "$(date '+%Y-%m-%d %H:%M:%S') | HOST_DEPENDENCY_BYPASS_EMERGENCY | $command_full" >> "$LOG_FILE"
        return 0
    else
        echo "❌ 操作被取消 - 请使用Docker容器进行依赖管理！"
        echo "💡 推荐命令：docker-compose exec [service] $command_full"
        exit 1
    fi
}

# 检测危险的宿主机依赖安装命令
args="$*"
command_full="$REAL_COMMAND $args"

case "$REAL_COMMAND" in
    npm|yarn|pnpm)
        if [[ "$args" =~ (^|[[:space:]])(install|ci|add|update|i)([[:space:]]|$) ]]; then
            show_host_dependency_warning "$command_full" "Node.js包管理违规"
        fi
        ;;
    pip|pip3)
        if [[ "$args" =~ (^|[[:space:]])(install|upgrade|-U)([[:space:]]|$) ]]; then
            show_host_dependency_warning "$command_full" "Python包管理违规"
        fi
        ;;
    apt|apt-get|yum|dnf|brew)
        if [[ "$args" =~ (^|[[:space:]])(install|update|upgrade)([[:space:]]|$) ]]; then
            show_host_dependency_warning "$command_full" "系统包管理违规"
        fi
        ;;
    composer)
        if [[ "$args" =~ (^|[[:space:]])(install|update|require)([[:space:]]|$) ]]; then
            show_host_dependency_warning "$command_full" "PHP包管理违规"
        fi
        ;;
esac

# 找到真正的命令并执行
real_command_path=""
case "$REAL_COMMAND" in
    npm)
        real_command_path="$(command -v npm.cmd 2>/dev/null || command -v npm 2>/dev/null | grep -v dependency-guard)"
        ;;
    pip|pip3)
        real_command_path="$(command -v $REAL_COMMAND 2>/dev/null | grep -v dependency-guard)"
        ;;
    *)
        real_command_path="$(command -v $REAL_COMMAND 2>/dev/null | grep -v dependency-guard)"
        ;;
esac

if [[ -x "$real_command_path" ]]; then
    exec "$real_command_path" "$@"
else
    echo "❌ 真正的 $REAL_COMMAND 命令未找到"
    exit 127
fi

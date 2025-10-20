#!/bin/bash
# 30秒超时输入助手函数
# 专门设计用于阻止AI自动化绕过

# 带超时的安全输入函数
read_with_timeout() {
    local prompt="$1"
    local timeout_seconds=${2:-30}
    local response=""

    # 所有提示信息输出到 stderr，避免污染返回值
    echo "" >&2
    echo "⏰ WARNING: ${timeout_seconds}秒后自动超时终止" >&2
    echo "🤖 INFO: AI无法通过等待绕过此验证" >&2
    echo "🛡️  INFO: 必须由人类在真实终端中手动输入" >&2
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2

    # 检测非交互式环境
    if ! tty -s; then
        echo "🚨 检测到非交互式输入尝试 - 拒绝验证" >&2
        echo "❌ 安全限制：必须在真实终端中手动输入" >&2
        return 1
    fi

    # 检测管道输入
    if [[ -p /dev/stdin ]]; then
        echo "🚨 检测到管道输入尝试 - 拒绝验证" >&2
        echo "❌ 安全限制：禁止使用 echo 'code' | command 等自动化绕过" >&2
        return 1
    fi

    # 使用bash内置的read超时功能
    echo -n "$prompt" >&2
    if read -t "$timeout_seconds" response; then
        # 只有用户输入输出到 stdout（被调用者捕获）
        echo "$response"
        return 0
    else
        echo "" >&2
        echo "" >&2
        echo "⏰ TIMEOUT: ${timeout_seconds}秒超时 - 自动拒绝操作" >&2
        echo "🤖 INFO: AI应该继续修复问题而不是尝试绕过保护机制" >&2
        echo "💡 TIP: 建议运行本地测试获得通行证后再操作" >&2
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2

        # 记录超时事件
        local log_file="logs/security-violations.log"
        mkdir -p "$(dirname "$log_file")"
        echo "$(date '+%Y-%m-%d %H:%M:%S') | TIMEOUT_REJECTION | ${timeout_seconds}秒超时拒绝 | $prompt" >> "$log_file"

        return 1
    fi
}

# 导出函数供其他脚本使用
export -f read_with_timeout

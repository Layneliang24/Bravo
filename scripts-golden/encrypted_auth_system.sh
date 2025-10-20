#!/bin/bash
# 基于加密密码的统一验证系统
# 只有知道真实密码的人类才能通过验证

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AUTH_CONFIG_FILE="$PROJECT_ROOT/.auth-config"

# 初始化加密密码配置（首次运行时）
initialize_auth_system() {
    if [[ ! -f "$AUTH_CONFIG_FILE" ]]; then
        echo "🔐 首次设置加密验证系统"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "请设置一个主密码（只有您知道）："
        echo "💡 建议使用包含数字、字母、符号的强密码"
        echo "⚠️  请妥善保管此密码，丢失后需重新初始化系统"
        echo ""

        read -s -p "设置主密码: " master_password
        echo ""
        read -s -p "确认主密码: " confirm_password
        echo ""

        if [[ "$master_password" != "$confirm_password" ]]; then
            echo "❌ 密码确认失败，请重新运行初始化"
            exit 1
        fi

        if [[ ${#master_password} -lt 8 ]]; then
            echo "❌ 密码长度不足8位，请重新运行初始化"
            exit 1
        fi

        # 生成盐值并加密密码
        local salt=$(openssl rand -hex 16)
        local hashed_password=$(echo -n "$master_password$salt" | sha256sum | cut -d' ' -f1)

        # 保存加密配置
        cat > "$AUTH_CONFIG_FILE" << EOF
# 加密验证系统配置文件
# 请勿手动修改此文件
SALT=$salt
HASH=$hashed_password
CREATED="$(date '+%Y-%m-%d %H:%M:%S')"
EOF

        chmod 600 "$AUTH_CONFIG_FILE"  # 只有所有者可读写

        echo ""
        echo "✅ 加密验证系统初始化成功"
        echo "🔐 密码已加密保存，AI无法获取您的真实密码"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi
}

# 验证密码
verify_password() {
    local prompt="$1"
    local context="$2"

    # 确保配置文件存在
    if [[ ! -f "$AUTH_CONFIG_FILE" ]]; then
        echo "❌ 加密验证系统未初始化"
        echo "💡 请运行: bash scripts/encrypted_auth_system.sh --init"
        return 1
    fi

    # 读取加密配置
    source "$AUTH_CONFIG_FILE"

    echo ""
    echo "🔐 加密验证检查点"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎯 验证场景: $context"
    echo "🤖 AI提示: AI无法知道您的真实密码"
    echo "👤 人类提示: 请输入您设置的主密码"
    echo "⏰ 30秒后自动超时"
    echo ""

    # 使用超时输入
    source "$PROJECT_ROOT/scripts-golden/timeout_input_helper.sh"
    local input_password
    input_password=$(read_with_timeout "🔑 请输入主密码: ")

    if [[ $? -ne 0 ]]; then
        echo "❌ 输入超时或被取消"
        return 1
    fi

    # 验证密码
    local test_hash=$(echo -n "$input_password$SALT" | sha256sum | cut -d' ' -f1)

    if [[ "$test_hash" == "$HASH" ]]; then
        echo ""
        echo "✅ 密码验证成功"
        echo "🔓 已授权继续操作"

        # 记录成功验证
        local log_file="$PROJECT_ROOT/logs/auth-success.log"
        mkdir -p "$(dirname "$log_file")"
        echo "$(date '+%Y-%m-%d %H:%M:%S') | AUTH_SUCCESS | $context | $(whoami)" >> "$log_file"

        return 0
    else
        echo ""
        echo "❌ 密码验证失败"
        echo "🚫 操作被拒绝"

        # 记录失败验证
        local log_file="$PROJECT_ROOT/logs/auth-failures.log"
        mkdir -p "$(dirname "$log_file")"
        echo "$(date '+%Y-%m-%d %H:%M:%S') | AUTH_FAILURE | $context | $(whoami)" >> "$log_file"

        return 1
    fi
}

# 重置验证系统
reset_auth_system() {
    echo "⚠️  警告：这将删除现有的加密验证配置"
    echo "🔄 您需要重新设置主密码"
    echo ""
    read -p "确定要重置验证系统吗？(输入 RESET 确认): " confirm

    if [[ "$confirm" == "RESET" ]]; then
        rm -f "$AUTH_CONFIG_FILE"
        echo "✅ 验证系统已重置"
        echo "💡 下次验证时将自动初始化新密码"
    else
        echo "❌ 重置被取消"
        exit 1
    fi
}

# 命令行接口
case "${1:-verify}" in
    --init|init)
        initialize_auth_system
        ;;
    --reset|reset)
        reset_auth_system
        ;;
    --verify|verify)
        verify_password "${2:-请输入密码}" "${3:-未知操作}"
        ;;
    --help|help)
        echo "加密验证系统使用说明："
        echo "  --init    初始化验证系统（设置主密码）"
        echo "  --verify  验证密码（默认操作）"
        echo "  --reset   重置验证系统（删除现有配置）"
        echo "  --help    显示此帮助信息"
        ;;
    *)
        verify_password "$1" "$2"
        ;;
esac

#!/bin/bash
# PATH劫持管理脚本 - 在PATH前面插入拦截器目录

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INTERCEPTORS_DIR="$PROJECT_ROOT/scripts-golden/path-interceptors"

# PATH劫持函数
setup_path_hijacking() {
    echo "🔧 设置PATH劫持拦截..."
    
    # 检查拦截器目录是否存在
    if [[ ! -d "$INTERCEPTORS_DIR" ]]; then
        echo "❌ 拦截器目录不存在: $INTERCEPTORS_DIR"
        return 1
    fi
    
    # 检查PATH中是否已包含拦截器目录
    if [[ ":$PATH:" == *":$INTERCEPTORS_DIR:"* ]]; then
        echo "✅ PATH劫持已激活"
        return 0
    fi
    
    # 将拦截器目录添加到PATH最前面
    export PATH="$INTERCEPTORS_DIR:$PATH"
    
    echo "✅ PATH劫持设置成功"
    echo "📋 拦截器路径: $INTERCEPTORS_DIR"
    
    # 验证拦截效果
    echo "🔍 验证拦截效果:"
    for cmd in npm pip python go cargo; do
        local cmd_path=$(which "$cmd" 2>/dev/null)
        if [[ "$cmd_path" == "$INTERCEPTORS_DIR/"* ]]; then
            echo "  ✅ $cmd -> $cmd_path"
        else
            echo "  ⚠️  $cmd -> $cmd_path (未被拦截)"
        fi
    done
}

# 移除PATH劫持
remove_path_hijacking() {
    echo "🔄 移除PATH劫持..."
    
    # 从PATH中移除拦截器目录
    PATH=$(echo "$PATH" | sed "s|$INTERCEPTORS_DIR:||g" | sed "s|:$INTERCEPTORS_DIR||g")
    export PATH
    
    echo "✅ PATH劫持已移除"
}

# 检查PATH劫持状态
check_path_hijacking_status() {
    if [[ ":$PATH:" == *":$INTERCEPTORS_DIR:"* ]]; then
        echo "✅ PATH劫持已激活"
        echo "📋 拦截器路径: $INTERCEPTORS_DIR"
        return 0
    else
        echo "❌ PATH劫持未激活"
        return 1
    fi
}

# 命令行接口
case "${1:-setup}" in
    setup|enable)
        setup_path_hijacking
        ;;
    remove|disable)
        remove_path_hijacking
        ;;
    status|check)
        check_path_hijacking_status
        ;;
    test)
        echo "🧪 测试拦截效果:"
        echo "Current PATH前3个目录:"
        echo "$PATH" | tr ':' '\n' | head -3 | nl
        echo ""
        echo "命令定位测试:"
        for cmd in npm pip python; do
            echo "$cmd: $(which "$cmd" 2>/dev/null || echo '未找到')"
        done
        ;;
    *)
        echo "PATH劫持管理脚本"
        echo "使用方法: $0 {setup|remove|status|test}"
        echo ""
        echo "  setup   - 启用PATH劫持拦截"
        echo "  remove  - 禁用PATH劫持拦截"
        echo "  status  - 检查拦截状态"
        echo "  test    - 测试拦截效果"
        ;;
esac

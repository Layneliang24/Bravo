#!/bin/bash
"""
Git --no-verify 保护设置脚本

提供多种方案阻止--no-verify的使用：
1. Git Alias方案
2. Shell Function方案  
3. PATH劫持方案
"""

echo "🛡️ Git --no-verify 保护设置脚本"
echo "基于30轮修复血泪教训 - 彻底阻止绕过检查！"
echo ""

# 创建日志目录
mkdir -p logs

echo "📋 可用方案："
echo "1. Git Alias方案 (推荐)"
echo "2. Shell Function方案"
echo "3. PATH劫持方案 (最强力)"
echo "4. 显示当前保护状态"
echo ""

read -p "选择方案 [1-4]: " choice

case $choice in
    1)
        echo "🔧 设置Git Alias方案..."
        
        # 设置git commit别名，检查--no-verify
        git config alias.commit '!f() { 
            if echo "$@" | grep -q "\-\-no-verify\|\-n"; then 
                echo "🚨 检测到--no-verify违规！"; 
                echo "❌ 禁止使用--no-verify跳过检查"; 
                echo "💡 请修复检查问题而非绕过检查"; 
                echo "$(date): BLOCKED git commit --no-verify $@" >> logs/git-no-verify-attempts.log; 
                exit 1; 
            fi; 
            git-real commit "$@"; 
        }; f'
        
        # 备份真正的git commit
        git config alias.git-real '!git'
        
        echo "✅ Git Alias保护已设置"
        echo "📊 违规尝试将记录到 logs/git-no-verify-attempts.log"
        ;;
        
    2) 
        echo "🔧 设置Shell Function方案..."
        
        # 创建shell function
        cat >> ~/.bashrc << 'EOF'

# Git --no-verify 保护函数
git() {
    if [[ "$1" == "commit" ]] && echo "$@" | grep -q "\-\-no-verify\|\-n"; then
        echo "🚨 检测到--no-verify违规！"
        echo "❌ 禁止使用--no-verify跳过检查" 
        echo "💡 请修复检查问题而非绕过检查"
        echo "$(date): BLOCKED git commit --no-verify $@" >> logs/git-no-verify-attempts.log
        return 1
    fi
    
    # 调用真正的git命令
    command git "$@"
}
EOF
        
        echo "✅ Shell Function保护已设置"
        echo "📝 请重新打开终端或执行: source ~/.bashrc"
        ;;
        
    3)
        echo "🔧 设置PATH劫持方案（最强力）..."
        
        # 创建git包装脚本
        mkdir -p ~/bin
        
        cat > ~/bin/git << 'EOF'
#!/bin/bash
# Git --no-verify 拦截脚本

if [[ "$1" == "commit" ]] && echo "$@" | grep -q "\-\-no-verify\|\-n"; then
    echo "🚨 检测到--no-verify违规！"
    echo "❌ 禁止使用--no-verify跳过检查"
    echo "💡 请修复检查问题而非绕过检查" 
    echo "🔗 文档: docs/architecture/ADR-001-npm-workspaces.md"
    echo "$(date): BLOCKED git commit --no-verify $@" >> logs/git-no-verify-attempts.log
    exit 1
fi

# 调用真正的git（从/usr/bin或/usr/local/bin）
if [[ -x "/usr/bin/git" ]]; then
    exec "/usr/bin/git" "$@"
elif [[ -x "/usr/local/bin/git" ]]; then
    exec "/usr/local/bin/git" "$@"  
else
    # Windows Git Bash 路径
    exec "/c/Program Files/Git/bin/git.exe" "$@"
fi
EOF
        
        chmod +x ~/bin/git
        
        # 添加到PATH
        if ! echo $PATH | grep -q "$HOME/bin"; then
            echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
            echo "📝 已添加 ~/bin 到 PATH，请重新打开终端"
        fi
        
        echo "✅ PATH劫持保护已设置"
        echo "🔧 包装脚本位置: ~/bin/git"
        ;;
        
    4)
        echo "📊 当前保护状态："
        echo ""
        
        # 检查Git Alias
        if git config --get alias.commit | grep -q "no-verify"; then
            echo "✅ Git Alias保护: 已启用"
        else
            echo "❌ Git Alias保护: 未启用"  
        fi
        
        # 检查Shell Function
        if declare -f git | grep -q "no-verify"; then
            echo "✅ Shell Function保护: 已启用"
        else
            echo "❌ Shell Function保护: 未启用"
        fi
        
        # 检查PATH劫持
        if [[ -x "~/bin/git" ]]; then
            echo "✅ PATH劫持保护: 已启用"
        else
            echo "❌ PATH劫持保护: 未启用"
        fi
        
        # 显示日志
        if [[ -f "logs/git-no-verify-attempts.log" ]]; then
            echo ""
            echo "📊 最近的违规尝试："
            tail -5 logs/git-no-verify-attempts.log
        fi
        ;;
        
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎯 测试保护是否生效："
echo "执行: git commit --no-verify -m 'test'"
echo "预期: 应该被拦截并显示错误信息"

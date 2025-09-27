#!/bin/bash
# Cursor AI保护系统设置脚本
# 专门对抗Cursor跳过本地测试直接推送的恶习

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
NC='\033[0m'

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

log_title() {
    echo -e "\n${PURPLE}🚀 $1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

show_banner() {
    echo "🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️"
    echo "🚨                 CURSOR AI 保护系统                   🚨"
    echo "🎯               强制本地测试，阻止盲目推送               🎯"
    echo "💡            基于30轮修复血泪教训，一劳永逸            💡"
    echo "🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️"
    echo ""
    echo "⚠️  问题：Cursor每次修改完就直接推送，跳过本地测试"
    echo "✅ 解决：强制通行证机制，必须本地测试通过才能推送"
    echo ""
}

# 设置git-guard拦截
setup_git_guard() {
    log_title "设置Git保护拦截"

    # 给脚本执行权限
    chmod +x scripts/git-guard.sh
    chmod +x scripts/one_click_test.sh
    chmod +x scripts/local_test_passport.py

    log_success "脚本权限已设置"

    # 创建git别名（推荐方式）
    log_info "设置Git别名保护..."

    # 方式1：项目级Git配置
    git config alias.safe-push '!bash scripts/git-guard.sh push'
    git config alias.safe-commit '!bash scripts/git-guard.sh commit'
    log_success "Git别名已设置（git safe-push, git safe-commit）"

    # 方式2：环境变量提示
    echo ""
    log_info "为了完全拦截所有git命令，请将以下别名添加到你的shell配置文件："
    echo ""
    echo "# 添加到 ~/.bashrc 或 ~/.zshrc"
    echo "alias git='bash \"$PROJECT_ROOT/scripts/git-guard.sh\"'"
    echo ""
    log_warning "注意：这将拦截所有git命令，包括Cursor的git操作"
}

# 创建便捷命令
create_convenience_commands() {
    log_title "创建便捷命令"

    # 创建test命令
    cat > test << 'EOF'
#!/bin/bash
# 便捷测试命令
bash scripts/one_click_test.sh "$@"
EOF
    chmod +x test
    log_success "创建了 ./test 命令"

    # 创建passport命令
    cat > passport << 'EOF'
#!/bin/bash
# 便捷通行证命令
python3 scripts/local_test_passport.py "$@"
EOF
    chmod +x passport
    log_success "创建了 ./passport 命令"

    # 创建safe-push命令
    cat > safe-push << 'EOF'
#!/bin/bash
# 安全推送命令
bash scripts/git-guard.sh push "$@"
EOF
    chmod +x safe-push
    log_success "创建了 ./safe-push 命令"

    echo ""
    log_info "现在你可以使用以下简化命令："
    echo "  ./test           # 运行本地测试并生成通行证"
    echo "  ./test --quick   # 快速测试"
    echo "  ./test --check   # 检查通行证状态"
    echo "  ./passport       # 管理通行证"
    echo "  ./safe-push      # 安全推送"
}

# 更新Makefile
update_makefile() {
    log_title "更新Makefile快捷命令"

    # 检查是否有Makefile
    if [ ! -f "Makefile" ]; then
        log_info "创建新的Makefile..."
        cat > Makefile << 'EOF'
# Bravo项目Makefile
# 包含Cursor AI保护系统相关命令

.PHONY: help test passport push setup-protection

help:
	@echo "🚀 Bravo项目快捷命令"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "📋 测试相关："
	@echo "  make test        - 运行本地测试并生成推送通行证"
	@echo "  make test-quick  - 快速测试（跳过完整功能测试）"
	@echo "  make test-check  - 检查通行证状态"
	@echo ""
	@echo "🎫 通行证管理："
	@echo "  make passport    - 检查通行证状态"
	@echo "  make passport-force - 强制重新生成通行证"
	@echo ""
	@echo "🚀 推送相关："
	@echo "  make safe-push   - 安全推送（会检查通行证）"
	@echo ""
	@echo "⚙️  系统设置："
	@echo "  make setup-protection - 设置Cursor保护系统"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test:
	@bash scripts/one_click_test.sh

test-quick:
	@bash scripts/one_click_test.sh --quick

test-check:
	@bash scripts/one_click_test.sh --check

passport:
	@python3 scripts/local_test_passport.py --check

passport-force:
	@python3 scripts/local_test_passport.py --force

safe-push:
	@bash scripts/git-guard.sh push origin $$(git branch --show-current)

setup-protection:
	@bash scripts/setup_cursor_protection.sh
EOF
    else
        log_info "更新现有Makefile..."
        # 备份原Makefile
        cp Makefile Makefile.backup

        # 添加新的目标到现有Makefile
        cat >> Makefile << 'EOF'

# ========== Cursor AI保护系统 ==========
.PHONY: test test-quick test-check passport passport-force safe-push setup-protection

test:
	@bash scripts/one_click_test.sh

test-quick:
	@bash scripts/one_click_test.sh --quick

test-check:
	@bash scripts/one_click_test.sh --check

passport:
	@python3 scripts/local_test_passport.py --check

passport-force:
	@python3 scripts/local_test_passport.py --force

safe-push:
	@bash scripts/git-guard.sh push origin $$(git branch --show-current)

setup-protection:
	@bash scripts/setup_cursor_protection.sh

cursor-help:
	@echo "🚀 Cursor AI保护系统命令"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  make test        - 运行本地测试并生成推送通行证"
	@echo "  make test-quick  - 快速测试"
	@echo "  make passport    - 检查通行证状态"
	@echo "  make safe-push   - 安全推送"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
EOF
    fi

    log_success "Makefile已更新"
}

# 创建Cursor工作区配置
create_cursor_config() {
    log_title "创建Cursor工作区配置"

    # 创建或更新.vscode/tasks.json（Cursor兼容）
    mkdir -p .vscode

    cat > .vscode/tasks.json << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "🧪 本地测试（生成推送通行证）",
            "type": "shell",
            "command": "bash",
            "args": ["scripts/one_click_test.sh"],
            "group": {
                "kind": "test",
                "isDefault": true
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "⚡ 快速测试",
            "type": "shell",
            "command": "bash",
            "args": ["scripts/one_click_test.sh", "--quick"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "🎫 检查通行证状态",
            "type": "shell",
            "command": "python3",
            "args": ["scripts/local_test_passport.py", "--check"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "🚀 安全推送",
            "type": "shell",
            "command": "bash",
            "args": ["scripts/git-guard.sh", "push", "origin", "${input:branchName}"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "problemMatcher": []
        }
    ],
    "inputs": [
        {
            "id": "branchName",
            "description": "分支名称",
            "default": "feature/force-local-test",
            "type": "promptString"
        }
    ]
}
EOF

    log_success "Cursor任务配置已创建"

    # 创建settings.json提示
    if [ ! -f ".vscode/settings.json" ]; then
        cat > .vscode/settings.json << 'EOF'
{
    "git.enableCommitSigning": false,
    "git.allowNoVerifyCommit": false,
    "git.useCommitInputAsStashMessage": true,
    "terminal.integrated.defaultProfile.windows": "Git Bash",
    "files.associations": {
        "*.sh": "shellscript"
    }
}
EOF
        log_success "Cursor设置已创建"
    else
        log_info "Cursor设置已存在，请手动添加以下配置："
        echo '  "git.allowNoVerifyCommit": false'
    fi
}

# 创建README
create_usage_guide() {
    log_title "创建使用指南"

    cat > CURSOR_PROTECTION_GUIDE.md << 'EOF'
# 🛡️ Cursor AI保护系统使用指南

## 🎯 目标

彻底解决Cursor AI跳过本地测试直接推送的问题，强制执行本地验证流程。

## 📋 核心原理

1. **拦截推送**：所有`git push`操作被拦截，检查本地测试通行证
2. **四层验证**：语法验证 → 环境验证 → 功能验证 → 差异验证
3. **通行证机制**：只有通过所有验证才能获得1小时有效期的推送通行证
4. **代码变更检测**：代码修改后通行证自动失效，需重新测试

## 🚀 快速开始

### 方式1：使用便捷命令

```bash
# 运行测试并生成通行证
./test

# 快速测试
./test --quick

# 检查通行证状态
./test --check

# 安全推送
./safe-push origin your-branch
```

### 方式2：使用Makefile命令

```bash
# 运行完整测试
make test

# 快速测试
make test-quick

# 检查通行证
make passport

# 安全推送
make safe-push
```

### 方式3：使用Cursor任务

1. 按 `Ctrl+Shift+P`
2. 输入 `Tasks: Run Task`
3. 选择：
   - `🧪 本地测试（生成推送通行证）`
   - `⚡ 快速测试`
   - `🎫 检查通行证状态`
   - `🚀 安全推送`

## 🔄 标准开发流程

```bash
# 1. 创建feature分支（如果还没有）
git checkout -b feature/your-feature

# 2. 进行代码修改
# ... 编码 ...

# 3. 运行本地测试获取通行证
make test
# 或者
./test

# 4. 等待验证完成，获取通行证

# 5. 提交代码
git add .
git commit -m "your commit message"

# 6. 安全推送（会自动验证通行证）
make safe-push
# 或者
git push origin feature/your-feature
```

## 🚨 被拦截了怎么办？

### 情况1：没有通行证

```
🎫🎫🎫 本地测试通行证验证失败！🎫🎫🎫
❌ 检测到推送操作，但未找到有效的本地测试通行证！
```

**解决**：运行 `make test` 或 `./test` 生成通行证

### 情况2：通行证过期

```
⚠️ 通行证已过期
```

**解决**：运行 `make test --force` 重新生成通行证

### 情况3：代码已修改

```
⚠️ 代码已修改，需要重新测试
```

**解决**：运行 `make test` 重新验证修改后的代码

### 情况4：紧急推送

如果确实需要紧急推送（极度不推荐）：

1. 环境变量绕过：
   ```bash
   export ALLOW_PUSH_WITHOUT_PASSPORT=true
   git push origin your-branch
   ```

2. 输入紧急确认码：`EMERGENCY_PUSH_BYPASS_2024`

## 🧪 测试模式说明

### 完整测试（默认）
- ✅ GitHub Actions语法验证
- ✅ Docker环境检查
- ✅ 完整功能测试（5-10分钟）
- ✅ 环境差异检查

### 快速测试（--quick）
- ✅ GitHub Actions语法验证
- ✅ Docker环境检查
- ✅ 基础功能检查（1-2分钟）
- ✅ 环境差异检查

### 单项测试
```bash
./test --act-only        # 仅语法验证
./test --docker-only     # 仅环境验证
./test --passport-only   # 仅生成通行证（要求其他测试已通过）
```

## 🛠️ 故障排除

### Python相关错误
```bash
# 确保Python3可用
python3 --version

# 如果Windows上没有python3命令
python --version  # 应该是3.x版本
```

### Docker相关错误
```bash
# 检查Docker状态
docker info

# 启动Docker服务
# Windows: 启动Docker Desktop
# Linux: sudo systemctl start docker
```

### Act相关错误
```bash
# 安装act（可选，用于GitHub Actions语法验证）
# Windows: choco install act-cli
# macOS: brew install act
# Linux: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

## 📁 文件说明

- `scripts/local_test_passport.py` - 通行证生成器
- `scripts/git-guard.sh` - Git命令拦截器
- `scripts/one_click_test.sh` - 一键测试脚本
- `scripts/setup_cursor_protection.sh` - 保护系统安装脚本
- `test` - 便捷测试命令
- `passport` - 便捷通行证命令
- `safe-push` - 便捷推送命令

## 💡 最佳实践

1. **每次修改代码后都要重新测试**
2. **优先使用快速测试进行迭代开发**
3. **完整测试用于最终验证**
4. **保持Docker服务运行以提高测试速度**
5. **定期清理Docker镜像和容器**

## 🔧 自定义配置

### 修改通行证有效期

编辑 `scripts/local_test_passport.py`，找到：
```python
expire_time = current_time + timedelta(hours=1)  # 修改这里
```

### 添加自定义验证

在 `scripts/one_click_test.sh` 中添加你的验证逻辑。

### 修改拦截规则

编辑 `scripts/git-guard.sh` 来自定义Git命令拦截规则。

---

🎉 现在你可以放心让Cursor工作，再也不用担心它跳过本地测试直接推送了！
EOF

    log_success "使用指南已创建：CURSOR_PROTECTION_GUIDE.md"
}

# 测试系统
test_protection_system() {
    log_title "测试保护系统"

    log_info "测试1：检查通行证状态..."
    if python3 scripts/local_test_passport.py --check; then
        log_warning "发现现有通行证"
    else
        log_success "无现有通行证（符合预期）"
    fi

    log_info "测试2：验证脚本权限..."
    if [ -x "scripts/git-guard.sh" ] && [ -x "scripts/one_click_test.sh" ]; then
        log_success "脚本权限正确"
    else
        log_error "脚本权限不正确"
        return 1
    fi

    log_info "测试3：验证便捷命令..."
    if [ -x "test" ] && [ -x "passport" ] && [ -x "safe-push" ]; then
        log_success "便捷命令已创建"
    else
        log_error "便捷命令创建失败"
        return 1
    fi

    log_success "系统测试完成"
}

# 显示最终使用说明
show_final_instructions() {
    log_title "🎉 安装完成！"

    echo "现在Cursor AI保护系统已经设置完成！"
    echo ""
    echo "🚀 快速开始："
    echo ""
    echo "1️⃣ 运行本地测试："
    echo "   make test"
    echo "   # 或者"
    echo "   ./test"
    echo ""
    echo "2️⃣ 获取通行证后推送："
    echo "   make safe-push"
    echo "   # 或者"
    echo "   git push origin your-branch  # 会自动检查通行证"
    echo ""
    echo "3️⃣ 在Cursor中使用任务："
    echo "   Ctrl+Shift+P → Tasks: Run Task → 选择测试任务"
    echo ""
    echo "📖 详细说明请查看：CURSOR_PROTECTION_GUIDE.md"
    echo ""
    echo "⚠️  重要提醒："
    echo "   • 每次代码修改后都需要重新运行测试"
    echo "   • 通行证有效期1小时"
    echo "   • 推送前会自动检查通行证状态"
    echo ""
    log_success "Cursor再也不能跳过本地测试了！🎉"
}

# 安装Git钩子以支持团队协作
install_git_hooks() {
    log_title "安装Git钩子以支持团队协作"

    # 确保脚本有执行权限
    chmod +x scripts/auto_deploy_on_pull.sh scripts/new_user_onboarding.sh

    # 安装post-merge钩子
    cat > .git/hooks/post-merge << 'EOF'
#!/bin/bash
# 自动检测保护系统更新并部署
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
if [[ -f "$PROJECT_ROOT/scripts/auto_deploy_on_pull.sh" ]]; then
    bash "$PROJECT_ROOT/scripts/auto_deploy_on_pull.sh"
fi
EOF

    chmod +x .git/hooks/post-merge
    log_success "Git post-merge钩子已安装"

    # 安装post-checkout钩子（检测新用户）
    cat > .git/hooks/post-checkout << 'EOF'
#!/bin/bash
# 检测新用户并引导安装
# 参数：$1=前一个HEAD $2=当前HEAD $3=1(分支切换) 0(文件切换)

PROJECT_ROOT="$(git rev-parse --show-toplevel)"

# 只在分支切换时运行新用户检查
if [[ "$3" = "1" ]] && [[ -f "$PROJECT_ROOT/scripts/new_user_onboarding.sh" ]]; then
    # 检查是否为新用户
    if bash "$PROJECT_ROOT/scripts/new_user_onboarding.sh" --check; then
        echo ""
        echo "🎉 欢迎！检测到这是您首次使用本项目的强制本地测试系统"
        echo "🚀 运行以下命令开始快速设置："
        echo "   bash scripts/new_user_onboarding.sh"
        echo ""
    fi
fi
EOF

    chmod +x .git/hooks/post-checkout
    log_success "Git post-checkout钩子已安装"

    log_success "团队协作Git钩子安装完成"
}

# 检测新用户并引导
check_new_user() {
    if [[ -f "scripts/new_user_onboarding.sh" ]]; then
        chmod +x scripts/new_user_onboarding.sh

        # 检查是否为新用户
        if bash scripts/new_user_onboarding.sh --check; then
            log_info "检测到新用户，启动入职引导..."
            if bash scripts/new_user_onboarding.sh; then
                log_success "新用户入职完成"
                return 0
            else
                log_warning "新用户入职过程中断"
                return 1
            fi
        fi
    fi
    return 0
}

# 跨Windows环境适配
adapt_for_windows() {
    log_title "Windows环境适配"

    # 检测Windows环境类型
    local windows_env=""
    if [[ -f "/proc/version" ]] && grep -q "Microsoft\|WSL" /proc/version; then
        windows_env="WSL"
    elif [[ "$OS" == "Windows_NT" ]]; then
        windows_env="Native Windows"
    elif command -v git.exe &> /dev/null; then
        windows_env="Git Bash"
    else
        windows_env="Unknown"
    fi

    log_info "检测到Windows环境: $windows_env"

    # 创建Windows特定的便捷命令
    if [[ "$windows_env" != "WSL" ]]; then
        # 创建.bat文件用于Windows直接执行
        cat > test.bat << 'EOF'
@echo off
bash scripts/one_click_test.sh %*
EOF

        cat > passport.bat << 'EOF'
@echo off
if exist python3.exe (
    python3 scripts/local_test_passport.py %*
) else (
    python scripts/local_test_passport.py %*
)
EOF

        log_success "Windows批处理文件已创建"
    fi

    # 创建PowerShell脚本
    cat > test.ps1 << 'EOF'
param([string]$Mode = "")
if ($Mode) {
    & bash "scripts/one_click_test.sh" "--$Mode"
} else {
    & bash "scripts/one_click_test.sh"
}
EOF

    cat > passport.ps1 << 'EOF'
param([string]$Action = "")
$pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $pythonCmd) { $pythonCmd = Get-Command python -ErrorAction SilentlyContinue }
if ($pythonCmd) {
    if ($Action) {
        & $pythonCmd.Source "scripts/local_test_passport.py" "--$Action"
    } else {
        & $pythonCmd.Source "scripts/local_test_passport.py" "--check"
    }
} else {
    Write-Error "Python not found. Please install Python 3.x"
}
EOF

    log_success "PowerShell脚本已创建"
}

# 主函数
main() {
    local mode="${1:-install}"

    # 处理命令行参数
    case "$mode" in
        --auto-update)
            log_info "执行自动更新模式..."
            adapt_for_windows
            install_git_hooks
            create_convenience_commands
            update_makefile
            create_cursor_config
            test_protection_system
            log_success "自动更新完成"
            return 0
            ;;
        --new-user)
            log_info "执行新用户安装模式..."
            show_banner
            check_new_user
            ;;
        --update)
            log_info "执行手动更新模式..."
            ;;
        --install-hooks)
            install_git_hooks
            return 0
            ;;
        --merge-config)
            log_info "合并配置文件..."
            create_cursor_config
            update_makefile
            return 0
            ;;
        *)
            # 默认完整安装流程
            ;;
    esac

    show_banner

    # 确保在正确的目录
    if [ ! -f "scripts/git-guard.sh" ]; then
        log_error "未找到git-guard.sh，请确保在项目根目录运行此脚本"
        exit 1
    fi

    log_info "开始设置Cursor AI保护系统..."
    echo ""

    # 执行安装步骤
    setup_git_guard
    create_convenience_commands
    update_makefile
    create_cursor_config
    create_usage_guide
    adapt_for_windows
    install_git_hooks
    test_protection_system
    show_final_instructions

    echo ""
    log_success "🛡️ Cursor AI保护系统设置完成！"
}

# 运行主函数
main "$@"

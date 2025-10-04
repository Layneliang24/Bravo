# 跨Windows协作部署方案

## 🎯 协作场景分析

### 典型团队协作场景

```
团队成员A (设计者)          团队成员B (新加入)          团队成员C (现有成员)
     │                          │                          │
     ▼                          ▼                          ▼
设计并部署系统              首次克隆项目                需要同步更新
     │                          │                          │
     ▼                          ▼                          ▼
推送到远程仓库              自动检测并部署              拉取最新变更
     │                          │                          │
     ▼                          ▼                          ▼
所有人同步获得              立即可用保护系统            自动更新保护系统
```

## 🚀 自动检测和部署机制

### 1. Git钩子自动部署

#### `scripts/auto_deploy_on_pull.sh` [自动创建]

```bash
#!/bin/bash
# Git post-merge 钩子：拉取代码后自动检测并部署保护系统

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# 检查是否是强制本地测试系统的更新
if git diff HEAD~1 HEAD --name-only | grep -E "(scripts/.*local.*test|scripts/.*git.*guard)" > /dev/null; then
    echo "🛡️ 检测到强制本地测试系统更新，正在自动部署..."

    # 运行自动部署脚本
    if [[ -f "scripts/setup_cursor_protection.sh" ]]; then
        bash scripts/setup_cursor_protection.sh --auto-update
        echo "✅ 保护系统已自动更新完成"
    fi
fi
```

#### 自动安装Git钩子

```bash
# 在setup_cursor_protection.sh中添加
install_git_hooks() {
    echo "📌 安装Git钩子以支持团队协作..."

    # 创建post-merge钩子
    cat > .git/hooks/post-merge << 'EOF'
#!/bin/bash
# 自动检测保护系统更新
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
if [[ -f "$PROJECT_ROOT/scripts/auto_deploy_on_pull.sh" ]]; then
    bash "$PROJECT_ROOT/scripts/auto_deploy_on_pull.sh"
fi
EOF

    chmod +x .git/hooks/post-merge
    echo "✅ Git钩子安装完成"
}
```

### 2. 环境检测和自适应

#### Windows环境自动检测

```bash
# scripts/detect_windows_environment.sh
detect_windows_environment() {
    local env_info=""

    # 检测Windows版本
    if [[ -f "/proc/version" ]] && grep -q "Microsoft\|WSL" /proc/version; then
        env_info="WSL"
        WINDOWS_ENV="WSL"
    elif [[ "$OS" == "Windows_NT" ]]; then
        env_info="Native Windows"
        WINDOWS_ENV="NATIVE"
    elif command -v git.exe &> /dev/null; then
        env_info="Git Bash"
        WINDOWS_ENV="GIT_BASH"
    else
        env_info="Unknown"
        WINDOWS_ENV="UNKNOWN"
    fi

    echo "🖥️ 检测到Windows环境: $env_info"

    # 根据环境调整配置
    case $WINDOWS_ENV in
        "WSL")
            setup_wsl_environment
            ;;
        "NATIVE"|"GIT_BASH")
            setup_native_windows_environment
            ;;
    esac
}
```

#### 路径和命令自适应

```bash
# 自适应路径处理
adapt_paths_for_windows() {
    # Windows路径转换
    if [[ "$WINDOWS_ENV" == "NATIVE" ]] || [[ "$WINDOWS_ENV" == "GIT_BASH" ]]; then
        # 转换路径格式
        PROJECT_ROOT=$(cygpath -m "$PROJECT_ROOT" 2>/dev/null || echo "$PROJECT_ROOT")
    fi

    # Python命令检测
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    elif command -v py &> /dev/null; then
        PYTHON_CMD="py -3"  # Windows Python Launcher
    else
        echo "❌ 未找到Python，请安装Python 3.x"
        exit 1
    fi

    # Docker命令检测
    if command -v docker.exe &> /dev/null; then
        DOCKER_CMD="docker.exe"
    elif command -v docker &> /dev/null; then
        DOCKER_CMD="docker"
    else
        echo "❌ 未找到Docker，请安装Docker Desktop"
        exit 1
    fi
}
```

## 🔄 团队同步策略

### 1. 配置文件版本控制

#### 版本控制的文件

```
✅ 纳入版本控制:
├── scripts/git-guard.sh
├── scripts/local_test_passport.py
├── scripts/one_click_test.sh
├── scripts/setup_cursor_protection.sh
├── .vscode/tasks.json
├── Makefile (保护系统部分)
└── docs/force_local_test/

❌ 排除版本控制:
├── .git/local_test_passport.json     # 个人通行证
├── logs/git-no-verify-attempts.log   # 个人日志
├── logs/local_test_passport.log      # 个人日志
└── test, passport, safe-push          # 便捷命令 (自动生成)
```

#### `.gitignore` 更新

```bash
# 在.gitignore中添加
# Force Local Test System - Personal Files
.git/local_test_passport.json
logs/git-no-verify-attempts.log
logs/local_test_passport.log

# Force Local Test System - Auto-generated Commands
/test
/passport
/safe-push
```

### 2. 配置同步机制

#### 智能配置合并

```bash
# scripts/sync_team_config.sh
sync_team_configuration() {
    echo "🔄 同步团队配置..."

    # 检查.vscode/tasks.json是否需要更新
    if [[ -f ".vscode/tasks.json" ]]; then
        # 备份现有配置
        cp .vscode/tasks.json .vscode/tasks.json.backup

        # 合并团队配置和个人配置
        merge_vscode_tasks_config
    fi

    # 检查Makefile是否需要更新保护系统部分
    if [[ -f "Makefile" ]]; then
        if ! grep -q "# Cursor AI保护系统" Makefile; then
            append_makefile_protection_targets
        fi
    fi
}

merge_vscode_tasks_config() {
    # 使用jq合并JSON配置（如果可用）
    if command -v jq &> /dev/null; then
        jq -s '.[0] * .[1]' .vscode/tasks.json.backup .vscode/tasks.template.json > .vscode/tasks.json
    else
        # 简单追加方式
        append_vscode_protection_tasks
    fi
}
```

## 🖥️ 不同Windows环境适配

### 1. WSL (Windows Subsystem for Linux) 环境

```bash
setup_wsl_environment() {
    echo "🐧 配置WSL环境..."

    # WSL特定配置
    export WINDOWS_ENV="WSL"

    # Docker Desktop集成检查
    if ! docker info &> /dev/null; then
        echo "⚠️ WSL中Docker不可用，检查Docker Desktop WSL集成设置"
        echo "   Settings → Resources → WSL Integration"
    fi

    # 路径处理
    PROJECT_ROOT_WINDOWS=$(wslpath -w "$PROJECT_ROOT")
    echo "🗂️ Windows路径: $PROJECT_ROOT_WINDOWS"

    # 创建Windows快捷方式
    create_windows_shortcuts_from_wsl
}

create_windows_shortcuts_from_wsl() {
    # 在Windows用户桌面创建快捷方式
    local windows_desktop="/mnt/c/Users/$USER/Desktop"
    if [[ -d "$windows_desktop" ]]; then
        cat > "$windows_desktop/Bravo-Local-Test.bat" << EOF
@echo off
wsl -d Ubuntu cd "$PROJECT_ROOT" && ./test
pause
EOF
        echo "✅ 已创建Windows桌面快捷方式"
    fi
}
```

### 2. Git Bash / MSYS2 环境

```bash
setup_git_bash_environment() {
    echo "🖥️ 配置Git Bash环境..."

    export WINDOWS_ENV="GIT_BASH"

    # 路径转换处理
    PROJECT_ROOT=$(cygpath -m "$PROJECT_ROOT" 2>/dev/null || echo "$PROJECT_ROOT")

    # Windows Python路径检测
    detect_windows_python_path

    # Docker Desktop连接
    if ! docker info &> /dev/null; then
        echo "⚠️ Docker不可用，请确保Docker Desktop正在运行"
    fi
}

detect_windows_python_path() {
    # 检测常见的Windows Python安装路径
    local python_paths=(
        "/c/Python3*/python.exe"
        "/c/Users/$USER/AppData/Local/Programs/Python/Python*/python.exe"
        "/c/Program Files/Python*/python.exe"
    )

    for path_pattern in "${python_paths[@]}"; do
        for python_path in $path_pattern; do
            if [[ -f "$python_path" ]]; then
                PYTHON_CMD="$python_path"
                echo "🐍 找到Python: $python_path"
                return 0
            fi
        done
    done
}
```

### 3. PowerShell 环境支持

#### PowerShell版本的便捷命令

```powershell
# test.ps1
param(
    [string]$Mode = ""
)

$scriptPath = Join-Path $PSScriptRoot "scripts\one_click_test.sh"
if ($Mode) {
    & bash $scriptPath "--$Mode"
} else {
    & bash $scriptPath
}
```

```powershell
# passport.ps1
param(
    [string]$Action = ""
)

$pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
}

if ($pythonCmd) {
    $scriptPath = Join-Path $PSScriptRoot "scripts\local_test_passport.py"
    if ($Action) {
        & $pythonCmd.Source $scriptPath "--$Action"
    } else {
        & $pythonCmd.Source $scriptPath "--check"
    }
} else {
    Write-Error "Python not found. Please install Python 3.x"
}
```

## 🤝 团队协作工作流

### 1. 首次部署流程

```bash
# 团队成员A (系统设计者)
git add .
git commit -m "feat: 添加强制本地测试系统"
git push origin feature/force-local-test

# 团队成员B (新加入)
git clone <repository>
cd <project>
# 自动检测并提示安装
if [[ -f "scripts/setup_cursor_protection.sh" ]]; then
    echo "🛡️ 检测到强制本地测试系统，是否自动安装？(Y/n)"
    read -r response
    if [[ "$response" != "n" && "$response" != "N" ]]; then
        bash scripts/setup_cursor_protection.sh
    fi
fi
```

### 2. 系统更新流程

```bash
# 当保护系统有更新时
git pull origin main

# 自动检测更新并提示
if [[ -f ".git/hooks/post-merge" ]]; then
    # post-merge钩子自动执行
    echo "🔄 保护系统已自动更新"
else
    # 手动检测更新
    if git diff HEAD~1 HEAD --name-only | grep -E "scripts/.*protection" > /dev/null; then
        echo "🛡️ 检测到保护系统更新，建议运行: bash scripts/setup_cursor_protection.sh --update"
    fi
fi
```

### 3. 配置冲突解决

```bash
# scripts/resolve_config_conflicts.sh
resolve_team_config_conflicts() {
    echo "🔧 解决配置冲突..."

    # 检查.vscode/tasks.json冲突
    if git status --porcelain | grep -q ".vscode/tasks.json"; then
        echo "⚠️ 检测到.vscode/tasks.json冲突"
        echo "选择解决方案:"
        echo "1. 保留团队标准配置"
        echo "2. 保留个人配置"
        echo "3. 手动合并"

        read -p "请选择 (1-3): " choice
        case $choice in
            1) git checkout --theirs .vscode/tasks.json ;;
            2) git checkout --ours .vscode/tasks.json ;;
            3) echo "请手动编辑 .vscode/tasks.json" ;;
        esac
    fi
}
```

## 📦 打包和分发机制

### 1. 便携版本创建

```bash
# scripts/create_portable_version.sh
create_portable_protection_system() {
    echo "📦 创建便携版保护系统..."

    local portable_dir="force_local_test_portable"
    mkdir -p "$portable_dir"

    # 复制核心文件
    cp scripts/git-guard.sh "$portable_dir/"
    cp scripts/local_test_passport.py "$portable_dir/"
    cp scripts/one_click_test.sh "$portable_dir/"
    cp scripts/setup_cursor_protection.sh "$portable_dir/"

    # 创建自动安装脚本
    cat > "$portable_dir/install.bat" << 'EOF'
@echo off
echo 正在安装强制本地测试系统...
bash setup_cursor_protection.sh --portable
pause
EOF

    # 创建说明文件
    cat > "$portable_dir/README.txt" << 'EOF'
强制本地测试系统 - 便携版

安装方法:
1. 双击 install.bat
2. 或在Git Bash中运行: bash setup_cursor_protection.sh --portable

使用方法:
1. 运行测试: bash one_click_test.sh
2. 检查通行证: python local_test_passport.py --check
3. 安全推送: bash git-guard.sh push origin branch-name
EOF

    echo "✅ 便携版创建完成: $portable_dir/"
}
```

### 2. 企业内网分发

```bash
# scripts/enterprise_deployment.sh
deploy_to_enterprise_network() {
    echo "🏢 企业内网部署..."

    # 创建网络共享安装包
    local enterprise_package="\\\\fileserver\\tools\\force_local_test"

    # 检查网络连接
    if [[ -d "$enterprise_package" ]]; then
        # 复制最新版本
        cp -r force_local_test_portable/* "$enterprise_package/"

        # 创建版本信息
        echo "$(date): $(git rev-parse HEAD)" > "$enterprise_package/VERSION"

        echo "✅ 已部署到企业网络: $enterprise_package"
    else
        echo "❌ 无法访问企业网络共享目录"
    fi
}
```

## 🔧 环境差异处理

### 1. 依赖工具自动安装

```bash
# scripts/install_dependencies_windows.sh
auto_install_windows_dependencies() {
    echo "🔧 检查和安装Windows依赖..."

    # 检查包管理器
    if command -v choco &> /dev/null; then
        PACKAGE_MANAGER="chocolatey"
    elif command -v winget &> /dev/null; then
        PACKAGE_MANAGER="winget"
    else
        PACKAGE_MANAGER="manual"
    fi

    # 检查并安装act
    if ! command -v act &> /dev/null; then
        echo "📥 安装act (GitHub Actions本地运行工具)..."
        case $PACKAGE_MANAGER in
            "chocolatey")
                choco install act-cli -y
                ;;
            "winget")
                winget install nektos.act
                ;;
            "manual")
                echo "⚠️ 请手动安装act: https://github.com/nektos/act"
                ;;
        esac
    fi

    # 检查Docker Desktop
    if ! command -v docker &> /dev/null; then
        echo "📥 请安装Docker Desktop: https://www.docker.com/products/docker-desktop"
        echo "⏸️ 安装完成后请重新运行此脚本"
        exit 1
    fi
}
```

### 2. 网络环境适配

```bash
# 中国大陆网络环境优化
optimize_for_china_network() {
    echo "🌐 检测网络环境并优化..."

    # 检测是否在中国大陆
    if curl -s --connect-timeout 3 google.com > /dev/null; then
        echo "🌍 检测到国际网络环境"
        NETWORK_ENV="international"
    else
        echo "🇨🇳 检测到中国大陆网络环境，启用镜像加速"
        NETWORK_ENV="china"

        # Docker镜像加速
        configure_docker_mirrors_china

        # npm镜像加速
        configure_npm_mirrors_china

        # pip镜像加速
        configure_pip_mirrors_china
    fi
}

configure_docker_mirrors_china() {
    echo "🐳 配置Docker镜像加速..."
    local docker_config="$HOME/.docker/daemon.json"

    if [[ ! -f "$docker_config" ]]; then
        mkdir -p "$(dirname "$docker_config")"
        cat > "$docker_config" << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF
        echo "✅ Docker镜像加速配置完成"
    fi
}
```

## 📊 团队使用统计

### 1. 使用情况统计

```bash
# scripts/team_usage_stats.sh
collect_team_usage_statistics() {
    echo "📊 收集团队使用统计..."

    local stats_file=".force_local_test_stats.json"
    local user_id="$(whoami)@$(hostname)"
    local timestamp="$(date -Iseconds)"

    # 创建或更新统计文件
    if [[ ! -f "$stats_file" ]]; then
        echo '{"users": {}, "total_runs": 0}' > "$stats_file"
    fi

    # 更新统计数据
    python3 -c "
import json
import sys

with open('$stats_file', 'r') as f:
    stats = json.load(f)

user_id = '$user_id'
if user_id not in stats['users']:
    stats['users'][user_id] = {'runs': 0, 'last_run': None}

stats['users'][user_id]['runs'] += 1
stats['users'][user_id]['last_run'] = '$timestamp'
stats['total_runs'] += 1

with open('$stats_file', 'w') as f:
    json.dump(stats, f, indent=2)
"
}

generate_team_usage_report() {
    echo "📈 生成团队使用报告..."

    if [[ -f ".force_local_test_stats.json" ]]; then
        python3 -c "
import json
from datetime import datetime

with open('.force_local_test_stats.json', 'r') as f:
    stats = json.load(f)

print('🛡️ 强制本地测试系统使用报告')
print('=' * 40)
print(f'总运行次数: {stats[\"total_runs\"]}')
print(f'活跃用户数: {len(stats[\"users\"])}')
print()
print('用户使用情况:')
for user, data in stats['users'].items():
    last_run = datetime.fromisoformat(data['last_run'].replace('Z', '+00:00'))
    print(f'  {user}: {data[\"runs\"]}次 (最后使用: {last_run.strftime(\"%Y-%m-%d %H:%M\")})')
"
    fi
}
```

---

**跨Windows协作核心策略**:

- **自动检测**: 智能识别环境并自适应配置
- **无缝同步**: Git钩子自动更新，最小化手动操作
- **环境兼容**: 支持WSL、Git Bash、PowerShell等多种环境
- **团队统一**: 标准化配置，个性化设置分离
- **渐进部署**: 可选安装，不强制全员立即使用

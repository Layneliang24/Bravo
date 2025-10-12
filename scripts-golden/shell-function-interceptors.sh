#!/bin/bash
# Shell函数拦截器 - 比alias优先级更高的拦截机制
# 在.bashrc中source这个文件来启用Shell函数拦截

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 🔐 Shell函数拦截机制（优先级高于alias）
# Shell函数 > Alias > PATH中的命令

# NPM拦截函数
npm() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" npm "$@"
}

# Python拦截函数
python() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" python "$@"
}

python3() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" python3 "$@"
}

# PIP拦截函数
pip() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" pip "$@"
}

pip3() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" pip3 "$@"
}

# Node.js包管理器拦截函数
yarn() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" yarn "$@"
}

pnpm() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" pnpm "$@"
}

# 其他开发工具拦截函数
go() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" go "$@"
}

cargo() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" cargo "$@"
}

gem() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" gem "$@"
}

mvn() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" mvn "$@"
}

gradle() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" gradle "$@"
}

conda() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" conda "$@"
}

mamba() {
    bash "$PROJECT_ROOT/scripts/dependency-guard.sh" mamba "$@"
}

# Source命令拦截（防止激活虚拟环境）
source() {
    # 检查是否是虚拟环境激活尝试
    if [[ "$1" =~ (venv|virtualenv|\.venv|env/bin/activate|\.env) ]]; then
        bash "$PROJECT_ROOT/scripts/dependency-guard.sh" source "$@"
    else
        # 对于其他source操作，使用内置source
        builtin source "$@"
    fi
}

# 导出函数使其在子shell中也生效
export -f npm python python3 pip pip3 yarn pnpm go cargo gem mvn gradle conda mamba source

echo "🛡️  Shell函数拦截器已加载 - 多层防护激活"

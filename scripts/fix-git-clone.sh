#!/bin/bash
# Git克隆问题修复脚本
# 解决GitHub访问TLS连接错误

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 方法1: 配置Git超时和重试
configure_git_timeout() {
    log_info "配置Git超时和重试设置..."

    git config --global http.postBuffer 524288000
    git config --global http.lowSpeedLimit 0
    git config --global http.lowSpeedTime 999999
    git config --global http.version HTTP/1.1

    log_success "Git超时配置完成"
}

# 方法2: 使用SSH方式克隆（推荐）
clone_with_ssh() {
    log_info "尝试使用SSH方式克隆..."

    REPO_URL="git@github.com:Layneliang24/Bravo.git"

    # 检查SSH密钥
    if [ ! -f ~/.ssh/id_rsa ] && [ ! -f ~/.ssh/id_ed25519 ]; then
        log_warning "未找到SSH密钥，需要先配置SSH密钥"
        log_info "生成SSH密钥："
        echo "  ssh-keygen -t ed25519 -C 'your_email@example.com'"
        echo "  然后将公钥添加到GitHub: https://github.com/settings/keys"
        return 1
    fi

    log_info "使用SSH克隆: $REPO_URL"
    git clone "$REPO_URL" bravo

    if [ $? -eq 0 ]; then
        log_success "SSH克隆成功！"
        return 0
    else
        log_error "SSH克隆失败"
        return 1
    fi
}

# 方法3: 使用HTTPS但增加重试
clone_with_retry() {
    log_info "使用HTTPS方式，增加重试次数..."

    REPO_URL="https://github.com/Layneliang24/Bravo.git"

    # 尝试多次
    for i in {1..5}; do
        log_info "尝试第 $i 次克隆..."
        if git clone "$REPO_URL" bravo; then
            log_success "克隆成功！"
            return 0
        else
            log_warning "第 $i 次尝试失败，等待5秒后重试..."
            sleep 5
        fi
    done

    log_error "多次尝试后仍然失败"
    return 1
}

# 方法4: 使用GitHub镜像（ghproxy）
clone_with_mirror() {
    log_info "使用GitHub镜像（ghproxy）..."

    REPO_URL="https://ghproxy.com/https://github.com/Layneliang24/Bravo.git"

    log_info "使用镜像克隆: $REPO_URL"
    if git clone "$REPO_URL" bravo; then
        log_success "镜像克隆成功！"

        # 修改远程地址为原始地址
        cd bravo
        git remote set-url origin https://github.com/Layneliang24/Bravo.git
        cd ..

        log_success "已修改远程地址为原始GitHub地址"
        return 0
    else
        log_error "镜像克隆失败"
        return 1
    fi
}

# 方法5: 使用Gitee镜像（如果有）
clone_with_gitee() {
    log_info "检查Gitee镜像..."

    # 检查Gitee是否有镜像
    GITEE_URL="https://gitee.com/Layneliang24/Bravo.git"

    log_info "尝试从Gitee克隆: $GITEE_URL"
    if git clone "$GITEE_URL" bravo 2>/dev/null; then
        log_success "Gitee克隆成功！"

        # 修改远程地址为GitHub
        cd bravo
        git remote set-url origin https://github.com/Layneliang24/Bravo.git
        cd ..

        log_success "已修改远程地址为GitHub"
        return 0
    else
        log_warning "Gitee镜像不存在或无法访问"
        return 1
    fi
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "  Git克隆问题修复工具"
    echo "=========================================="
    echo ""

    # 检查当前目录
    if [ -d "bravo" ]; then
        log_warning "bravo目录已存在"
        read -p "是否删除并重新克隆？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf bravo
        else
            log_info "退出"
            exit 0
        fi
    fi

    # 配置Git超时
    configure_git_timeout

    # 尝试不同的克隆方法
    log_info "开始尝试不同的克隆方法..."
    echo ""

    # 方法1: SSH方式（最推荐）
    log_info "方法1: 尝试SSH方式克隆..."
    if clone_with_ssh; then
        exit 0
    fi
    echo ""

    # 方法2: 使用镜像
    log_info "方法2: 尝试使用GitHub镜像..."
    if clone_with_mirror; then
        exit 0
    fi
    echo ""

    # 方法3: 使用Gitee
    log_info "方法3: 尝试使用Gitee镜像..."
    if clone_with_gitee; then
        exit 0
    fi
    echo ""

    # 方法4: HTTPS重试
    log_info "方法4: 使用HTTPS重试..."
    if clone_with_retry; then
        exit 0
    fi
    echo ""

    # 所有方法都失败
    log_error "所有克隆方法都失败了"
    echo ""
    log_info "建议："
    echo "  1. 配置SSH密钥（最稳定）"
    echo "  2. 使用代理服务器"
    echo "  3. 在本地克隆后上传到服务器"
    echo ""
    log_info "配置SSH密钥步骤："
    echo "  1. ssh-keygen -t ed25519 -C 'your_email@example.com'"
    echo "  2. cat ~/.ssh/id_ed25519.pub"
    echo "  3. 复制公钥到GitHub: https://github.com/settings/keys"
    echo "  4. 然后使用: git clone git@github.com:Layneliang24/Bravo.git bravo"
    exit 1
}

main

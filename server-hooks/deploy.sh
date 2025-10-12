#!/bin/bash
# 🚀 服务器端钩子部署脚本
# 用途：自动化部署 pre-receive 钩子到 Git 服务器

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${BLUE}  🛡️ 服务器端钩子部署工具${NC}"
echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# 检查参数
if [ $# -lt 2 ]; then
    echo -e "${RED}错误: 缺少必需参数${NC}\n"
    echo "用法:"
    echo "  $0 <服务器类型> <仓库路径> [SSH主机]"
    echo ""
    echo "服务器类型:"
    echo "  gitea    - Gitea/Gogs 服务器"
    echo "  gitlab   - GitLab 服务器"
    echo "  bare     - 裸仓库"
    echo ""
    echo "示例:"
    echo "  # 部署到 Gitea (本地)"
    echo "  $0 gitea /data/gitea/repositories/org/repo.git"
    echo ""
    echo "  # 部署到 GitLab (远程)"
    echo "  $0 gitlab /var/opt/gitlab/git-data/repositories/namespace/project.git user@gitlab-server.com"
    echo ""
    echo "  # 部署到裸仓库 (远程)"
    echo "  $0 bare /opt/git/repos/project.git user@git-server.com"
    exit 1
fi

SERVER_TYPE=$1
REPO_PATH=$2
SSH_HOST=${3:-""}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_FILE="$SCRIPT_DIR/pre-receive"

# 检查钩子文件是否存在
if [ ! -f "$HOOK_FILE" ]; then
    echo -e "${RED}错误: 找不到钩子文件: $HOOK_FILE${NC}"
    exit 1
fi

echo -e "${BLUE}[INFO]${NC} 部署配置:"
echo -e "  服务器类型: ${BOLD}$SERVER_TYPE${NC}"
echo -e "  仓库路径: ${BOLD}$REPO_PATH${NC}"
if [ -n "$SSH_HOST" ]; then
    echo -e "  SSH 主机: ${BOLD}$SSH_HOST${NC}"
else
    echo -e "  部署方式: ${BOLD}本地${NC}"
fi
echo ""

# 确认部署
read -p "确认部署? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}部署已取消${NC}"
    exit 0
fi

# 根据服务器类型确定钩子路径
case "$SERVER_TYPE" in
    gitea|bare)
        HOOK_PATH="$REPO_PATH/hooks/pre-receive"
        ;;
    gitlab)
        HOOK_PATH="$REPO_PATH/custom_hooks/pre-receive"
        ;;
    *)
        echo -e "${RED}错误: 不支持的服务器类型: $SERVER_TYPE${NC}"
        echo "支持的类型: gitea, gitlab, bare"
        exit 1
        ;;
esac

# 部署函数
deploy_local() {
    echo -e "${BLUE}[INFO]${NC} 部署到本地: $HOOK_PATH"

    # 检查仓库路径是否存在
    if [ ! -d "$REPO_PATH" ]; then
        echo -e "${RED}错误: 仓库路径不存在: $REPO_PATH${NC}"
        exit 1
    fi

    # 创建钩子目录（如果需要）
    if [ "$SERVER_TYPE" = "gitlab" ]; then
        mkdir -p "$(dirname "$HOOK_PATH")"
    fi

    # 备份现有钩子
    if [ -f "$HOOK_PATH" ]; then
        BACKUP_PATH="${HOOK_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}[WARN]${NC} 发现现有钩子，备份到: $BACKUP_PATH"
        cp "$HOOK_PATH" "$BACKUP_PATH"
    fi

    # 复制钩子
    cp "$HOOK_FILE" "$HOOK_PATH"
    chmod +x "$HOOK_PATH"

    echo -e "${GREEN}[SUCCESS]${NC} 钩子部署成功！"
}

deploy_remote() {
    echo -e "${BLUE}[INFO]${NC} 部署到远程: $SSH_HOST:$HOOK_PATH"

    # 检查 SSH 连接
    if ! ssh "$SSH_HOST" "exit" 2>/dev/null; then
        echo -e "${RED}错误: 无法连接到 SSH 主机: $SSH_HOST${NC}"
        exit 1
    fi

    # 检查远程仓库路径
    if ! ssh "$SSH_HOST" "test -d '$REPO_PATH'"; then
        echo -e "${RED}错误: 远程仓库路径不存在: $REPO_PATH${NC}"
        exit 1
    fi

    # 创建钩子目录（如果需要）
    if [ "$SERVER_TYPE" = "gitlab" ]; then
        ssh "$SSH_HOST" "mkdir -p '$(dirname "$HOOK_PATH")'"
    fi

    # 备份现有钩子
    if ssh "$SSH_HOST" "test -f '$HOOK_PATH'"; then
        BACKUP_PATH="${HOOK_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}[WARN]${NC} 发现现有钩子，备份到: $BACKUP_PATH"
        ssh "$SSH_HOST" "cp '$HOOK_PATH' '$BACKUP_PATH'"
    fi

    # 上传钩子
    scp "$HOOK_FILE" "$SSH_HOST:$HOOK_PATH"
    ssh "$SSH_HOST" "chmod +x '$HOOK_PATH'"

    echo -e "${GREEN}[SUCCESS]${NC} 钩子部署成功！"
}

# 执行部署
if [ -z "$SSH_HOST" ]; then
    deploy_local
else
    deploy_remote
fi

# 测试建议
echo ""
echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${BLUE}  🧪 部署后测试${NC}"
echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
echo "建议执行以下测试:"
echo ""
echo "1. 测试推送到 feature 分支 (应该成功):"
echo "   git push origin feature/test-hook"
echo ""
echo "2. 测试推送到 main 分支 (应该被拒绝):"
echo "   git push origin main"
echo ""
echo "3. 测试推送大文件 (应该被拒绝):"
echo "   dd if=/dev/zero of=large.bin bs=1M count=11"
echo "   git add large.bin && git commit -m 'test large file'"
echo "   git push origin feature/test"
echo ""
echo -e "${GREEN}部署完成！${NC}"

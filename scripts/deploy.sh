#!/bin/bash
# 生产环境部署脚本

set -e  # 遇到错误立即退出

# 配置变量
SERVER_IP="8.129.16.190"
SERVER_USER="${DEPLOY_USER:-root}"
SERVER_PORT="${DEPLOY_PORT:-22}"
PROJECT_PATH="${DEPLOY_PATH:-/opt/bravo}"
REPO_URL="https://github.com/Layneliang24/Bravo.git"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# 检查必需的工具
check_requirements() {
    log "检查部署工具..."

    if ! command -v ssh &> /dev/null; then
        error "SSH not found. Please install OpenSSH client."
    fi

    if ! command -v rsync &> /dev/null; then
        warn "rsync not found. Will use scp instead (slower)."
        USE_RSYNC=false
    else
        USE_RSYNC=true
    fi

    log "工具检查完成"
}

# 测试服务器连接
test_connection() {
    log "测试服务器连接..."

    if ! ssh -o ConnectTimeout=10 -p $SERVER_PORT $SERVER_USER@$SERVER_IP "echo 'Connection successful'" &> /dev/null; then
        error "无法连接到服务器 $SERVER_USER@$SERVER_IP:$SERVER_PORT"
    fi

    log "服务器连接正常"
}

# 在服务器上安装Docker
install_docker() {
    log "检查Docker安装状态..."

    if ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP "docker --version" &> /dev/null; then
        log "Docker已安装"
        return
    fi

    log "安装Docker..."
    ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP << 'EOF'
        # 更新系统
        apt-get update
        apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

        # 添加Docker官方GPG key
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

        # 设置Docker仓库
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

        # 安装Docker
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io

        # 安装Docker Compose
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose

        # 启动Docker服务
        systemctl start docker
        systemctl enable docker

        # 创建项目目录
        mkdir -p /opt/bravo

        echo "Docker安装完成"
EOF

    log "Docker安装完成"
}

# 部署代码
deploy_code() {
    log "部署代码到服务器..."

    # 创建临时目录
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT

    # 克隆代码
    log "克隆代码..."
    git clone --depth 1 -b main $REPO_URL $TEMP_DIR

    # 复制生产环境配置
    cp .env.production $TEMP_DIR/.env

    # 上传代码到服务器
    log "上传代码到服务器..."
    if [ "$USE_RSYNC" = true ]; then
        rsync -avz --delete --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
            -e "ssh -p $SERVER_PORT" $TEMP_DIR/ $SERVER_USER@$SERVER_IP:$PROJECT_PATH/
    else
        ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP "rm -rf $PROJECT_PATH && mkdir -p $PROJECT_PATH"
        scp -P $SERVER_PORT -r $TEMP_DIR/* $SERVER_USER@$SERVER_IP:$PROJECT_PATH/
    fi

    log "代码上传完成"
}

# 构建和启动服务
start_services() {
    log "构建和启动服务..."

    ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP << EOF
        cd $PROJECT_PATH

        # 停止现有服务
        docker-compose -f docker-compose.production.yml down || true

        # 清理旧的镜像
        docker system prune -f || true

        # 构建镜像
        docker-compose -f docker-compose.production.yml build --no-cache

        # 启动服务
        docker-compose -f docker-compose.production.yml up -d

        # 等待数据库启动
        sleep 30

        # 运行数据库迁移
        docker-compose -f docker-compose.production.yml exec -T backend python manage.py migrate

        # 收集静态文件
        docker-compose -f docker-compose.production.yml exec -T backend python manage.py collectstatic --noinput

        # 创建超级用户（如果不存在）
        docker-compose -f docker-compose.production.yml exec -T backend python manage.py shell << 'PYTHON'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print('Admin user created: admin / admin123456')
else:
    print('Admin user already exists')
PYTHON

        echo "服务启动完成"
EOF

    log "服务启动完成"
}

# 健康检查
health_check() {
    log "执行健康检查..."

    # 等待服务启动
    sleep 60

    # 检查后端
    if curl -f http://$SERVER_IP:8000/health/ &> /dev/null; then
        log "后端服务健康检查通过"
    else
        warn "后端服务健康检查失败"
    fi

    # 检查前端
    if curl -f http://$SERVER_IP/health &> /dev/null; then
        log "前端服务健康检查通过"
    else
        warn "前端服务健康检查失败"
    fi

    log "健康检查完成"
}

# 显示部署信息
show_info() {
    log "部署完成！"
    echo ""
    echo -e "${BLUE}🚀 部署信息${NC}"
    echo "================================"
    echo -e "前端地址: ${GREEN}http://$SERVER_IP${NC}"
    echo -e "后端API: ${GREEN}http://$SERVER_IP:8000/api${NC}"
    echo -e "管理后台: ${GREEN}http://$SERVER_IP:8000/admin${NC}"
    echo -e "默认管理员: ${YELLOW}admin / admin123456${NC}"
    echo ""
    echo -e "${YELLOW}请立即修改默认密码！${NC}"
    echo ""
    echo "服务管理命令："
    echo "  查看状态: ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP 'cd $PROJECT_PATH && docker-compose -f docker-compose.production.yml ps'"
    echo "  查看日志: ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP 'cd $PROJECT_PATH && docker-compose -f docker-compose.production.yml logs'"
    echo "  重启服务: ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP 'cd $PROJECT_PATH && docker-compose -f docker-compose.production.yml restart'"
    echo ""
}

# 主函数
main() {
    log "开始Bravo生产环境部署"
    echo "================================"
    echo "服务器: $SERVER_USER@$SERVER_IP:$SERVER_PORT"
    echo "项目路径: $PROJECT_PATH"
    echo "================================"
    echo ""

    # 确认部署
    read -p "确认开始部署? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "部署已取消"
        exit 0
    fi

    check_requirements
    test_connection
    install_docker
    deploy_code
    start_services
    health_check
    show_info

    log "部署流程完成！🎉"
}

# 运行主函数
main "$@"

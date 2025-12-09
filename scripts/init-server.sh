#!/bin/bash
# Bravo项目服务器初始化脚本
# 适用于 Ubuntu 22.04 LTS
# 使用方式: bash scripts/init-server.sh

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_PATH="/home/layne/project/bravo"
PROJECT_USER="layne"

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

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root权限运行此脚本"
        log_info "使用: sudo bash scripts/init-server.sh"
        exit 1
    fi
    log_success "权限检查通过"
}

# 检查系统版本
check_system() {
    log_info "检查系统版本..."

    if [ ! -f /etc/os-release ]; then
        log_error "无法检测系统版本"
        exit 1
    fi

    . /etc/os-release

    if [ "$ID" != "ubuntu" ] || [ "$VERSION_ID" != "22.04" ]; then
        log_warning "检测到系统: $ID $VERSION_ID"
        log_warning "此脚本针对 Ubuntu 22.04 优化，其他版本可能不兼容"
        read -p "是否继续？(y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_success "系统版本: Ubuntu 22.04 LTS"
    fi
}

# 更新系统
update_system() {
    log_info "更新系统包列表..."
    apt-get update -qq

    log_info "升级系统包..."
    apt-get upgrade -y -qq

    log_success "系统更新完成"
}

# 安装基础工具
install_basic_tools() {
    log_info "安装基础工具..."

    apt-get install -y -qq \
        curl \
        wget \
        git \
        vim \
        htop \
        net-tools \
        ufw \
        ca-certificates \
        gnupg \
        lsb-release \
        apt-transport-https

    log_success "基础工具安装完成"

    # 配置Git以解决GitHub访问问题
    log_info "配置Git以优化GitHub访问..."
    git config --global http.postBuffer 524288000
    git config --global http.lowSpeedLimit 0
    git config --global http.lowSpeedTime 999999
    git config --global http.version HTTP/1.1
    log_success "Git配置完成"
}

# 安装Docker
install_docker() {
    log_info "检查Docker安装状态..."

    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        log_warning "Docker已安装: $DOCKER_VERSION"
        read -p "是否重新安装Docker？(y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi

    log_info "安装Docker..."

    # 卸载旧版本（如果存在）
    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

    # 添加Docker官方GPG密钥
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    # 设置Docker仓库
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

    # 安装Docker Engine
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # 启动Docker服务
    systemctl start docker
    systemctl enable docker

    # 验证Docker安装
    if docker --version &> /dev/null; then
        log_success "Docker安装成功: $(docker --version)"
    else
        log_error "Docker安装失败"
        exit 1
    fi
}

# 配置Docker镜像加速（国内服务器）
configure_docker_mirror() {
    log_info "配置Docker镜像加速..."

    mkdir -p /etc/docker

    # 检查是否已配置
    if [ -f /etc/docker/daemon.json ]; then
        log_warning "daemon.json已存在，备份为daemon.json.backup"
        cp /etc/docker/daemon.json /etc/docker/daemon.json.backup
    fi

    # 配置镜像加速器（阿里云、中科大、网易）
    cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://registry.docker-cn.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
EOF

    # 重启Docker服务
    systemctl daemon-reload
    systemctl restart docker

    log_success "Docker镜像加速配置完成"
}

# 配置时区
configure_timezone() {
    log_info "配置时区为Asia/Shanghai..."

    timedatectl set-timezone Asia/Shanghai

    # 验证时区
    CURRENT_TZ=$(timedatectl | grep "Time zone" | awk '{print $3}')
    if [ "$CURRENT_TZ" = "Asia/Shanghai" ]; then
        log_success "时区配置成功: $CURRENT_TZ"
    else
        log_warning "时区配置可能失败，当前时区: $CURRENT_TZ"
    fi
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙规则..."

    # 启用UFW（如果未启用）
    if ! ufw status | grep -q "Status: active"; then
        log_info "启用UFW防火墙..."
        ufw --force enable
    fi

    # 允许SSH（防止锁定）
    ufw allow 22/tcp comment 'SSH'

    # 允许项目所需端口
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    ufw allow 8000/tcp comment 'Django Backend'

    # 可选：允许MySQL和Redis外部访问（生产环境建议关闭）
    read -p "是否允许MySQL(3306)和Redis(6379)外部访问？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ufw allow 3306/tcp comment 'MySQL'
        ufw allow 6379/tcp comment 'Redis'
        log_warning "已开放MySQL和Redis端口，请确保配置了强密码！"
    fi

    # 显示防火墙状态
    log_info "防火墙规则："
    ufw status numbered

    log_success "防火墙配置完成"
}

# 创建项目用户和目录
setup_project_directory() {
    log_info "创建项目目录结构..."

    # 创建用户（如果不存在）
    if ! id "$PROJECT_USER" &>/dev/null; then
        log_info "创建用户: $PROJECT_USER"
        useradd -m -s /bin/bash "$PROJECT_USER" || true
    fi

    # 创建项目目录
    mkdir -p "$PROJECT_PATH"

    # 设置目录权限
    chown -R "$PROJECT_USER:$PROJECT_USER" "$(dirname $PROJECT_PATH)"

    # 将用户添加到docker组（无需sudo使用docker）
    usermod -aG docker "$PROJECT_USER" || true

    log_success "项目目录创建完成: $PROJECT_PATH"
}

# 安装Docker Compose（如果使用独立版本）
install_docker_compose_standalone() {
    log_info "检查Docker Compose..."

    # Docker Compose Plugin已包含在docker-compose-plugin中
    if docker compose version &> /dev/null; then
        log_success "Docker Compose已安装: $(docker compose version)"
        return
    fi

    log_warning "Docker Compose未找到，尝试安装独立版本..."

    # 安装独立版本（作为备用）
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    if docker-compose --version &> /dev/null; then
        log_success "Docker Compose独立版本安装成功"
    else
        log_error "Docker Compose安装失败"
        exit 1
    fi
}

# 优化系统配置
optimize_system() {
    log_info "优化系统配置..."

    # 增加文件描述符限制
    cat >> /etc/security/limits.conf << 'EOF'

# Docker优化配置
* soft nofile 65535
* hard nofile 65535
EOF

    # 优化内核参数（Docker相关）
    cat >> /etc/sysctl.conf << 'EOF'

# Docker网络优化
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

    sysctl -p > /dev/null 2>&1 || true

    log_success "系统优化配置完成"
}

# 验证安装
verify_installation() {
    log_info "验证安装..."

    echo ""
    echo "=========================================="
    echo "安装验证报告"
    echo "=========================================="

    # 检查Docker
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✅ Docker: $(docker --version)${NC}"
    else
        echo -e "${RED}❌ Docker未安装${NC}"
    fi

    # 检查Docker Compose
    if docker compose version &> /dev/null; then
        echo -e "${GREEN}✅ Docker Compose: $(docker compose version)${NC}"
    elif command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}✅ Docker Compose: $(docker-compose --version)${NC}"
    else
        echo -e "${RED}❌ Docker Compose未安装${NC}"
    fi

    # 检查Git
    if command -v git &> /dev/null; then
        echo -e "${GREEN}✅ Git: $(git --version)${NC}"
    else
        echo -e "${RED}❌ Git未安装${NC}"
    fi

    # 检查时区
    CURRENT_TZ=$(timedatectl | grep "Time zone" | awk '{print $3}')
    if [ "$CURRENT_TZ" = "Asia/Shanghai" ]; then
        echo -e "${GREEN}✅ 时区: $CURRENT_TZ${NC}"
    else
        echo -e "${YELLOW}⚠️  时区: $CURRENT_TZ (应为Asia/Shanghai)${NC}"
    fi

    # 检查项目目录
    if [ -d "$PROJECT_PATH" ]; then
        echo -e "${GREEN}✅ 项目目录: $PROJECT_PATH${NC}"
    else
        echo -e "${RED}❌ 项目目录不存在: $PROJECT_PATH${NC}"
    fi

    # 检查Docker服务状态
    if systemctl is-active --quiet docker; then
        echo -e "${GREEN}✅ Docker服务: 运行中${NC}"
    else
        echo -e "${RED}❌ Docker服务: 未运行${NC}"
    fi

    # 测试Docker
    if docker run --rm hello-world &> /dev/null; then
        echo -e "${GREEN}✅ Docker测试: 成功${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker测试: 失败（可能需要重启）${NC}"
    fi

    echo "=========================================="
    echo ""
}

# 显示后续步骤
show_next_steps() {
    log_info "后续步骤："
    echo ""
    echo "1. 切换到项目用户："
    echo "   ${BLUE}su - $PROJECT_USER${NC}"
    echo ""
    echo "2. 进入项目目录："
    echo "   ${BLUE}cd $PROJECT_PATH${NC}"
    echo ""
    echo "3. 克隆项目代码（如果尚未克隆）："
    echo "   ${BLUE}git clone <your-repo-url> .${NC}"
    echo ""
    echo "4. 配置环境变量："
    echo "   ${BLUE}cp docker/env/env.production.example .env.production${NC}"
    echo "   ${BLUE}nano .env.production${NC}"
    echo ""
    echo "5. 启动服务："
    echo "   ${BLUE}docker compose -f docker-compose.prod.yml up -d${NC}"
    echo ""
    echo "6. 查看服务状态："
    echo "   ${BLUE}docker compose -f docker-compose.prod.yml ps${NC}"
    echo ""
    echo "7. 查看日志："
    echo "   ${BLUE}docker compose -f docker-compose.prod.yml logs -f${NC}"
    echo ""
    log_success "服务器初始化完成！"
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "  Bravo项目服务器初始化脚本"
    echo "  Ubuntu 22.04 LTS"
    echo "=========================================="
    echo ""

    check_root
    check_system
    update_system
    install_basic_tools
    install_docker
    configure_docker_mirror
    install_docker_compose_standalone
    configure_timezone
    configure_firewall
    setup_project_directory
    optimize_system
    verify_installation
    show_next_steps
}

# 执行主函数
main

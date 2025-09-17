#!/bin/bash
# 测试GitHub Actions国内源配置是否正确
# 模拟CI环境中的配置过程

set -e

echo "🧪 测试GitHub Actions国内源配置"
echo "========================================"

# 模拟GitHub Actions环境变量
export CI=true
export GITHUB_ACTIONS=true

echo "🔧 1. 测试npm国内源配置..."
if command -v npm &> /dev/null; then
    # 备份原始配置
    ORIGINAL_REGISTRY=$(npm config get registry)

    # 配置国内源
    npm config set registry https://registry.npmmirror.com

    # 设置各种工具镜像环境变量（替代废弃的npm config选项）
    export NODEJS_ORG_MIRROR=https://npmmirror.com/mirrors/node
    export ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
    export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
    export SASS_BINARY_SITE=https://npmmirror.com/mirrors/node-sass/
    export PHANTOMJS_CDNURL=https://npmmirror.com/mirrors/phantomjs/
    export PUPPETEER_DOWNLOAD_HOST=https://npmmirror.com/mirrors
    export PUPPETEER_CHROMIUM_REVISION=119.0.6045.105
    export CHROME_BIN=/usr/bin/google-chrome-stable
    export FIREFOX_BIN=/usr/bin/firefox

    # 验证配置
    CURRENT_REGISTRY=$(npm config get registry)
    if [[ "$CURRENT_REGISTRY" == "https://registry.npmmirror.com" ]] || [[ "$CURRENT_REGISTRY" == "https://registry.npmmirror.com/" ]]; then
        echo "✅ npm国内源配置成功"
    else
        echo "❌ npm国内源配置失败"
        echo "  期望: https://registry.npmmirror.com"
        echo "  实际: $CURRENT_REGISTRY"
    fi

    # 验证环境变量设置
    if [[ "$NODEJS_ORG_MIRROR" == "https://npmmirror.com/mirrors/node" ]]; then
        echo "✅ Node.js镜像环境变量配置成功"
    else
        echo "❌ Node.js镜像环境变量配置失败"
    fi

    if [[ "$ELECTRON_MIRROR" == "https://npmmirror.com/mirrors/electron/" ]]; then
        echo "✅ Electron镜像环境变量配置成功"
    else
        echo "❌ Electron镜像环境变量配置失败"
    fi

    if [[ "$PUPPETEER_DOWNLOAD_HOST" == "https://npmmirror.com/mirrors" ]]; then
        echo "✅ Puppeteer镜像环境变量配置成功"
    else
        echo "❌ Puppeteer镜像环境变量配置失败"
    fi

    # 恢复原始配置
    npm config set registry "$ORIGINAL_REGISTRY"
    unset NODEJS_ORG_MIRROR ELECTRON_MIRROR PLAYWRIGHT_DOWNLOAD_HOST SASS_BINARY_SITE PHANTOMJS_CDNURL PUPPETEER_DOWNLOAD_HOST PUPPETEER_CHROMIUM_REVISION CHROME_BIN FIREFOX_BIN
else
    echo "⚠️ npm未安装，跳过npm配置测试"
fi

echo ""
echo "🐍 2. 测试pip国内源配置..."
if command -v pip &> /dev/null; then
    # 备份原始配置
    ORIGINAL_INDEX=$(pip config get global.index-url 2>/dev/null || echo "")

    # 配置国内源
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

    # 验证配置
    CURRENT_INDEX=$(pip config get global.index-url 2>/dev/null || echo "")
    if [[ "$CURRENT_INDEX" == "https://pypi.tuna.tsinghua.edu.cn/simple/" ]]; then
        echo "✅ pip国内源配置成功"
    else
        echo "❌ pip国内源配置失败"
        echo "  期望: https://pypi.tuna.tsinghua.edu.cn/simple/"
        echo "  实际: $CURRENT_INDEX"
    fi

    # 恢复原始配置（如果有的话）
    if [[ -n "$ORIGINAL_INDEX" ]]; then
        pip config set global.index-url "$ORIGINAL_INDEX"
    fi
else
    echo "⚠️ pip未安装，跳过pip配置测试"
fi

echo ""
echo "📦 3. 测试apt国内源配置..."
if command -v apt-get &> /dev/null; then
    # 检查当前apt源
    if grep -q "mirrors.aliyun.com" /etc/apt/sources.list 2>/dev/null; then
        echo "✅ apt国内源已配置"
    else
        echo "ℹ️ apt国内源未配置（这在GitHub Actions中会自动配置）"
    fi
else
    echo "⚠️ apt-get未安装，跳过apt配置测试"
fi

echo ""
echo "🐳 4. 测试Docker镜像加速器配置..."
if command -v docker &> /dev/null; then
    if [[ -f /etc/docker/daemon.json ]]; then
        if grep -q "registry.docker-cn.com" /etc/docker/daemon.json; then
            echo "✅ Docker镜像加速器已配置"
        else
            echo "ℹ️ Docker镜像加速器未配置（这在GitHub Actions中会自动配置）"
        fi
    else
        echo "ℹ️ Docker配置文件不存在（这在GitHub Actions中会自动创建）"
    fi
else
    echo "⚠️ docker未安装，跳过Docker配置测试"
fi

echo ""
echo "📊 5. 网络连通性测试..."

# 测试npm源连通性
echo "  测试npm源连通性..."
if curl -s --connect-timeout 5 https://registry.npmmirror.com/ > /dev/null 2>&1; then
    echo "  ✅ npmmirror.com 连通正常"
else
    echo "  ❌ npmmirror.com 连接失败"
fi

# 测试pip源连通性
echo "  测试pip源连通性..."
if curl -s --connect-timeout 5 https://pypi.tuna.tsinghua.edu.cn/ > /dev/null 2>&1; then
    echo "  ✅ pypi.tuna.tsinghua.edu.cn 连通正常"
else
    echo "  ❌ pypi.tuna.tsinghua.edu.cn 连接失败"
fi

# 测试apt源连通性
echo "  测试apt源连通性..."
if curl -s --connect-timeout 5 http://mirrors.aliyun.com/ > /dev/null 2>&1; then
    echo "  ✅ mirrors.aliyun.com 连通正常"
else
    echo "  ❌ mirrors.aliyun.com 连接失败"
fi

echo ""
echo "🎉 GitHub Actions国内源配置测试完成!"
echo "========================================"
echo ""
echo "💡 使用建议:"
echo "1. 在GitHub Actions中添加 'Configure China Mirrors' 步骤"
echo "2. 定期检查镜像源的可用性"
echo "3. 如果某个镜像源失效，可以切换到其他备选源"
echo "4. 考虑使用GitHub Actions缓存来进一步提升性能"

#!/bin/bash

# Lighthouse 性能审计脚本
# 用于对网站进行性能、可访问性、最佳实践和SEO审计

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
URL="${1:-http://localhost:3000}"
OUTPUT_DIR="./tests/reports/lighthouse"
CONFIG_FILE="./e2e/lighthouse/config.js"

echo -e "${BLUE}🚀 开始 Lighthouse 性能审计...${NC}"
echo -e "${BLUE}目标URL: $URL${NC}"

# 检查 Lighthouse 是否安装
if ! command -v lighthouse &> /dev/null; then
    echo -e "${RED}❌ Lighthouse 未安装，正在安装...${NC}"
    npm install -g lighthouse
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 运行 Lighthouse 审计
echo -e "${YELLOW}📊 运行性能审计...${NC}"
lighthouse "$URL" \
    --config-path="$CONFIG_FILE" \
    --output=html \
    --output=json \
    --output-path="$OUTPUT_DIR/lighthouse-report" \
    --chrome-flags="--headless --no-sandbox --disable-dev-shm-usage" \
    --quiet

# 检查审计结果
if [ -f "$OUTPUT_DIR/lighthouse-report.json" ]; then
    echo -e "${GREEN}✅ Lighthouse 审计完成！${NC}"
    echo -e "${GREEN}📄 HTML报告: $OUTPUT_DIR/lighthouse-report.html${NC}"
    echo -e "${GREEN}📊 JSON数据: $OUTPUT_DIR/lighthouse-report.json${NC}"
    
    # 提取关键指标
    echo -e "${BLUE}📈 关键性能指标:${NC}"
    node -e "
        const report = require('./$OUTPUT_DIR/lighthouse-report.json');
        const categories = report.categories;
        console.log('性能评分:', Math.round(categories.performance.score * 100));
        console.log('可访问性:', Math.round(categories.accessibility.score * 100));
        console.log('最佳实践:', Math.round(categories['best-practices'].score * 100));
        console.log('SEO评分:', Math.round(categories.seo.score * 100));
    "
else
    echo -e "${RED}❌ Lighthouse 审计失败${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Lighthouse 审计完成！${NC}"
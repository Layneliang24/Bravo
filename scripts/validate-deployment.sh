#!/bin/bash

# Dev环境部署验证脚本
# 用于快速验证部署环境的核心功能

set -e

SERVER_URL="${1:-http://8.129.16.190}"
ADMIN_USER="${2:-admin}"
ADMIN_PASS="${3:-admin123}"

echo "🔍 开始验证部署环境: $SERVER_URL"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
PASSED=0
FAILED=0
SKIPPED=0

# 测试函数
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"

    echo -n "测试: $name ... "

    http_code=$(curl -s -o /dev/null -w "%{http_code}" -L "$url" 2>/dev/null || echo "000")

    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code, 期望 $expected_code)"
        ((FAILED++))
    fi
}

test_api_json() {
    local name="$1"
    local url="$2"
    local expected_key="$3"

    echo -n "测试: $name ... "

    response=$(curl -s "$url" 2>/dev/null)

    if echo "$response" | grep -q "\"$expected_key\""; then
        echo -e "${GREEN}✅ PASS${NC} (包含 '$expected_key')"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} (未找到 '$expected_key')"
        echo "响应: $response"
        ((FAILED++))
    fi
}

test_static_files() {
    local name="$1"
    local url="$2"

    echo -n "测试: $name ... "

    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    content_type=$(curl -s -I "$url" 2>/dev/null | grep -i "content-type" | head -1)

    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code, $content_type)"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code)"
        ((FAILED++))
    fi
}

echo "=========================================="
echo "【1. 基础连通性测试】"
echo "=========================================="

test_endpoint "前端首页" "$SERVER_URL/" "200"
test_endpoint "后端健康检查" "$SERVER_URL/health" "200"
test_endpoint "Admin后台" "$SERVER_URL/admin/" "200"

echo ""
echo "=========================================="
echo "【2. API端点测试】"
echo "=========================================="

test_api_json "API根路径" "$SERVER_URL/api/" "message"
test_api_json "API版本信息" "$SERVER_URL/api/" "version"
test_api_json "API端点列表" "$SERVER_URL/api/" "endpoints"

echo ""
echo "=========================================="
echo "【3. 静态文件测试】"
echo "=========================================="

test_static_files "Django Admin CSS" "$SERVER_URL/static/admin/css/base.css"
test_static_files "Django Admin JS" "$SERVER_URL/static/admin/js/core.js"

echo ""
echo "=========================================="
echo "【4. 响应时间测试】"
echo "=========================================="

echo -n "测试: 首页响应时间 ... "
response_time=$(curl -s -o /dev/null -w "%{time_total}" "$SERVER_URL/" 2>/dev/null || echo "999")
if (( $(echo "$response_time < 2.0" | bc -l 2>/dev/null || echo 0) )); then
    echo -e "${GREEN}✅ PASS${NC} (${response_time}s)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  WARN${NC} (${response_time}s, 较慢)"
    ((PASSED++))
fi

echo -n "测试: API响应时间 ... "
response_time=$(curl -s -o /dev/null -w "%{time_total}" "$SERVER_URL/api/" 2>/dev/null || echo "999")
if (( $(echo "$response_time < 1.0" | bc -l 2>/dev/null || echo 0) )); then
    echo -e "${GREEN}✅ PASS${NC} (${response_time}s)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  WARN${NC} (${response_time}s, 较慢)"
    ((PASSED++))
fi

echo ""
echo "=========================================="
echo "【测试总结】"
echo "=========================================="
echo -e "通过: ${GREEN}$PASSED${NC}"
echo -e "失败: ${RED}$FAILED${NC}"
echo -e "跳过: ${YELLOW}$SKIPPED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
    echo ""
    echo "✅ Dev环境部署验证成功"
    echo "📝 可以进行下一步操作："
    echo "   1. 创建release分支进行最终测试"
    echo "   2. 合并到main分支触发生产部署"
    exit 0
else
    echo -e "${RED}❌ 存在失败的测试项${NC}"
    echo ""
    echo "请检查并修复失败的项目后再继续"
    exit 1
fi

#!/bin/bash
# V4合规引擎自动化测试脚本
# 用于快速验证各个测试场景

set -e

TEST_DIR=".v4-test-results"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_DIR="$TEST_DIR/logs"
SCREENSHOT_DIR="$TEST_DIR/screenshots"
REPORT_DIR="$TEST_DIR/reports"

mkdir -p "$LOG_DIR" "$SCREENSHOT_DIR" "$REPORT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/test-$TIMESTAMP.log"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_DIR/test-$TIMESTAMP.log"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_DIR/test-$TIMESTAMP.log"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}" | tee -a "$LOG_DIR/test-$TIMESTAMP.log"
}

# 清理测试文件
cleanup() {
    log "清理测试文件..."
    git checkout -- backend/apps/example/ 2>/dev/null || true
    git checkout -- backend/tests/unit/test_example_*.py 2>/dev/null || true
    git checkout -- docs/00_product/requirements/REQ-2025-TEST-*/ 2>/dev/null || true
    rm -rf backend/apps/example/test_*.py
    rm -rf docs/00_product/requirements/REQ-2025-TEST-*
    rm -rf .taskmaster/tasks/REQ-2025-TEST-*
}

# 场景1: 缺少PRD关联
test_scenario1() {
    log "=========================================="
    log "测试场景1: 缺少PRD关联的代码提交"
    log "=========================================="

    mkdir -p backend/apps/example
    cat > backend/apps/example/views.py << 'EOF'
# 注意：这个文件没有REQ-ID
def test_view(request):
    return {"status": "ok"}
EOF

    log "尝试提交缺少REQ-ID的文件..."
    if git add backend/apps/example/views.py 2>&1 | tee -a "$LOG_DIR/scenario1-precommit.log"; then
        if git commit -m "[REQ-2025-TEST] 测试缺少PRD关联" 2>&1 | tee -a "$LOG_DIR/scenario1-precommit.log"; then
            error "场景1失败: 提交应该被拦截，但实际通过了"
            return 1
        else
            success "场景1通过: 提交被正确拦截"
            return 0
        fi
    else
        error "场景1失败: git add失败"
        return 1
    fi
}

# 场景2: 缺少测试文件
test_scenario2() {
    log "=========================================="
    log "测试场景2: 缺少测试文件的代码提交"
    log "=========================================="

    mkdir -p backend/apps/example
    cat > backend/apps/example/views.py << 'EOF'
# REQ-ID: REQ-2025-TEST-002
def test_view(request):
    return {"status": "ok"}
EOF

    log "尝试提交缺少测试文件的代码..."
    git add backend/apps/example/views.py 2>&1 | tee -a "$LOG_DIR/scenario2-precommit.log"

    if git commit -m "[REQ-2025-TEST-002] 测试缺少测试文件" 2>&1 | tee -a "$LOG_DIR/scenario2-precommit.log"; then
        error "场景2失败: 提交应该被拦截，但实际通过了"
        return 1
    else
        success "场景2通过: 提交被正确拦截"
        return 0
    fi
}

# 场景3: 缺少Task-Master任务
test_scenario3() {
    log "=========================================="
    log "测试场景3: 缺少Task-Master任务的代码提交"
    log "=========================================="

    mkdir -p backend/apps/example backend/tests/unit
    cat > backend/apps/example/views.py << 'EOF'
# REQ-ID: REQ-2025-TEST-003
def test_view(request):
    return {"status": "ok"}
EOF

    cat > backend/tests/unit/test_example_views.py << 'EOF'
def test_test_view():
    assert True
EOF

    log "尝试提交缺少Task-Master任务的代码..."
    git add backend/apps/example/views.py backend/tests/unit/test_example_views.py 2>&1 | tee -a "$LOG_DIR/scenario3-precommit.log"

    if git commit -m "[REQ-2025-TEST-003] 测试缺少Task-Master任务" 2>&1 | tee -a "$LOG_DIR/scenario3-precommit.log"; then
        error "场景3失败: 提交应该被拦截，但实际通过了"
        return 1
    else
        success "场景3通过: 提交被正确拦截"
        return 0
    fi
}

# 场景4: PRD元数据不完整
test_scenario4() {
    log "=========================================="
    log "测试场景4: PRD元数据不完整的提交"
    log "=========================================="

    mkdir -p docs/00_product/requirements/REQ-2025-TEST-004
    cat > docs/00_product/requirements/REQ-2025-TEST-004/REQ-2025-TEST-004.md << 'EOF'
---
req_id: REQ-2025-TEST-004
title: 测试PRD
status: draft
# 缺少 test_files
# 缺少 implementation_files
---
# 测试PRD内容
EOF

    log "尝试提交元数据不完整的PRD..."
    git add docs/00_product/requirements/REQ-2025-TEST-004/REQ-2025-TEST-004.md 2>&1 | tee -a "$LOG_DIR/scenario4-precommit.log"

    if git commit -m "[REQ-2025-TEST-004] 测试PRD元数据不完整" 2>&1 | tee -a "$LOG_DIR/scenario4-precommit.log"; then
        error "场景4失败: 提交应该被拦截，但实际通过了"
        return 1
    else
        success "场景4通过: 提交被正确拦截"
        return 0
    fi
}

# 场景5: 删除功能未授权
test_scenario5() {
    log "=========================================="
    log "测试场景5: 删除功能未授权的提交"
    log "=========================================="

    # 先创建一个功能文件
    mkdir -p backend/apps/example
    cat > backend/apps/example/views.py << 'EOF'
# REQ-ID: REQ-2025-TEST-005
def important_function(request):
    return {"status": "important"}
EOF

    # 创建PRD，但deletable为false
    mkdir -p docs/00_product/requirements/REQ-2025-TEST-005
    cat > docs/00_product/requirements/REQ-2025-TEST-005/REQ-2025-TEST-005.md << 'EOF'
---
req_id: REQ-2025-TEST-005
title: 测试PRD
status: draft
deletable: false
test_files: []
implementation_files: [backend/apps/example/views.py]
---
# 测试PRD内容
EOF

    git add backend/apps/example/views.py docs/00_product/requirements/REQ-2025-TEST-005/REQ-2025-TEST-005.md
    git commit -m "[REQ-2025-TEST-005] 添加功能" --no-verify || true

    # 现在删除该文件
    rm backend/apps/example/views.py
    git add backend/apps/example/views.py 2>&1 | tee -a "$LOG_DIR/scenario5-precommit.log"

    log "尝试提交未授权的删除..."
    if git commit -m "[REQ-2025-TEST-005] 删除功能（未授权）" 2>&1 | tee -a "$LOG_DIR/scenario5-precommit.log"; then
        error "场景5失败: 提交应该被拦截，但实际通过了"
        return 1
    else
        success "场景5通过: 提交被正确拦截"
        return 0
    fi
}

# 场景6: 提交信息格式错误
test_scenario6() {
    log "=========================================="
    log "测试场景6: 提交信息格式错误的提交"
    log "=========================================="

    # 创建一个符合所有要求的文件
    mkdir -p backend/apps/example backend/tests/unit .taskmaster/tasks/REQ-2025-TEST-006
    cat > backend/apps/example/views.py << 'EOF'
# REQ-ID: REQ-2025-TEST-006
def test_view(request):
    return {"status": "ok"}
EOF

    cat > backend/tests/unit/test_example_views.py << 'EOF'
def test_test_view():
    assert True
EOF

    cat > .taskmaster/tasks/REQ-2025-TEST-006/task.md << 'EOF'
# Task-1: 测试任务
EOF

    git add backend/apps/example/views.py backend/tests/unit/test_example_views.py .taskmaster/tasks/REQ-2025-TEST-006/task.md 2>&1 | tee -a "$LOG_DIR/scenario6-precommit.log"

    log "尝试使用错误格式的提交信息..."
    if git commit -m "fix: 测试提交" 2>&1 | tee -a "$LOG_DIR/scenario6-commitmsg.log"; then
        error "场景6失败: 提交应该被拦截，但实际通过了"
        return 1
    else
        success "场景6通过: 提交被正确拦截"
        return 0
    fi
}

# 场景7: 正确的提交（应该通过）
test_scenario7() {
    log "=========================================="
    log "测试场景7: 正确的提交（应该通过）"
    log "=========================================="

    # 创建完整的PRD
    mkdir -p docs/00_product/requirements/REQ-2025-TEST-007
    cat > docs/00_product/requirements/REQ-2025-TEST-007/REQ-2025-TEST-007.md << 'EOF'
---
req_id: REQ-2025-TEST-007
title: 测试PRD
status: draft
test_files: [backend/tests/unit/test_example_views.py]
implementation_files: [backend/apps/example/views.py]
deletable: true
---
# 测试PRD内容
EOF

    # 创建代码文件
    mkdir -p backend/apps/example backend/tests/unit .taskmaster/tasks/REQ-2025-TEST-007
    cat > backend/apps/example/views.py << 'EOF'
# REQ-ID: REQ-2025-TEST-007
def test_view(request):
    return {"status": "ok"}
EOF

    cat > backend/tests/unit/test_example_views.py << 'EOF'
def test_test_view():
    assert True
EOF

    cat > .taskmaster/tasks/REQ-2025-TEST-007/task.md << 'EOF'
# Task-1: 测试任务
EOF

    git add docs/00_product/requirements/REQ-2025-TEST-007/ backend/apps/example/views.py backend/tests/unit/test_example_views.py .taskmaster/tasks/REQ-2025-TEST-007/task.md 2>&1 | tee -a "$LOG_DIR/scenario7-precommit.log"

    log "尝试提交符合所有要求的代码..."
    if git commit -m "[REQ-2025-TEST-007] Task-1 实现测试功能" 2>&1 | tee -a "$LOG_DIR/scenario7-commitmsg.log"; then
        success "场景7通过: 提交成功"
        return 0
    else
        error "场景7失败: 提交应该通过，但实际被拦截"
        return 1
    fi
}

# 主测试函数
main() {
    log "🧪 开始V4合规引擎自动化测试"
    log "测试时间: $TIMESTAMP"
    log "测试目录: $TEST_DIR"

    PASSED=0
    FAILED=0

    # 执行所有测试场景
    test_scenario1 && ((PASSED++)) || ((FAILED++))
    cleanup

    test_scenario2 && ((PASSED++)) || ((FAILED++))
    cleanup

    test_scenario3 && ((PASSED++)) || ((FAILED++))
    cleanup

    test_scenario4 && ((PASSED++)) || ((FAILED++))
    cleanup

    test_scenario5 && ((PASSED++)) || ((FAILED++))
    cleanup

    test_scenario6 && ((PASSED++)) || ((FAILED++))
    cleanup

    test_scenario7 && ((PASSED++)) || ((FAILED++))
    cleanup

    # 生成测试报告
    log "=========================================="
    log "测试完成"
    log "=========================================="
    log "通过: $PASSED"
    log "失败: $FAILED"
    log "总计: $((PASSED + FAILED))"

    # 生成报告文件
    cat > "$REPORT_DIR/test-report-$TIMESTAMP.md" << EOF
# V4合规引擎测试报告

**测试时间**: $TIMESTAMP
**通过**: $PASSED
**失败**: $FAILED
**总计**: $((PASSED + FAILED))

## 详细日志
请查看: $LOG_DIR/test-$TIMESTAMP.log
EOF

    if [ $FAILED -eq 0 ]; then
        success "所有测试通过！"
        exit 0
    else
        error "有 $FAILED 个测试失败，请查看日志"
        exit 1
    fi
}

# 运行测试
main

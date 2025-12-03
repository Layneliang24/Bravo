#!/bin/bash
# 测试新实现的检查器功能
# T02, T04, T09测试脚本

set -e

echo "=========================================="
echo "V4方案新功能测试脚本"
echo "=========================================="
echo ""

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

TEST_DIR=".v4-test-results/new-checkers"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$TEST_DIR/test-$TIMESTAMP.log"

mkdir -p "$TEST_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}ℹ️ $1${NC}" | tee -a "$LOG_FILE"
}

# 清理测试文件
cleanup() {
    log "清理测试文件..."
    git checkout -- backend/apps/test_checker/ 2>/dev/null || true
    git checkout -- backend/tests/unit/test_checker_*.py 2>/dev/null || true
    git checkout -- docs/00_product/requirements/REQ-TEST-CHECKER/ 2>/dev/null || true
    rm -rf backend/apps/test_checker/
    rm -rf docs/00_product/requirements/REQ-TEST-CHECKER/
}

# 测试1: Task-0自检机制
test_task0_checker() {
    log "=========================================="
    log "测试1: Task-0自检机制"
    log "=========================================="

    # 检查Task-0是否存在
    if [ ! -f ".taskmaster/tasks/tasks.json" ]; then
        warning "Task-Master未初始化，跳过Task-0测试"
        return 0
    fi

    # 读取Task-0状态
    TASK0_STATUS=$(python3 -c "
import json
try:
    with open('.taskmaster/tasks/tasks.json', 'r') as f:
        data = json.load(f)
    current_tag = data.get('state', {}).get('currentTag', 'master')
    tasks = data.get('tags', {}).get(current_tag, {}).get('tasks', [])
    task0 = next((t for t in tasks if str(t.get('id')) == '0'), None)
    if task0:
        print(task0.get('status', 'unknown'))
    else:
        print('not_found')
except Exception as e:
    print('error')
" 2>/dev/null)

    info "Task-0状态: $TASK0_STATUS"

    if [ "$TASK0_STATUS" = "done" ]; then
        success "Task-0已完成，检查器应该允许提交"
    elif [ "$TASK0_STATUS" = "not_found" ]; then
        warning "Task-0不存在，检查器会给出警告"
    else
        info "Task-0未完成，检查器应该拦截提交"
    fi

    log "Task-0检查器测试完成"
}

# 测试2: 测试运行器
test_test_runner() {
    log "=========================================="
    log "测试2: 测试运行器集成"
    log "=========================================="

    # 创建测试文件
    mkdir -p backend/tests/unit
    cat > backend/tests/unit/test_checker_example.py << 'EOF'
def test_example_pass():
    """这个测试应该通过"""
    assert True

def test_example_math():
    """简单的数学测试"""
    assert 1 + 1 == 2
EOF

    info "创建测试文件: backend/tests/unit/test_checker_example.py"

    # 尝试运行测试
    if command -v pytest &> /dev/null; then
        log "运行pytest测试..."
        if pytest backend/tests/unit/test_checker_example.py -v 2>&1 | tee -a "$LOG_FILE"; then
            success "测试通过，检查器应该允许提交"
        else
            error "测试失败，检查器应该拦截提交"
        fi
    else
        warning "pytest未安装，跳过测试运行"
    fi

    # 清理
    rm -f backend/tests/unit/test_checker_example.py
    log "测试运行器测试完成"
}

# 测试3: PRD状态检查
test_prd_status() {
    log "=========================================="
    log "测试3: PRD状态检查"
    log "=========================================="

    # 创建draft状态的PRD
    mkdir -p docs/00_product/requirements/REQ-TEST-CHECKER
    cat > docs/00_product/requirements/REQ-TEST-CHECKER/REQ-TEST-CHECKER.md << 'EOF'
---
req_id: REQ-TEST-CHECKER
title: 测试检查器功能
status: draft
test_files:
  - backend/tests/unit/test_checker_example.py
implementation_files:
  - backend/apps/test_checker/views.py
deletable: false
---

# 测试检查器功能

这是一个用于测试新检查器的PRD。
EOF

    info "创建draft状态的PRD: REQ-TEST-CHECKER"

    # 尝试提交（应被拦截）
    git add docs/00_product/requirements/REQ-TEST-CHECKER/ 2>&1 | tee -a "$LOG_FILE"

    log "尝试提交draft状态的PRD..."
    if git commit -m "[REQ-TEST-CHECKER] 测试PRD状态检查" 2>&1 | tee -a "$LOG_FILE"; then
        error "PRD状态为draft，但提交成功了（应该被拦截）"
        git reset --soft HEAD~1
    else
        success "PRD状态为draft，提交被正确拦截"
    fi

    # 修改为approved状态
    sed -i 's/status: draft/status: approved/' docs/00_product/requirements/REQ-TEST-CHECKER/REQ-TEST-CHECKER.md
    info "修改PRD状态为approved"

    # 再次尝试提交（应通过）
    git add docs/00_product/requirements/REQ-TEST-CHECKER/
    log "尝试提交approved状态的PRD..."
    if git commit -m "[REQ-TEST-CHECKER] 测试PRD状态检查 - approved" 2>&1 | tee -a "$LOG_FILE"; then
        success "PRD状态为approved，提交成功"
        git reset --soft HEAD~1
    else
        warning "PRD状态为approved，但提交失败（可能有其他检查未通过）"
    fi

    log "PRD状态检查测试完成"
}

# 测试4: 验证检查器加载
test_checker_loading() {
    log "=========================================="
    log "测试4: 验证检查器加载"
    log "=========================================="

    # 检查检查器文件是否存在
    CHECKERS=(
        ".compliance/checkers/task0_checker.py"
        ".compliance/checkers/test_runner_checker.py"
        ".compliance/checkers/prd_checker.py"
    )

    for checker in "${CHECKERS[@]}"; do
        if [ -f "$checker" ]; then
            success "检查器文件存在: $checker"
        else
            error "检查器文件不存在: $checker"
        fi
    done

    # 检查规则文件是否存在
    RULES=(
        ".compliance/rules/task0.yaml"
        ".compliance/rules/test_runner.yaml"
    )

    for rule in "${RULES[@]}"; do
        if [ -f "$rule" ]; then
            success "规则文件存在: $rule"
        else
            error "规则文件不存在: $rule"
        fi
    done

    # 尝试导入检查器（Python语法检查）
    log "检查Python语法..."
    for checker in "${CHECKERS[@]}"; do
        if python3 -m py_compile "$checker" 2>&1 | tee -a "$LOG_FILE"; then
            success "Python语法正确: $checker"
        else
            error "Python语法错误: $checker"
        fi
    done

    log "检查器加载测试完成"
}

# 主测试流程
main() {
    log "开始测试新实现的检查器..."
    echo ""

    # 清理之前的测试文件
    cleanup

    # 执行测试
    test_checker_loading
    echo ""

    test_task0_checker
    echo ""

    test_test_runner
    echo ""

    test_prd_status
    echo ""

    # 清理
    cleanup

    log "=========================================="
    log "所有测试完成！"
    log "详细日志: $LOG_FILE"
    log "=========================================="
}

# 执行主流程
main

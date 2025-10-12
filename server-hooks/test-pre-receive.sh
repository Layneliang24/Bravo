#!/bin/bash
# 🧪 Pre-receive 钩子测试脚本
# 用途：在本地模拟 Git 服务器环境，测试 pre-receive 钩子

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${BLUE}  🧪 Pre-Receive 钩子测试工具${NC}"
echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOK_FILE="$SCRIPT_DIR/pre-receive"

# 测试工作目录
TEST_DIR="$PROJECT_ROOT/.test-pre-receive"
BARE_REPO="$TEST_DIR/bare-repo.git"
WORK_REPO="$TEST_DIR/work-repo"

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 清理函数
cleanup() {
    echo -e "\n${BLUE}[CLEANUP]${NC} 清理测试环境..."
    rm -rf "$TEST_DIR"
}

# 测试结果记录
test_pass() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo -e "${GREEN}[✓ PASS]${NC} $1"
}

test_fail() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
    echo -e "${RED}[✗ FAIL]${NC} $1"
}

test_section() {
    echo -e "\n${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE}  测试 $TOTAL_TESTS: $1${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# 设置测试环境
setup_test_env() {
    echo -e "${BLUE}[SETUP]${NC} 创建测试环境..."

    # 清理旧的测试环境
    rm -rf "$TEST_DIR"
    mkdir -p "$TEST_DIR"

    # 创建裸仓库（模拟 Git 服务器）
    echo -e "${BLUE}[SETUP]${NC} 创建裸仓库: $BARE_REPO"
    git init --bare "$BARE_REPO"

    # 部署 pre-receive 钩子到裸仓库（暂时禁用，等初始化完成后启用）
    echo -e "${BLUE}[SETUP]${NC} 准备 pre-receive 钩子"
    cp "$HOOK_FILE" "$BARE_REPO/hooks/pre-receive.disabled"
    chmod +x "$BARE_REPO/hooks/pre-receive.disabled"

    # 创建工作仓库（模拟开发者本地仓库）
    echo -e "${BLUE}[SETUP]${NC} 创建工作仓库: $WORK_REPO"
    git clone "$BARE_REPO" "$WORK_REPO"

    # 配置工作仓库
    cd "$WORK_REPO"
    git config user.name "Test User"
    git config user.email "test@example.com"

    # 创建初始提交
    echo "# Test Repository" > README.md
    git add README.md
    git commit -m "chore: initial commit"
    git push origin master

    # 重命名 master 为 main
    git branch -m master main
    git push origin -u main
    git push origin --delete master 2>/dev/null || true

    # 创建 dev 分支
    git checkout -b dev
    echo "Development branch" > dev.txt
    git add dev.txt
    git commit -m "chore: create dev branch"
    git push origin dev

    # 初始化完成后，启用 pre-receive 钩子
    echo -e "${BLUE}[SETUP]${NC} 启用 pre-receive 钩子"
    mv "$BARE_REPO/hooks/pre-receive.disabled" "$BARE_REPO/hooks/pre-receive"

    echo -e "${GREEN}[SETUP]${NC} 测试环境创建完成！\n"
}

# 测试1：允许推送到 feature 分支
test_feature_branch_allowed() {
    test_section "允许推送到 feature 分支"

    cd "$WORK_REPO"
    git checkout -b feature/test-1
    mkdir -p src
    echo "Feature 1" > src/feature1.txt
    git add src/feature1.txt
    git commit -m "feat: add feature 1"

    if git push origin feature/test-1 2>&1; then
        test_pass "Feature 分支推送成功"
        return 0
    else
        test_fail "Feature 分支推送失败（应该成功）"
        return 1
    fi
}

# 测试2：拒绝推送到 main 分支
test_main_branch_rejected() {
    test_section "拒绝推送到 main 分支"

    cd "$WORK_REPO"
    git checkout main
    mkdir -p src
    echo "Direct push to main" > src/main-change.txt
    git add src/main-change.txt
    git commit -m "feat: direct push to main"

    # 捕获推送输出
    push_output=$(git push origin main 2>&1 || true)

    if echo "$push_output" | grep -q "protected branch\|pre-receive hook declined\|remote rejected"; then
        test_pass "Main 分支推送被拒绝（符合预期）"
        git reset --hard HEAD~1  # 回滚提交
        return 0
    else
        test_fail "Main 分支推送未被拒绝（应该被拒绝）"
        echo "推送输出: $push_output" >&2
        return 1
    fi
}

# 测试3：拒绝推送到 dev 分支
test_dev_branch_rejected() {
    test_section "拒绝推送到 dev 分支"

    cd "$WORK_REPO"
    git checkout dev
    mkdir -p src
    echo "Direct push to dev" > src/dev-change.txt
    git add src/dev-change.txt
    git commit -m "feat: direct push to dev"

    # 捕获推送输出
    push_output=$(git push origin dev 2>&1 || true)

    if echo "$push_output" | grep -q "protected branch\|pre-receive hook declined\|remote rejected"; then
        test_pass "Dev 分支推送被拒绝（符合预期）"
        git reset --hard HEAD~1  # 回滚提交
        return 0
    else
        test_fail "Dev 分支推送未被拒绝（应该被拒绝）"
        echo "推送输出: $push_output" >&2
        return 1
    fi
}

# 测试4：拒绝推送敏感文件
test_sensitive_files_rejected() {
    test_section "拒绝推送敏感文件"

    cd "$WORK_REPO"
    git checkout -b feature/test-sensitive

    # 创建敏感文件
    echo "SECRET_KEY=12345" > .env
    git add .env
    git commit -m "feat: add env file"

    push_output=$(git push origin feature/test-sensitive 2>&1 || true)

    if echo "$push_output" | grep -q "禁止的文件\|pre-receive hook declined\|remote rejected"; then
        test_pass "敏感文件推送被拒绝（符合预期）"
        git reset --hard HEAD~1
        return 0
    else
        test_fail "敏感文件推送未被拒绝（应该被拒绝）"
        echo "推送输出: $push_output" >&2
        return 1
    fi
}

# 测试5：拒绝推送大文件
test_large_files_rejected() {
    test_section "拒绝推送大文件"

    cd "$WORK_REPO"
    git checkout -b feature/test-large-file

    # 创建大文件（11MB）
    dd if=/dev/zero of=large-file.bin bs=1M count=11 2>/dev/null
    git add large-file.bin
    git commit -m "feat: add large file"

    push_output=$(git push origin feature/test-large-file 2>&1 || true)

    if echo "$push_output" | grep -q "大文件\|pre-receive hook declined\|remote rejected"; then
        test_pass "大文件推送被拒绝（符合预期）"
        git reset --hard HEAD~1
        rm -f large-file.bin
        return 0
    else
        test_fail "大文件推送未被拒绝（应该被拒绝）"
        echo "推送输出: $push_output" >&2
        rm -f large-file.bin
        return 1
    fi
}

# 测试6：拒绝推送包含合并冲突标记的代码
test_merge_conflict_markers_rejected() {
    test_section "拒绝推送包含合并冲突标记的代码"

    cd "$WORK_REPO"
    git checkout -b feature/test-conflict

    # 创建包含合并冲突标记的文件
    cat > conflict.txt << 'EOF'
<<<<<<< HEAD
This is version A
=======
This is version B
>>>>>>> feature/other
EOF

    git add conflict.txt
    git commit -m "feat: add conflict markers"

    push_output=$(git push origin feature/test-conflict 2>&1 || true)

    if echo "$push_output" | grep -q "合并冲突\|pre-receive hook declined\|remote rejected"; then
        test_pass "合并冲突标记推送被拒绝（符合预期）"
        git reset --hard HEAD~1
        return 0
    else
        test_fail "合并冲突标记推送未被拒绝（应该被拒绝）"
        echo "推送输出: $push_output" >&2
        return 1
    fi
}

# 测试7：拒绝提交消息过短
test_short_commit_message_rejected() {
    test_section "拒绝提交消息过短"

    cd "$WORK_REPO"
    git checkout -b feature/test-short-msg

    mkdir -p src
    echo "test" > src/short-msg.txt
    git add src/short-msg.txt
    git commit -m "short"  # 只有5个字符

    push_output=$(git push origin feature/test-short-msg 2>&1 || true)

    if echo "$push_output" | grep -q "提交消息太短\|pre-receive hook declined\|remote rejected"; then
        test_pass "短提交消息推送被拒绝（符合预期）"
        git reset --hard HEAD~1
        return 0
    else
        test_fail "短提交消息推送未被拒绝（应该被拒绝）"
        echo "推送输出: $push_output" >&2
        return 1
    fi
}

# 测试8：检测 npm workspaces 依赖结构破坏
test_npm_workspaces_protection() {
    test_section "检测 npm workspaces 依赖结构破坏"

    cd "$WORK_REPO"
    git checkout -b feature/test-npm-workspaces

    # 模拟破坏 npm workspaces 结构
    mkdir -p frontend/e2e
    echo '{"name": "e2e"}' > frontend/e2e/package.json
    echo '{"lockfileVersion": 2}' > frontend/e2e/package-lock.json
    git add frontend/e2e/
    git commit -m "feat: add e2e package-lock (should fail)"

    push_output=$(git push origin feature/test-npm-workspaces 2>&1 || true)

    if echo "$push_output" | grep -q "npm workspaces\|pre-receive hook declined\|remote rejected"; then
        test_pass "npm workspaces 破坏被检测（符合预期）"
        git reset --hard HEAD~1
        return 0
    else
        test_fail "npm workspaces 破坏未被检测（应该被拒绝）"
        echo "推送输出: $push_output" >&2
        return 1
    fi
}

# 主测试流程
main() {
    echo -e "${BOLD}Pre-receive 钩子测试开始...${NC}\n"

    # 检查钩子文件是否存在
    if [ ! -f "$HOOK_FILE" ]; then
        echo -e "${RED}错误: 找不到钩子文件: $HOOK_FILE${NC}"
        exit 1
    fi

    # 捕获退出信号，确保清理
    trap cleanup EXIT INT TERM

    # 设置测试环境
    setup_test_env

    # 运行测试
    test_feature_branch_allowed
    test_main_branch_rejected
    test_dev_branch_rejected
    test_sensitive_files_rejected
    test_large_files_rejected
    test_merge_conflict_markers_rejected
    test_short_commit_message_rejected
    test_npm_workspaces_protection

    # 输出测试结果
    echo -e "\n${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE}  测试结果汇总${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

    echo -e "总测试数: ${BOLD}$TOTAL_TESTS${NC}"
    echo -e "${GREEN}通过: $PASSED_TESTS${NC}"
    echo -e "${RED}失败: $FAILED_TESTS${NC}"

    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "\n${GREEN}${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}${BOLD}║  ✅ 所有测试通过！Pre-receive 钩子工作正常！           ║${NC}"
        echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}\n"
        exit 0
    else
        echo -e "\n${RED}${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}${BOLD}║  ❌ 部分测试失败！请检查钩子配置！                      ║${NC}"
        echo -e "${RED}${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}\n"
        exit 1
    fi
}

# 运行主函数
main "$@"

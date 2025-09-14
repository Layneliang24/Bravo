#!/bin/bash

# 新Workflow架构快速验证脚本
# 无需Docker，直接验证workflow文件的正确性

echo "🚀 新Workflow架构快速验证"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计数器
PASSED=0
FAILED=0

# 测试函数
test_workflow_syntax() {
    local workflow_file="$1"
    local description="$2"

    echo -e "\n${BLUE}🔍 测试: $description${NC}"
    echo "文件: $workflow_file"

    if [ ! -f "$workflow_file" ]; then
        echo -e "${RED}❌ 文件不存在${NC}"
        ((FAILED++))
        return 1
    fi

    # 使用Python验证YAML语法
    python3 -c "
import yaml
import sys

try:
    with open('$workflow_file', 'r', encoding='utf-8') as f:
        workflow = yaml.safe_load(f)

    # 基本结构检查
    if 'name' not in workflow:
        print('❌ 缺少name字段')
        sys.exit(1)

    if 'on' not in workflow:
        print('❌ 缺少on字段')
        sys.exit(1)

    if 'jobs' not in workflow:
        print('❌ 缺少jobs字段')
        sys.exit(1)

    print(f'✅ 语法正确: {workflow[\"name\"]}')
    print(f'📋 包含 {len(workflow[\"jobs\"])} 个jobs')

    # 显示job依赖关系
    for job_name, job_config in workflow['jobs'].items():
        needs = job_config.get('needs', [])
        if isinstance(needs, str):
            needs = [needs]
        elif not isinstance(needs, list):
            needs = []

        uses = job_config.get('uses', '')
        if uses:
            print(f'  🧩 {job_name} -> {uses} (依赖: {needs})')
        else:
            print(f'  🔧 {job_name} (依赖: {needs})')

except yaml.YAMLError as e:
    print(f'❌ YAML语法错误: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ 验证失败: {e}')
    sys.exit(1)
    " 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $description 验证通过${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ $description 验证失败${NC}"
        ((FAILED++))
        return 1
    fi
}

# 检查依赖
check_dependencies() {
    echo -e "\n${BLUE}🔧 检查依赖环境${NC}"

    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ 需要Python3环境${NC}"
        exit 1
    fi

    python3 -c "import yaml" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  安装PyYAML...${NC}"
        pip3 install PyYAML
    fi

    echo -e "${GREEN}✅ 依赖检查完成${NC}"
}

# 测试原子组件
test_atomic_components() {
    echo -e "\n${BLUE}🧩 测试原子组件${NC}"
    echo "--------------------------------"

    # 原子组件列表
    local components=(
        "setup-cache:统一缓存管理"
        "test-unit-backend:后端单元测试"
        "test-unit-frontend:前端单元测试"
        "test-integration:集成测试"
        "test-e2e-smoke:E2E烟雾测试"
        "test-e2e-full:E2E完整测试"
        "test-regression:回归测试"
        "quality-security:安全扫描"
        "quality-performance:性能测试"
        "quality-coverage:覆盖率检查"
    )

    for component_info in "${components[@]}"; do
        IFS=':' read -r component_name description <<< "$component_info"
        workflow_file=".github/workflows/${component_name}.yml"
        test_workflow_syntax "$workflow_file" "原子组件 - $description"
    done
}

# 测试场景触发器
test_scenario_triggers() {
    echo -e "\n${BLUE}🎯 测试场景触发器${NC}"
    echo "--------------------------------"

    # 场景触发器列表
    local scenarios=(
        "on-pr:PR验证流程"
        "on-push-dev:Dev推送验证"
    )

    for scenario_info in "${scenarios[@]}"; do
        IFS=':' read -r scenario_name description <<< "$scenario_info"
        workflow_file=".github/workflows/${scenario_name}.yml"
        test_workflow_syntax "$workflow_file" "场景触发器 - $description"
    done
}

# 分析workflow依赖关系
analyze_dependencies() {
    echo -e "\n${BLUE}🔗 分析workflow依赖关系${NC}"
    echo "--------------------------------"

    python3 -c "
import yaml
import os
from pathlib import Path

workflows_dir = Path('.github/workflows')
if not workflows_dir.exists():
    print('❌ .github/workflows目录不存在')
    exit(1)

print('📊 Workflow依赖分析:')
print()

# 收集所有workflow
workflows = {}
for workflow_file in workflows_dir.glob('*.yml'):
    try:
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)
        workflows[workflow_file.stem] = workflow
    except Exception as e:
        print(f'⚠️  跳过无效文件: {workflow_file.name} ({e})')

# 分析依赖关系
reusable_workflows = []
trigger_workflows = []

for name, workflow in workflows.items():
    on_config = workflow.get('on', {})
    if 'workflow_call' in on_config:
        reusable_workflows.append(name)
    else:
        trigger_workflows.append(name)

print(f'🧩 可复用组件 ({len(reusable_workflows)} 个):')
for wf in sorted(reusable_workflows):
    print(f'  - {wf}')

print(f'\\n🎯 触发器workflow ({len(trigger_workflows)} 个):')
for wf in sorted(trigger_workflows):
    print(f'  - {wf}')

# 检查uses依赖
print('\\n🔗 依赖关系:')
for name, workflow in workflows.items():
    if name in trigger_workflows:
        jobs = workflow.get('jobs', {})
        uses_list = []
        for job_name, job_config in jobs.items():
            uses = job_config.get('uses', '')
            if uses and uses.startswith('./'):
                component = uses.split('/')[-1].replace('.yml', '')
                uses_list.append(component)

        if uses_list:
            print(f'  {name} -> {uses_list}')

print('\\n✅ 依赖关系分析完成')
    "
}

# 检查workflow完整性
check_completeness() {
    echo -e "\n${BLUE}🎯 检查架构完整性${NC}"
    echo "--------------------------------"

    # 必需的原子组件
    local required_components=(
        "setup-cache"
        "test-unit-backend"
        "test-unit-frontend"
        "test-integration"
        "test-e2e-smoke"
    )

    # 必需的场景触发器
    local required_triggers=(
        "on-pr"
        "on-push-dev"
    )

    echo "🔍 检查必需组件..."
    local missing_components=()

    for component in "${required_components[@]}"; do
        if [ ! -f ".github/workflows/${component}.yml" ]; then
            missing_components+=("$component")
        fi
    done

    for trigger in "${required_triggers[@]}"; do
        if [ ! -f ".github/workflows/${trigger}.yml" ]; then
            missing_components+=("$trigger")
        fi
    done

    if [ ${#missing_components[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ 所有必需组件都存在${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ 缺少以下组件:${NC}"
        for component in "${missing_components[@]}"; do
            echo "  - $component"
        done
        ((FAILED++))
    fi
}

# 性能预估
estimate_performance() {
    echo -e "\n${BLUE}⚡ 性能预估${NC}"
    echo "--------------------------------"

    echo "📊 预估执行时间 (基于并行优化):"
    echo "  🚀 PR验证:     8-15分钟  (快速验证)"
    echo "  🔄 Dev推送:    15-25分钟 (中等验证)"
    echo "  🎯 Main推送:   25-40分钟 (完整验证)"
    echo ""
    echo "💾 缓存优化效果:"
    echo "  📦 依赖缓存:   节省 3-5分钟"
    echo "  🏗️  构建缓存:   节省 2-3分钟"
    echo "  🧪 测试缓存:   节省 1-2分钟"
    echo ""
    echo "⚡ 并行执行优化:"
    echo "  🔧 单元测试:   并行执行 (2-3分钟)"
    echo "  🔗 集成测试:   依赖单元测试"
    echo "  🎭 E2E测试:    依赖集成测试"
}

# 主函数
main() {
    echo "开始时间: $(date)"

    # 检查依赖
    check_dependencies

    # 测试原子组件
    test_atomic_components

    # 测试场景触发器
    test_scenario_triggers

    # 分析依赖关系
    analyze_dependencies

    # 检查完整性
    check_completeness

    # 性能预估
    estimate_performance

    # 输出总结
    echo ""
    echo "=================================="
    echo -e "${BLUE}📊 测试结果汇总${NC}"
    echo "=================================="
    echo -e "✅ 通过: ${GREEN}$PASSED${NC}"
    echo -e "❌ 失败: ${RED}$FAILED${NC}"
    echo ""

    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 新Workflow架构验证成功！${NC}"
        echo -e "${GREEN}所有组件都已正确配置，可以开始实际测试。${NC}"
        exit 0
    else
        echo -e "${RED}⚠️  发现问题，需要修复后再测试。${NC}"
        exit 1
    fi
}

# 运行主函数
main "$@"

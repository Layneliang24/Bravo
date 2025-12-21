#!/bin/bash
# Task-Master parse-prd包装脚本，带PRD状态验证
# 用法: ./scripts/task-master-parse-prd.sh <prd-file> [其他task-master参数]

set -e  # 遇到错误立即退出

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查参数
if [ $# -lt 1 ]; then
    echo -e "${RED}❌ 错误：缺少参数${NC}"
    echo ""
    echo "用法: $0 <prd-file> [其他task-master参数]"
    echo ""
    echo "示例:"
    echo "  $0 docs/00_product/requirements/REQ-2025-001/REQ-2025-001.md"
    echo "  $0 .taskmaster/docs/user-login.txt --num-tasks=5 --research"
    exit 1
fi

PRD_FILE="$1"
shift  # 移除第一个参数，剩下的都是task-master参数

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Task-Master Parse-PRD（带PRD状态验证 + 自动生成Task-0）${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# 步骤1：验证PRD文件是否存在
echo -e "${YELLOW}📁 [步骤1/6] 检查PRD文件...${NC}"
if [ ! -f "$PRD_FILE" ]; then
    echo -e "${RED}❌ PRD文件不存在: $PRD_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✅ PRD文件存在${NC}"
echo ""

# 步骤2：验证PRD状态
echo -e "${YELLOW}🔍 [步骤2/6] 验证PRD状态...${NC}"
cd "$PROJECT_ROOT"

# 在Docker容器内执行验证器（避免宿主机Python环境问题）
if command -v docker-compose >/dev/null 2>&1; then
    # 转换路径为容器内路径
    if [[ "$PRD_FILE" == docs/* ]]; then
        CONTAINER_PRD_PATH="/app/$PRD_FILE"
    elif [[ "$PRD_FILE" == .taskmaster/* ]]; then
        CONTAINER_PRD_PATH="/app/$PRD_FILE"
    else
        CONTAINER_PRD_PATH="/app/$PRD_FILE"
    fi

    docker-compose exec -T backend sh -c \
        "cd /app && python project_scripts/task-master/prd_status_validator.py $CONTAINER_PRD_PATH" \
        2>&1 | grep -v "WARNING:.*docker-compose" || true
    VALIDATOR_EXIT_CODE=${PIPESTATUS[0]}
else
    # 回退到宿主机执行（不推荐）
    python scripts/task-master/prd_status_validator.py "$PRD_FILE" 2>&1
    VALIDATOR_EXIT_CODE=$?
fi

if [ $VALIDATOR_EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${RED}════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ❌ PRD状态验证失败，parse-prd操作被拒绝${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════${NC}"
    exit 1
fi
echo -e "${GREEN}✅ PRD状态验证通过${NC}"
echo ""

# 步骤3：调用真实的task-master parse-prd
echo -e "${YELLOW}🚀 [步骤3/6] 执行task-master parse-prd...${NC}"
echo -e "${BLUE}📋 命令: task-master parse-prd --input=\"$PRD_FILE\" $@${NC}"
echo ""

# 执行task-master parse-prd
task-master parse-prd --input="$PRD_FILE" "$@"
PARSE_EXIT_CODE=$?

if [ $PARSE_EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${RED}❌ parse-prd执行失败（退出码: $PARSE_EXIT_CODE）${NC}"
    exit $PARSE_EXIT_CODE
fi

echo ""
echo -e "${GREEN}✅ parse-prd执行成功${NC}"
echo ""

# 步骤4：记录PRD路径到tasks.json的metadata
echo -e "${YELLOW}📝 [步骤4/6] 记录PRD路径到tasks.json metadata...${NC}"

# 提取tag参数（如果有）
TAG_ARG=""
APPEND_ARG=""
for arg in "$@"; do
    if [[ "$arg" == --tag=* ]]; then
        TAG_ARG="${arg#--tag=}"
    elif [[ "$arg" == "--append" ]]; then
        APPEND_ARG="true"
    fi
done

# 如果没有指定tag，使用master
if [ -z "$TAG_ARG" ]; then
    TAG_ARG="master"
fi

# 调用Python脚本更新metadata
docker-compose exec -T backend sh -c \
    "cd /app && python project_scripts/task-master/update_tasks_metadata.py \
    --tag='$TAG_ARG' \
    --prd-path='$CONTAINER_PRD_PATH' \
    --append='$APPEND_ARG'" \
    2>&1 | grep -v "WARNING:.*docker-compose" || true
METADATA_EXIT_CODE=${PIPESTATUS[0]}

if [ $METADATA_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ PRD路径已记录到metadata${NC}"
else
    echo -e "${YELLOW}⚠️  metadata更新失败（非阻塞）${NC}"
fi

# 步骤5：自动生成Task-0
echo ""
echo -e "${YELLOW}🎯 [步骤5/6] 自动生成Task-0...${NC}"

# 使用步骤4中提取的TAG_ARG作为REQ-ID（如果存在且不是master）
REQ_ID=""
if [ -n "$TAG_ARG" ] && [ "$TAG_ARG" != "master" ]; then
    REQ_ID="$TAG_ARG"
fi

# 如果没有从TAG_ARG获取，尝试从PRD文件路径提取
if [ -z "$REQ_ID" ]; then
    if [[ "$PRD_FILE" =~ REQ-[0-9]{4}-[0-9]{3}-[a-z0-9-]+ ]]; then
        REQ_ID="${BASH_REMATCH[0]}"
    fi
fi

# 如果仍然没有，尝试从tasks.json查找最新更新的tag
if [ -z "$REQ_ID" ]; then
    TASKS_JSON="$PROJECT_ROOT/.taskmaster/tasks/tasks.json"
    if [ -f "$TASKS_JSON" ]; then
        REQ_ID=$(python3 -c "
import json
try:
    with open('$TASKS_JSON', 'r', encoding='utf-8') as f:
        data = json.load(f)
    latest_tag = None
    latest_time = None
    for tag, tag_data in data.items():
        if tag == 'master':
            continue
        if isinstance(tag_data, dict) and 'metadata' in tag_data:
            updated = tag_data['metadata'].get('updated_at', '')
            if updated and (latest_time is None or updated > latest_time):
                latest_time = updated
                latest_tag = tag
    if latest_tag:
        print(latest_tag)
except Exception:
    pass
" 2>/dev/null)
    fi
fi

# 如果找到REQ-ID，自动生成Task-0
if [ -n "$REQ_ID" ]; then
    echo -e "${BLUE}📋 检测到REQ-ID: $REQ_ID${NC}"

    # 在宿主机执行adapter.py（因为需要修改tasks.json文件）
    cd "$PROJECT_ROOT"
    ADAPTER_OUTPUT=$(python3 scripts/task-master/adapter.py "$REQ_ID" 2>&1)
    ADAPTER_EXIT_CODE=$?

    # 过滤掉"警告: Task-0已存在"的消息（这是正常情况）
    if echo "$ADAPTER_OUTPUT" | grep -qv "警告: Task-0已存在"; then
        echo "$ADAPTER_OUTPUT" | grep -v "警告: Task-0已存在"
    fi

    if [ $ADAPTER_EXIT_CODE -eq 0 ]; then
        # 检查是否是因为Task-0已存在而跳过
        if echo "$ADAPTER_OUTPUT" | grep -q "警告: Task-0已存在"; then
            echo -e "${YELLOW}⚠️  Task-0已存在，跳过生成${NC}"
        else
            echo -e "${GREEN}✅ Task-0已自动生成${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Task-0生成失败（非阻塞）${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  无法自动检测REQ-ID，请手动运行: ${GREEN}python scripts/task-master/adapter.py <REQ-ID>${NC}"
fi

# 步骤6：自动更新PRD状态为implementing
echo ""
echo -e "${YELLOW}🔄 [步骤6/6] 更新PRD状态...${NC}"
docker-compose exec -T backend sh -c \
    "cd /app && python project_scripts/task-master/prd_status_validator.py $CONTAINER_PRD_PATH --update-status" \
    2>&1 | grep -v "WARNING:.*docker-compose" || true
UPDATE_EXIT_CODE=${PIPESTATUS[0]}

if [ $UPDATE_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ PRD状态已更新为implementing${NC}"
else
    echo -e "${YELLOW}⚠️  PRD状态更新失败（非阻塞）${NC}"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ parse-prd操作完成！${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📁 任务文件位置:${NC}"
echo -e "   .taskmaster/tasks/tasks.json"
echo ""
echo -e "${BLUE}📝 下一步操作:${NC}"
echo -e "   1. 查看任务列表: ${GREEN}task-master list${NC}"
echo -e "   2. 查看Task-0: ${GREEN}task-master show 0${NC}"
echo -e "   3. 展开任务: ${GREEN}task-master expand --all --research${NC}"
echo -e "   4. 开始开发: 按任务顺序实施"
echo ""

exit 0

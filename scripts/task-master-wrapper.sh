#!/bin/bash
# Task-Master全局包装脚本
# 拦截parse-prd命令，自动添加PRD状态验证

# 获取真实的task-master命令
REAL_TASK_MASTER="$(command -v task-master 2>/dev/null || echo "task-master")"

# 检查是否是parse-prd命令
if [ "$1" = "parse-prd" ] || [ "$1" = "parsePrd" ]; then
    # 保存原始参数
    ORIGINAL_ARGS=("$@")

    # 提取PRD文件路径
    PRD_FILE=""
    shift  # 移除parse-prd

    # 解析参数，找到--input或第一个非选项参数
    while [ $# -gt 0 ]; do
        case "$1" in
            --input=*)
                PRD_FILE="${1#*=}"
                shift
                ;;
            -i|--input)
                PRD_FILE="$2"
                shift 2
                ;;
            -*)
                shift
                ;;
            *)
                if [ -z "$PRD_FILE" ]; then
                    PRD_FILE="$1"
                fi
                shift
                ;;
        esac
    done

    # 如果找到了PRD文件，验证状态
    if [ -n "$PRD_FILE" ] && [ -f "$PRD_FILE" ]; then
        # 检查是否是标准PRD路径
        if [[ "$PRD_FILE" == docs/00_product/requirements/* ]]; then
            # 在Docker容器内执行验证器
            if command -v docker-compose >/dev/null 2>&1; then
                # 获取项目根目录（从包装脚本位置推断）
                SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
                PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
                # 确保PRD文件路径是相对于项目根目录的
                if [[ "$PRD_FILE" != /* ]]; then
                    CONTAINER_PRD_PATH="/app/$PRD_FILE"
                else
                    # 绝对路径，需要转换为容器内路径
                    CONTAINER_PRD_PATH="/app${PRD_FILE#$PROJECT_ROOT}"
                fi

                # 执行验证
                docker-compose exec -T backend sh -c \
                    "cd /app && python project_scripts/task-master/prd_status_validator.py $CONTAINER_PRD_PATH" \
                    2>&1 | grep -v "WARNING:.*docker-compose" >&2
                VALIDATOR_EXIT_CODE=${PIPESTATUS[0]}

                if [ $VALIDATOR_EXIT_CODE -ne 0 ]; then
                    exit 1
                fi
            fi
        fi
    fi

    # 验证通过，调用真实的task-master parse-prd（使用原始参数）
    exec "$REAL_TASK_MASTER" "${ORIGINAL_ARGS[@]}"
else
    # 其他命令直接透传
    exec "$REAL_TASK_MASTER" "$@"
fi

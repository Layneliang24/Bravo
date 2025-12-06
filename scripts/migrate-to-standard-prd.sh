#!/bin/bash
# PRD迁移脚本：从.taskmaster/docs/到docs/00_product/
# 用途：将精化后的需求迁移到标准PRD目录

set -e

REFINED_FILE=$1
REQ_ID=$2

if [ -z "$REFINED_FILE" ] || [ -z "$REQ_ID" ]; then
    echo "❌ 错误：缺少参数"
    echo ""
    echo "用法："
    echo "  bash scripts/migrate-to-standard-prd.sh <refined-file> <REQ-ID>"
    echo ""
    echo "示例："
    echo "  bash scripts/migrate-to-standard-prd.sh .taskmaster/docs/user-login-refined.txt REQ-2025-001-user-login"
    echo ""
    echo "REQ-ID格式："
    echo "  REQ-YYYY-NNN-description"
    echo "  - YYYY: 年份（如2025）"
    echo "  - NNN: 三位数字序号（001-999）"
    echo "  - description: 简短描述（kebab-case）"
    echo ""
    exit 1
fi

# 检查文件是否存在
if [ ! -f "$REFINED_FILE" ]; then
    echo "❌ 错误：文件不存在: $REFINED_FILE"
    exit 1
fi

# 验证REQ-ID格式
if ! echo "$REQ_ID" | grep -qE "^REQ-[0-9]{4}-[0-9]{3}-.+$"; then
    echo "❌ 错误：REQ-ID格式不正确"
    echo ""
    echo "正确格式：REQ-YYYY-NNN-description"
    echo "示例：REQ-2025-001-user-login"
    echo ""
    exit 1
fi

# 创建目标目录
TARGET_DIR="docs/00_product/requirements/${REQ_ID}"
TARGET_FILE="${TARGET_DIR}/${REQ_ID}.md"

mkdir -p "$TARGET_DIR"

# 检查目标文件是否已存在
if [ -f "$TARGET_FILE" ]; then
    echo "⚠️  警告：目标文件已存在: $TARGET_FILE"
    read -p "是否覆盖？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 取消迁移"
        exit 1
    fi
fi

# 提取功能标题（从第一行）
TITLE=$(head -1 "$REFINED_FILE" | sed 's/^# //')

echo "=========================================="
echo "📋 PRD迁移工具"
echo "=========================================="
echo ""
echo "📁 源文件: $REFINED_FILE"
echo "📁 目标文件: $TARGET_FILE"
echo "🆔 REQ-ID: $REQ_ID"
echo "📝 标题: $TITLE"
echo ""
echo "=========================================="
echo "🔄 正在迁移..."
echo "=========================================="
echo ""

# 创建YAML frontmatter
cat > "$TARGET_FILE" << EOF
---
req_id: $REQ_ID
title: $TITLE
status: draft
priority: medium
type: feature
created_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date +"%Y-%m-%dT%H:%M:%SZ")
updated_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date +"%Y-%m-%dT%H:%M:%SZ")
author: human
refined_by: cursor
test_files: []  # TODO: 填写测试文件列表
implementation_files: []  # TODO: 填写实现文件列表
api_contract: docs/01_guideline/api-contracts/${REQ_ID}/api.yaml
deletable: false
---

EOF

# 复制refined文件内容（跳过frontmatter如果有）
if grep -q "^---$" "$REFINED_FILE"; then
    # 文件已有frontmatter，跳过
    sed -n '/^---$/,/^---$/!p;//!p' "$REFINED_FILE" >> "$TARGET_FILE"
else
    # 直接复制所有内容
    cat "$REFINED_FILE" >> "$TARGET_FILE"
fi

echo "✅ 迁移完成!"
echo ""
echo "=========================================="
echo "📝 下一步操作："
echo "=========================================="
echo ""
echo "1. 打开PRD文件并补充元数据："
echo "   vim $TARGET_FILE"
echo ""
echo "   需要补充："
echo "   - test_files: 测试文件列表"
echo "   - implementation_files: 实现文件列表"
echo ""
echo "2. 审核PRD内容（如果使用严格模式）："
echo "   - 修改status: draft → review → approved"
echo ""
echo "3. Parse PRD："
echo "   task-master parse-prd --input=$TARGET_FILE"
echo ""
echo "4. 如果parse成功："
echo "   - PRD状态自动更新：approved → implementing"
echo "   - 生成tasks.json"
echo ""
echo "5. 展开任务："
echo "   task-master expand --all --research"
echo ""
echo "=========================================="

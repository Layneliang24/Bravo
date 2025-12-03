#!/bin/bash
# PRD精化辅助脚本
# 用途：辅助提示Cursor精化需求文件

set -e

RAW_FILE=$1

if [ -z "$RAW_FILE" ]; then
    echo "❌ 错误：缺少参数"
    echo ""
    echo "用法："
    echo "  bash scripts/refine-prd.sh <raw-file>"
    echo ""
    echo "示例："
    echo "  bash scripts/refine-prd.sh .taskmaster/docs/user-login-raw.txt"
    echo ""
    exit 1
fi

# 检查文件是否存在
if [ ! -f "$RAW_FILE" ]; then
    echo "❌ 错误：文件不存在: $RAW_FILE"
    exit 1
fi

# 提取文件名（无扩展名）
BASENAME=$(basename "$RAW_FILE" .txt)
DIRNAME=$(dirname "$RAW_FILE")
REFINED_FILE="${DIRNAME}/${BASENAME}-refined.txt"

echo "=========================================="
echo "📝 PRD精化辅助工具"
echo "=========================================="
echo ""
echo "📁 原始需求文件: $RAW_FILE"
echo "📁 精化输出文件: $REFINED_FILE"
echo ""
echo "=========================================="
echo "🤖 请在Cursor中执行以下操作："
echo "=========================================="
echo ""
echo "方式1：直接对话"
echo "---"
echo "@$RAW_FILE 请精化这个需求，补充以下内容并保存到 $REFINED_FILE："
echo ""
echo "1. 数据库设计（表结构、字段、约束、关系）"
echo "2. API接口定义（端点、方法、请求/响应格式）"
echo "3. 前端组件设计（页面结构、组件层次、状态管理）"
echo "4. 测试策略（测试文件路径、测试用例）"
echo "5. 技术实现细节（技术选型、第三方库、架构决策）"
echo ""
echo "请使用清晰的Markdown格式，包含完整的章节结构。"
echo "---"
echo ""
echo "方式2：使用精化规则（如果已创建.cursor/rules/prd-refinement.md）"
echo "---"
echo "@$RAW_FILE 按照PRD精化规则，补充技术细节并保存到 $REFINED_FILE"
echo "---"
echo ""
echo "=========================================="
echo "📋 精化完成后的下一步："
echo "=========================================="
echo ""
echo "1. 快速验证（可选）："
echo "   task-master parse-prd --input=$REFINED_FILE"
echo ""
echo "2. 迁移到标准PRD（正式立项）："
echo "   bash scripts/migrate-to-standard-prd.sh $REFINED_FILE REQ-YYYY-NNN-description"
echo ""
echo "=========================================="

#!/bin/bash
# 检查合规警告并自动修复常见问题
# 用法: ./scripts/check-compliance-warnings.sh

set -e

echo "🔍 检查合规警告..."

# 检查所有代码文件是否包含REQ-ID
echo ""
echo "📋 检查REQ-ID注释..."
missing_req_id=0

find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.vue" \) \
  ! -path "*/node_modules/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/migrations/*" \
  ! -path "*/tests/*" \
  ! -path "*/.git/*" \
  ! -path "*/venv/*" \
  ! -path "*/dist/*" \
  ! -path "*/build/*" \
  | while read file; do
    # 跳过已经有REQ-ID的文件
    if grep -q "REQ-ID" "$file" 2>/dev/null; then
      continue
    fi

    # 跳过一些特殊文件
    if [[ "$file" == *"__init__.py" ]] || \
       [[ "$file" == *".test.ts" ]] || \
       [[ "$file" == *".spec.ts" ]] || \
       [[ "$file" == *"shims-vue.d.ts" ]]; then
      continue
    fi

    echo "⚠️  缺少REQ-ID: $file"
    missing_req_id=$((missing_req_id + 1))
  done

if [ $missing_req_id -gt 0 ]; then
  echo ""
  echo "❌ 发现 $missing_req_id 个文件缺少REQ-ID注释"
  echo "💡 修复方法："
  echo "   Python文件: 在文件头部添加 # REQ-ID: REQ-YYYY-NNN-description"
  echo "   TS/JS文件: 在文件头部添加 // REQ-ID: REQ-YYYY-NNN-description"
  echo "   Vue文件: 在<script>标签内第一行添加 // REQ-ID: REQ-YYYY-NNN-description"
  exit 1
else
  echo "✅ 所有代码文件都包含REQ-ID注释"
fi

echo ""
echo "✅ 合规检查完成"

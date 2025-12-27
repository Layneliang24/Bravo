#!/bin/bash
# 检查所有规则文件的声明格式是否一致

echo "=== 检查声明格式一致性 ==="
echo ""

find .cursor/rules -name "*.mdc" -type f | \
  grep -v "RULE_TEMPLATE\|intent-recognition\|v4-core" | \
  while read file; do
    if grep -q "## 规则应用声明" "$file"; then
      # 检查是否包含必需的格式元素
      has_rule_declaration=$(grep -c "应用规则：@.cursor/rules" "$file" 2>/dev/null || echo "0")
      has_verification=$(grep -c "验证要求" "$file" 2>/dev/null || echo "0")

      if [ "$has_rule_declaration" -gt 0 ] && [ "$has_verification" -gt 0 ]; then
        echo "✅ $(basename $file) - 格式正确"
      else
        echo "❌ $(basename $file) - 格式不完整"
      fi
    fi
  done

echo ""
echo "=== 检查完成 ==="

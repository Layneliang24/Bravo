#!/bin/bash
# 检查所有被路由的规则文件是否都有声明部分

echo "=== 检查规则文件完整性 ==="
echo ""

# 获取intent-recognition中引用的所有规则文件
grep -o "@\.cursor/rules/[^\"]*\.mdc" .cursor/rules/00-core/intent-recognition.mdc | \
  sed 's/@\.cursor\/rules\///' | \
  sort -u | \
  while read file; do
    if [ -f ".cursor/rules/$file" ]; then
      if grep -q "## 规则应用声明" ".cursor/rules/$file"; then
        echo "✅ $file - 有声明"
      else
        echo "❌ $file - 缺少声明"
      fi
    else
      echo "⚠️  $file - 文件不存在"
    fi
  done

echo ""
echo "=== 检查完成 ==="

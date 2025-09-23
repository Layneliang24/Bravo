#!/bin/bash
echo "🧪 测试 --no-verify 保护是否生效..."
echo ""

echo "测试1: 直接--no-verify (应被拦截)"
git commit --no-verify -m "test protection" 2>&1

echo ""
echo "测试2: -n 简写形式 (应被拦截)" 
git commit -n -m "test protection" 2>&1

echo ""
echo "测试3: 正常commit (应正常工作)"
echo "git commit -m 'normal commit' (不会实际提交)"

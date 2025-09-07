#!/bin/bash

# Bravo 项目命名规范检查脚本
# 用于在提交前检查代码是否符合命名规范

set -e

echo "🔍 开始检查命名规范..."

# 检查 Python 命名规范
echo "📋 检查 Python 命名规范..."
if [ -d "backend" ]; then
    cd backend
    echo "  运行 flake8 命名检查..."
    python -m flake8 --select=N --config=.flake8 . || {
        echo "❌ Python flake8 命名检查失败"
        exit 1
    }
    
    echo "  运行 pylint 命名检查..."
    python -m pylint --rcfile=.pylintrc.naming --load-plugins=pylint.extensions.bad_builtin,pylint.extensions.check_elif,pylint.extensions.docparams,pylint.extensions.docstyle,pylint.extensions.empty_comment,pylint.extensions.mccabe,pylint.extensions.overlapping_exceptions,pylint.extensions.private_import,pylint.extensions.redefined_variable_type,pylint.extensions.typing,pylint.extensions.while_used . || {
        echo "❌ Python pylint 命名检查失败"
        exit 1
    }
    cd ..
    echo "✅ Python 命名规范检查通过"
else
    echo "⚠️  未找到 backend 目录，跳过 Python 检查"
fi

# 检查前端命名规范
echo "📋 检查前端命名规范..."
if [ -d "frontend" ]; then
    cd frontend
    
    echo "  检查 TypeScript/JavaScript 命名规范..."
    if [ -f "package.json" ]; then
        npx eslint --config .eslintrc.js --rule '@typescript-eslint/naming-convention: error' src/ || {
            echo "❌ TypeScript 命名检查失败"
            exit 1
        }
        
        echo "  检查 Vue 组件命名规范..."
        npx eslint --config .eslintrc.js --rule 'vue/component-name-in-template-casing: error' --rule 'vue/component-definition-name-casing: error' src/ || {
            echo "❌ Vue 组件命名检查失败"
            exit 1
        }
    else
        echo "⚠️  未找到 package.json，跳过前端检查"
    fi
    cd ..
    echo "✅ 前端命名规范检查通过"
else
    echo "⚠️  未找到 frontend 目录，跳过前端检查"
fi

# 检查数据库命名规范
echo "📋 检查数据库命名规范..."
if [ -f "backend/manage.py" ]; then
    cd backend
    echo "  检查 Django 模型命名规范..."
    python manage.py check --database || {
        echo "❌ Django 模型检查失败"
        exit 1
    }
    cd ..
    echo "✅ 数据库命名规范检查通过"
else
    echo "⚠️  未找到 Django 项目，跳过数据库检查"
fi

echo "🎉 所有命名规范检查通过！"
echo "📖 命名规范文档位于: docs/01_guideline/命名规范.md"
echo "📖 数据库命名约定文档位于: docs/01_guideline/数据库命名约定.md"
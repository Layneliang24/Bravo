# PART6: 实施落地手册

> **版本**: V4.0
> **主题**: 安装脚本、配置示例、完整演示、故障排查
> **定位**: 从零开始部署整个AI驱动开发工作流

---

## 目录

- [1. 前置条件](#1-前置条件)
- [2. 一键安装脚本](#2-一键安装脚本)
- [3. 完整配置文件](#3-完整配置文件)
- [4. Task-Master适配层完整实现](#4-task-master适配层完整实现)
- [5. 完整开发流程演示](#5-完整开发流程演示)
- [6. 故障排查指南](#6-故障排查指南)
- [7. 常见问题FAQ](#7-常见问题faq)
- [8. 最佳实践](#8-最佳实践)

---

## 1. 前置条件

### 1.1 系统要求

| 组件               | 最低版本 | 推荐版本 | 说明              |
| ------------------ | -------- | -------- | ----------------- |
| **Python**         | 3.9      | 3.11+    | 后端开发          |
| **Node.js**        | 18       | 20+      | 前端开发和E2E测试 |
| **Git**            | 2.30     | 2.40+    | 版本控制          |
| **Docker**         | 20.10    | 24.0+    | 容器化开发        |
| **Docker Compose** | 2.0      | 2.20+    | 多容器编排        |

### 1.2 可选工具

| 工具            | 用途                   | 安装                                |
| --------------- | ---------------------- | ----------------------------------- |
| **Task-Master** | 任务管理               | `npm install -g claude-task-master` |
| **act**         | 本地测试GitHub Actions | `brew install act` (macOS)          |
| **jq**          | JSON处理               | `brew install jq` (macOS)           |
| **yq**          | YAML处理               | `brew install yq` (macOS)           |

### 1.3 权限要求

- Git仓库的写权限
- GitHub Actions的配置权限（如果使用GitHub）
- Slack Webhook URL（如果需要通知）
- Codecov Token（如果使用代码覆盖率）

---

## 2. 一键安装脚本

### 2.1 主安装脚本

**文件**: `scripts/setup/install_compliance.sh`

````bash
#!/bin/bash
# 一键安装合规引擎和所有工具

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  AI驱动开发工作流 - 安装向导${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 1. 检查前置条件
echo -e "${YELLOW}1/10 检查前置条件...${NC}"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3未安装${NC}"
    echo "请安装Python 3.9+: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js未安装${NC}"
    echo "请安装Node.js 18+: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js $NODE_VERSION${NC}"

# 检查Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git未安装${NC}"
    exit 1
fi

GIT_VERSION=$(git --version | awk '{print $3}')
echo -e "${GREEN}✅ Git $GIT_VERSION${NC}"

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️ Docker未安装（可选）${NC}"
else
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
    echo -e "${GREEN}✅ Docker $DOCKER_VERSION${NC}"
fi

# 2. 创建目录结构
echo ""
echo -e "${YELLOW}2/10 创建目录结构...${NC}"

mkdir -p .compliance/rules
mkdir -p .compliance/checkers
mkdir -p .taskmaster/tasks
mkdir -p docs/00_product/requirements
mkdir -p docs/01_guideline/api-contracts
mkdir -p backend/tests/{unit,integration,regression,fixtures}
mkdir -p e2e/tests/{smoke,regression,performance}
mkdir -p scripts/task-master
mkdir -p scripts/compliance
mkdir -p scripts/notifications
mkdir -p .githooks

echo -e "${GREEN}✅ 目录结构创建完成${NC}"

# 3. 安装Python依赖
echo ""
echo -e "${YELLOW}3/10 安装Python依赖...${NC}"

pip install pyyaml requests pytest pytest-cov black -q

echo -e "${GREEN}✅ Python依赖安装完成${NC}"

# 4. 安装Node.js全局工具
echo ""
echo -e "${YELLOW}4/10 安装Node.js全局工具...${NC}"

# 检查Task-Master
if ! command -v task-master &> /dev/null; then
    echo "安装Task-Master..."
    npm install -g claude-task-master --silent
    echo -e "${GREEN}✅ Task-Master安装完成${NC}"
else
    echo -e "${GREEN}✅ Task-Master已安装${NC}"
fi

# 5. 复制配置文件
echo ""
echo -e "${YELLOW}5/10 复制配置文件...${NC}"

# 复制合规引擎配置
if [ ! -f ".compliance/config.yaml" ]; then
    cat > .compliance/config.yaml << 'EOF'
# 合规引擎全局配置
engine:
  version: "1.0"
  strict_mode: true
  enable_audit_log: true
  audit_log_path: .compliance/audit.log

rules:
  enabled: true
  auto_discover: true
  rules_dir: .compliance/rules

checkers:
  enabled: true
  auto_discover: true
  checkers_dir: .compliance/checkers

bypass:
  allow_bypass: false
  bypass_require_reason: true
  bypass_require_approval: true

notifications:
  enabled: true
  slack_webhook: ${SLACK_WEBHOOK_URL}
  notify_on_failure: true
  notify_on_bypass_attempt: true

file_rules_mapping:
  - pattern: "docs/00_product/requirements/**/*.md"
    rules: [prd]
  - pattern: "backend/tests/**/*.py"
    rules: [test, code]
  - pattern: "e2e/tests/**/*.ts"
    rules: [test, code]
  - pattern: "backend/apps/**/*.py"
    rules: [code]
  - pattern: "frontend/src/**/*.{vue,ts}"
    rules: [code]

exclude_paths:
  - "node_modules/**"
  - "venv/**"
  - ".git/**"
  - "*.pyc"
  - "__pycache__/**"
EOF
    echo -e "${GREEN}✅ .compliance/config.yaml${NC}"
fi

# 复制PRD规则
if [ ! -f ".compliance/rules/prd.yaml" ]; then
    cat > .compliance/rules/prd.yaml << 'EOF'
name: prd
description: PRD文件合规规则
version: "1.0"

required_metadata_fields:
  - req_id
  - title
  - status
  - test_files
  - implementation_files
  - api_contract
  - deletable

metadata_validation:
  req_id:
    pattern: "^REQ-\\d{4}-\\d{3}-.+$"
  status:
    enum: [draft, refined, reviewed, approved, implementing, completed, archived]
EOF
    echo -e "${GREEN}✅ .compliance/rules/prd.yaml${NC}"
fi

# 6. 安装Git Hooks
echo ""
echo -e "${YELLOW}6/10 安装Git Hooks...${NC}"

# 配置Git Hooks目录
git config core.hooksPath .githooks

# Pre-commit Hook
cat > .githooks/pre-commit << 'EOF'
#!/bin/bash
set -e

echo "🔍 执行Pre-commit检查..."

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

# 运行合规引擎
python .compliance/engine.py $STAGED_FILES

echo "✅ Pre-commit检查通过"
exit 0
EOF

chmod +x .githooks/pre-commit
echo -e "${GREEN}✅ Pre-commit Hook${NC}"

# Commit-msg Hook
cat > .githooks/commit-msg << 'EOF'
#!/bin/bash
COMMIT_MSG=$(cat "$1")

if echo "$COMMIT_MSG" | grep -qE '^\[(REQ-[0-9]{4}-[0-9]{3}-[a-z0-9-]+|BUGFIX|REFACTOR)\]'; then
    exit 0
else
    echo "❌ 提交消息格式错误"
    echo "正确格式: [REQ-ID] Task-X 描述"
    exit 1
fi
EOF

chmod +x .githooks/commit-msg
echo -e "${GREEN}✅ Commit-msg Hook${NC}"

# Post-commit Hook
cat > .githooks/post-commit << 'EOF'
#!/bin/bash
COMMIT_SHA=$(git rev-parse HEAD)
echo "📝 记录提交到审计日志: $COMMIT_SHA"
exit 0
EOF

chmod +x .githooks/post-commit
echo -e "${GREEN}✅ Post-commit Hook${NC}"

# 7. 配置Git Commit模板
echo ""
echo -e "${YELLOW}7/10 配置Git Commit模板...${NC}"

cat > .gitmessage << 'EOF'
# [REQ-ID] Task-X Subtask-Y <简短描述>
#
# 详细描述:
# - 做了什么
# - 为什么这样做
#
# 示例:
# [REQ-2025-001-user-login] Task-1 Subtask-2 实现登录API
EOF

git config commit.template .gitmessage
echo -e "${GREEN}✅ Git Commit模板配置完成${NC}"

# 8. 创建示例PRD
echo ""
echo -e "${YELLOW}8/10 创建示例PRD...${NC}"

EXAMPLE_PRD_DIR="docs/00_product/requirements/REQ-2025-EXAMPLE-demo"
mkdir -p "$EXAMPLE_PRD_DIR"

cat > "$EXAMPLE_PRD_DIR/REQ-2025-EXAMPLE-demo.md" << 'EOF'
---
req_id: REQ-2025-EXAMPLE-demo
title: 示例需求
version: "1.0"
status: draft
priority: low
type: feature
created_at: 2025-10-24T10:00:00Z
updated_at: 2025-10-24T10:00:00Z
author: system
task_master_task: .taskmaster/tasks/REQ-2025-EXAMPLE-demo/tasks.json
test_files:
  - backend/tests/unit/test_example.py
implementation_files:
  - backend/apps/example/views.py
api_contract: docs/01_guideline/api-contracts/REQ-2025-EXAMPLE/api.yaml
deletable: true
delete_requires_review: false
---

# REQ-2025-EXAMPLE: 示例需求

这是一个示例PRD，用于演示工作流。

## 功能概述
演示如何编写PRD。

## 用户故事
作为一个用户，我希望能够看到示例功能。
EOF

echo -e "${GREEN}✅ 示例PRD创建完成${NC}"

# 9. 创建README
echo ""
echo -e "${YELLOW}9/10 创建README...${NC}"

cat > INSTALL_README.md << 'EOF'
# AI驱动开发工作流 - 安装完成

## ✅ 安装成功

恭喜！AI驱动开发工作流已成功安装。

## 📚 快速开始

1. 查看架构文档:
   ```bash
   cat docs/architecture/AI-WORKFLOW-V4-README.md
````

2. 查看示例PRD:

   ```bash
   cat docs/00_product/requirements/REQ-2025-EXAMPLE-demo/REQ-2025-EXAMPLE-demo.md
   ```

3. 测试Pre-commit Hook:
   ```bash
   echo "test" > test.txt
   git add test.txt
   git commit -m "[TEST] 测试提交"  # 会失败（格式错误）
   git commit -m "[REQ-2025-EXAMPLE-demo] Task-1 测试提交"  # 会成功
   ```

## 🔧 验证安装

运行验证脚本:

```bash
bash scripts/setup/verify_installation.sh
```

## 📖 下一步

1. 阅读完整文档: `docs/architecture/AI-WORKFLOW-V4-README.md`
2. 创建第一个PRD
3. 使用Task-Master生成任务
4. 开始开发

## 🆘 遇到问题?

查看故障排查指南: `docs/architecture/AI-WORKFLOW-V4-PART6-IMPL.md#6-故障排查指南`
EOF

echo -e "${GREEN}✅ README创建完成${NC}"

# 10. 完成

echo ""
echo -e "${YELLOW}10/10 完成安装...${NC}"

# 创建审计日志文件

touch .compliance/audit.log

# 验证安装

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}🎉 安装完成！${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "${GREEN}✅ 合规引擎已安装${NC}"
echo -e "${GREEN}✅ Git Hooks已配置${NC}"
echo -e "${GREEN}✅ 目录结构已创建${NC}"
echo -e "${GREEN}✅ 示例文件已创建${NC}"
echo ""
echo -e "${YELLOW}📖 请阅读 INSTALL_README.md 开始使用${NC}"
echo ""

# 运行验证脚本（如果存在）

if [ -f "scripts/setup/verify_installation.sh" ]; then
bash scripts/setup/verify_installation.sh
fi

````

### 2.2 验证安装脚本

**文件**: `scripts/setup/verify_installation.sh`

```bash
#!/bin/bash
# 验证安装是否成功

echo "🔍 验证安装..."
echo ""

FAILED=0

# 1. 检查目录
echo "1. 检查目录结构..."
REQUIRED_DIRS=(
    ".compliance"
    ".compliance/rules"
    ".compliance/checkers"
    ".taskmaster"
    ".githooks"
    "docs/00_product/requirements"
    "backend/tests/unit"
    "backend/tests/integration"
    "e2e/tests"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir"
    else
        echo "  ❌ $dir (缺失)"
        FAILED=1
    fi
done

# 2. 检查配置文件
echo ""
echo "2. 检查配置文件..."
REQUIRED_FILES=(
    ".compliance/config.yaml"
    ".compliance/rules/prd.yaml"
    ".githooks/pre-commit"
    ".githooks/commit-msg"
    ".gitmessage"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (缺失)"
        FAILED=1
    fi
done

# 3. 检查Git配置
echo ""
echo "3. 检查Git配置..."

HOOKS_PATH=$(git config core.hooksPath)
if [ "$HOOKS_PATH" == ".githooks" ]; then
    echo "  ✅ Git Hooks路径已配置"
else
    echo "  ❌ Git Hooks路径未配置"
    FAILED=1
fi

COMMIT_TEMPLATE=$(git config commit.template)
if [ "$COMMIT_TEMPLATE" == ".gitmessage" ]; then
    echo "  ✅ Git Commit模板已配置"
else
    echo "  ❌ Git Commit模板未配置"
    FAILED=1
fi

# 4. 检查工具
echo ""
echo "4. 检查工具..."

if command -v task-master &> /dev/null; then
    echo "  ✅ Task-Master已安装"
else
    echo "  ⚠️ Task-Master未安装（可选）"
fi

if command -v pytest &> /dev/null; then
    echo "  ✅ Pytest已安装"
else
    echo "  ❌ Pytest未安装"
    FAILED=1
fi

# 5. 测试合规引擎
echo ""
echo "5. 测试合规引擎..."

if [ -f ".compliance/engine.py" ]; then
    # 创建测试文件
    echo "test" > /tmp/test_compliance.txt

    if python .compliance/engine.py /tmp/test_compliance.txt &> /dev/null; then
        echo "  ✅ 合规引擎运行正常"
    else
        echo "  ❌ 合规引擎运行异常"
        FAILED=1
    fi

    rm /tmp/test_compliance.txt
else
    echo "  ❌ 合规引擎未安装"
    FAILED=1
fi

# 总结
echo ""
echo "======================================"
if [ $FAILED -eq 0 ]; then
    echo "✅ 验证通过！安装成功"
    exit 0
else
    echo "❌ 验证失败，请检查上述错误"
    exit 1
fi
````

---

## 3. 完整配置文件

### 3.1 合规引擎配置

已在安装脚本中包含，详见 [2.1节](#21-主安装脚本)

### 3.2 Pytest配置

**文件**: `backend/pytest.ini`

```ini
[pytest]
# Pytest配置文件

# 测试路径
testpaths = tests

# Python路径
pythonpath = .

# 输出选项
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=apps
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80

# 标记
markers =
    unit: 单元测试
    integration: 集成测试
    regression: 回归测试
    slow: 慢速测试

# Django设置
DJANGO_SETTINGS_MODULE = bravo.settings.test

# 警告过滤
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### 3.3 Playwright配置

**文件**: `e2e/playwright.config.ts`

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",

  // 超时设置
  timeout: 30 * 1000,
  expect: {
    timeout: 5000,
  },

  // 重试
  retries: process.env.CI ? 2 : 0,

  // 并行
  workers: process.env.CI ? 1 : undefined,

  // 报告
  reporter: [
    ["html", { outputFolder: "playwright-report" }],
    ["junit", { outputFile: "test-results.xml" }],
    ["json", { outputFile: "test-results.json" }],
  ],

  // 全局设置
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },

  // 浏览器项目
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
  ],

  // Web服务器
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
  },
});
```

### 3.4 Docker Compose配置

**文件**: `docker-compose.yml` (已存在，仅展示关键部分)

```yaml
version: "3.8"

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: bravo
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - mysql
      - redis
    environment:
      DATABASE_URL: mysql://root:${MYSQL_ROOT_PASSWORD}@mysql:3306/bravo
      REDIS_URL: redis://redis:6379/0

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend:/app
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  mysql_data:
```

---

## 4. Task-Master适配层完整实现

**文件**: `scripts/task-master/adapter.py`

（完整代码已在PART2中提供，这里提供简化的核心逻辑）

```python
#!/usr/bin/env python3
"""
Task-Master适配层完整实现
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List


class TaskMasterAdapter:
    def __init__(self, req_id: str):
        self.req_id = req_id
        self.root_dir = Path.cwd()
        self.taskmaster_dir = self.root_dir / '.taskmaster' / 'tasks' / req_id
        self.tasks_json_path = self.taskmaster_dir / 'tasks.json'

    def convert(self):
        """主入口"""
        print(f"🚀 开始转换 {self.req_id}")

        # 1. 读取原始tasks.json
        with open(self.tasks_json_path, 'r', encoding='utf-8') as f:
            original_tasks = json.load(f)

        # 2. 生成Task-0
        task_0 = self._generate_task_0()

        # 3. 为每个任务生成子任务
        enhanced_tasks = [task_0]
        for task in original_tasks.get('tasks', []):
            enhanced_task = self._enhance_task(task)
            enhanced_tasks.append(enhanced_task)

        # 4. 更新tasks.json
        enhanced_json = {
            'req_id': self.req_id,
            'tasks': enhanced_tasks
        }

        with open(self.tasks_json_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_json, f, indent=2, ensure_ascii=False)

        # 5. 创建目录和Markdown文件
        for task in enhanced_tasks:
            self._create_task_directory(task)
            self._create_task_md(task)
            for subtask in task['subtasks']:
                self._create_subtask_md(task, subtask)

        print(f"🎉 转换完成！")

    def _generate_task_0(self) -> Dict:
        """生成Task-0自检任务"""
        return {
            'id': 0,
            'title': 'Self-check and validation',
            'description': 'Validate PRD and setup',
            'status': 'pending',
            'directory': 'task-0-self-check',
            'subtasks': [
                {'id': 1, 'title': 'Validate PRD metadata', 'status': 'pending', 'file': 'subtask-1-validate-prd.md'},
                {'id': 2, 'title': 'Check test directories', 'status': 'pending', 'file': 'subtask-2-check-dirs.md'},
                {'id': 3, 'title': 'Verify API contract', 'status': 'pending', 'file': 'subtask-3-verify-api.md'},
            ]
        }

    def _enhance_task(self, task: Dict) -> Dict:
        """增强任务（读取Task-Master生成的子任务并添加文件关联）"""
        # Task-Master已经通过expand命令生成了subtasks
        # 适配层只需要：
        # 1. 读取现有的subtasks
        # 2. 为每个subtask关联测试文件和代码文件
        # 3. 添加PRD章节链接

        subtasks = task.get('subtasks', [])
        enhanced_subtasks = []

        for subtask in subtasks:
            # 关联测试文件和代码文件
            enhanced_subtask = self._link_files_to_subtask(subtask, task)
            # 关联PRD章节
            enhanced_subtask = self._link_prd_section(enhanced_subtask, task)
            enhanced_subtasks.append(enhanced_subtask)

        return {
            'id': task['id'] + 1,  # 重新编号
            'title': task['title'],
            'description': task.get('description', ''),
            'status': 'pending',
            'directory': f"task-{task['id'] + 1}-{self._slugify(task['title'])}",
            'subtasks': enhanced_subtasks
        }

    def _link_files_to_subtask(self, subtask: Dict, parent_task: Dict) -> Dict:
        """为子任务关联测试文件和代码文件"""
        title_lower = subtask['title'].lower()
        app_name = self._guess_app_name(subtask, parent_task)

        # 初始化文件列表
        subtask['test_files'] = []
        subtask['implementation_files'] = []

        # 根据子任务标题关联文件
        if 'model' in title_lower or '数据库' in title_lower:
            subtask['implementation_files'].append(f'backend/apps/{app_name}/models.py')
            subtask['test_files'].append(f'backend/tests/unit/test_{app_name}_model.py')

        elif 'view' in title_lower or 'endpoint' in title_lower or 'api' in title_lower:
            subtask['implementation_files'].append(f'backend/apps/{app_name}/views.py')
            subtask['test_files'].append(f'backend/tests/unit/test_{app_name}_views.py')

        elif 'serializer' in title_lower:
            subtask['implementation_files'].append(f'backend/apps/{app_name}/serializers.py')
            subtask['test_files'].append(f'backend/tests/unit/test_{app_name}_serializers.py')

        elif 'component' in title_lower or 'vue' in title_lower:
            feature = self._extract_feature_name(subtask['title'])
            subtask['implementation_files'].append(f'frontend/src/components/{feature}.vue')

        elif 'e2e' in title_lower or 'test' in title_lower:
            feature = self._extract_feature_name(subtask['title'])
            subtask['test_files'].append(f'e2e/tests/test-{feature}.spec.ts')

        # 添加文件名字段用于生成markdown
        subtask['file'] = f"subtask-{subtask['id']}-{self._slugify(subtask['title'])}.md"

        return subtask

    def _link_prd_section(self, subtask: Dict, parent_task: Dict) -> Dict:
        """关联PRD章节（简化实现）"""
        # 实际实现中，可以解析PRD文件，匹配关键词
        # 这里简化为添加一个prd_section字段
        subtask['prd_section'] = f"#{self._slugify(parent_task['title'])}"
        return subtask

    def _guess_app_name(self, subtask: Dict, parent_task: Dict) -> str:
        """推断Django App名称"""
        text = f"{subtask['title']} {parent_task['title']}".lower()

        if any(kw in text for kw in ['user', 'auth', 'login']):
            return 'users'
        elif 'product' in text:
            return 'products'
        elif 'order' in text:
            return 'orders'
        else:
            return 'core'

    def _extract_feature_name(self, title: str) -> str:
        """从标题提取功能名"""
        # 简化实现：取第一个单词
        return self._slugify(title.split()[0]) if title else 'feature'

    def _create_task_directory(self, task: Dict):
        """创建任务目录"""
        task_dir = self.taskmaster_dir / task['directory']
        task_dir.mkdir(parents=True, exist_ok=True)

    def _create_task_md(self, task: Dict):
        """创建task.md"""
        task_dir = self.taskmaster_dir / task['directory']
        content = f"# {task['title']}\n\n{task['description']}"
        (task_dir / 'task.md').write_text(content, encoding='utf-8')

    def _create_subtask_md(self, task: Dict, subtask: Dict):
        """创建subtask.md"""
        task_dir = self.taskmaster_dir / task['directory']
        content = f"# {subtask['title']}\n\nStatus: {subtask['status']}"
        (task_dir / subtask['file']).write_text(content, encoding='utf-8')

    def _slugify(self, text: str) -> str:
        """转换为slug"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')


def main():
    if len(sys.argv) != 2:
        print("用法: python adapter.py <REQ-ID>")
        sys.exit(1)

    req_id = sys.argv[1]
    adapter = TaskMasterAdapter(req_id)
    adapter.convert()


if __name__ == '__main__':
    main()
```

---

## 5. 完整开发流程演示

### 5.1 创建新需求

```bash
# 1. 创建PRD目录
REQ_ID="REQ-2025-001-user-login"
mkdir -p "docs/00_product/requirements/$REQ_ID"

# 2. 创建PRD文件
cat > "docs/00_product/requirements/$REQ_ID/$REQ_ID.md" << 'EOF'
---
req_id: REQ-2025-001-user-login
title: 用户登录功能
version: "1.0"
status: draft
priority: high
type: feature
created_at: 2025-10-24T10:00:00Z
updated_at: 2025-10-24T10:00:00Z
author: human
task_master_task: .taskmaster/tasks/REQ-2025-001-user-login/tasks.json
test_files:
  - backend/tests/unit/test_user_login.py
  - backend/tests/integration/test_user_authentication.py
  - e2e/tests/test-user-login.spec.ts
implementation_files:
  - backend/apps/users/models.py
  - backend/apps/users/views.py
  - backend/apps/users/serializers.py
  - frontend/src/views/LoginView.vue
  - frontend/src/api/auth.ts
api_contract: docs/01_guideline/api-contracts/REQ-2025-001/api.yaml
deletable: false
delete_requires_review: true
---

# REQ-2025-001: 用户登录功能

## 功能概述
实现用户通过邮箱和密码进行登录的功能。

## 用户故事
作为一个用户，我希望能够使用邮箱和密码登录系统。

## 验收标准
- 用户可以输入邮箱和密码
- 系统验证并返回JWT Token
- 支持"记住我"功能
EOF

echo "✅ PRD创建完成"
```

### 5.2 使用Cursor精化PRD

```bash
# 在Cursor中打开PRD文件
cursor "docs/00_product/requirements/$REQ_ID/$REQ_ID.md"

# Cursor会补充:
# - 数据库设计
# - Redis缓存策略
# - API接口定义
# - 测试用例
# - 前端UI/UX细节
```

### 5.3 使用Task-Master生成任务

```bash
# 1. 使用Task-Master解析PRD生成主任务
cd .taskmaster/tasks
task-master parse-prd --input="../../docs/00_product/requirements/$REQ_ID/$REQ_ID.md"

# 输出: REQ-2025-001-user-login/tasks.json (主任务列表)

# 2. 分析任务复杂度
task-master analyze-complexity --threshold=5

# 输出: 复杂度报告，推荐需要展开的任务

# 3. AI自动展开任务为子任务
task-master expand --all --research

# 输出: tasks.json 现在包含AI生成的subtasks

# 4. 使用适配层转换为项目目录结构
python ../../scripts/task-master/adapter.py $REQ_ID

# 适配层的工作：
# - 读取Task-Master生成的subtasks
# - 添加Task-0自检任务
# - 为每个subtask关联测试文件和代码文件
# - 生成三层目录结构和Markdown文件

# 最终输出:
# .taskmaster/tasks/REQ-2025-001-user-login/
# ├── tasks.json (增强版：含文件关联)
# ├── task-0-self-check/
# │   ├── task.md
# │   ├── subtask-1-validate-prd.md
# │   └── ...
# ├── task-1-implement-backend-api/
# │   └── ...
# └── task-2-implement-frontend-ui/
#     └── ...

echo "✅ 任务生成完成"
```

### 5.4 执行Task-0自检

```bash
# 1. 验证PRD元数据
python scripts/compliance/validate_prd.py $REQ_ID

# 2. 检查测试目录
python scripts/compliance/check_test_directories.py

# 3. 验证API契约
python scripts/compliance/validate_api_contract.py $REQ_ID

# 更新任务状态
python scripts/task-master/sync_status.py \
  --req-id $REQ_ID \
  --task-id task-0 \
  --subtask-id subtask-1 \
  --status completed

echo "✅ Task-0自检完成"
```

### 5.5 编写测试（TDD红色阶段）

```bash
# 1. 创建测试文件
cat > backend/tests/unit/test_user_login.py << 'EOF'
def test_login_success():
    result = login_user("user@example.com", "password123")
    assert result['success'] == True
    assert 'token' in result
EOF

# 2. 运行测试（应该失败）
pytest backend/tests/unit/test_user_login.py::test_login_success

# 预期输出:
# FAILED - NameError: name 'login_user' is not defined

echo "✅ 测试编写完成（红色阶段）"
```

### 5.6 实现功能代码（TDD绿色阶段）

```bash
# 1. 创建功能代码
mkdir -p backend/apps/users
cat > backend/apps/users/services.py << 'EOF'
def login_user(email, password):
    # 最小实现，使测试通过
    if email == "user@example.com" and password == "password123":
        return {'success': True, 'token': 'fake-token'}
    return {'success': False}
EOF

# 2. 运行测试（应该通过）
pytest backend/tests/unit/test_user_login.py::test_login_success

# 预期输出:
# PASSED

echo "✅ 功能实现完成（绿色阶段）"
```

### 5.7 提交代码

```bash
# 1. 添加文件
git add .

# 2. 提交（Pre-commit自动检查）
git commit -m "[REQ-2025-001-user-login] Task-1 Subtask-4 实现登录功能"

# Pre-commit执行:
# ✅ 合规引擎检查通过
# ✅ PRD关联检查通过
# ✅ 测试文件检查通过
# ✅ 功能删除检查通过
# ✅ 测试通过
# ✅ 代码格式检查通过

# 3. 推送到远程
git push origin feature/user-login

echo "✅ 代码提交完成"
```

### 5.8 CI/CD自动验证

```bash
# GitHub Actions自动执行:
# 1. 合规引擎检查
# 2. PRD关联检查
# 3. 测试文件检查
# 4. 运行所有测试
# 5. 代码覆盖率检查
# 6. 构建Docker镜像
# 7. 部署到Dev环境

# 查看CI状态
gh run list --branch feature/user-login

echo "✅ CI/CD验证完成"
```

---

## 6. 故障排查指南

### 6.1 Pre-commit Hook不执行

**问题**: 提交时Pre-commit Hook没有执行

**原因**:

1. Git Hooks路径未配置
2. Hook文件没有执行权限

**解决方案**:

```bash
# 1. 检查Git Hooks路径
git config core.hooksPath
# 应该输出: .githooks

# 如果未配置，执行:
git config core.hooksPath .githooks

# 2. 检查Hook文件权限
ls -l .githooks/pre-commit
# 应该有x权限

# 如果没有，执行:
chmod +x .githooks/pre-commit
chmod +x .githooks/commit-msg
chmod +x .githooks/post-commit

# 3. 验证
echo "test" > test.txt
git add test.txt
git commit -m "test"  # 应该触发Pre-commit
```

### 6.2 合规引擎检查失败

**问题**: `python .compliance/engine.py` 运行失败

**原因**:

1. Python依赖未安装
2. 配置文件格式错误
3. 检查器模块缺失

**解决方案**:

```bash
# 1. 安装依赖
pip install pyyaml requests

# 2. 验证配置文件
python -c "import yaml; yaml.safe_load(open('.compliance/config.yaml'))"

# 3. 测试引擎
python .compliance/engine.py --help

# 4. 查看日志
cat .compliance/audit.log
```

### 6.3 Task-Master生成任务失败

**问题**: `task-master -r <prd>` 失败

**原因**:

1. Task-Master未安装
2. PRD格式不符合Task-Master要求

**解决方案**:

```bash
# 1. 检查Task-Master
task-master --version

# 如果未安装:
npm install -g claude-task-master

# 2. 验证PRD格式
# Task-Master需要清晰的章节结构

# 3. 手动测试
task-master -r "docs/00_product/requirements/REQ-2025-EXAMPLE-demo/REQ-2025-EXAMPLE-demo.md"
```

### 6.4 测试运行失败

**问题**: Pytest或Playwright测试失败

**原因**:

1. 测试环境未启动（数据库、Redis）
2. 测试依赖未安装
3. 测试文件路径错误

**解决方案**:

```bash
# 后端测试
# 1. 启动Docker服务
docker-compose up -d mysql redis

# 2. 运行测试
pytest backend/tests/unit/ -v

# E2E测试
# 1. 安装Playwright浏览器
cd e2e
npx playwright install

# 2. 启动前后端服务
docker-compose up -d

# 3. 运行测试
npx playwright test
```

### 6.5 CI/CD失败

**问题**: GitHub Actions工作流失败

**原因**:

1. 本地检查通过但CI失败
2. 环境差异（Python/Node版本）
3. Secrets未配置

**解决方案**:

```bash
# 1. 本地模拟CI环境
# 使用act工具
act -j compliance

# 2. 检查环境变量
# 在GitHub仓库设置中配置Secrets:
# - SLACK_WEBHOOK_URL
# - CODECOV_TOKEN

# 3. 查看CI日志
gh run view --log

# 4. 重新触发CI
gh run rerun <run-id>
```

---

## 7. 常见问题FAQ

### Q1: 如何绕过Pre-commit检查（紧急情况）?

**A**: 不建议绕过，但紧急情况下:

```bash
# 方法1: 使用--no-verify（会被Git Wrapper拦截）
git commit --no-verify -m "紧急修复"  # ❌ 会失败

# 方法2: 临时禁用Git Hooks
git config core.hooksPath ""
git commit -m "紧急修复"
git config core.hooksPath ".githooks"  # 恢复

# ⚠️ 注意: CI/CD会重新检查，无法绕过
```

### Q2: 如何修改已有代码文件但PRD中没有记录?

**A**: 先更新PRD元数据

```bash
# 1. 在PRD的implementation_files中添加该文件
vim docs/00_product/requirements/REQ-XXX/REQ-XXX.md

# 2. 然后再提交代码
git add <file>
git commit -m "[REQ-XXX] Task-X 修改<file>"
```

### Q3: 如何处理多个PRD对应一个代码文件?

**A**: 每个PRD都在元数据中列出该文件

```yaml
# REQ-2025-001.md
implementation_files:
  - backend/apps/users/views.py  # 共享文件

# REQ-2025-002.md
implementation_files:
  - backend/apps/users/views.py  # 共享文件
```

### Q4: 如何删除PRD定义的功能?

**A**: 先修改PRD，再删除代码

```bash
# 1. 修改PRD，移除该功能
# 2. 提交PRD修改
git add docs/00_product/requirements/REQ-XXX/REQ-XXX.md
git commit -m "[REQ-XXX] 移除功能X"

# 3. 删除代码
git rm backend/apps/xxx/views.py
git commit -m "[REQ-XXX] Task-X 删除功能X代码"
```

### Q5: Task-Master生成的任务不符合预期怎么办?

**A**: 手动修改tasks.json

```bash
# 1. 编辑tasks.json
vim .taskmaster/tasks/REQ-XXX/tasks.json

# 2. 重新运行适配层
python scripts/task-master/adapter.py REQ-XXX
```

### Q6: 如何在多台电脑上协作?

**A**: Git同步.taskmaster目录

```bash
# 电脑A: 完成Task-1 Subtask-1
git add .taskmaster/tasks/REQ-XXX/
git commit -m "[REQ-XXX] Task-1 Subtask-1 完成"
git push

# 电脑B: 拉取最新代码
git pull
# 继续Task-1 Subtask-2
```

### Q7: 如何查看审计日志?

**A**: 查看`.compliance/audit.log`

```bash
# 查看最近10条
tail -10 .compliance/audit.log

# 搜索特定提交
grep "abc123" .compliance/audit.log

# 格式化查看（使用jq）
cat .compliance/audit.log | jq .
```

---

## 8. 最佳实践

### 8.1 PRD编写

1. **结构清晰**: 使用统一的章节结构
2. **细节完整**: 包含数据库设计、API接口、测试用例
3. **可测试**: 验收标准明确、可量化
4. **元数据完整**: 所有必填字段都填写

### 8.2 任务管理

1. **Task-0先行**: 始终先完成自检任务
2. **子任务独立**: 每个子任务独立可验证
3. **状态及时更新**: 完成子任务立即同步状态
4. **文档记录**: 在subtask.md中记录问题和解决方案

### 8.3 测试驱动

1. **测试先行**: 先写测试，再写代码
2. **覆盖全面**: 正常、异常、边界都要测试
3. **测试独立**: 测试间不相互依赖
4. **测试快速**: 单元测试应<100ms

### 8.4 提交规范

1. **提交消息格式**: 严格遵循`[REQ-ID] Task-X Subtask-Y 描述`
2. **原子提交**: 每次提交一个逻辑修改
3. **频繁提交**: 完成子任务就提交
4. **描述清晰**: 说明做了什么、为什么

### 8.5 代码审查

1. **自我审查**: 提交前先自己审查
2. **检查追溯链**: 确保PRD、测试、代码关联
3. **运行测试**: 本地运行所有测试
4. **格式检查**: 确保代码格式符合规范

---

## 小结

本章节提供了完整的实施落地手册，包括：

1. **前置条件**: 系统要求和可选工具
2. **一键安装脚本**: 自动安装所有组件和配置
3. **完整配置文件**: Pytest、Playwright、Docker Compose等
4. **Task-Master适配层**: 完整实现代码
5. **完整开发流程**: 从PRD到部署的完整演示
6. **故障排查指南**: 常见问题的解决方案
7. **FAQ**: 常见问题解答
8. **最佳实践**: PRD编写、任务管理、TDD、提交规范

**下一步**: 阅读 [APPENDIX-QA映射](./AI-WORKFLOW-V4-APPENDIX-QA.md) 查看26个核心问题的详细解答。

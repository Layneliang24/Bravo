#!/usr/bin/env bash
# 在宿主机 python 被拦截（如 system-interceptors）或需在容器内运行时，用 Docker 执行 validate-commit
# 优先使用 validator 容器，失败时回退到宿主机 python（CI 或未装 Docker 时）
set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if command -v docker-compose &>/dev/null && docker-compose run --rm -T validator python3 scripts/code_change_tracker.py --validate-commit 2>/dev/null; then
    exit 0
fi
exec python scripts/code_change_tracker.py --validate-commit

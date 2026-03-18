#!/usr/bin/env bash
# 在宿主机 python 被拦截或需在容器内运行时，用 Docker 执行项目内 Python 脚本
# 用法: run_python_in_project.sh <script路径> [参数...]
# 优先使用 validator 容器，失败时回退到宿主机 python
set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
if [ $# -eq 0 ]; then
  echo "Usage: $0 <script_path> [args...]" >&2
  exit 1
fi
if command -v docker-compose &>/dev/null && docker-compose run --rm -T validator python3 "$@" 2>/dev/null; then
  exit 0
fi
exec python "$@"

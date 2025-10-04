# 项目命令管理模板

.PHONY: help install dev build test clean deploy

# 默认目标
help: ## 显示帮助信息
	@echo "可用的命令："
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# 安装依赖
install: ## 安装所有依赖
	cd backend && pip install -r requirements/local.txt
	npm ci --prefer-offline --no-audit

# 开发环境
dev: ## 启动开发环境
	docker-compose up -d postgres redis
	cd backend && python manage.py migrate
	cd backend && python manage.py runserver &
	cd frontend && npm run dev

# 构建项目
build: ## 构建项目
	cd backend && python manage.py collectstatic --noinput
	cd frontend && npm run build

# 运行测试
test: ## 运行所有测试
	cd backend && pytest
	cd frontend && npm run test
	cd e2e && npm run test

# 统一测试入口 - 业内标准做法
test-all: ## 一键运行全量测试（单元+回归+E2E+性能+质量）
	@chmod +x test_all.sh
	@./test_all.sh

test-regression: ## 运行回归测试
	@echo "Running regression tests..."
	node tests/regression/run-regression.js

test-regression-api: ## 运行API回归测试
	@echo "Running API regression tests..."
	node tests/regression/run-regression.js --api-only

test-regression-ui: ## 运行UI回归测试
	@echo "Running UI regression tests..."
	node tests/regression/run-regression.js --ui-only

test-regression-db: ## 运行数据库回归测试
	@echo "Running database regression tests..."
	node tests/regression/run-regression.js --db-only

test-regression-update: ## 更新回归测试基线
	@echo "Updating regression test baselines..."
	node tests/regression/run-regression.js --update-snapshots

# 代码质量检查
quality: ## 运行代码质量检查
	cd backend && pylint apps/
	cd backend && black --check .
	cd backend && isort --check-only .
	cd frontend && npm run lint
	cd frontend && npm run type-check

# 覆盖率报告
coverage: ## 生成覆盖率报告
	cd backend && pytest --cov=. --cov-report=html
	cd frontend && npm run test:coverage

# 清理
clean: ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	cd frontend && rm -rf node_modules dist
	cd e2e && rm -rf node_modules

# 部署
deploy: ## 部署到生产环境
	docker-compose -f docker-compose.prod.yml up -d

# 停止服务
stop: ## 停止所有服务
	docker-compose down

# 重启服务
restart: ## 重启所有服务
	docker-compose restart

# 查看日志
logs: ## 查看服务日志
	docker-compose logs -f

# 数据库迁移
migrate: ## 运行数据库迁移
	cd backend && python manage.py migrate

# 创建超级用户
createsuperuser: ## 创建超级用户
	cd backend && python manage.py createsuperuser

# 收集静态文件
collectstatic: ## 收集静态文件
	cd backend && python manage.py collectstatic --noinput

# 清理误放根目录的文件（按类型/用途分类路由）
move-clutter: ## 将根目录误放文件按类型归档至对应目录
	@echo "🔍 扫描根目录违规文件..."
	@files=$$(find . -maxdepth 1 -type f \
		-not -name "Makefile" -not -name "README.md" -not -name "LICENSE" \
		-not -name ".gitignore" -not -name "CODE_OF_CONDUCT.md" \
		-not -name "CONTRIBUTING.md" -not -name "SECURITY.md" \
		-not -name "package.json" -not -name "docker-compose*.yml" \
		-not -name "tsconfig.json" -not -name "pyproject.toml" \
		-not -name "requirements*.txt" \
	); \
	if [ -n "$$files" ]; then \
		echo "📁 发现违规文件，按规则分类移动..."; \
		for f in $$files; do \
			base=$$(basename "$$f"); \
			case "$$base" in \
				product_*|prd_*|roadmap*|*product*.md) dest="docs/00_product" ;; \
				guideline_*|policy_*|process_*|*guideline*.md) dest="docs/01_guideline" ;; \
				*report*.md|*report*.json|coverage*|junit*|lighthouse*) dest="docs/02_test_report" ;; \
				operate_*|ops_*|sre_*|deploy_*|runbook*|*operate*.md) dest="docs/03_operate" ;; \
				guide_*|quickstart_*|howto_*|*usage*.md) dest="docs/03_usage_guide" ;; \
				adr-*.md|architecture*|design*) dest="docs/architecture" ;; \
				test_*.py|*_test.py) dest="tests/system" ;; \
				*.sh|*.bat|*.ps1|*.js) dest="scripts" ;; \
				*.example) dest="docs/usage_configs" ;; \
				*.md|*.txt|*.json) dest="docs/99_misc" ;; \
				*) dest="" ;; \
			esac; \
			if [ -n "$$dest" ]; then \
				mkdir -p "$$dest"; \
				git mv "$$f" "$$dest"/ 2>/dev/null || mv "$$f" "$$dest"/; \
				echo "✅ 移动 $$base -> $$dest/"; \
			fi; \
		done; \
		echo "✨ 分类移动完成"; \
	else \
		echo "✨ 未发现违规文件"; \
	fi

# ========== Cursor AI保护系统 ==========
.PHONY: test test-quick test-check passport passport-force safe-push setup-protection

test:
	@bash scripts/one_click_test.sh

test-quick:
	@bash scripts/one_click_test.sh --quick

test-check:
	@bash scripts/one_click_test.sh --check

passport:
	@python3 scripts/local_test_passport.py --check

passport-force:
	@python3 scripts/local_test_passport.py --force

safe-push:
	@bash scripts/git-guard.sh push origin $$(git branch --show-current)

setup-protection:
	@bash scripts/setup_cursor_protection.sh

cursor-help:
	@echo "🚀 Cursor AI保护系统命令"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  make test        - 运行本地测试并生成推送通行证"
	@echo "  make test-quick  - 快速测试"
	@echo "  make passport    - 检查通行证状态"
	@echo "  make safe-push   - 安全推送"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

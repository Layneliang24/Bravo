# 项目命令管理模板

.PHONY: help install dev build test clean deploy

# 默认目标
help: ## 显示帮助信息
	@echo "可用的命令："
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# 安装依赖
install: ## 安装所有依赖
	cd backend && pip install -r requirements/local.txt
	cd frontend && npm install
	cd e2e && npm install

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

# 清理误放根目录的文件
move-clutter: ## 将误放根目录的文件移动到正确位置
	@echo "🔍 扫描根目录违规文件..."
	@files=$$(find . -maxdepth 1 -type f \( -name "*.md" -o -name "*.txt" -o -name "test_*.py" -o -name "*_test.py" -o -name "*.keep" -o -name "*.example" \) -not -name "Makefile" -not -name "README.md" -not -name "LICENSE" -not -name ".gitignore"); \
	if [ -n "$$files" ]; then \
		echo "📁 发现违规文件，正在移动到 docs/00_product/"; \
		mkdir -p docs/00_product; \
		for file in $$files; do \
			mv "$$file" docs/00_product/; \
			echo "✅ 移动 $$file -> docs/00_product/"; \
		done; \
	else \
		echo "✨ 未发现违规文件"; \
	fi

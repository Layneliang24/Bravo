
    steps:
      - uses: actions/checkout@v4

      # 使用预构建的Docker容器
      - name: Run E2E with Container
        run: |
          echo "🚀 使用容器化E2E测试..."

          # 启动所有服务
          if command -v docker-compose >/dev/null 2>&1; then
            echo "启动Docker服务..."
            # 🎯 最优方案：移除环境变量传递，容器自给自足
            docker compose -f docker-compose.test.yml up --build -d

            echo "等待E2E测试完成..."
            # 🎯 彻底修复：使用直接的容器退出码检测

            # 等待e2e-tests容器完成，获取其退出码
            echo "等待E2E容器完成..."
            docker compose -f docker-compose.test.yml logs -f e2e-tests || true

            # 直接获取容器退出码，不依赖if分支
            E2E_CID=$(docker compose -f docker-compose.test.yml ps -q e2e-tests)
            echo "E2E容器ID: $E2E_CID"

            if [ -n "$E2E_CID" ]; then
              # 等待容器完全停止
              docker wait "$E2E_CID" > /dev/null 2>&1 || true
              E2E_EXIT_CODE=$(docker inspect --format='{{.State.ExitCode}}' "$E2E_CID" 2>/dev/null || echo "1")
            else
              echo "❌ 无法获取E2E容器ID"
              E2E_EXIT_CODE=1
            fi

            echo "E2E测试真实退出码: $E2E_EXIT_CODE"

            echo "📦 收集E2E测试产物..."
            mkdir -p e2e-artifacts || true
            if [ -n "$E2E_CID" ]; then
              docker cp "$E2E_CID:/app/test-results" e2e-artifacts/test-results 2>/dev/null || true
              docker cp "$E2E_CID:/app/playwright-report" e2e-artifacts/playwright-report 2>/dev/null || true
              docker cp "$E2E_CID:/app/e2e-results.xml" e2e-artifacts/e2e-results.xml 2>/dev/null || true
            fi

            echo "清理Docker服务..."
            docker compose -f docker-compose.test.yml down

            exit $E2E_EXIT_CODE
          else
            echo "docker-compose not found, using 'docker compose' instead..."
            # 🎯 最优方案：移除环境变量传递，容器自给自足
            docker compose -f docker-compose.test.yml up --build -d

            echo "等待E2E测试完成..."
            # 🎯 彻底修复：使用直接的容器退出码检测

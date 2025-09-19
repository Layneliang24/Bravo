# FUCKING_CI - 问题修复记录簿

用途：持续记录 CI 问题与修复，避免重复踩坑。每次修复追加一条“记录项”。

## 记录模板

- 北京时间：YYYY-MM-DD HH:mm:ss
- 第几次推送到 feature：N（本周期累计）
- 第几次 PR：N（本周期累计）
- 第几次 dev post merge：N（本周期累计）
- 关联提交/分支/Run 链接：
  - commit: <sha>
  - feature: <branch>
  - runs:
    - <workflow-name> <run-url>
- 原因定位：简述根因
- 证据：日志/代码片段/链接
- 修复方案：明确且可验证的动作
- 预期效果：成功判据（哪些 workflow/job 通过）

---

## 记录项 1

- 北京时间：待填（提交时更新）
- 第几次推送到 feature：1
- 第几次 PR：1
- 第几次 dev post merge：1
- 关联提交/分支/Run 链接：
  - commit: ee85baa
  - feature: feature/fix-e2e-critical-baseurl
  - runs:
    - Dev Branch - Optimized Post-Merge Validation https://github.com/Layneliang24/Bravo/actions/runs/17835618521
    - Dev Branch - Medium Validation https://github.com/Layneliang24/Bravo/actions/runs/17835618528
- 原因定位：
  - e2e-critical 失败源于用例断言将 URL 硬编码为 http://localhost:3001，与容器内 TEST_BASE_URL=http://frontend-test:3000 不一致。
  - Regression 的 API Compatibility 检查依赖后端根路径文案（"Welcome to Bravo API"），与实际返回不一致。
- 证据：
  - 代码证据：`e2e/tests/app.spec.ts` 中正则断言 localhost:3001；`e2e/playwright.config.ts` 使用 TEST_BASE_URL/FRONTEND_URL；`docker-compose.test.yml` 将 TEST_BASE_URL 指向 http://frontend-test:3000。
  - 运行证据：对应 runs 中 e2e-critical 与 regression-tests 失败（链接见上）。
- 修复方案：
  - e2e：将 `app.spec.ts` 中 URL 断言改为基于环境的 BASE_URL 正则匹配，避免硬编码。
  - regression（后续项）：与后端对齐根路径文案或放宽检查为 200/可达；此次记录仅完成 e2e 修复。
- 预期效果：
  - Fast Validation 的 `e2e-critical` job 通过；Medium Validation 保持其他子套件通过，回归契约后续修复再关闭。

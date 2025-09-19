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

- 北京时间：2025-09-19 04:15:59 CST
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

---

## 记录项 2

- 北京时间：2025-09-19 06:02:00 CST
- 第几次推送到 feature：1
- 第几次 PR：1
- 第几次 dev post merge：2
- 关联提交/分支/Run 链接：
  - commit: da6cb7f (dev head)
  - feature: feature/fix-e2e-critical-baseurl (merged)
  - runs:
    - Dev Branch - Optimized Post-Merge Validation https://github.com/Layneliang24/Bravo/actions/runs/17849528297
    - Dev Branch - Medium Validation https://github.com/Layneliang24/Bravo/actions/runs/17849528313
- 原因定位：
  - Fast Validation / e2e-critical 仍失败（需抓取日志确认用例断言/环境差异）。
  - Regression Tests (Light) 仍失败于 API Compatibility Tests（后端根路径文案/契约检查未对齐）。
- 证据：
  - 失败 Job：
    - 50755380809 Fast Validation Pipeline / e2e-critical
    - 50755539157 Validation Summary (fast)
    - 50755576987 Regression Tests (Light) / regression-tests
    - 50755708957 Dev Validation Summary
- 修复方案（下一步）：
  - e2e-critical：继续核对 @critical 用例是否还有隐含 localhost 依赖，必要时将 BASE_URL 注入到所有相关断言；拉取失败日志定位具体用例。
  - Regression：调整 `.github/workflows/test-regression.yml` 对根路径的强校验，或对齐后端根路径文案；优先以“200/可达+关键端点可访问”为准。
- 预期效果：
  - Dev Post-Merge 的 Optimized Validation 与 Medium Validation 均全部成功。

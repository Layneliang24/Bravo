# 新机配置与限制生效说明

本文档说明哪些限制已纳入版本控制、在新电脑上如何配置才能让限制生效，以及哪些不能纳入、需每台机器单独设置。

## 一、已纳入版本控制的内容（clone 即同步）

| 类型                     | 路径                     | 说明                                                                     |
| ------------------------ | ------------------------ | ------------------------------------------------------------------------ |
| Cursor 规则              | `.cursor/rules/**/*.mdc` | AI 行为准则、TDD、追溯链、禁止 --no-verify 等                            |
| Git 钩子定义             | `.husky/*`               | pre-commit、pre-push、commit-msg、post-commit、post-checkout             |
| 保护脚本                 | `scripts-golden/*`       | git-guard、dependency-guard、通行证校验、path-interceptors 等            |
| 系统级拦截器（可选安装） | `system-interceptors/*`  | Windows 下将 python/pip 重定向到 Docker 的 .cmd/.bat，需手动安装后才生效 |

## 二、新机配置步骤（必须）

在**项目根目录**执行一次，使 Git 钩子在本机生效：

```bash
# 1. 克隆仓库
git clone <repo-url>
cd Bravo

# 2. 安装依赖并激活钩子（关键：会执行 npx husky install，把 .husky/* 安装到 .git/hooks/）
npm install
# 或
npm ci
```

完成后：

- **Cursor 规则**：用 Cursor 打开本项目即生效，无需额外步骤。
- **Git 钩子**：`git commit` / `git push` 时会自动执行 pre-commit、pre-push 等，禁止 `--no-verify`、保护分支等限制生效。

## 三、可选配置

### 3.1 系统级命令拦截（仅 Windows，可选）

若希望在本机任意终端中执行 `python`/`pip` 时都被重定向到 Docker（防止宿主机误用），可安装 `system-interceptors`：

1. 用**管理员权限**打开 cmd 或 PowerShell。
2. 进入项目目录并执行：
   ```cmd
   cd <Bravo 项目路径>\system-interceptors
   install.bat
   ```
3. 按提示操作：脚本会把 `python.cmd`、`python3.cmd`、`pip.cmd`、`pip3.cmd` 复制到 `S:\`。
4. 确保 **`S:\` 在系统 PATH 中且优先于真实 Python 所在目录**，拦截才会生效。

恢复原始命令：删除 `S:\python.cmd`、`S:\python3.cmd`、`S:\pip.cmd`、`S:\pip3.cmd`，并保证 PATH 中指向真实 Python 可执行文件。

### 3.2 推送前通行证与敏感操作

- **推送**：推送前需本地测试通行证（如 `./test` + `./safe-push`），详见项目根目录 `scripts/` 及 `scripts-golden/`。
- **强制删除分支**（`git branch -D`）等敏感操作：首次在本机需按提示设置**主密码**，仅本机保存，不进入版本控制。

## 四、不能纳入版本控制、需每台机器单独配置的

| 项目                     | 说明                                                                |
| ------------------------ | ------------------------------------------------------------------- |
| 主密码                   | 加密验证用，不能进仓库，每人/每机自行设置                           |
| `.passport` / 本地通行证 | 已列入 .gitignore，本地生成、本地有效                               |
| `.git/hooks/*`           | 由 `npx husky install` 根据 `.husky/` 生成，不直接提交              |
| PATH / 环境              | Node、Docker、Python、是否使用 system-interceptors 等，依赖本机环境 |

## 五、生效情况速查

| 限制类型                             | 是否随版本控制同步  | 新机自动生效条件                                           |
| ------------------------------------ | ------------------- | ---------------------------------------------------------- |
| Cursor 规则                          | ✅ 是               | 用 Cursor 打开项目即可                                     |
| Git 钩子（pre-commit / pre-push 等） | ✅ 是               | 在项目根执行一次 `npm install` 或 `npm ci`                 |
| system-interceptors                  | ✅ 是（仓库内已有） | 需在本机执行 `system-interceptors/install.bat` 并配置 PATH |
| 主密码 / .passport                   | ❌ 否               | 每台机器按提示单独设置                                     |

---

**参考**：[@git-hooks-architecture.md](./git-hooks-architecture.md)、`scripts-golden/README`（若有）、根目录 `scripts/README.md`。

# Workflow Token 使用修复说明

## 问题描述

在 Actions workflow 运行时出现认证失败：

```
fatal: Authentication failed for 'http://49.234.193.192:3000/course-test/hw1-stu_sit001.git/'
```

## 根本原因

在 "Manual checkout" 步骤中，错误地使用了 `TESTS_TOKEN` 来克隆学生自己的仓库。

### 问题分析

```yaml
# ❌ 错误的实现
- name: Manual checkout (local Gitea)
  env:
    TESTS_TOKEN: ${{ secrets.TESTS_TOKEN }}  # 错误！这是访问 hw1-tests 的 token
  run: |
    if [ -n "$TESTS_TOKEN" ]; then
      REMOTE_URL="http://oauth2:${TESTS_TOKEN}@${HOST}/${REPO}.git"
    fi
```

**为什么会失败？**

- `TESTS_TOKEN` 是为了访问 `hw1-tests` 私有测试仓库而配置的
- 它只有访问 `hw1-tests` 的权限
- 不能用来访问学生自己的仓库 `hw1-stu_xxx`

## 修复方案

### 正确的 Token 使用

| 操作 | 使用的凭据 | 说明 |
|-----|-----------|------|
| Clone 学生自己的仓库 | `${{ github.token }}` | Gitea Actions 自动注入的运行令牌 |
| Clone hw1-tests 私有仓库 | `RUNNER_TESTS_USERNAME` + `RUNNER_TESTS_TOKEN` | 在 act_runner 服务中配置的环境变量，workflow 直接读取 |
| 发布评论到 PR | `${{ github.token }}` | 自动提供的令牌 |

### 触发事件调整

Gitea 在 `pull_request` / `pull_request_target` 事件中仍会屏蔽仓库 Secrets。为保证评分流程稳定，模板统一改为：

```yaml
on:
  push:
    branches: ["main"]
  workflow_dispatch:
```

也就是说：学生 push 即触发自动评分；需要人工重跑时教师可在 Web UI 触发 `workflow_dispatch`。若想做代码审阅，可以单独创建 PR，但评分结果以 push 为准。

### Runner 级凭据注入

由于学生并非仓库所有者，即便在 push 事件中也无法读取仓库 Secrets。最终方案是：**仅在 `act_runner` 服务中配置访问私有测试的凭据**，workflow 不再尝试仓库 Secrets，直接使用 `RUNNER_TESTS_USERNAME` / `RUNNER_TESTS_TOKEN`。

1. 编辑 Runner Service（systemd 示例）：
   ```bash
   sudo systemctl edit act_runner
   ```
   内容：
   ```
   [Service]
   Environment="RUNNER_TESTS_USERNAME=hblu"
   Environment="RUNNER_TESTS_TOKEN=9f38be..."
   ```
2. 重新加载并重启：
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart act_runner
   ```

### 修复代码

```yaml
# ✅ 正确的实现
- name: Manual checkout (local Gitea)
  env:
    GITHUB_TOKEN: ${{ github.token }}  # 内置运行令牌（无需额外配置）
  run: |
    # 使用 GITHUB_TOKEN (由 Gitea Actions 自动提供) 来访问当前仓库
    if [ -n "$GITHUB_TOKEN" ]; then
      REMOTE_URL="http://oauth2:${GITHUB_TOKEN}@${HOST}/${REPO}.git"
    fi
    git -c http.sslVerify=false fetch --depth=1 origin "$REF"
```

## 修改的文件

修复已应用到以下 3 个 workflow 文件：

1. ✅ `hw1-template/.gitea/workflows/grade.yml`
2. ✅ `hw1-template/.gitea/workflows/objective_grade.yml`
3. ✅ `hw1-template/.gitea/workflows/llm_autograde.yml`

## 更新到学生仓库

### 方法 1: 使用批量更新脚本（推荐）

```bash
python3 scripts/update_workflows_all_branches.py \
  --org course-test \
  --pattern hw1-stu \
  --workflow-dir hw1-template/.gitea/workflows \
  --commit-message "fix: 修复 Manual checkout 认证问题"
```

### 方法 2: 手动推送并让学生拉取

```bash
# 在 hw1-template 仓库中
cd /path/to/hw1-template
git add .gitea/workflows/
git commit -m "fix: 修复 Manual checkout 的认证问题"
git push

# 通知学生在各自仓库中
git pull origin main
```

## 技术细节

### GITHUB_TOKEN 自动提供

`${{ github.token }}` 是 Gitea Actions 在每次运行时自动注入的临时 token：

- ✅ 自动为每个 workflow run 生成
- ✅ 有权限访问当前仓库
- ✅ 可以读取代码、发布评论
- ✅ 生命周期与 workflow run 相同
- ✅ 无需手动配置

### RUNNER_TESTS_USERNAME / RUNNER_TESTS_TOKEN 配置

Runner 级环境变量在 `docker-compose.yml` 或 systemd 单元中声明：

- 🔐 `RUNNER_TESTS_TOKEN`：个人访问 token（PAT），具备 `read:repository` 权限
- 👤 `RUNNER_TESTS_USERNAME`：拥有该 token 的账号用户名（例如 `course-admin`）
- 🧩 两者组合成 HTTP Basic Auth 凭据，供 workflow 拉取 `hw1-tests`
- 🎯 仅用于 "Fetch private tests" / "Fetch standard answers" 步骤
### RUNNER_METADATA_REPO / RUNNER_METADATA_TOKEN

为了让每次评分的 `metadata.json` 仅对教师可见，需要补充以下 Runner 环境变量：

- `RUNNER_METADATA_REPO`: 私有仓库名称（如 `course-test/hw1-metadata`）
- `RUNNER_METADATA_TOKEN`: 具有写权限的 PAT，用于上传 `metadata.json`
- `RUNNER_METADATA_BRANCH`: 分支（通常 `main`）

工作流通过 `.autograde/upload_metadata.py` 读取这些变量，使用 HTTP Basic Auth 自动将 metadata 上传到 `records/{org}__{repo}/`，代替直接在 PR 上发布评论。请确保这些变量写入 `docker-compose.yml` / `data/runner/config.yaml` 并重启 Runner。

### SSL 证书问题

**Manual checkout 步骤**：添加了 `-c http.sslVerify=false` 参数：

```bash
git -c http.sslVerify=false fetch --depth=1 origin "$REF"
```

**Fetch private tests / Fetch standard answers 步骤**：改用 `http://username:token@host` 形式，并通过 `::add-mask::` 隐藏凭据：

```bash
echo "::add-mask::$TESTS_TOKEN"
echo "::add-mask::$TESTS_USERNAME"
AUTH_URL="http://${TESTS_USERNAME}:${TESTS_TOKEN}@${HOST}/course-test/hw1-tests.git"
git -c http.sslVerify=false clone --depth=1 "$AUTH_URL" _priv_tests
```
这样能兼容所有 git 版本，并确保日志中看不到 Token。

原因：
- Gitea 服务器使用自签名证书
- `https://` + `http.sslVerify=false` 仍会尝试 TLS 握手，可能失败
- `http://` 完全避免 TLS，更简单可靠
- OAuth2 token 认证仍然保证访问安全
- 在内网环境中使用 `http://` 是安全的

## 验证修复

### 1. 检查 workflow 文件

确认 "Manual checkout" 步骤使用 `GITHUB_TOKEN`：

```bash
grep -A 5 "Manual checkout" hw1-template/.gitea/workflows/grade.yml
```

应该看到：

```yaml
env:
  GITHUB_TOKEN: ${{ github.token }}
```

### 2. 创建测试 PR

在学生仓库中创建一个 PR，查看 Actions 日志：

```
✅ Manual checkout (local Gitea)
   Gitea host: gitea:3000 (using: 49.234.193.192:3000)
   Repo: course-test/hw1-stu_sit001
   Ref: 6b8a5453ad870b2ad8315c961736100515b96f24
   [成功 clone 仓库]
```

### 3. 验证私有测试访问

检查 "Fetch private tests" 步骤仍然工作正常：

```
✅ Fetch private tests
   📥 Fetching tests from hw1-tests repository...
   Cloning into '_priv_tests'...
   ✅ Tests copied: _priv_tests/python/tests/ → tests/
```

## 常见问题

### Q: 为什么不能用 TESTS_TOKEN 访问学生仓库？

A: `TESTS_TOKEN` 是专门为访问 `hw1-tests` 配置的 token，它的权限范围仅限于该仓库。无法用它访问其他仓库。

### Q: GITHUB_TOKEN 是如何提供的？

A: Gitea Actions 在启动 workflow 时自动生成并注入 `GITHUB_TOKEN`，类似于 GitHub Actions 的行为。这个 token 具有访问当前仓库的权限。

### Q: 修复后学生需要做什么？

A: 如果使用批量更新脚本，学生不需要做任何操作。如果手动推送到 template，学生需要在各自仓库中执行 `git pull origin main`。

### Q: 这个修复会影响私有测试吗？

A: 不会。"Fetch private tests" 步骤仍然使用 `TESTS_TOKEN`，功能完全不受影响。

### Q: 为什么增加了 TESTS_USERNAME secret？

A: Gitea 的 Git 基础认证需要「用户名 + Token」组合。早期直接把 token 写进 URL（`https://token@...`）不仅会在日志中泄露敏感信息，而且在 TLS 问题下也会失败。现在通过
`TESTS_USERNAME`（账号名） + `TESTS_TOKEN`（PAT）组合生成 `Authorization: Basic ...` 头，既安全又稳定。

### Q: 使用 http:// 代替 https:// 安全吗？

A: 在**内网环境**中是安全的：

**安全因素：**
- ✅ OAuth2 token 认证仍然有效，访问控制正常
- ✅ Gitea 的权限系统完全正常工作
- ✅ 私有仓库内容仍然受 `TESTS_TOKEN` 保护
- ✅ 内网通信，不经过公网，中间人攻击风险极低

**为什么不用 https://?**
- Gitea 使用自签名证书
- `https://` 会触发 TLS 握手
- 即使用 `http.sslVerify=false`，TLS 握手仍可能失败
- `http://` 完全避免 SSL/TLS，更简单可靠

**公网部署建议：**
- 如果 Gitea 暴露在公网，建议配置有效的 SSL 证书（Let's Encrypt）
- 或使用反向代理（Nginx/Traefik）处理 SSL
- 避免在公网使用 `http://` 传输敏感数据

### Q: 为什么会出现 "TLS handshake failed" 错误？

A: 这是由于 Gitea 服务器使用自签名 SSL 证书导致的：
- 自签名证书不被 Git 客户端信任
- Git 尝试验证证书时失败
- 解决方案是使用 `http://` 协议完全避免 TLS

### Q: 为什么 `pull_request` 事件里 Secret 长度总是 8（显示为 `********`）？

A: 这是 Gitea 的安全策略：`pull_request` / `pull_request_target` 默认不暴露仓库 Secrets，以防恶意 PR 窃取 Token。即便改为 push，协作者也无法读取仓库 Secrets，因此需依赖 Runner 级环境变量。现在模板改为 `push` + `workflow_dispatch`，并在 Runner 上注入 `RUNNER_TESTS_*`，即可稳定获取凭据。

### Q: 如何本地验证 Token 是否可访问 hw1-tests？

A: 运行 `python3 scripts/test_private_repo_access.py`。脚本会读取当前环境变量并对 `hw1-tests` 执行 `git ls-remote`。若输出 ✅，说明凭据有效，可在 Actions 中安全使用。

## 总结

✅ **关键修复**：将 "Manual checkout" 步骤的认证从 `TESTS_TOKEN` 改为 `GITHUB_TOKEN`

✅ **凭据职责明确**：
- `GITHUB_TOKEN` → 访问当前仓库（由 Actions 自动提供）
- `RUNNER_TESTS_USERNAME` + `RUNNER_TESTS_TOKEN` → 访问私有测试仓库（在 act_runner 中统一配置）

✅ **所有功能正常**：
- ✓ 学生代码 checkout
- ✓ 私有测试获取
- ✓ 元数据上传到私有 `hw1-metadata`（教师可访问，学生不可见）

🎯 **核心原则**：合适的场景使用合适的 token，同时把元数据保存在教师可见的私有仓库！



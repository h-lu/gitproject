# Gitea Actions Secrets 配置指南（Runner 版）

## 背景

Gitea 1.22 默认不会在协作者触发的 `push` / `pull_request` 事件中注入仓库级 Secrets，工作流中读取到的值会被替换为 `********`。因此，访问私有测试仓库必须改为 **在 act_runner 进程中注入凭据**，workflow 直接读取这些 Runner 级环境变量。

## Docker Compose 示例

```yaml
services:
  runner:
    image: gitea/act_runner:latest
    depends_on:
      - gitea
    environment:
      GITEA_INSTANCE_URL: http://gitea:3000
      RUNNER_REGISTRATION_TOKEN: <你的注册 token>
      DOCKER_HOST: unix:///var/run/docker.sock
      RUNNER_TESTS_USERNAME: hblu
      RUNNER_TESTS_TOKEN: 9f38be014ffc9fdae840eebb2047fb360fba1adb
      RUNNER_METADATA_REPO: course-test/hw1-metadata
      RUNNER_METADATA_TOKEN: 5b12...metadata-pat...
      RUNNER_METADATA_BRANCH: main
    volumes:
      - ./data/runner:/data
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
```

修改后执行：

```bash
docker compose up -d runner
```

（老版本命令：`docker-compose up -d runner`）

## systemd 示例

```bash
sudo systemctl edit act_runner
```

```
[Service]
Environment="RUNNER_TESTS_USERNAME=hblu"
Environment="RUNNER_TESTS_TOKEN=9f38be014ffc9fdae840eebb2047fb360fba1adb"
```

然后：

```bash
sudo systemctl daemon-reload
sudo systemctl restart act_runner
```

## Workflow 如何读取

在最新模板中，workflow **直接**读取 `RUNNER_TESTS_USERNAME` / `RUNNER_TESTS_TOKEN`，不再尝试仓库 Secret。也就是说，只要 Runner 层环境变量存在，学生 push 时就能克隆 `hwX-tests`。

## 验证步骤

1. **确认 Runner 环境变量**
   ```bash
   docker compose exec runner env | grep RUNNER_TESTS
   # 或 systemctl show -p Environment act_runner
   ```

2. **本地测试 Token**
   ```bash
   python3 scripts/test_private_repo_access.py
   ```
   若输出 “✅ 访问成功”，说明当前环境变量中的账号/Token 可用。

3. **触发一次 workflow**
   学生 push 到 `main` 后查看日志，应看到：
   ```
   🔐 TESTS_USERNAME length: 4
   ```
   并成功克隆 `_priv_tests`，随后 `upload_metadata.py` 会将 `metadata.json` 推送到 `hw1-metadata`。
4. **验证元数据上传**
   ```bash
   git clone http://49.234.193.192:3000/course-test/hw1-metadata.git
   ls records | head
   ```
   若能看到 `records/` 目录（或使用 `python scripts/collect_grades.py` 读取），说明 `RUNNER_METADATA_*` 配置生效。

## 常见问题

- **一个 Token 可以覆盖多个作业吗？**  
  可以，只要该账号对所有 `hwX-tests` 拥有读取权限。

- **如何更换 Token？**  
  更新 Runner 环境变量并重启 Runner，workflow 会自动读取新值。

- **为何不再提供 setup_tests_token.py？**  
  因为协作者 workflow 无法读取 repo Secret（得到的永远是 `********`），所以批量配置学生仓库的 Secret 没有意义。改用 Runner 环境变量更简单且可扩展。

## 参考

- [Gitea Actions 文档](https://docs.gitea.com/usage/actions/overview)
- [act_runner 项目](https://gitea.com/gitea/act_runner)



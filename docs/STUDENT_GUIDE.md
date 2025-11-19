# 📖 学生指南

本指南说明如何提交作业和查看成绩。

## 1. 访问作业

1.  登录教师提供的 Gitea 系统。
2.  您应该看到一个以作业和用户名命名的仓库（例如 `hw1-stu_yourname`）。
3.  将此仓库克隆到本地计算机：

    ```bash
    git clone http://<gitea-url>/<org>/hw1-stu_yourname.git
    cd hw1-stu_yourname
    ```

## 2. 完成作业

1.  **阅读 README**: 仓库包含一个 `README.md`，其中有作业的具体说明。
2.  **编写代码**: 在 `src/` 目录（或按指定位置）实现您的解决方案。
3.  **运行本地测试**:
    如果提供了公开测试，您可以在本地运行：
    ```bash
    # Python 示例
    pip install -r requirements.txt
    pytest tests_public/
    ```

## 3. 提交作业

要提交，只需将代码推送到 `main` 分支：

```bash
git add .
git commit -m "完成作业"
git push origin main
```

## 4. 查看反馈

推送后，系统将自动评分您的提交。

1.  进入 Gitea 上的仓库页面。
2.  点击 **Actions** 选项卡查看评分进度。
3.  完成后，点击 **Pull Requests**（或查看最新提交评论）。
4.  系统将发布一条包含您的分数和详细反馈的评论。

> [!NOTE]
> 您可以在截止日期前多次提交。系统将评分最新的提交。

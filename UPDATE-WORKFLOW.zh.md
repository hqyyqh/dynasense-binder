# CI 与后续更新

当前执行规则（2026-10-16）：正式 Release 是在线演示的更新来源。普通源码 push、草稿和预发布版本不提升演示。历史快照说明不再适用。

## 自动流程

1. `check-plugin-release.yml` 每天北京时间 09:23 唤醒。距上次成功检查满 30 天才查询上游；手动运行立即查询。使用 Actions artifact `release-check-success` 记录成功检查，保留 90 天，不制造空提交。失败不会更新这个时间，次日再试。
2. 无新版则结束。有新版则核验原始 Linux x64 VSIX 的身份、版本、平台和摘要，更新固定资产清单；手册保持独立固定版本。
3. 创建 `codex/release-<releaseId>-<assetId>` 分支和 PR，显式触发 `validate-runtime.yml`。这是必要的：由 GITHUB_TOKEN 推送的提交不会自动触发普通 push 工作流。已有 PR 不重复创建。
4. 镜像检查构建完整环境并验证安装包、VS Code 兼容性、Linux SQLite 和双语路由；失败不会改主页。
5. 后续 AI 按双语引导检查实际功能、补充引导和真实录屏，再提升主页固定部署提交。不要把主页改为 `main` 或 `latest`。

## 手动检查和故障接续

在部署仓库执行：

```sh
gh workflow run check-plugin-release.yml --ref main
gh run list --workflow check-plugin-release.yml --limit 5
gh pr list --state open
gh workflow run validate-runtime.yml --ref codex/release-RELEASE_ID-ASSET_ID
```

已有候选 PR 的镜像检查失败时，修复该分支并手动重跑镜像检查，不创建重复 PR。Release 检查成功代表候选已准备或没有新版；不代表候选镜像和人工验收都通过。

定时工作流必须在默认分支。GitHub 公共仓库长期无活动可能停用 schedule；遇到停用，在 Actions 中重新启用并手动检查。不要用无意义提交保活。

## 提升与回退

验收后合并候选 PR，保留已验收提交 SHA。同步本站 `deployment/binder/` 中的配方、`src/online-experience.js` 与 HTML 默认入口，并更新 `docs/binder-release-delivery.md`。运行 `npm test`、`npm run build`，实际检查中英文入口，然后提交。

回退恢复上一个已验收部署 SHA；不删除历史 Release。用户现有会话不会被升级或清空。

## 产品页 CI

产品页仓库的 `.github/workflows/validate-site.yml` 对 push、PR 和手动运行执行 Node 22 的 `npm ci`、测试及静态构建，并保存 `dist/` 为构建产物。当前产品页仅有本地 Git 仓库，没有配置远端；此工作流在未来推送到 GitHub 后才运行。部署仓库的远端 CI 独立运行。

当前发布包、手册摘要、主页部署 SHA 与历史验收见 产品页仓库的 `docs/binder-release-delivery.md`。继续任务前先检查两仓 Git 状态，保护未提交修改。

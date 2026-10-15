# DynaSense online experience

Deployment work for a real DynaSense extension in Binder and code-server.

当前正在完成首次环境验收；正式体验启动入口将在验收后提供。
The initial environment is undergoing acceptance. A launch link will follow after validation.

## Walkthroughs

- [中文操作引导](demo/GUIDE.zh.md)
- [English walkthrough](demo/GUIDE.en.md)

## Release checks

GitHub Actions checks the official hqyyqh/vscode-lsdyna stable release daily and on manual dispatch.
The initial local-source package is newer than the public v3.2.0 release, so release-policy.json
holds that baseline instead of downgrading it. Once an accepted release baseline is recorded,
the workflow downloads a Linux x64 candidate, checks its identity and available upstream digest,
and retains it as an Actions artifact for runtime validation. It does not promote a candidate
or change a running visitor session.

The image, bilingual walkthroughs and manual assets are shared by both language experiences.
Each visitor edits their own temporary workspace. Refreshing an active session keeps edits.
The homepage will use a Binder launch URL, never a temporary /user/ session URL.

Scheduled workflows can pause after 60 days without repository activity. Use the Actions
manual trigger to check explicitly; release-triggered cross-repository dispatch can be added
when the upstream publishing workflow is connected.

## Runtime validation

See [deployment instructions](DEPLOYMENT.md). Runtime builds use pinned release assets.
The Chinese and English proxy paths are vscode-zh/ and vscode-en/.
Homepage promotion waits for real UI acceptance.


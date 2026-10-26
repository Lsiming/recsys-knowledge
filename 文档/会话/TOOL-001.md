# TOOL-001：GitHub MCP 与 CLI 安装配置

更新日期：2026-10-25。

## 身份与范围

- 状态：已完成安装、配置、账户认证和真实公开仓库读取验证；负责人及整合者：当前 Codex 会话。Codex 新会话加载、私有仓库和写入的验证边界见下文。
- 用户指令：安装和配置 GitHub MCP 和 CLI；按已确认的 Codex/Claude Code 使用方式配置两个客户端，优先只读资料调研。
- 完成条件：安装 `gh`、登记官方 GitHub MCP、验证实际认证和公开仓库读取；需要人工认证时保存可执行恢复步骤，不将未认证写成已可用。
- 基线：`main`，`9bb819e`；开始时工作区干净，无并行 Agent。
- 写入范围：本机用户目录中的二进制/启动器、shell 与 MCP 配置、`docs/工具/GitHub访问.md`、本交接及相关共享入口；凭证和本机配置不入 Git。
- 本仓库继续只维护本地 Git；工具安装不改变 remote 约定。

## 已完成与证据

- 开始时已检查：macOS arm64，Homebrew 可用；未安装 `gh`，未发现 `gh` 登录配置或 GitHub token 环境变量。
- 已查阅 GitHub 官方 MCP 的接入文档；OpenAI 官方文档站与文档 MCP 在本机均返回 HTTP 403，已结合 GitHub 官方指南与本机 CLI 帮助核对配置。
- Homebrew 下载缓慢且本机目录缓存较旧；已中止 CLI 安装，最终使用用户保存到 `~/Downloads` 的官方 Release 压缩包，分别核对官方 SHA256 后安装 CLI 2.103.2、MCP 2.0.3。校验值与路径见 [使用说明](../工具/GitHub访问.md)。
- 二进制保存在 `~/.local/opt/github-tools/`，通过 `~/.local/bin` 暴露命令；已更新 `~/.zprofile`，显式启动的登录/交互 shell 都能定位 `gh`。当前 Agent 的旧 shell 快照仍使用绝对路径。
- Codex 与 Claude Code 的用户级 `github` 服务都调用 `~/.local/bin/github-mcp-gh`。启动器默认只读，从 `gh` 读取凭证；支持以后显式使用 `--read-write`。原有 Codex 配置正文、Claude 配置其他字段均核对保留。
- 修改前备份位于 `~/.local/state/github-mcp-setup/20261025-185805/`；两个客户端配置权限为 0600，启动器为 0700。
- 首次浏览器登录请求失败，重试进入 GitHub device flow 后在 token 交换时连接 `github.com` 超时，该流程已结束且未保存凭证。Python 访问授权域名也超时；Go CLI 访问 `api.github.com` 收到预期 HTTP 401，表明 API 连通，不能据此声称已认证。
- 已准备 `~/.local/bin/github-login`：用户在本机终端输入 PAT，不回显，经官方 `gh auth login --with-token` 保存登录。该脚本不保存 Token 到自定义文件，不将 Token 放入命令参数或聊天。用户随后确认已登录，`gh auth status --hostname github.com` 返回已认证且使用系统钥匙串（keyring）；认证用户 API 返回同一账户。

## 工作区与验证

- 两个官方二进制均已成功执行版本命令；MCP 实际版本支持所选工具组和 `--read-only` 参数。
- `sh -n` 检查启动器、`zsh -n` 检查 shell 配置均通过；本机登录脚本的语法编译和 `--help` 检查通过。
- 登录前曾用占位凭证验证本机 MCP 协议发现；登录后已通过共用启动器重新执行 JSON-RPC `initialize`、`tools/list` 和 `tools/call`，真实账户凭证由系统钥匙串经 CLI 读取，MCP 2.0.3 暴露 28 个只读工具，无写工具。
- CLI 成功读取认证用户 API，以及 `nashsu/llm_wiki` 固定 commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` 的 `README.md`，文件为 32048 字节，Git blob SHA 为 `89d124047f93cb8a9d73adbe1c9a92ffdd71ecea`。MCP 的 `get_file_contents` 成功返回同一 SHA 与实际 Markdown 正文。
- `claude mcp get github` 返回 user scope、stdio 和 `Connected`；`codex mcp get github` 确认已启用并指向同一启动器。当前 Codex 会话未加载新增 GitHub MCP，未声称已完成桌面会话内调用；新会话或重启后加载。此边界不影响已通过启动器完成的真实 MCP 读取验证。
- `python3 scripts/check_context.py` 通过：26 份活跃 Markdown、123 个本地链接目标；覆盖入口、占位符及无远端约定，不验证账户认证。
- 全局 `git diff --check` 仅报告知识库设计 README 第 40 行已有的无关行尾空格；保留该改动。本任务文件的差异检查和提交前的 `git diff --cached --check` 通过。
- 安装及登录恢复步骤已本地提交为 `f3fb5f7`；本次认证与读取验收另作中文本地提交，哈希以 Git 历史为准。没有运行训练、改动算法代码或执行远端写入。
- 工作期间发现知识库设计 README 有不属于本任务的并发修改，保留且不纳入本任务提交。

## 验证边界与后续使用

当前无认证阻塞。Codex 新会话或重启后加载 GitHub MCP；Claude Code 新会话可用 `/mcp` 查看连接。CLI 与共用启动器均已在真实账户下访问公开仓库。

私有仓库、组织 SSO、远端写入及读写模式未验证，后续按具体项目任务核验。本仓库继续仅本地 Git；本轮未设置 remote、执行推送或创建远端 PR。凭证过期时按 [使用说明](../工具/GitHub访问.md) 在本机重新登录。

临时检查脚本在 `/tmp/github-mcp-smoke-20261025.py`；临时文件不是长期恢复依据，缺失时按上述协议重新检查。

## 待整合内容

安装、认证与真实读取结果已同步到项目记忆、总交接和使用说明，TOOL-001 已移出有效队列；无待整合专题。用户级配置可供其他个人项目复用，默认只读，后续按项目任务切换读写能力。

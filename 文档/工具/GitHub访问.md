# GitHub MCP 与 CLI

任务：TOOL-001；配置及验收日期：2026-10-25。已完成安装、客户端配置与账户认证；CLI/MCP 真实公开仓库读取和 Claude Code 连接检查通过。Codex 配置已核验，新会话或重启后加载；详细证据与验证边界见 [任务交接](../会话/TOOL-001.md)。

## 本机配置

使用用户保存到 `~/Downloads` 的官方 Release 压缩包，核对 SHA256 后安装 GitHub CLI `gh` 与 GitHub 官方 `github-mcp-server` 本机二进制。Codex 与 Claude Code 都通过用户级启动器调用 MCP，无需 Docker。

| 项目 | 本机位置或设置 |
|---|---|
| GitHub CLI | 2.103.2，`~/.local/bin/gh` |
| 官方 MCP 二进制 | 2.0.3，`~/.local/bin/github-mcp-server` |
| 实际版本目录 | `~/.local/opt/github-tools/`，上面的命令路径为符号链接 |
| 共用启动器 | `~/.local/bin/github-mcp-gh` |
| Codex | `~/.codex/config.toml` 中的 `mcp_servers.github`，用户级配置 |
| Claude Code | `~/.claude.json` 中的 `mcpServers.github`，user scope |
| MCP 模式 | stdio，`--read-only` |
| 已选择工具组 | `repos,issues,pull_requests,discussions,gists` |

安装来源及校验值：

| 官方压缩包 | SHA256 |
|---|---|
| [CLI 2.103.2 macOS arm64](https://github.com/cli/cli/releases/download/v2.103.2/gh_2.103.2_macOS_arm64.zip) | `5416000f5d17580a187339e0c4068a01ca5c87f7d4fe6ca64933696f967bc418` |
| [MCP 2.0.3 Darwin arm64](https://github.com/github/github-mcp-server/releases/download/v2.0.3/github-mcp-server_Darwin_arm64.tar.gz) | `5c95c01f75a7ec2370607e989b2968d314b02a54d78af8a9fdf38f3dfe6135f4` |

校验值来自对应 GitHub Release asset 的 `digest` 字段。本机安装清单保存在 `~/.local/opt/github-tools/install-20261025.json`。最初 Homebrew 下载缓慢且本机目录缓存较旧，已停止该 CLI 安装尝试；最终工具由官方压缩包安装，不由 Homebrew 管理。

启动器通过 `gh auth token --hostname github.com` 读取 CLI 的登录凭证，再以进程环境变量交给官方 MCP。两个客户端配置只保存启动器路径，凭证不写入本仓库。本次 `gh auth status` 已确认凭证保存在系统钥匙串（keyring）。

本机配置修改前的私有备份位于 `~/.local/state/github-mcp-setup/20261025-185805/`。这不是项目分发配置；迁移到另一台机器时，应按新机器的安装路径重新登记客户端。

2026-10-26 本仓库已获授权转为 [GitHub 共建](GitHub共建.md)，此前仅本地 Git 限制已替代；本页安装路径为最初本机记录，其他贡献者无需使用这些工具或个人配置。GitHub MCP 提供外部资料读取能力；`gh` 的完整能力仍按用户当前任务授权使用。

`~/.zprofile` 已加入 `~/.local/bin` 的 PATH 配置；新开登录终端可使用短命令，现有终端可以执行 `source ~/.zprofile`。MCP 使用绝对路径，不依赖桌面应用继承该 PATH。

## 登录与启用

本次已完成账户登录；`gh auth status` 与认证用户 API 均验证通过。此前浏览器 device flow 的 token 交换超时，旧验证码流程已结束；后续使用本机 PAT 登录入口完成了认证。以下命令用于迁移、凭证过期或需要重新登录时。

在本机终端执行：

```bash
~/.local/bin/github-login
```

根据提示输入已有的 GitHub PAT，输入不回显；脚本通过官方 `gh auth login --with-token` 保存登录。Token 只在本机输入，不发到聊天或写入本仓库。没有 Token 时可使用 [GitHub 官方创建页面](https://github.com/settings/tokens/new?description=GitHub%20CLI%20and%20MCP&scopes=repo,read:org,gist)；该页面预选官方 CLI 接受的 classic PAT 权限 `repo`、`read:org`、`gist`，用户自行确认账户、权限与有效期。

若后续授权域名网络恢复，也可使用标准浏览器登录：

```bash
gh auth login --hostname github.com --git-protocol https --web
```

按终端显示的 device code 完成 GitHub 浏览器授权。若询问是否用该凭证配置 Git 身份验证，可选择 No；CLI 与 MCP 的资料读取不依赖本仓库设置远端。

登录成功后，新启动器进程会自动取得最新凭证。Codex 新会话或重启客户端后查看 GitHub MCP；Claude Code 新会话内使用 `/mcp` 查看连接状态。当前会话已有的工具列表不代表配置变更已自动热加载。

## 常用检查

```bash
gh --version
gh auth status --hostname github.com
gh api repos/nashsu/llm_wiki --jq '{full_name,default_branch,html_url}'
github-mcp-server --version
codex mcp get github
claude mcp get github
```

CLI 能访问 GitHub 不等于 MCP 已连接。完整验证还需要成功初始化 MCP、列出工具、确认只读工具集合，并通过 MCP 读取一份公开仓库文件。实际已执行项以任务交接为准。

## 在知识库中的使用

- 查找某篇论文的官方实现，核对作者、仓库所有者、维护状态和版本。
- 阅读指定文件和提交，定位训练目标、模型结构、数据处理和推理入口。
- 搜索 Issue、PR 和 Discussion，查找复现条件、实现差异和作者解释。
- 阅读 Gist，例如 Karpathy 的 LLM Wiki 设计文档。
- 将有价值的资料按 [研究工作流](../规范/研究工作流.md) 沉淀；代码证据记录 commit，引用尽量使用固定版本链接。

例如可以直接提出：

> 阅读 nashsu/llm_wiki 的资料入库流程，固定当前 commit，定位核心实现文件，再比较它与本仓库知识库设计的差异。

深度分析仍应结合实际源码、论文与运行证据；MCP 返回了源码不等于已经执行过实现。

## 后续与个人 GitHub 项目交互

这套用户级安装可被其他项目复用。登录后可读取公开仓库；私有仓库或组织资源需具备对应访问授权。实际验证若只覆盖公开仓库，不据此声称已验证私有仓库或组织 SSO。

`gh` 可按具体任务管理 Issue、PR、Release 和 Actions；源码提交仍结合该项目自己的 Git 约定。当前知识库的远端授权仅适用于本项目及明确范围，不自动扩展到其他项目。

启动器默认是只读。后续需要 MCP 读写能力时，在该客户端的 MCP 配置中为启动器添加参数 `--read-write`，重连即可；此模式会额外启用 `git,actions` 工具组。恢复只读时移除该参数或使用 `--read-only`。客户端的 `command` 路径和账户登录方式保持一致。

读写模式提供操作能力，具体外部写入仍以用户任务授权和项目规则为准。本轮只配置默认只读服务，后续读写、私有资源、发布和远端提交另按真实任务验证。

## 恢复与维护

认证过期时重新运行 `github-login` 或 `gh auth login`，然后重连 MCP。启动器每次启动都会重新读取凭证，无需手工把 token 复制到两个客户端。

若 CLI 正常但 MCP 启动失败，检查启动器和两个二进制的绝对路径、执行权限，以及客户端显示的错误。启动器的 stdout 专供 MCP 协议使用，诊断信息应写入 stderr。

升级时下载新的官方 Release，核对官方 SHA256 后放入新的版本目录，再调整符号链接；不要同时用 Homebrew 覆盖这套用户目录安装。升级后重新核验启动参数、只读工具集合和真实文件读取，不仅凭版本号判定兼容。

## 官方来源与核验边界

- [GitHub CLI](https://cli.github.com/) 与 [CLI 源码](https://github.com/cli/cli)。
- [GitHub 官方 MCP](https://github.com/github/github-mcp-server)。
- [Codex 安装指南](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-codex.md)，本次读取文件 SHA：`9336a26d7ba6df62c4e34c02ee78db310a0aeacd`。
- [Claude Code 安装指南](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-claude.md)，本次读取文件 SHA：`04658c45205debe6a35da55ff092e76b7930bbe8`。

OpenAI 官方 MCP 文档站和文档 MCP 在本机返回 HTTP 403；Codex 配置改用本机 `codex mcp` 帮助及 GitHub 官方接入指南核对。安装版本的参数和能力以实际二进制及真实协议检查为准。

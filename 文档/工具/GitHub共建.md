# GitHub 共建与本地附件

2026-10-26 用户授权将本项目作为公开知识库维护，目标仓库为 [Lsiming/recsys-knowledge](https://github.com/Lsiming/recsys-knowledge)。贡献流程见 [CONTRIBUTING](../../CONTRIBUTING.md)，内容/代码及第三方材料许可见 [LICENSE](../../LICENSE)。此前“仅本地 Git”是历史决定，已由本次授权替代。

## Git 保存的内容

Git 保存知识正文、来源卡与阅读笔记、经过逐篇许可核实的正式 Markdown 译文、维护规则、模板、脚本与测试、项目级协作记录。`.local/` 保存来源原件、PDF、LaTeX、编译与 QA、下载缓存、备份、运行库；`.obsidian/` 是个人浏览配置，也不分发。

原文和中文PDF统一在独立私有附件库的Releases维护，公开Git只保存[PDF盘点](../../译文/PDF目录.md)和访问说明。私有Git维护完整版本/哈希目录与登录下载工具；普通克隆不附带PDF或私有访问权，每篇新论文沿用[私有维护流程](中文PDF发布.md)。LaTeX、渲染与其他运行产物仍单独管理。

原文引用优先采用固定版本公开 PDF/HTML 或 DOI。只有本机存在的附件使用行内代码路径并标注“本地附件，不随 Git 分发”；不要将其写成 GitHub 上无法打开的相对链接。公开Markdown译文链接进入 `译文/`，尚未确认公开授权的译文不放入公开远端。原文/中文PDF统一私有维护，公开笔记链接[PDF访问说明](中文PDF发布.md)，不提供需登录的逐篇下载作为公开入口；普通贡献者不需要私有权限。

## 维护远端

首次发布由维护者完成：创建空远端、确认账号与可见性、添加 origin、检查历史与发布内容、推送已验证提交并设置 upstream。不能在创建时添加初始化 README 或许可，以免与本地历史无谓分叉。普通贡献者使用 Fork/分支与 PR，维护者按实际权限决定合并。禁止强推和把本地附件塞进历史。

配置 remote 或读取远端不再被检查器当作错误。Agent 只在用户授权的发布/协作范围内推送或创建 PR，普通论文学习仍默认仅作中文本地提交。自动检查允许没有任何本地原件的克隆；`lint --local` 只用于完整快照持有者。

## 提交身份与发布检查

Git 提交身份独立于 GitHub CLI 登录。维护者使用 GitHub 账号 `Lsiming` 与该账号的公开 noreply 邮箱；其他贡献者也使用自己 GitHub 设置中提供的 noreply 地址，避免把私人或公司邮箱写入提交历史。

```bash
git config --local user.name 你的GitHub账号
git config --local user.email 你的GitHub隐私邮箱
git config --local core.hooksPath .githooks
python3 scripts/check_public.py
```

`.githooks/pre-push` 拒绝推送或创建`archive/`归档分支，并在推送前检查完整待发布历史，阻止非 noreply 提交邮箱、凭证、本机用户绝对路径、内网地址及不允许分发的附件；CI 同样检查完整历史。机器检查不替代对非公开业务文字与样本的人工判断，不要在知识正文或交接中写入公司资料。

## 日常只维护一条可公开的主线

首次发布中发现旧提交身份包含公司邮箱、少量交接含本机用户名路径，仓库随即转私有。用户明确要求远端不保留原始历史，因此删除原远端并重建同名公开仓库，使用脱敏内容与 GitHub noreply 身份生成新的初始提交；远端无原始历史或备份仓库。本地原主目录仍有其他会话的未完成工作，保留原状。

2026-10-28用户要求消除反复迁移。日常主目录main统一采用脱敏公开历史并跟踪origin/main；旧历史保留在本地`archive/local-main-20261028`，不再作为日常写入入口。本次从远端`4cbefc2`出发，仅迁移本地`e0542fd`中已完成的文件内容，包括`ce726b4`整合成果、TaQFormer和工作流；不合入旧祖先。两处本机路径在公开副本脱敏，历史快照同时登记原哈希与公开副本哈希。详见[KB-012](../会话/KB-012.md)。

2026-11-08用户要求后续会话默认直接在日常主目录main上本地提交，不再默认创建codex分支/worktree；明确需要隔离时按协作规范临时处理，完成后回到main。仅在旧分支还有独有且明确要保留的增量时按文件迁移。推送沿用具体有效授权，读取远端最新状态并检查待推范围。2026-11-08用户指定以后采用下节的GitHub API通道，替代本机反复超时的Git HTTPS推送；不再把普通`git fetch`/`git push`作为发布前的网络探测。其他会话未完成内容继续保留在工作区，只有已完成且审查过的提交进入发布范围。

## 通过GitHub API推送

本机已验证`github.com`的Git HTTPS通道超时，而`api.github.com`的Git Database API可达。API本身仍使用HTTPS；此流程规避的是前一条网络通道，保留本地Git提交身份、父链与SHA。`16fa557`和`7e53451`已通过此方式同步main，对应CI的Python 3.9/3.13均成功；验收见[KB-014](../会话/KB-014.md)。

### 脚本归档

可复用实现为[push_github_api.py](../../scripts/push_github_api.py)，替代旧会话忽略目录中的临时脚本；环境约定见[CONFIG](../../scripts/CONFIG.md)。Python 3.9+标准库、Git与已登录的GitHub CLI即可运行。凭证由`gh api`读取现有登录，脚本不读取、打印或保存token；运行收据和调试日志如需保存，放忽略的`.local/`。

1. 核对`git status --short --branch`、最近提交、origin与upstream，完成明确文件的本地提交并清空暂存区；未提交的其他用户文件原样保留。运行适用文档/代码检查。
2. 用API读取目标分支最新完整SHA，确认本地已有该提交且为HEAD祖先，审查`<远端SHA>..HEAD`的全部提交与文件。不要用陈旧的origin/main充当远端最新状态。
3. 运行脚本预览；它校验origin、upstream、分支、基线、完整公开历史和全部待上传提交的结构。已有发布授权且范围已核对后，同参数加`--publish`直接执行，无需再次请求批准。
4. 工具按原内容上传blob、基于父tree构建tree、按原消息/父链/作者/提交者/时间构建commit，逐项核对返回SHA。更新ref前再次检查HEAD、暂存区及远端基线；使用`force=false`快进更新，随后读取远端核验并更新origin跟踪ref。API不触发Git pre-push，脚本显式执行同一`check_public.py --ref <HEAD>`完整历史检查。
5. 核验本地HEAD、origin/main与GitHub main一致，等待该SHA对应的Actions工作流结束，失败时读取日志并修复；对象上传成功或ref更新成功均不能代替CI验收。

在仓库根执行，`<远端SHA>`替换为第一条命令实际返回的40位SHA，不写死旧基线：

```bash
gh api repos/Lsiming/recsys-knowledge/git/ref/heads/main --jq .object.sha
git log --oneline <远端SHA>..HEAD
git diff --stat <远端SHA>..HEAD
python3 scripts/push_github_api.py --repo Lsiming/recsys-knowledge --base <远端SHA>
python3 scripts/push_github_api.py --repo Lsiming/recsys-knowledge --base <远端SHA> --publish
gh run list --repo Lsiming/recsys-knowledge --commit <本地HEAD完整SHA> --limit 3
gh run watch <对应run-ID> --repo Lsiming/recsys-knowledge --exit-status
```

脚本默认main；其他已授权分支显式传`--branch`，并要求本地当前分支与origin的同名upstream对应。预览只读API，不上传对象或修改ref；首次建库/建分支、远端提交本地缺失、分叉整合、合并/签名提交、子模块和符号链接暂不由该工具处理，须按原历史保留要求单独处理，不改写历史迁就工具。

任何SHA不一致都停止ref更新；上传的孤立对象不代表已发布。远端基线变化时先保留工作、读取并整合远端，再重新审查增量，禁止强推。若更新ref请求超时，先用API读取实际目标SHA：等于本地HEAD则核验成功后对齐跟踪ref并检查CI；仍为旧基线则可同参数重试；为其他SHA则按远端前进处理。默认不自动回退远端或覆盖工作区。API也不可达时如实记录实际阻塞，不重复尝试已知失败的Git HTTPS通道。

本机钩子使用`git config --local core.hooksPath .githooks`，避免引用另一会话worktree的绝对路径；每个新克隆按同样方式启用。首次主目录对齐先建立归档分支，核对用户未提交文件哈希与本地附件，再切换和复查。目标分支会覆盖未提交文件时暂停该切换，改在隔离worktree完成整合；不得stash/reset/clean或删除用户内容。完整历史检查会拒绝重新引入旧身份和路径。

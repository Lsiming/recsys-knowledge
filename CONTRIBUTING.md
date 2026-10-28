# 共同建设知识库

欢迎补充论文、修正解释、改进问题比较与工具。学习入口是 [知识地图](知识库/知识地图.md)，内容字段遵循 [知识契约](SCHEMA.md)，论文处理遵循 [标准流程](维护/工作流.md#论文知识沉淀标准流程)。不要求安装 Agent、Obsidian、LaTeX 或下载整库论文。

## 开始一个改动

先搜索论文题名、别名、来源 ID 和问题关键词，优先完善已有页面。小型纠错可以直接提 PR；跨模块重构、批量论文或多人同时处理同一问题，先开 Issue 说明范围并认领。跨会话任务由维护者同步到 [任务队列](TODO.md)，Issue 与交接相互引用，避免两套执行状态漂移。

有仓库权限时新建 `codex/主题` 分支；外部贡献者先 Fork，再在自己的仓库建分支。每个 PR 聚焦一个知识增量。

```bash
git clone https://github.com/Lsiming/recsys-knowledge.git
cd recsys-knowledge
git switch -c codex/你的主题
git config --local user.name 你的GitHub账号
git config --local user.email 你的GitHub隐私邮箱
git config --local core.hooksPath .githooks
python3 scripts/wiki.py search "问题关键词"
```

## 新增论文

1. 核实题名、作者、年份、DOI/arXiv ID、固定版本和实际阅读范围。还没精读的论文先加入 [候选阅读](知识库/阅读/候选论文.md)，不要伪造完整笔记或论文实验结论。
2. 需要登记证据时，自行下载该篇原文，用 [工具说明](scripts/README.md#登记来源) 的 `register` 命令创建 `来源/<ID>/来源.json`。下载原件只放 `.local/`；账本保存公开 locator、revision、SHA256 与实际阅读范围。已有论文继续原 ID，新版本追加保留历史。
3. 在 `来源/<ID>/阅读笔记.md` 写明问题、已有缺口、机制、必要公式、实验条件、代价与局限。就近标明章节、公式/表图编号，能确认页码时提供固定版本 PDF 的 `#page=N` 链接。作者报告、自己的推断和本仓库复现分别表述。
4. 按标准流程制作和核对译文；译文受阻时继续能做的精读，明确未完成部分。全文 Markdown 公开前检查 [许可与共享规则](LICENSE)，在 [译文目录](译文/目录.md) 登记逐篇许可、版本、署名、修改说明、范围与哈希。未确认授权时只分享原创解读与公开原文入口，全文译文留本地。

   原文与中文 PDF 另按[私有维护流程](文档/工具/中文PDF发布.md)处理，公开[PDF目录](译文/PDF目录.md)只记许可、范围及备份摘要；PDF不在公开Releases分发，也不提交到任何Git。维护者在独立私有库登录上传/下载并核对原字节与哈希。贡献者不需要私有库访问权限或整库论文；PR只提交来源记录、原创知识及明确可公开的Markdown译文。

5. 将可复用机制和方法差异合并到已有问题页。只有确有独立问题和论文依据时才新建页；候选方法不能伪装为已核实结论。

## 修改问题页与证据

保留页面稳定 ID；更新日期、摘要、相关页与来源绑定。`problem` 必须维护 `module` 和 `solutions`，方案的 `papers` 指向已登记的 paper 来源，并在 `sources` 绑定对应指纹。字段和模板见 [SCHEMA](SCHEMA.md#按问题学习) 与 [问题页模板](文档/模板/问题模块模板.md)。

比较时写明任务、人群、数据、切分、候选集、指标和资源。不同实验协议的数字不直接排名；离线提升不能代替线上或因果收益。来源冲突保留条件并在 [审核台](维护/审核台.md) 登记，不静默覆盖。

改了来源版本或笔记后，先运行 `python3 scripts/wiki.py plan`。对直接引用页逐条复核，确实完成自查后再按 [工具说明](scripts/README.md) 执行 `integrate`。仅链接/排版变化可以保留已有证据自查，追加本次检查范围；不要只改哈希掩盖未复核的实质变更。

## 生成索引与验证

知识地图与来源目录由脚本生成，请勿手工维护第二份目录。更新正式译文记录后同样生成译文目录。

```bash
python3 scripts/wiki.py plan
python3 scripts/wiki.py index
python3 scripts/translations.py index
python3 scripts/pdf_releases.py index
python3 scripts/wiki.py index --check
python3 scripts/wiki.py lint
python3 scripts/translations.py check
python3 scripts/pdf_releases.py check
python3 scripts/check_context.py
python3 scripts/check_public.py
python3 -m unittest discover -s tests -p 'test_*.py'
git diff --check
```

上述检查不要求 `.local/` 存在，也不联网。原件在本机存在时 `lint` 仍核验其哈希；`lint --local` 是拥有全部快照的维护者额外检查，PR/CI 不运行。普通贡献者只需下载自己实际研究的资料。

## 提交与 Pull Request

只暂存本次明确文件，检查实际内容和暂存差异，提交简短中文说明，再推送自己的分支并从 GitHub 页面发起 PR。

```bash
git add 知识库/问题/你修改的页面.md
git diff --cached
git diff --cached --check
git commit -m "补充某问题的机制与证据"
git push -u origin HEAD
```

PR 说明具体问题、最终变化、依据版本/章节、实际验证和未覆盖范围。使用仓库 PR 模板；维护者检查证据与许可，CI 负责结构和工具行为。CI 通过不等于翻译质量或科研结论已获独立验证。不要上传原件、PDF、LaTeX 工程、渲染图、缓存、个人环境、凭证、样本和权重；小型原创说明图按需明确提交。

请在 GitHub Settings → Emails 查找自己的 noreply 邮箱；Git 的作者/提交者身份与 `gh` 登录独立，CI 会拒绝非 noreply 提交邮箱。不要上传本机用户绝对路径、内网地址或非公开业务资料。日常main统一采用脱敏公开历史，新分支从该main创建；旧私人历史只留本地归档，旧分支独有成果按明确文件迁移，不能直接合并旧祖先或推送归档。详见[主线规则](文档/工具/GitHub共建.md)。

提交贡献表示你有权按 [LICENSE](LICENSE) 中适用的许可分享自己的贡献。第三方引用、图表与全文译文不因贡献动作自动改为本仓库原创许可；请保留原作者及逐篇许可说明。

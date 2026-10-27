# 推荐与搜索系统知识库

围绕推荐与搜索系统，持续把资料与问答编译为可回查、可修订的知识。欢迎通过 GitHub Issue 与 Pull Request 共同建设。传统与生成式方法共用模块和问题主干，营销补贴按因果收益、预算与策略等具体问题接入。主要通过 Codex / Claude Code + Markdown 使用，按需用 Obsidian 浏览。

公开仓库：[Lsiming/recsys-knowledge](https://github.com/Lsiming/recsys-knowledge)。贡献从 [贡献指南](CONTRIBUTING.md) 开始；已核实逐篇许可的正式 Markdown 见 [译文目录](译文/目录.md)。原创知识与文档采用 CC BY 4.0，原创工具采用 MIT，论文与全文译文按各自授权处理，详见 [许可与共享规则](LICENSE)。原文和中文 PDF 统一在独立私有附件仓库维护，公开仓库不再提供 PDF 附件；访问范围见 [PDF目录](译文/PDF目录.md)，有权账号按[私有维护流程](文档/工具/中文PDF发布.md)登录下载。只需 Python 3.9+ 即可执行检查，无需本地论文原件、模型服务或 LaTeX。

日常直接给一篇论文（链接、ID、PDF 或题名），Agent 默认完成 **翻译 → 精读笔记 → 核心知识提炼 → 相关问题与方法比较**，保存结果、核对译文并维护双向引用。后续论文统一沿用 ESMM 已跑通的[标准流程](维护/工作流.md#论文知识沉淀标准流程)，无需指定目录、填写元数据或逐阶段确认。只想翻译/解答时说明即可。

学习从 [推荐系统总图](知识库/总览/推荐系统总图.md) 或自动 [知识地图](知识库/知识地图.md) 进入：**模块 → 问题 → 有哪些解法、差别与条件 → 对应论文精读**。已建立14个推荐模块与[4个搜索模块](知识库/总览/搜索系统总图.md)、[生成式跨模块专题](知识库/总览/生成式推荐专题.md)与 [58 篇论文阅读线索](知识库/阅读/候选论文.md)（首批38篇，新增15篇搜推候选与5篇已精读Transformer基础论文；其中9篇搜索论文已核对摘要并拆解模块问题，待全文精读）。查资料依据进入 [来源目录](来源/来源目录.md)。ESMM、[P5](来源/SRC-P5/阅读笔记.md)、[HSTU](来源/SRC-HSTU-PAPER/阅读笔记.md)、[S-DPO](来源/SRC-SDPO/阅读笔记.md)、[Decoding Matters](来源/SRC-DECODING/阅读笔记.md)、[AtSpeed](来源/SRC-ATSPEED/阅读笔记.md)、[LIGER](来源/SRC-LIGER/阅读笔记.md) 与 [RecBole](来源/SRC-RECBOLE-PAPER/阅读笔记.md) 已有中文 PDF、精读和问题比较（附录等翻译范围见笔记）；BPR、DeepFM、SASRec、DPP、TIGER、LightGCN、MIND、COLD、IntTower、Wide & Deep、DCNv2、DIEN、SIM、PLE、STAR、PEPNet、Seq2Slate、DFM、LinUCB、SlateQ、[LC-Rec](来源/SRC-LCREC/阅读笔记.md)、[OneRec](来源/SRC-ONEREC/阅读笔记.md)、[DiffRec](来源/SRC-DIFFREC/阅读笔记.md)、[GRID实践手册](来源/SRC-GRID-PAPER/阅读笔记.md)、[Gen-RecSys综述](来源/SRC-GENRECSYS-REVIEW/阅读笔记.md) 已有中文 Markdown、精读与问题比较，除 BPR、PLE、DFM 外另保留译后源码，初批处理时均缺中文 PDF。首批38篇已全部尝试：33篇有沉淀（含复用ESMM），其中8篇有中文PDF；其余25篇保留中文Markdown，3篇无可用LaTeX。5篇未取得原文，以上数字是初批处理时的记录，具体交付与失败原因见 [批量任务](文档/会话/PAPER-001.md)。2026-10-27 附件盘点已找到 44 篇现有中文 PDF，44篇均已私有备份（原29篇、迁入的9篇及补齐的6篇），原有9篇公开附件已撤下；另有46份原文PDF私有备份（44篇登记原件、1份未核实STAR镜像及1份额外BERT出版版），最新范围以 [PDF目录](译文/PDF目录.md) 和私有附件目录为准；本次没有合入其他会话的知识正文。

[Transformer基础五篇](知识库/阅读/经典论文路线.md#transformer基础与推荐衔接)已完成正文中文PDF、独立精读与问题比较：Transformer、GPT初代、BERT、BERT4Rec、T5。可沿“Transformer → SASRec → T5 → TIGER”理解自注意力到生成推荐，再补双向恢复与因果预训练分支；译文范围与可编辑工程见各笔记；五篇中文 PDF 均已按统一规则私有备份；T5 的 CC BY 4.0 许可记录保留，私有保存不改变各版本的公开分发权利。

首篇已完成论文为 [ESMM](来源/SRC-ESMM/阅读笔记.md)，从 [点击后转化率估计](知识库/问题/点击后转化率估计.md) 比较点击样本直接训练、概率相除与全空间多任务方案。

知识页与精读笔记写成面向人的技术文章，重点讲清问题、原理、具体解法和方法异同；引用随结论给出，维护记录留在元数据与交接中。

阅读目录、文件名、模块与章节标题优先中文，例如“知识库/模块/召回与检索.md”“知识库/阅读/经典论文路线.md”。论文与模型名、稳定 ID 和工具约定入口保留原文，见 [命名约定](SCHEMA.md#知识页)。

```mermaid
flowchart LR
    P[给一篇论文] --> T[翻译与原文对照]
    T --> N[精读笔记：问题、解法、证据]
    N --> W[模块中的问题与方案比较]
    W --> Q[按问题学习，回查论文]
    Q -->|新理解与纠错| W
```

| 要做什么 | 入口 |
|---|---|
| 学习搜索方向 | [搜索系统总图](知识库/总览/搜索系统总图.md)：查询理解、改写规划、联想补全与相关性验证；当前为9篇摘要驱动框架 |
| 问一个问题、找已有理解 | [知识地图](知识库/知识地图.md)、[按任务选上下文](维护/上下文路由.md) |
| 从经典论文开始学习 | [模块经典与第一轮主线](知识库/阅读/经典论文路线.md)、[Transformer基础与推荐衔接](知识库/阅读/经典论文路线.md#transformer基础与推荐衔接) |
| 先建立模块框架、选择下一篇论文 | [系统总图](知识库/总览/推荐系统总图.md)、[候选阅读](知识库/阅读/候选论文.md)、[GitHub 资源导读](知识库/总览/学习资源导读.md) |
| 给一篇论文，保存完整学习结果 | [论文标准流程与产物位置](维护/工作流.md#论文知识沉淀标准流程)、[来源目录](来源/来源目录.md) |
| 了解字段与证据要求 | [知识契约](SCHEMA.md) |
| 检查矛盾、过时或缺口 | [审核台](维护/审核台.md)、`python3 scripts/wiki.py plan` |
| 接续未完成工作 | [有效任务](TODO.md)、[总交接](SESSION.md) |
| 理解目标与系统取舍 | [长期背景](文档/项目背景.md)、[架构决定](维护/架构决定.md) |
| 查旧设计、工具与实验记录 | [支持文档导航](文档/目录.md) |

知识正文的唯一归属是 `知识库/`；来源身份、版本和阅读笔记在 `来源/<来源ID>/`；规则、路由和审核在 `维护/`；任务与交接记录执行状态。根记忆只保留当前事实及入口，不复制知识正文。目录按实际知识生长，不预建几十个空栏目。

```bash
python3 scripts/wiki.py search "增量摄入"
python3 scripts/wiki.py plan
python3 scripts/wiki.py lint
python3 scripts/wiki.py index --check
python3 scripts/translations.py check
python3 scripts/pdf_releases.py check
python3 scripts/check_context.py
python3 scripts/check_public.py
```

日常检查只用 Python 3 标准库；私有附件下载另需 GitHub CLI 与有权账号，维护者核查 PDF 另需可选依赖；它登记、检索和检查，不调用模型或自动判定论文真伪。完整命令、原件恢复及验收见 [工具说明](scripts/README.md)。本仓库通过 GitHub 分支与 PR 共建；默认自查后用中文提交明确文件，远端操作遵循具体授权。知识、来源记录、许可确认的正式 Markdown 译文和工具入 Git；PDF、LaTeX、快照、渲染、运行库与个人配置不入 Git。原件快照在忽略的 `.local/sources/`，原文 PDF 在私有附件库按原字节备份；LaTeX 等其他原件仍需单独备份，Git 中的哈希不能代替原件。正文内行内代码形式的 `.local/` 路径是本地附件；公共阅读使用固定版本原文链接。

# PAPER-010 第 07–10 批论文精读

2026-11-22 在日常 main 推进[第 07–10 批](../../知识库/阅读/论文分批精读路线.md#batch-07)。12 篇既有笔记重读并补图，10 篇补读已形成技术精读。2026-11-23 全部 22 篇完成。各批次入口以路线为准。

| 批次 | 已回写的问题 | 交付状态 |
|---|---|---|
| 07 显式交叉、字段注意力与粗排表达 | [稀疏特征交互](../../知识库/问题/稀疏特征的低高阶交互学习.md)、[粗排预算](../../知识库/问题/粗排如何在计算预算内保留精排候选.md) | 本批三份新译文均已验收和备份，既有附件复核见文末 |
| 08 候选感知兴趣与级联预算 | [长历史压缩](../../知识库/问题/长历史怎样在候选条件下压缩计算.md)、[粗排预算](../../知识库/问题/粗排如何在计算预算内保留精排候选.md) | Que2Search 与 TWIN 译文、精读和附件均完成 |
| 09 转化漏斗、多任务共享与损失权重 | [点击后转化](../../知识库/问题/点击后转化率估计.md)、[多任务共享](../../知识库/问题/多任务共享如何避免负迁移.md) | 已完成 |
| 10 多场景共享与新品适配 | [多场景共享](../../知识库/问题/多场景怎样共享模型又保留差异.md)、[新品初始化与反馈适配](../../知识库/问题/新品怎样用属性初始化并从少量反馈适配.md) | M3REC、MAML 与 Meta-Embedding 译文、精读和附件均完成 |

在已有原件上补作者原图 26 张，首次精读补 16 张。顺读样本输入、状态、训练监督及上线读出，并复算了向量交叉、字段注意力、兴趣写入、最小范数及元梯度示例。全库反查以 20 个来源与方法名定位 23 个直接绑定页、4 个正文提及页、49 个相关页及 9 篇其他笔记，重点复核会传播批次结论的入口。原文问题包括 ESCM² 定理 1 的预测独立假设、CAN 诱导与馈入侧指派冲突、TWIN 图文日志数量单位不一致，见[审核台](../../维护/审核台.md)。由当前 Agent 自查，未运行模型实验。

Que2Search 与 M3REC 的题名、作者和 DOI 已与 Crossref 核对。出版方 PDF 和 ePDF 请求返回 403，Semantic Scholar、OpenAlex 和 Unpaywall 未提供可用的独立全文地址。2026-11-23 从 ACM eReader 下载正式会议 PDF，两篇均可解析，核对 DOI 与题名页。Que2Search 为 KDD 2021 第 3376–3384 页，M3REC 为 RecSys 2023 第 771–776 页。两篇译文、原图与精读已交付。

十篇新来源 PDF 均可解析。MGDA 的 arXiv 源码已完整取得并逐个解包。ESCM² 和 MAML 的采用版 PDF 已从固定版本独立重下，SHA-256 均与冻结快照一致。两篇源码也均完整独立重下，SHA-256 与原有快照一致。既有 12 份中文 PDF 的本地文件可解析且可提取中文，沿用既有排版验收记录，没有重做逐页检查。既有 12 篇的 24 份原、译 PDF 已全部完成认证重新下载，逐份核对 SHA-256 后清理临时核验件。DIN 的原、译两份用认证资产 API 完成完整下载。

精读阶段通过知识索引、来源快照、双向导航、Markdown 译文登记和 PDF 目录检查。实际从来源 ID、方法别名和问题题名检索到正文。候选总表超过 200 行的结构提醒仍保留。最终 10 篇新增中文 PDF 逐页检查共 94 页，20 份新增原译附件与 24 份既有附件均通过真实认证下载和完整 SHA-256 核验。

DCN v1 的 7 页采用版原文和 6 页中文正文译本均完成私有备份及首次认证下载核验。译文逐页目视，核对公式、四表、三图和引文，支持中文提取。 本地正式件位于 `.local/papers/SRC-DCN/translation/Deep & Cross Network for Ad Click Predictions.pdf`，译文 SHA-256 为 `ded6ba243ec0033228025161b41f275fbba804642e5b0c49db3e83d533033a43`。远程 LuaLaTeX 编译失败后改用本地 XeLaTeX 与系统中文字体，图由采用版 PDF 矢量裁取，保持双栏。附录、参考文献与图内文字保留原文。

AutoInt v2 的 10 页采用版原文和 8 页中文正文与致谢译本均完成私有备份和首次认证下载核验。译文逐页目视，核对 10 个编号公式、五张表、七张图和引文。 本地正式件位于 `.local/papers/SRC-AUTOINT/translation/AutoInt Automatic Feature Interaction Learning via Self-Attentive Neural Networks.pdf`，译文 SHA-256 为 `73b871e9f69de9ca68415bcfbc5be435593842b30b609699c81800a8b9e8f966`。远程 LuaLaTeX 超时后改用本地 XeLaTeX，保留作者双栏模板、原图和 ACM 声明。正式采用版无附录，LaTeX 中未引入的 appendix.tex 未纳入译本。

CAN v3 的 9 页采用版原文和 7 页中文正文译本均完成私有备份和首次认证下载核验。译文逐页目视，核对 13 个编号公式、六张表、五张图和引文。 本地正式件位于 `.local/papers/SRC-CAN/translation/CAN Feature Co-Action for Click-Through Rate Prediction.pdf`，译文 SHA-256 为 `c2a70ca46d4d02aece86ae6a16d9bf0f7faaf2d12b66b9e74d7e76644581d777`。本地 XeLaTeX 用兼容版 acmart 解决旧模板冲突，保留双栏、WSDM 声明和原图，移除译本中一处继承的图片构建路径。固定公开代码复核了候选侧供参和逐行为池化，未运行模型。

TWIN v2 的 10 页采用版原文和 8 页中文正文译本均完成私有备份和首次认证下载核验。译文逐页目视，核对 8 个编号公式、五张表、六张图和 37 条参考文献。 本地正式件位于 `.local/papers/SRC-TWIN/translation/TWIN TWo-stage Interest Network for Lifelong User Behavior Modeling in CTR Prediction at Kuaishou.pdf`，译文 SHA-256 为 `242939aecad5fe8522f2df2193de3ab3901192b402e2c0eb3539859298609e07`。本地 XeLaTeX 用兼容版 acmart 解决旧模板冲突，保留双栏、KDD 声明和原图。采用版源码中的附录被条件语句关闭，固定 PDF 也未收录。图 4 按各模型自己的 ESU Oracle 口径回填知识正文。

Meta-Embedding v1 的 10 页采用版原文和 9 页中文正文译本均完成私有备份和首次认证下载核验。译文逐页目视，核对 17 个编号公式、两张表、八张图、算法 1 和 46 条参考文献。 本地正式件位于 `.local/papers/SRC-META-EMBEDDING/translation/Warm Up Cold-start Advertisements Improving CTR Predictions via Learning to Learn ID Embeddings.pdf`，译文 SHA-256 为 `2c36f360a9b25433c7c7c082dedd3ce9e3c05a077773d6fa48a6f2d7b6289cc1`。本地 XeLaTeX 用兼容版 acmart 解决旧模板冲突，保留双栏、SIGIR 声明和原图。采用版首页 DOI 与 ISBN 为模板占位，Crossref 核对 SIGIR 2019 正式 DOI 10.1145/3331184.3331268。按 MAML 算法 1 区分共享元初始化与任务适配后参数。

ESCM² v2 的 10 页采用版原文和 9 页中文正文译本均完成私有备份和首次认证下载核验。译文逐页目视，核对 27 个编号公式、五张表、七张图和 28 条参考文献。 本地正式件位于 `.local/papers/SRC-ESCM2/translation/ESCM2 Entire Space Counterfactual Multi-Task Model for Post-Click Conversion Rate Estimation.pdf`，译文 SHA-256 为 `1860322e91ccbbaf77486fdd77da1753a1c781ba91b05b69668fe6311ed20793`。本地 XeLaTeX 用兼容版 acmart 解决旧模板冲突，保留双栏、SIGIR 声明和原图。翻译致谢和实现附录。PDF、源码分别完整重下，与此前快照同哈希。arXiv 许可页与 ACM 声明均保留。

MAML v3 的 13 页采用版原文和 11 页中文译本均完成私有备份和首次认证下载核验。译文逐页目视，核对 4 个编号公式、五张表、七张图、三段算法和 40 条参考文献。 本地正式件位于 `.local/papers/SRC-MAML/translation/Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks.pdf`，译文 SHA-256 为 `2be14525da2441cd5a2b49462de64e5b7cb74a5dcbf3747dc51e570290e45df9`。本地 XeLaTeX 修复旧模板的链接宏冲突，保留 ICML 双栏。图 1 从采用版 PDF 矢量裁取以保留图层。附录 A–C 已翻译。式 (3) 缺交叉熵负号，译文保留印式并加译注。

MGDA v2 的 15 页采用版原文和 14 页中文译本均完成私有备份和首次认证下载核验。译文逐页目视，核对 12 个编号公式、MGDA-UB 命名式、五张表、八张图、两段算法和 60 条参考文献。 本地正式件位于 `.local/papers/SRC-MGDA/translation/Multi-Task Learning as Multi-Objective Optimization.pdf`，译文 SHA-256 为 `71c910bfe05d6f2cff185705bdca18ceb96f9c5e2fdeeba39ce0eeaa0ce2b935`。远程 LuaLaTeX 试编失败后使用本地 XeLaTeX。保留附录 A–C 原文。固定 v2 作者源码已按上游压缩包原字节登记。译注及读书笔记核对附录 A 的共同下降证明，并用二维满秩反例说明适用边界。

Que2Search 的 9 页 ACM 正式原件与 13 页中文正文译本均已通过首次认证下载核验。本地正式译本为 `.local/papers/SRC-QUE2SEARCH/translation/Que2Search Fast and Accurate Query and Document Understanding for Search at Facebook.pdf`，SHA-256 为 `ded8b7586a939265b396b1c212b9e5b475e4909b2a0b8065b227c5132661fec2`。13 页逐页渲染目视，核对 6 个编号公式、5 表共 28 个数值、5 个作者原图、29 条参考文献、ACM 权利声明。编译版与元数据清理版的各页文字与渲染像素相同。已保留逐节对照 Markdown 和可编辑重排工程，图中文字与参考文献保留原文。

M3REC 的 6 页 ACM 正式原件与 9 页中文正文译本均已通过首次认证下载核验。本地正式译本为 `.local/papers/SRC-M3REC/translation/M3REC A Meta-based Multi-scenario Multi-task Recommendation Framework.pdf`，SHA-256 为 `570605a4a7f45e39185f119af69de42f691edcc2f90bcda2ef8ebcdf8e4db851`。9 页逐页渲染目视，核对 15 个编号公式、4 表共 320 个数值、2 个作者原图、19 条参考文献、ACM 权利声明。编译版与元数据清理版的各页文字与渲染像素相同。已保留逐节对照 Markdown 和可编辑重排工程，图中文字与参考文献保留原文。

最后两篇共新增 6 张作者原图。复查范围包括多场景共享、新品适配、粗排预算、双塔负采样及相邻 ANN 问题。核对 M3REC 的 TAG 行 Softmax 和表 2、Que2Search 的式 (4)、式 (6) 与表 3–5，问题页链接唯一解释和正式原文。

合并 22 个来源复跑全库反查，定位 24 个直接绑定页、6 个正文提及页、46 个关联候选页与 9 篇其他笔记。复核集中在传播本批结论的陈述与入口。以两篇完整题名、方法别名和问题题名分别查询，核对模块到问题、问题到精读、精读返回问题的路径。结构检查通过，候选总表仍有长度提示。

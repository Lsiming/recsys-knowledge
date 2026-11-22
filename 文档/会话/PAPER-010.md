# PAPER-010 第 07–10 批论文精读

2026-11-22 在日常 main 推进[第 07–10 批](../../知识库/阅读/论文分批精读路线.md#batch-07)。12 篇既有笔记重读并补图，8 篇补读已形成技术精读，2 篇等待全文。各批次入口以路线为准。

| 批次 | 已回写的问题 | 待完成 |
|---|---|---|
| 07 显式交叉、字段注意力与粗排表达 | [稀疏特征交互](../../知识库/问题/稀疏特征的低高阶交互学习.md)、[粗排预算](../../知识库/问题/粗排如何在计算预算内保留精排候选.md) | 本批三份新译文均已验收和备份，既有附件复核见文末 |
| 08 候选感知兴趣与级联预算 | [长历史压缩](../../知识库/问题/长历史怎样在候选条件下压缩计算.md)、[粗排预算](../../知识库/问题/粗排如何在计算预算内保留精排候选.md) | Que2Search 全文，既有附件复核见文末 |
| 09 转化漏斗、多任务共享与损失权重 | [点击后转化](../../知识库/问题/点击后转化率估计.md)、[多任务共享](../../知识库/问题/多任务共享如何避免负迁移.md) | ESCM²、MGDA 翻译与附件 |
| 10 多场景共享与新品适配 | [多场景共享](../../知识库/问题/多场景怎样共享模型又保留差异.md)、[新品初始化与反馈适配](../../知识库/问题/新品怎样用属性初始化并从少量反馈适配.md) | MAML 翻译与附件，M3REC 全文 |

在已有原件上补作者原图 26 张，首次精读补 16 张。顺读样本输入、状态、训练监督及上线读出，并复算了向量交叉、字段注意力、兴趣写入、最小范数及元梯度示例。全库反查以 20 个来源与方法名定位 23 个直接绑定页、4 个正文提及页、49 个相关页及 9 篇其他笔记，重点复核会传播批次结论的入口。原文问题包括 ESCM² 定理 1 的预测独立假设、CAN 诱导与馈入侧指派冲突、TWIN 图文日志数量单位不一致，见[审核台](../../维护/审核台.md)。由当前 Agent 自查，未运行模型实验。

Que2Search 与 M3REC 的题名、作者和 DOI 已与 Crossref 核对。出版方 PDF 和 ePDF 请求返回 403，Semantic Scholar、OpenAlex 和 Unpaywall 未提供可用的独立全文地址。拿到正式会议 PDF 或作者版后，先核对身份及版本，再补图、译文和知识比较。

八篇新来源 PDF 均可解析。MGDA 的 arXiv 源码已完整取得并逐个解包。ESCM² 和 MAML 的采用版 PDF 已从固定版本独立重下，SHA-256 均与冻结快照一致。两篇源码先经 HTTP 字节区间完整解包，正在独立下载复验。既有 12 份中文 PDF 的本地文件可解析且可提取中文，沿用既有排版验收记录，没有重做逐页检查。既有 12 篇的 24 份原、译 PDF 已全部完成认证重新下载，逐份核对 SHA-256 后清理临时核验件。DIN 的原、译两份用认证资产 API 完成完整下载。

精读阶段通过知识索引、来源快照、双向导航、Markdown 译文登记和 PDF 目录检查。实际从来源 ID、方法别名和问题题名检索到正文。候选总表超过 200 行的结构提醒仍保留。中文 PDF 与认证下载继续按上表推进。

DCN v1 的 7 页采用版原文和 6 页中文正文译本均完成私有备份及首次认证下载核验。译文逐页目视，核对公式、四表、三图和引文，支持中文提取。 本地正式件位于 `.local/papers/SRC-DCN/translation/Deep & Cross Network for Ad Click Predictions.pdf`，译文 SHA-256 为 `ded6ba243ec0033228025161b41f275fbba804642e5b0c49db3e83d533033a43`。远程 LuaLaTeX 编译失败后改用本地 XeLaTeX 与系统中文字体，图由采用版 PDF 矢量裁取，保持双栏。附录、参考文献与图内文字保留原文。

AutoInt v2 的 10 页采用版原文和 8 页中文正文与致谢译本均完成私有备份和首次认证下载核验。译文逐页目视，核对 10 个编号公式、五张表、七张图和引文。 本地正式件位于 `.local/papers/SRC-AUTOINT/translation/AutoInt Automatic Feature Interaction Learning via Self-Attentive Neural Networks.pdf`，译文 SHA-256 为 `73b871e9f69de9ca68415bcfbc5be435593842b30b609699c81800a8b9e8f966`。远程 LuaLaTeX 超时后改用本地 XeLaTeX，保留作者双栏模板、原图和 ACM 声明。正式采用版无附录，LaTeX 中未引入的 appendix.tex 未纳入译本。

CAN v3 的 9 页采用版原文和 7 页中文正文译本均完成私有备份和首次认证下载核验。译文逐页目视，核对 13 个编号公式、六张表、五张图和引文。 本地正式件位于 `.local/papers/SRC-CAN/translation/CAN Feature Co-Action for Click-Through Rate Prediction.pdf`，译文 SHA-256 为 `c2a70ca46d4d02aece86ae6a16d9bf0f7faaf2d12b66b9e74d7e76644581d777`。本地 XeLaTeX 用兼容版 acmart 解决旧模板冲突，保留双栏、WSDM 声明和原图，移除译本中一处继承的图片构建路径。固定公开代码复核了候选侧供参和逐行为池化，未运行模型。

TWIN v2 的 10 页采用版原文和 8 页中文正文译本均完成私有备份和首次认证下载核验。译文逐页目视，核对 8 个编号公式、五张表、六张图和 37 条参考文献。 本地正式件位于 `.local/papers/SRC-TWIN/translation/TWIN TWo-stage Interest Network for Lifelong User Behavior Modeling in CTR Prediction at Kuaishou.pdf`，译文 SHA-256 为 `242939aecad5fe8522f2df2193de3ab3901192b402e2c0eb3539859298609e07`。本地 XeLaTeX 用兼容版 acmart 解决旧模板冲突，保留双栏、KDD 声明和原图。采用版源码中的附录被条件语句关闭，固定 PDF 也未收录。图 4 按各模型自己的 ESU Oracle 口径回填知识正文。

Meta-Embedding v1 的 10 页采用版原文和 9 页中文正文译本均完成私有备份和首次认证下载核验。译文逐页目视，核对 17 个编号公式、两张表、八张图、算法 1 和 46 条参考文献。 本地正式件位于 `.local/papers/SRC-META-EMBEDDING/translation/Warm Up Cold-start Advertisements Improving CTR Predictions via Learning to Learn ID Embeddings.pdf`，译文 SHA-256 为 `2c36f360a9b25433c7c7c082dedd3ce9e3c05a077773d6fa48a6f2d7b6289cc1`。本地 XeLaTeX 用兼容版 acmart 解决旧模板冲突，保留双栏、SIGIR 声明和原图。采用版首页 DOI 与 ISBN 为模板占位，Crossref 核对 SIGIR 2019 正式 DOI 10.1145/3331184.3331268。按 MAML 算法 1 区分共享元初始化与任务适配后参数。

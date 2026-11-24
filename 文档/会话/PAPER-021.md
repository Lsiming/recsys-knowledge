# PAPER-021 · Push 时机、用户响应与长期策略

按[第 21 批](../../知识库/阅读/论文分批精读路线.md#batch-21)执行。七篇原文已取得，四篇采用 arXiv 固定 v1，分别保留了未经改动的源码目录与原压缩包。研究与翻译本地工作件归 `.local/paper-batch-21/`，可编辑译后工程及正式 PDF 归 `.local/papers/<来源ID>/translation/`。

| 论文 | 固定版本与当前进展 |
|---|---|
| TIM | [笔记](../../来源/SRC-TIM/阅读笔记.md)增加图 1 与图 2 两个子图以及贯穿算例。既有 4 页中文 PDF 重新逐页渲染目视，两份附件通过认证下载、完整 SHA-256 核验并自动清理。已复核配额问题、模块和阅读路线并重做整合。 |
| TSIL | [笔记](../../来源/SRC-TSIL/阅读笔记.md)核对 SIGIR 2026 Industry Track 的 6 页 CC BY 4.0 版本，采用作者 GitHub 固定提交保存的出版 PDF。两张作者原图已登记。9 页中文正文 PDF 已逐页看图及提取文字，连同六表、原文参考文献及译注；SHA-256 为 `b85f9a01d8f276772cf5b02690376c7c1c2093ffb4e98dde9a5f32537e339a22`。已接到因果模块和月初 Push 场景。原译件已在私有 Release 认证下载并校验 SHA-256。 |
| DeepPvisit | [笔记](../../来源/SRC-DEEPPVISIT/阅读笔记.md)核对 ACM WWW 2023 Companion 正式 5 页 PDF，登记两个作者图。8 页 XeLaTeX 正文译本逐页渲染目视，核对八式、两图、线上表和 20 条参考文献；SHA-256 为 `a1f4721e2b1dcb3c1a7cc4210c835797ad6040c7526722db8f51061720fd3dc7`。月初 Push 场景已回链。两份 PDF 已在私有 Release 认证下载并校验 SHA-256。 |
| Offline Reinforcement Learning for Mobile Notifications | [笔记](../../来源/SRC-LINKEDIN-NOTIFICATION-RL/阅读笔记.md)核对固定 `2202.03867v1`、CIKM 2022 DOI 10.1145/3511808.3557083。作者模板的远端 LuaLaTeX 字库初始化超时后，用本地 XeLaTeX 和同一 IEEEtran 排版编译，逐页渲染并提取核对 8 页正文、五图、表 I 和 44 条参考文献。译文 SHA-256 为 `1a685163dbfe14bbee45f7d2ab1ff29a7dc3ce82ae00774d2d1a706c93bc264f`。笔记嵌入四个关键作者原图，勘误离线评估中密度比分母和一步条件方向。原件与译文的资产 ID 787543168、787543371，已登录下载并校验完整 SHA-256。 |
| Multi-objective Optimization of Notifications Using Offline Reinforcement Learning | [笔记](../../来源/SRC-LINKEDIN-NOTIFICATION-MORL/阅读笔记.md)核对 arXiv:2207.03029v1，KDD 2022 DOI 10.1145/3534678.3539193。远端 LuaLaTeX 超时后沿用 ACM 模板在本地 XeLaTeX 编译，7 页中文译文逐页目视、核对可提取文字、六图两表、算法、13 个编号公式和 38 条参考文献。译文 SHA-256 为 fd7143221522d96a9e4bdebc6578cd51f19547c66831069edbc623bfde7a5ede。图 4 的发送量权衡及图 6 实际坐标已对照，原文逐步 IS 权重重复除样本数等处保留并加译注。资产 787578419、787578646 已登录下载并校验完整 SHA-256。 |
| Generative Sequential Notification Optimization via Multi-Objective Decision Transformers | `2509.02458v1`，8 页采用版，`decision-transformer/`，主文件 `main.tex` 经 `sections/` 加载正文。[精读](../../来源/SRC-LINKEDIN-NOTIFICATION-DT/阅读笔记.md)及 12 页正式中文正文 PDF 已完成。保留四图、三表、十式与 36 条参考文献。远端编译和本地 ACM 模板报错后用 XeLaTeX 单栏重排并逐页目视，核对中文提取。译文 SHA-256 为 `120d16af57f0417b7279323ac845b36ce29989893509742e39442fd1c8a3faf7`。资产 ID 787487070 和 787492449 已登录下载并校验完整 SHA-256。固定 v1 标 Under review，许可为 CC BY 4.0。 |
| Should I send this notification? | [笔记](../../来源/SRC-TWITTER-NOTIFICATION-RL/阅读笔记.md)核对 9 页固定 v1、三图、表 1、伪代码和附录 A。远端超时，旧 ACM 模板存在宏包顺序、子图引用和超宽公式，保留正文改为本地 XeLaTeX 单栏。正式 PDF 12 页均目视核对，正文可提取，附录、图内英文与参考文献保留。译文 SHA-256 为 72f4cf670733b20494d89531c4fb3508747eac6804ffd3d2430d10ced9eb560c。两份附件资产 ID 787634338、787634552。 |

已在[动态发送问题](../../知识库/问题/通知候选到达后怎样决定发送或等待.md)对照条件访问窗、固定检查点、近实时不等间隔、显式响应状态和回报提示。固定频次干预与按日预规划归入[优惠 Push 场景](../../知识库/总览/优惠信息Push触达场景.md)。审核台保留原文公式、数值与图示范围的待核项。未执行作者代码、训练或业务复现实验。

私有 Release ID 456834085、456834199，标签分别为 private-original-pdfs-20261124-batch-21-21 和 private-zh-pdfs-20261124-batch-21-21，均已启用。12 份新增 PDF 与两份 TIM 既有资产均真实登录下载，核对 PDF 类型、远端摘要、字节数和完整 SHA-256。核验副本自动清理。六篇新增译文共 56 页，另复验 TIM 既有译文 4 页。两库本地目录已依据实际收据更新。上一批私有目录基线为 4bdb8c3。

本批七个来源均完成全库反查与当前 Agent 的技术证据和读者路径自查。知识计划返回空列表；来源索引、正式译文和 PDF 目录一致，检索可用来源 ID、“状态边缘化重要性采样”和“发送或等待”进入问题与模块。检查了原图字节及说明、问题与阅读笔记的双向入口。结构检查仅有候选书目长页的既有提示。私有目录与 268 份远端正式 PDF 一致，附件工具 10 项测试通过。

启动时公开远端 main 为 74d1352，私有为 4bdb8c3。日常工作区先有独立的营销补贴清单提交 30151e7。本轮公开提交从已核实的远端基线独立构建，只纳入第 21 批内容，两个项目的推送及 CI 以远端 SHA 核验为准。

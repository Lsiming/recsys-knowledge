# 营销补贴第 9–10 批论文精读

2026-11-27 恢复。日常 `main` 基线为 `6306b2c`，公开 `origin/main` 与 GitHub 同为 `76632b0`，私有工作副本和 GitHub 同为 `d56c116`。前者已有其他会话的一份 E3IR 澄清；本批发布时按授权隔离。 [第 9–10 批清单](../../知识库/阅读/营销补贴待读论文.md#剩余论文分批建议)

- 已取得并解析 Causal Tree、Causal Forest、GRF、Uplift 树分裂、CTS、VAE、CEVAE、TED-VAE、CLUB 的固定原文。Uplift 树分裂为 Springer 正式刊版，其余完整流程项现有匹配的 arXiv LaTeX。各版本、PDF 页数、原字节 SHA-256 和主文件见本地 `.local/marketing-batch-09-10/sources.json`。七篇作者源码已原样另存并建立可编辑副本。四篇尚待翻译的树模型均有可核对的原文，其中 Causal Tree、Causal Forest、GRF 采用作者 LaTeX 副本，Uplift 树分裂采用 Springer 版重排。
- VAE、CEVAE 中文译本分别为 13 页、11 页，共 8 张关键作者原图。XeLaTeX 初稿的中文字体缺少 ToUnicode，Poppler 无法稳定显示。两篇均以 LuaLaTeX 重编，复验字体嵌入、ToUnicode、中文提取和全部 24 页 Poppler 渲染，原译件均通过认证下载和完整 SHA-256 核对。初稿资产已撤下。私有账本 `21c3dd6` 已同步，CI `45934227880` 通过，360 份正式 PDF 与 Releases 对账一致。 [VAE 精读](../../来源/SRC-VAE/阅读笔记.md) · [CEVAE 精读](../../来源/SRC-CEVAE/阅读笔记.md)
- CLUB 已按清单完成仅解读。固定 PMLR 版已冻结并登记，三张作者原图已目视检查。笔记给出 vCLUB 的两个 KL 差和同索引项的有限样本分析，同步回填 MIM-DRCFR 和历史发券问题。已运行 plan、索引复核、lint 和上下文检查。三条长页提醒来自已有页面。 [CLUB 精读](../../来源/SRC-CLUB/阅读笔记.md) · [历史发券比较](../../知识库/问题/历史发券日志如何估计补贴增量.md#应该让两组在哪些特征上可比)
- GANITE 已对照 ICLR 2018 官方会议信息与作者仓库确认题名、作者和 OpenReview ID。OpenReview PDF 和两个版本的公开 API 返回 403，论坛及内置浏览器的固定 PDF 入口返回浏览器验证页，替代搜索页面超时。待继续找可核对的作者全文入口。 [ICLR 2018 会议记录](https://iclr.cc/Conferences/2018/Schedule?showEvent=153) · [作者仓库](https://github.com/jsyoon0823/GANITE)

- TED-VAE 与 CTS 已完成两轮精读自查及各 7 页正文译本。四张 TED-VAE 作者图和 CTS 的五张作者图及算法框均嵌入对应机制处。LuaLaTeX 内嵌字体均有 ToUnicode，最终版逐页用 Poppler 核对。TED-VAE 回填历史发券页，CTS 回填策略价值及组合策略问题页。已复核三处直接引用、阅读入口、相邻方法与 E3IR 所引用的随机日志估计式。源内分母和评估端点疑问已记审核台。 [TED-VAE 精读](../../来源/SRC-TED-VAE/阅读笔记.md) · [CTS 精读](../../来源/SRC-CTS/阅读笔记.md)
- 四份 TED-VAE 与 CTS 原译件已认证下载核对大小及完整 SHA-256，临时下载自动清理。TED-VAE 私有提交 `d8f72d9` 的 CI `45936238365` 成功，CTS 私有提交 `6c16804` 的 CI `45937397131` 成功。全部 364 份正式 PDF 与私有 Releases 对账通过。

- Causal Tree 已完成精读和 17 页中文正文 PDF。再次目视核对重排受影响的第 7–13 页，并复查采用版 §3–4、表 1 与表 A1 的符号、变换结果和误差比方向。以译注保留原印式，疑问已记审核台。原译件均已认证下载核验大小和 SHA-256，临时下载已清理。私有目录与 GitHub main 同为 `10d09e9`，CI `45967356447` 已通过。 [Causal Tree 精读](../../来源/SRC-CAUSAL-TREE/阅读笔记.md)

- Causal Tree 及此前首组知识经隔离发布到公开 `f986a6c`，CI `45968441404` 通过。日常 main 对齐该版本后重放原有本地 E3IR 澄清，核对文件树相同，原提交链留在本地归档。
- Causal Forest 固定 2017 年 7 月 11 日的 arXiv v4，完成 36 页正文译本和精读。五幅作者原图对应双样本树、倾向树、方差诊断、效应峰值和边界模拟。核对式 (5)、(8)、(24)、定理 11 及三组模拟的覆盖与误差，并回填历史发券和评估两页。原译件经实际认证下载校验，私有提交 `a19f77f` 与远端一致，368 份正式 PDF 对账通过。 [Causal Forest 精读](../../来源/SRC-CAUSAL-FOREST/阅读笔记.md)


## 第 9–10 批最终交付

2026-11-28 核对完成。第 9 批为 Causal Tree、Causal Forest、GRF、Uplift 树分裂、CTS，第 10 批为 VAE、CEVAE、TED-VAE、GANITE 与只解读的 CLUB。共十篇精读、九份正文中文 PDF、40 张嵌入笔记的作者图表或算法框。 [待读清单](../../知识库/阅读/营销补贴待读论文.md#剩余论文分批建议)

| 批次 | 论文 | 中文 PDF 页数 |
|---|---|---:|
| 09 | Causal Tree、Causal Forest、GRF、Uplift 树分裂、CTS | 17、36、36、21、7 |
| 10 | VAE、CEVAE、TED-VAE、GANITE | 13、11、7、23 |
| 10 | CLUB | 按清单仅解读 |

- [GRF](../../来源/SRC-GRF/阅读笔记.md)用同一两树例比较逐树平均的 10 个百分点和先合并权重再解局部矩的 8.73。核对局部中心化、分位数与小袋方差。最终译本去掉作者模板构建页脚，并校验纸面内容与已核对的前版像素一致。
- [Uplift 树分裂](../../来源/SRC-UPLIFT-TREE/阅读笔记.md)按 Springer 固定刊版重排，保留四幅作者图、两张数据表及英文附录。核对散度分裂、验证集剪枝、动作匹配评估及多处理权重边界，和 Causal Tree、CTS 比较。原刊注明 CC BY-NC，译文仍以私有 PDF 维护。
- [GANITE](../../来源/SRC-GANITE/阅读笔记.md)采用 GitHub 固定提交保存的 22 页 ICLR 2018 会议版镜像。题名、作者、会议信息与官方题录一致。OpenReview 仍返回访问验证，无法核对两份文件是否字节一致。译本覆盖全部正文，附录维持英文。论文两阶段对抗结构与作者公开的二元三网络实现分开记录。回查 MIL 与 TED-VAE 的基线引用，区分各自样本、指标和实验协议。 [固定镜像](https://github.com/gasanchez10/freganv2/blob/3037720047e4cdd02d11394ff77919f93ce385df/Papers_elegidos/588_ganite_estimation_of_individua%20%281%29.pdf) · [会议题录](https://iclr.cc/Conferences/2018/Schedule?showEvent=153)
- 反查六个直接引用问题页及营销模块、相关总览和旧论文对照。两轮自查涵盖公式、算例、图表、证据定位与阅读路径。以题名、别名、问题和方法检索核对 24 个入口，题名索引可直达论文，问题页和精读笔记可互查。未进行模型复现或独立审查。
- 171 页译文逐页渲染检查，九对正式原译件已实际认证下载并校验完整 SHA-256，临时下载自动清理。私有目录推进到 `e58ae92`，374 份正式 PDF 与 Releases 对账一致，匿名访问返回 404，私有 CI 通过。 [私有 CI](https://github.com/Lsiming/recsys-knowledge-attachments/actions/runs/46108344664) · [PDF 访问说明](../工具/中文PDF发布.md)
- 公开发布以上一远端 `36e85b4` 为基线整合 GRF、Uplift 树分裂和 GANITE 的当轮内容；日常 main 上另一会话的 E3IR 澄清保留在本地。

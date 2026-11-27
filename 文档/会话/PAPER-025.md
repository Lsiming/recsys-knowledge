# 营销补贴第 9–10 批论文精读

2026-11-27 恢复。日常 `main` 基线为 `6306b2c`，公开 `origin/main` 与 GitHub 同为 `76632b0`，私有工作副本和 GitHub 同为 `d56c116`。前者已有其他会话的一份 E3IR 澄清；本批发布时按授权隔离。 [第 9–10 批清单](../../知识库/阅读/营销补贴待读论文.md#剩余论文分批建议)

- 已取得并解析 Causal Tree、Causal Forest、GRF、Uplift 树分裂、CTS、VAE、CEVAE、TED-VAE、CLUB 的固定原文。Uplift 树分裂为 Springer 正式刊版，其余完整流程项现有匹配的 arXiv LaTeX。各版本、PDF 页数、原字节 SHA-256 和主文件见本地 `.local/marketing-batch-09-10/sources.json`。七篇作者源码已原样另存并建立可编辑副本。四篇尚待翻译的树模型均有可核对的原文，其中 Causal Tree、Causal Forest、GRF 采用作者 LaTeX 副本，Uplift 树分裂采用 Springer 版重排。
- VAE、CEVAE 中文译本分别为 13 页、11 页，共 8 张关键作者原图。XeLaTeX 初稿的中文字体缺少 ToUnicode，Poppler 无法稳定显示。两篇均以 LuaLaTeX 重编，复验字体嵌入、ToUnicode、中文提取和全部 24 页 Poppler 渲染，原译件均通过认证下载和完整 SHA-256 核对。初稿资产已撤下。私有账本 `21c3dd6` 已同步，CI `45934227880` 通过，360 份正式 PDF 与 Releases 对账一致。 [VAE 精读](../../来源/SRC-VAE/阅读笔记.md) · [CEVAE 精读](../../来源/SRC-CEVAE/阅读笔记.md)
- CLUB 已按清单完成仅解读。固定 PMLR 版已冻结并登记，三张作者原图已目视检查。笔记给出 vCLUB 的两个 KL 差和同索引项的有限样本分析，同步回填 MIM-DRCFR 和历史发券问题。已运行 plan、索引复核、lint 和上下文检查。三条长页提醒来自已有页面。 [CLUB 精读](../../来源/SRC-CLUB/阅读笔记.md) · [历史发券比较](../../知识库/问题/历史发券日志如何估计补贴增量.md#应该让两组在哪些特征上可比)
- GANITE 已对照 ICLR 2018 官方会议信息与作者仓库确认题名、作者和 OpenReview ID。OpenReview PDF 和两个版本的公开 API 返回 403，论坛及内置浏览器的固定 PDF 入口返回浏览器验证页，替代搜索页面超时。待继续找可核对的作者全文入口。 [ICLR 2018 会议记录](https://iclr.cc/Conferences/2018/Schedule?showEvent=153) · [作者仓库](https://github.com/jsyoon0823/GANITE)

- TED-VAE 与 CTS 已完成两轮精读自查及各 7 页正文译本。四张 TED-VAE 作者图和 CTS 的五张作者图及算法框均嵌入对应机制处。LuaLaTeX 内嵌字体均有 ToUnicode，最终版逐页用 Poppler 核对。TED-VAE 回填历史发券页，CTS 回填策略价值及组合策略问题页。已复核三处直接引用、阅读入口、相邻方法与 E3IR 所引用的随机日志估计式。源内分母和评估端点疑问已记审核台。 [TED-VAE 精读](../../来源/SRC-TED-VAE/阅读笔记.md) · [CTS 精读](../../来源/SRC-CTS/阅读笔记.md)
- 四份 TED-VAE 与 CTS 原译件已认证下载核对大小及完整 SHA-256，临时下载自动清理。TED-VAE 私有提交 `d8f72d9` 的 CI `45936238365` 成功，CTS 私有提交 `6c16804` 的 CI `45937397131` 成功。全部 364 份正式 PDF 与私有 Releases 对账通过。

本批已完成五篇精读和四份中文正文 PDF（38 页），尚待 Causal Tree、Causal Forest、GRF、Uplift 树分裂、GANITE 的精读和正文 PDF，以及整批全库反查、检索验收和公开同步。公开远端核对仍在第 7–8 批的 `76632b0`。待编译的三篇作者 LaTeX 优先复用 LuaLaTeX 和可用 locale，再核中文字体映射并逐页验收。

# Transformer知识覆盖审计

检索截至 **2026-11-02**。结论：已有知识对2017原始Transformer的结构、训练与论文证据覆盖较好，但不能称为完整的Transformer技术问答库。基础解释经本轮补齐后更连贯，现代位置、推理优化与可运行验证仍有真实缺口。学习正文入口为[问题驱动路线](../知识库/阅读/Transformer问题驱动学习路线.md)，逐题状态只在本审计记录。

## 检索范围与判定方法

GitHub仓库搜索包括`Transformer 面试 in:name,description`、`LLM interview in:name,description stars:>500`与`ML-NLP in:name`。宽泛README+stars搜索杂项过多，随后定向读取文件；选择依据是是否包含实际Transformer问题及互补主题，不按stars作质量评分。发现`km1994/LLMs_interview_notes`等仓库，但本轮只查看其目录，未作为正文证据或计入题目。未抓取所有Issue、图内文字和外链课程。

| 简称 | 固定版本与文件 | 用途 |
|---|---|---|
| I | [ch3nboyu/Transformer-interview README](https://github.com/ch3nboyu/Transformer-interview/blob/989af53d07eb54fb82243236a5c7eb70d6cc843d/README.md) | 结构、张量、多头、mask、LN、复杂度问题 |
| M | [NLP-LOVE/ML-NLP Transformer章](https://github.com/NLP-LOVE/ML-NLP/blob/16733eb5e2958fd6f36d6a4fb60934dd6a550c3b/NLP/16.7%20Transformer/README.md) | 中文结构导读、RNN/seq2seq比较 |
| W | [wdndev架构](https://github.com/wdndev/llm_interview_note/blob/581d54dd9a72e1d0a4eb28ae50859db83901b783/02.%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E6%9E%B6%E6%9E%84/Transformer%E6%9E%B6%E6%9E%84%E7%BB%86%E8%8A%82/Transformer%E6%9E%B6%E6%9E%84%E7%BB%86%E8%8A%82.md)、[Attention](https://github.com/wdndev/llm_interview_note/blob/581d54dd9a72e1d0a4eb28ae50859db83901b783/02.%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E6%9E%B6%E6%9E%84/1.attention/1.attention.md)、[位置](https://github.com/wdndev/llm_interview_note/blob/581d54dd9a72e1d0a4eb28ae50859db83901b783/02.%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E6%9E%B6%E6%9E%84/3.%E4%BD%8D%E7%BD%AE%E7%BC%96%E7%A0%81/3.%E4%BD%8D%E7%BD%AE%E7%BC%96%E7%A0%81.md)、[推理](https://github.com/wdndev/llm_interview_note/blob/581d54dd9a72e1d0a4eb28ae50859db83901b783/06.%E6%8E%A8%E7%90%86/llm%E6%8E%A8%E7%90%86%E4%BC%98%E5%8C%96%E6%8A%80%E6%9C%AF/llm%E6%8E%A8%E7%90%86%E4%BC%98%E5%8C%96%E6%8A%80%E6%9C%AF.md) | 缩放推导、现代位置、KV和高效注意力 |
| A | [harvardnlp/annotated-transformer](https://github.com/harvardnlp/annotated-transformer/blob/debc9fd747bb2123160a98046ad1c2d4da44a567/the_annotated_transformer.py) | 定向静态核对分头、归一化、mask、共享与损失 |

题目归并为 **32项核验点**，包含题库原问题、对过宽措辞的加严追问，以及论文/推荐迁移补充核验。它们不是32条独立真实面试记录，也没有题频统计；“常考”仅指选定资源的组织定位。把论文、现代架构和代码验证分开评判，不要求2017笔记承包后来的所有技术。

“完整”指库内正文能回答本行所列机制及关键条件，不代表科研实验已复现；“部分”指只有术语、局部机制、分散场景或尚缺本行要求的推导/验证；“缺失”指定向检索与相关页阅读后未找到可用解释。审计基线是修改前HEAD `c5258e8`；仅评知识正文与阅读笔记，不把全文译文、候选题名或匹配一个关键词算作覆盖。

| 状态 | 补齐前 | 本轮后 |
|---|---:|---:|
| 完整 | 12 | 23 |
| 部分 | 14 | 6 |
| 缺失 | 6 | 3 |

数字是这32项的人工自查汇总，不是全知识库覆盖率或面试通过率。

## 问题到现有知识的对应

下表“精读”指[Transformer阅读笔记](../来源/SRC-TRANSFORMER/阅读笔记.md)，“上下文”指[自注意力问题页](../知识库/问题/序列怎样用自注意力建立上下文.md)。迁移相关入口是[预训练迁移](../知识库/问题/预训练怎样迁移到不同任务.md)、[下一物品](../知识库/问题/从历史顺序预测下一物品.md)、[目标解码](../知识库/问题/生成推荐怎样把计算集中到目标解码.md)、[历史复用](../知识库/问题/目标感知排序怎样复用历史计算.md)、[生成机制](../知识库/模块/生成机制与约束解码.md)。精读内的章节链接、公式和原文页码负责进一步定位。

| 编号 | 核验问题 | 问题出处/范围 | 补齐前 | 本轮后 | 对应解释或仍缺什么 |
|---|---|---|---|---|---|
| T01 | 原始Encoder/Decoder/交叉注意力如何连接？ | I Encoder和Decoder；M §2 | 完整 | 完整 | 精读“从输入句子到逐个输出的译文”与“三种注意力” |
| T02 | Q/K/V同源是否相等？可否令Q=K？ | I 为什么QKV相同；W Attention §6.2 | 部分 | 完整 | 上下文“投影、分头与张量形状”：独立投影及均匀注意力反例 |
| T03 | 为什么除以每头维度的平方根？ | I 缩放；W 架构§4 | 完整 | 完整 | 精读QKV：独立假设、方差推导与适用限制 |
| T04 | Softmax梯度、平移不变与数值稳定如何解释？ | W 架构§4；Attention §5.2 | 缺失 | 完整 | 上下文“缩放影响分数差距”：Jacobian、平移反例、交叉熵边界 |
| T05 | 多头比单头多了什么，是否越多越好？ | I 多头；M §3；W 架构§5 | 完整 | 完整 | 精读多头公式与表3消融；不承诺每头具可命名语义 |
| T06 | 批量与交叉注意力的张量形状如何变化？ | I Attention/MHA；A MultiHeadedAttention | 部分 | 完整 | 上下文张量表，2×8×3×5例；batch不进入参数轴 |
| T07 | 点积、加性注意力和余弦有什么区别？ | I 点积；W Attention §6.2 | 部分 | 完整 | 上下文缩放节：理论成本与实现效率、模长与角度 |
| T08 | 目标右移和因果mask为何缺一不可？ | I Decoder Mask；M §2.3；A Batch | 完整 | 完整 | 精读及上下文：BOS/A/B输入、A/B/C监督 |
| T09 | padding、因果、loss mask怎样组合？全遮罩怎么办？ | M §2.3.1；W Attention §6.2；A Batch | 部分 | 完整 | 上下文遮罩小节：广播、逻辑与/加法、NaN与无效监督 |
| T10 | 训练能并行，生成为何仍逐步？ | I 并行；W 架构§8 | 完整 | 完整 | 精读三种注意力；同层读取不等于RNN递推 |
| T11 | FFN与输出投影各做什么，参数是否共享？ | I FFN；M §2.2.5 | 完整 | 完整 | 精读前馈公式；MHA输出Linear与逐位置非线性分开 |
| T12 | LN按哪一轴归一化，为何通常不用BN？ | I 归一化；W Attention §6.2；A LayerNorm | 部分 | 完整 | 上下文LN公式及统计轴；结构动机，不虚构LN/BN消融 |
| T13 | 残差、Pre-LN/Post-LN如何影响梯度与深层训练？ | I 残差；W Attention §6.2；A SublayerConnection | 部分 | 部分 | 已补Jacobian与无梯度下界保证；缺Pre/Post-LN专门理论与受控证据 |
| T14 | 正弦与学习位置有何区别，相对偏移如何推出？ | I 位置；M §2.2.1；W 位置 | 部分 | 完整 | 精读原设置；上下文新增和角矩阵推导及非外推保证 |
| T15 | 去掉位置编码为何是置换等变而非不变？ | W Attention §6.2的无序问题，归并后加严表述 | 部分 | 完整 | 上下文PAP转置与PO推导，注明因果mask例外 |
| T16 | Embedding共享、输出投影与乘根号d是什么？ | W Attention §6.2；A Embeddings/make_model | 部分 | 完整 | 精读新增共享矩阵、兼容条件与初始化解释边界 |
| T17 | Attention与整个块的复杂度、依赖路径区别？ | I 复杂度/RNN；M §4 | 完整 | 完整 | 精读§4与完整块O(n²d+nd²)，不能当实测时延 |
| T18 | 固定总宽时头数改变参数量和中间存储吗？ | I 多头/复杂度追问；A MultiHeadedAttention | 缺失 | 完整 | 上下文4d²、2dd_ff参数推算与Bhn²分数存储 |
| T19 | 训练/推理显存有哪些项，如何估算实际字节？ | I 显存；W 推理§1.5 | 部分 | 部分 | 已补训练组成；缺具体dtype、优化器、重计算及峰值账本 |
| T20 | warmup、优化器、Dropout怎样配置？ | A rate；原论文补充核验 | 完整 | 完整 | 精读§5：学习率公式、4000步、Adam与Dropout范围 |
| T21 | 标签平滑如何分质量，与padding和困惑度什么关系？ | A LabelSmoothing；原论文§5.4 | 部分 | 完整 | 精读新增分布定义、实现差异；原表3 PPL/BLEU反例 |
| T22 | greedy/beam、长度惩罚与输出长度如何影响生成？ | M §2.3.2；A greedy_decode | 完整 | 完整 | 精读beam4/长度惩罚0.6；已有生成解码页补搜索边界 |
| T23 | 原论文结果支持什么，消融有哪些反例？ | M §4的效果概括，原论文补充核验 | 完整 | 完整 | 精读表2–4，区分数据/开发/测试、头数及英法数字冲突 |
| T24 | GPT、BERT、T5的结构与预训练目标怎样区分？ | W Attention §3标题；库内迁移对照 | 完整 | 完整 | 预训练迁移及三篇精读；GPT初代不等于现代LLaMA |
| T25 | SASRec/BERT4Rec如何复用构件，何时不能缓存？ | 库内推荐迁移追问 | 完整 | 完整 | 下一物品页：目标/损失差异、双向历史变化的缓存边界 |
| T26 | KV Cache为何缓存K/V、prefill/decode成本如何推？ | W 推理§1.1–1.5 | 部分 | 部分 | 历史复用/目标解码页有具体场景；缺通用逐层递推、position offset与beam重排 |
| T27 | MHA/MQA/GQA头数、缓存量和质量代价怎样比较？ | W Attention §4；推理§1.5 | 部分 | 部分 | OneRec-V2仅场景化说明；缺通用KV头参数化与原论文/代码核验 |
| T28 | RoPE/ALiBi如何计算，和相对偏置如何区别？ | I 其他位置；W 位置§2–3 | 缺失 | 缺失 | T5有相对偏置，但没有RoPE/ALiBi推导及实现，不能互相抵扣 |
| T29 | FlashAttention为什么精确，节省IO而非取消二次运算？ | W Attention §5 | 缺失 | 缺失 | HSTU仅把FlashAttention2作基线，未讲online softmax/分块/反传重算 |
| T30 | 现代RMSNorm/SwiGLU与LN/ReLU差在哪里？ | I FFN激活扩展；LN比较延伸出的审计追问 | 缺失 | 缺失 | GPT/T5构件零散说明不足以覆盖现代两项的定义、参数与算量 |
| T31 | 长上下文外推/插值怎样验证，能计算是否就有效？ | W 位置§4 | 部分 | 部分 | 原论文笔记已否定必然外推；缺扩展方法、位置/检索/任务指标协议 |
| T32 | 能否手写并验证mask、shape、梯度和缓存等价性？ | I MHA示例；A 教学实现 | 缺失 | 部分 | 已静态检查并纠错；没有本库可运行实现及数值等价/梯度验证 |

## 题库答案的纠错边界

[I来源笔记](../来源/SRC-TRANSFORMER-INTERVIEW/阅读笔记.md)记录了投影参数含batch轴、分头后按总维缩放、未定义mask参数和“训练mask不能并行”等问题；[M来源笔记](../来源/SRC-MLNLP-TRANSFORMER/阅读笔记.md)区分FFN与多头输出投影、seq2seq范式与RNN实现；[W来源笔记](../来源/SRC-LLM-INTERVIEW-TRANSFORMER/阅读笔记.md)限制Softmax绝对值、Q=K、残差梯度保底和外推优劣的过强说法。现代方法未核原论文的结果没有写入知识层当成定论。

[A来源笔记](../来源/SRC-ANNOTATED-TRANSFORMER/阅读笔记.md)则核对出教学实现的Pre-LN、标准差epsilon位置、未绑定嵌入权重及未用KV缓存。教学代码的文字引用和执行路径必须分开。原论文§3–5的补充复核使用既有冻结原件/正文源码，仅取已发表正文，不将源码注释或未发表实验采入。

## 剩余学习顺序与完成条件

| 顺序 | 缺口 | 补到什么程度才可改为完整 |
|---|---|---|
| 1 | T26/T27：KV Cache与MHA/MQA/GQA | 写出逐层增量递推及适用前提，按KV头数估算字节；解释prefill、单步与总解码成本，核对缓存位置和beam重排；回查原论文/固定实现 |
| 2 | T28/T31：RoPE、ALiBi与长度扩展 | 给出位置变换/偏置公式和相对位置关系，区分可计算与有效泛化；明确训练长度、测试长度、长距任务与资源协议 |
| 3 | T29：FlashAttention | 解释online softmax的分块合并、IO与算术复杂度、反传重算；核对精确性的数值含义，不用HSTU基线提及替代原理 |
| 4 | T13/T30：归一化与现代FFN | 定义LN/RMSNorm、ReLU/SwiGLU及成本；Pre/Post-LN稳定性回查专门论文，不能由残差局部导数推普遍优劣 |
| 5 | T19/T32：显存与可运行验证 | 在声明dtype/模型/优化器后核算参数、梯度、状态、激活、KV和峰值；用小规模用例验证因果隔离、padding、形状、梯度与缓存/全前缀等价 |

这些是知识缺口与后续完成条件，不是已完成论文阅读，也不自动启动训练或安装环境。本轮只完成问题审计、经典机制增补及静态代码核对；未执行模型训练、推理性能或代码数值等价测试。没有改动中文PDF或原件，因此不产生新的PDF备份版本。

## 本轮验证记录

`check_context.py`通过活跃Markdown与本地链接检查；`wiki.py lint`为0 errors，3条已有warning分别为组合策略页contested、SRC-POUL与SRC-TAQFORMER待整合，均不属于本轮改动。`wiki.py index --check`通过；`plan`仅剩这两个既有来源待整合。本轮文件的Git差异检查通过。全工作树`git diff --check`发现既有治理目录文件第40行尾随空格，该文件的用户改动保留，未纳入提交。

“Transformer 面试”“Softmax梯度”“RoPE”“KV Cache”检索已执行：可回到学习路线、基础解释或已有服务场景；词面搜索可能命中`propensity`等包含相同字母的无关内容，因此覆盖判定依据实际读页，不靠搜索数量。未验证所有外链、上游图片、API运行语义或模型性能。

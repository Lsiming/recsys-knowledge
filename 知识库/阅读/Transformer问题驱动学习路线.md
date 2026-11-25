---
id: "transformer-question-path"
title: "Transformer问题驱动学习路线"
type: "map"
status: "reviewed"
updated: "2026-11-21"
summary: "从注意力与序列监督进入分词、共享权重、归一化、RoPE 和 FlashAttention 的论文与推导"
aliases: ["Transformer面试", "Transformer常考题", "Transformer八股", "Transformer知识覆盖", "技术问题梳理", "RoPE", "ALiBi", "FlashAttention", "KV Cache", "GQA", "RMSNorm", "SwiGLU"]
sources: {"SRC-TRANSFORMER-INTERVIEW": "d4e96b7bc7f5b8b1d308be92016b2e6fb93fa24e40be0d045e9cf883ffeb3392", "SRC-MLNLP-TRANSFORMER": "f79f30e659d0550e6501c10897ed9bc022b0d6f43f199f976d7deb77b1faaa41", "SRC-LLM-INTERVIEW-TRANSFORMER": "1187df8efd6eec8ef65ce5c8f965d4928a911e948d2618c0d418e869e12972b6", "SRC-ANNOTATED-TRANSFORMER": "beeb95223c4b6291a6731ea8154535c34d236a83e1b35b47636be38504caba28"}
related: ["self-attention-context", "pretraining-task-transfer", "classic-reading-path", "learning-resources", "target-decoding-compute", "transformer-position", "layernorm-residual", "attention-mask-padding", "transformer-training-translation", "embedding-weight-tying", "attention-compute-memory", "language-model-loss-gradient", "sequence-representation-pooling"]
---
# Transformer问题驱动学习路线

理解Transformer要能沿着一条完整链路解释：输入如何投影、一个位置如何选择可见信息、信息怎样变成输出、训练与生成为何不同、计算和存储花在哪里。GitHub题目可以用来检验这条链是否连贯，但参考答案可能混用原论文、教学改写和现代变体。

## 从历史疑问直接找到推导与例子

| 学习疑问                                              | 知识正文                                          |
| ------------------------------------------------- | --------------------------------------------- |
| 点积方差、Score/Probability、QKV形状、分头换轴                 | [注意力张量与数学](../问题/序列怎样用自注意力建立上下文.md#投影分头与张量形状) |
| pos/i、高低频、成对sin/cos、相对偏移、RoPE                     | [位置编码](../概念/Transformer位置编码.md)              |
| make_std_mask、广播、PAD Query、NaN、Loss Mask          | [遮罩与填充](../概念/Attention遮罩与填充.md)              |
| 目标右移、Teacher Forcing、Loss、梯度回到Encoder、推理          | [训练与机器翻译](../概念/Transformer训练与机器翻译.md)        |
| 两种词表、联合BPE、SentencePiece、hE转置、Weight Tying、Xavier | [词表嵌入与权重共享](../概念/词表嵌入与权重共享.md)               |
| LN统计轴、gamma/beta、反传、推理、Pre/Post-LN恒等路径            | [LayerNorm与残差梯度](../概念/LayerNorm与残差梯度.md)     |
| 平方矩阵、FP16字节数、KV缓存、FlashAttention在线Softmax         | [计算与存储](../概念/Attention计算与存储.md)              |

[GPT初代学习思考](../../来源/SRC-GPT1/学习思考.md)把论文追问串成“架构 → 逐位置预测 → 损失反传 → 任务迁移 → 序列读出”。其中[交叉熵与梯度](../概念/语言模型的词表预测与交叉熵.md)给出p−q、共享Embedding和QKV反传，[序列表示](../概念/Token表示怎样汇聚成序列表示.md)比较Extract、CLS、Last、Mean与Attention Pooling。

这些正文保留公式、最小例子和来源定位，不要求先阅读论文全文。102题的逐项对应、历史答案纠正及核验范围集中在[沉淀核验](../../维护/Transformer历史问答沉淀核验.md)，问题状态不混入技术正文。

## 从结构走到可计算的注意力

先读[Transformer精读](../../来源/SRC-TRANSFORMER/阅读笔记.md)，说明编码器、因果解码器和交叉注意力的输入输出。再到[上下文问题页](../问题/序列怎样用自注意力建立上下文.md)，试着回答：Q/K/V为什么同源但不相等？分成8头后张量各有几维？Softmax沿哪一轴？为何按每头维度的平方根缩放？

把每个位置汇聚后的状态送入[逐位置前馈层](../概念/逐位置前馈层的门控与宽度.md)，可以沿普通 FFN 和 SwiGLU 的两个计算路径比较隐藏宽度与训练预算。

随后检查边界：把mask乘0为何不够？padding键与padding目标是否都处理了？无位置模型是置换等变还是置换不变？FFN是否跨Token混合？LN对哪些数求均值？这些问题应能写出公式或一个最小反例，而不只背诵“多头捕捉多种信息”。

## 把训练目标与网络结构分开

[原论文训练与评估](../../来源/SRC-TRANSFORMER/阅读笔记.md#原论文怎样训练与评估)解释右移监督、warmup、Dropout、标签平滑、束搜索和BLEU条件；[预训练迁移](../问题/预训练怎样迁移到不同任务.md)进一步比较GPT、BERT和T5。自回归训练可并行计算已知目标位置，不等于生成未来Token无需逐步依赖；双向编码也不意味着能把真实待预测答案直接放入输入。

读代码时对照[Annotated Transformer](../../来源/SRC-ANNOTATED-TRANSFORMER/阅读笔记.md)：其Pre-LN、未绑定的嵌入和整前缀解码与原论文或现代高效推理并不完全相同。代码“看起来像Transformer”不足以证明细节一致。

## 从序列构件走向推荐与服务

[下一物品预测](../问题/从历史顺序预测下一物品.md)比较SASRec与BERT4Rec的信息可见范围、恢复目标和候选打分；[目标解码计算](../问题/生成推荐怎样把计算集中到目标解码.md)与[历史复用](../问题/目标感知排序怎样复用历史计算.md)把缓存和候选隔离放回推荐场景。先说清输出是物品分数、SID还是文本，再比较架构。

## 从四个问题回到八篇构件论文

| 阅读时要区分什么 | 知识正文 | 对照精读 |
|---|---|---|
| 切分规则、词元 ID 和词表参数分别怎样共享？ | [词表嵌入与权重共享](../概念/词表嵌入与权重共享.md) | [BPE 的有序合并](../../来源/SRC-BPE/阅读笔记.md)、[SentencePiece 的规范化与采样](../../来源/SRC-SENTENCEPIECE/阅读笔记.md)、[Weight Tying 的两条梯度路径](../../来源/SRC-WEIGHT-TYING/阅读笔记.md) |
| 改变统计量与移动残差支路上的归一化，各自改变哪一步？ | [归一化与残差梯度](../概念/LayerNorm与残差梯度.md) | [LayerNorm 的统计轴](../../来源/SRC-LAYERNORM/阅读笔记.md)、[Pre-LN 的恒等路径与预热实验](../../来源/SRC-PRELN/阅读笔记.md)、[RMSNorm 的均方根](../../来源/SRC-RMSNORM/阅读笔记.md) |
| 位置如何进入 Q、K 的点积？ | [加性位置向量与 RoPE](../概念/Transformer位置编码.md#从加性位置向量到rope) | [RoFormer 的二维旋转与相对位移](../../来源/SRC-ROFORMER/阅读笔记.md) |
| 精确注意力如何减少显存读写，反向时重新算什么？ | [分块前向与反向重算](../概念/Attention计算与存储.md#flashattention为什么不必保存完整概率矩阵) | [FlashAttention 的在线 Softmax、HBM 访问与算量](../../来源/SRC-FLASHATTENTION/阅读笔记.md) |

[SwiGLU 精读](../../来源/SRC-SWIGLU/阅读笔记.md)用相同矩阵预算比较普通 FFN 和门控 FFN。[GQA 精读](../../来源/SRC-GQA/阅读笔记.md)结合组内投影平均和追加训练比较 MHA、MQA 与 GQA。[ALiBi 精读](../../来源/SRC-ALIBI/阅读笔记.md)用不重叠与滑窗评估区分长输入的困惑度和远距离证据利用。此前的 [32 项覆盖审计](../../维护/Transformer知识覆盖审计.md)和 [102 题逐项核验](../../维护/Transformer历史问答沉淀核验.md)保留各自日期的范围。

## GitHub题目从哪里来

| 资源 | 建议用途 | 阅读边界 |
|---|---|---|
| [Transformer-interview](../../来源/SRC-TRANSFORMER-INTERVIEW/阅读笔记.md) | 用结构、mask、复杂度和LN问题自测 | README代码与部分答案存在具体错误 |
| [ML-NLP Transformer章](../../来源/SRC-MLNLP-TRANSFORMER/阅读笔记.md) | 从结构图式导读进入基础概念 | 多头输出与FFN、seq2seq术语需辨析 |
| [LLM面试笔记](../../来源/SRC-LLM-INTERVIEW-TRANSFORMER/阅读笔记.md) | 从基础问题延伸到位置与推理 | 定向读取部分章节，现代方法效果未经原文核验 |
| [Annotated Transformer](../../来源/SRC-ANNOTATED-TRANSFORMER/阅读笔记.md) | 对照张量与损失实现 | 教学代码，不是逐项复刻原论文；未运行 |

检索截至2026-11-02；这是定向取样，不是全GitHub穷举，也不是公司面试题频统计。来源卡固定commit与文件哈希；题目归并保留出处，技术答案优先采用论文、明确推导与已核对的代码路径。

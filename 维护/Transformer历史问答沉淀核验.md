# Transformer历史102题沉淀核验

核验日期：2026-11-08。输入为用户本轮102题及其提供的《Transformer 原理学习笔记》；该笔记自称是历史讨论重建，且公式含导出损坏，因此只用作缺口线索，不登记成独立科研证据。原文件在本地保留，SHA256为`ccd8f9828feff40caae8ac8c9b87596ca8dd3a72e235430b2a86b5438f970542`。

基线为`49ea864`。已有自注意力问题页已覆盖大多数基础名词和部分公式，但分头换轴、统计量反传、PAD Query与端到端监督等解释较短；RoPE缺少正式原理页，词表/共享说明分散。现将正文归入六个主题主页面，原总览保留入口；不复制损坏公式或重复102份回答。

## 补充与核验依据

| 内容 | 基线不足与本轮增量 | 原始依据/表述类型 |
|---|---|---|
| Attention 1–13 | 展开协方差假设、矩阵算例、分数/概率、Linear与换轴；保留原有模型比较 | Transformer v7 §3.2、脚注4；教学代码固定commit；维度/方差为显式推导 |
| 位置14–31 | 展开频率、线性偏移、纯PE点积；新增RoPE和旋转Key缓存 | Transformer v7 §3.5；RoFormer v5 §3.1–3.4；Llama 2固定代码 |
| Mask 32–49 | 区分三维教学返回与四维广播、PAD Query、loss与全mask行 | Transformer §3.1/3.2.3；Annotated Transformer静态代码；数值边界分析 |
| Encoder/Decoder 50–60 | 完整样本、未平滑交叉熵基式、平滑差异、Value梯度通路与交叉K/V缓存 | Transformer架构/§5.4；代码；链式法则及固定因果条件推导 |
| 词表/Embedding 61–76 | 不同词表、统一索引、共享梯度、Xavier一般方差和条件 | BPE §3.2；SentencePiece §1–2；Press/Wolf §1/3；Xiong §3.3 |
| LN 77–102 | 数值例、共享参数、输入反传、推理统计、BN轴、Jacobian及多层限制 | LN v1 §3；Transformer §3.1；Xiong §3；RMSNorm §4 |

## 需要修正或限定的历史表述

- 历史总结图把位置编码统一放在Embedding之后，无法表达每层投影后作用Q/K的RoPE，已区分。
- “Adam按参数减学习率乘梯度”只是SGD示意，不是Adam完整更新。
- 纯PE向量内积的相对距离性质不能直接推广到内容加位置再投影的实际Attention。
- 正弦波长有限维最大值并不严格取到10000×2π；高低频不是固定语义职责。
- 输入查表路径可能稀疏，但Weight Tying的完整输出Softmax会贡献到多数乃至全部词表行。
- “KV Cache只省历史K/V投影”过窄：还省去了被缓存因果历史位置的多层状态重算。
- 全部logit替换为同一个有限常数会均匀；给全部原logit加同常数则精确保持原分布，两者都不等于全屏蔽。
- 加epsilon后LN标准化方差是v/(v+epsilon)，常量输入方差为0；最终仿射输出不必零均值/单位方差。
- LN层训练/推理计算一致，不等于整网Dropout等行为一致；eval也不自动关闭求导。
- Pre-LN恒等项、RoPE位置外推和Weight Tying都不能推出普遍质量或稳定性保证。

## 逐题主归属

下表每题链接到实际可回答的小节；“已沉淀”指理论解释和适用边界已自查，不表示模型实验已复现或执行独立审查。

| 编号 | 可检索问题 | 主要解释位置 |
|---|---|---|
| 1 | 点积与内积 | [注意力数学与张量](../知识库/问题/序列怎样用自注意力建立上下文.md#缩放影响分数差距softmax不是梯度保证) |
| 2 | 点积方差为何是d_k | [注意力数学与张量](../知识库/问题/序列怎样用自注意力建立上下文.md#缩放影响分数差距softmax不是梯度保证) |
| 3 | 为何除以根号d_k | [注意力数学与张量](../知识库/问题/序列怎样用自注意力建立上下文.md#缩放影响分数差距softmax不是梯度保证) |
| 4 | 注意力矩阵维度 | [注意力数学与张量](../知识库/问题/序列怎样用自注意力建立上下文.md#投影分头与张量形状) |
| 5 | 为何得到二维Score | [注意力数学与张量](../知识库/问题/序列怎样用自注意力建立上下文.md#分数与概率的区别以及二维矩阵从哪里来) |
| 6 | 平方存储项 | [注意力数学与张量](../知识库/问题/序列怎样用自注意力建立上下文.md#分数与概率的区别以及二维矩阵从哪里来) |
| 7 | Q/K/V投影 | [注意力数学与张量](../知识库/问题/序列怎样用自注意力建立上下文.md#从相似度到可学习的信息读取) |
| 8 | QK转置如何计算 | [注意力数学与张量](../知识库/问题/序列怎样用自注意力建立上下文.md#分数与概率的区别以及二维矩阵从哪里来) |
| 9 | Softmax沿Key轴 | [注意力数学与张量](../知识库/问题/序列怎样用自注意力建立上下文.md#分数与概率的区别以及二维矩阵从哪里来) |
| 10 | Score与Probability | [注意力数学与张量](../知识库/问题/序列怎样用自注意力建立上下文.md#分数与概率的区别以及二维矩阵从哪里来) |
| 11 | 先Linear再拆Head | [注意力数学与张量](../知识库/问题/序列怎样用自注意力建立上下文.md#为什么分头以后要换轴) |
| 12 | 交换Head与序列轴 | [注意力数学与张量](../知识库/问题/序列怎样用自注意力建立上下文.md#为什么分头以后要换轴) |
| 13 | 每Head独立matmul | [注意力数学与张量](../知识库/问题/序列怎样用自注意力建立上下文.md#为什么分头以后要换轴) |
| 14 | FFN与PE的职责 | [前馈与位置的分工](../知识库/问题/序列怎样用自注意力建立上下文.md#位置前馈与归一化各自承担不同工作) |
| 15 | pos与i | [位置编码基础](../知识库/概念/Transformer位置编码.md#正弦公式中的位置维度与频率) |
| 16 | 为何sin/cos | [位置编码基础](../知识库/概念/Transformer位置编码.md#为什么sin与cos成对能表达偏移) |
| 17 | 原文设计依据 | [位置编码基础](../知识库/概念/Transformer位置编码.md#为什么sin与cos成对能表达偏移) |
| 18 | 正弦优势与其他PE | [位置编码基础](../知识库/概念/Transformer位置编码.md#从加性位置向量到rope) |
| 19 | 高低频是否代表相对位置 | [位置编码基础](../知识库/概念/Transformer位置编码.md#正弦公式中的位置维度与频率) |
| 20 | 维度与频率尺度 | [位置编码基础](../知识库/概念/Transformer位置编码.md#正弦公式中的位置维度与频率) |
| 21 | 偶数sin奇数cos | [位置编码基础](../知识库/概念/Transformer位置编码.md#为什么sin与cos成对能表达偏移) |
| 22 | 线性位置偏移 | [位置编码基础](../知识库/概念/Transformer位置编码.md#为什么sin与cos成对能表达偏移) |
| 23 | 是否训练位置表 | [位置编码基础](../知识库/概念/Transformer位置编码.md#正弦公式中的位置维度与频率) |
| 24 | 位置方法比较 | [RoPE与缓存](../知识库/概念/Transformer位置编码.md#从加性位置向量到rope) |
| 25 | 自回归兼容的含义 | [RoPE与缓存](../知识库/概念/Transformer位置编码.md#从加性位置向量到rope) |
| 26 | RoPE结构优势与限制 | [RoPE与缓存](../知识库/概念/Transformer位置编码.md#从加性位置向量到rope) |
| 27 | RoPE数学原理 | [RoPE与缓存](../知识库/概念/Transformer位置编码.md#从加性位置向量到rope) |
| 28 | 旋转与相对偏移 | [RoPE与缓存](../知识库/概念/Transformer位置编码.md#从加性位置向量到rope) |
| 29 | 是否仅限自回归 | [RoPE与缓存](../知识库/概念/Transformer位置编码.md#从加性位置向量到rope) |
| 30 | 历史Key缓存 | [RoPE与缓存](../知识库/概念/Transformer位置编码.md#为什么缓存已经旋转的key) |
| 31 | 为何缓存旋转Key | [RoPE与缓存](../知识库/概念/Transformer位置编码.md#为什么缓存已经旋转的key) |
| 32 | 右移必须配合mask | [右移与因果生成](../知识库/概念/Transformer训练与机器翻译.md#右移监督与teacher-forcing) |
| 33 | 右移后的训练并行 | [右移与因果生成](../知识库/概念/Transformer训练与机器翻译.md#为什么mask与训练并行不冲突) |
| 34 | 训练并行与推理逐步 | [右移与因果生成](../知识库/概念/Transformer训练与机器翻译.md#生成时哪些可以重用) |
| 35 | 因果mask防泄漏 | [右移与因果生成](../知识库/概念/Transformer训练与机器翻译.md#右移监督与teacher-forcing) |
| 36 | make_std_mask实现 | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#make_std_mask的逐轴过程) |
| 37 | 组合Key与Causal | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#从布尔条件到attention-logits) |
| 38 | 为何逻辑组合 | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#从布尔条件到attention-logits) |
| 39 | 广播维度 | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#make_std_mask的逐轴过程) |
| 40 | PAD Query发生什么 | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#make_std_mask的逐轴过程) |
| 41 | PAD Query读有效Key | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#make_std_mask的逐轴过程) |
| 42 | PAD Query需否清零 | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#pad输出和pad监督分别处理) |
| 43 | PAD目标loss屏蔽 | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#pad输出和pad监督分别处理) |
| 44 | Attention Mask不足以替代loss mask | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#pad输出和pad监督分别处理) |
| 45 | 全负无穷NaN | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#一整行没有合法key时为什么危险) |
| 46 | 有限负常数为何非全屏蔽 | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#一整行没有合法key时为什么危险) |
| 47 | mask为何仍并行 | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#因果依赖为何不阻止训练并行) |
| 48 | 为何不用Token循环 | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#因果依赖为何不阻止训练并行) |
| 49 | 并行训练与自回归推理 | [Padding与mask实现](../知识库/概念/Attention遮罩与填充.md#因果依赖为何不阻止训练并行) |
| 50 | 训练与推理数据流 | [Encoder/Decoder训练](../知识库/概念/Transformer训练与机器翻译.md#编码源序列解码目标序列) |
| 51 | 源语言与目标语言 | [Encoder/Decoder训练](../知识库/概念/Transformer训练与机器翻译.md#编码源序列解码目标序列) |
| 52 | Decoder右移 | [Encoder/Decoder训练](../知识库/概念/Transformer训练与机器翻译.md#右移监督与teacher-forcing) |
| 53 | 监督构建 | [Encoder/Decoder训练](../知识库/概念/Transformer训练与机器翻译.md#右移监督与teacher-forcing) |
| 54 | Loss计算 | [Encoder/Decoder训练](../知识库/概念/Transformer训练与机器翻译.md#全词表logits怎样变成一个loss) |
| 55 | 梯度回到Encoder | [Encoder/Decoder训练](../知识库/概念/Transformer训练与机器翻译.md#一个翻译loss怎样把梯度传回encoder) |
| 56 | Encoder独立Loss | [Encoder/Decoder训练](../知识库/概念/Transformer训练与机器翻译.md#一个翻译loss怎样把梯度传回encoder) |
| 57 | Teacher Forcing | [Encoder/Decoder训练](../知识库/概念/Transformer训练与机器翻译.md#右移监督与teacher-forcing) |
| 58 | 推理逐Token | [Encoder/Decoder训练](../知识库/概念/Transformer训练与机器翻译.md#生成时哪些可以重用) |
| 59 | Encoder是否重跑 | [Encoder/Decoder训练](../知识库/概念/Transformer训练与机器翻译.md#生成时哪些可以重用) |
| 60 | Cross-Attention训练/推理 | [Encoder/Decoder训练](../知识库/概念/Transformer训练与机器翻译.md#生成时哪些可以重用) |
| 61 | 右移是否要求共词表 | [词表与分词](../知识库/概念/词表嵌入与权重共享.md#为什么右移不要求源和目标共用词表) |
| 62 | 中英是否必须共词表 | [词表与分词](../知识库/概念/词表嵌入与权重共享.md#为什么右移不要求源和目标共用词表) |
| 63 | 源目标Token ID | [词表与分词](../知识库/概念/词表嵌入与权重共享.md#为什么右移不要求源和目标共用词表) |
| 64 | 联合BPE与SentencePiece | [词表与分词](../知识库/概念/词表嵌入与权重共享.md#联合bpe和sentencepiece分别是什么) |
| 65 | 联合词表与共享 | [词表与分词](../知识库/概念/词表嵌入与权重共享.md#为什么右移不要求源和目标共用词表) |
| 66 | Embedding查表 | [Embedding与Weight Tying](../知识库/概念/词表嵌入与权重共享.md#查一行向量与给整个词表打分) |
| 67 | 查表与输出logits | [Embedding与Weight Tying](../知识库/概念/词表嵌入与权重共享.md#查一行向量与给整个词表打分) |
| 68 | 为何hE转置 | [Embedding与Weight Tying](../知识库/概念/词表嵌入与权重共享.md#查一行向量与给整个词表打分) |
| 69 | 输入输出共享的含义 | [Embedding与Weight Tying](../知识库/概念/词表嵌入与权重共享.md#查一行向量与给整个词表打分) |
| 70 | 共享的作用和边界 | [Embedding与Weight Tying](../知识库/概念/词表嵌入与权重共享.md#为什么右移不要求源和目标共用词表) |
| 71 | 三方共享 | [Embedding与Weight Tying](../知识库/概念/词表嵌入与权重共享.md#为什么右移不要求源和目标共用词表) |
| 72 | 不同词表的共享条件 | [Embedding与Weight Tying](../知识库/概念/词表嵌入与权重共享.md#为什么右移不要求源和目标共用词表) |
| 73 | 输入根号d缩放 | [Embedding与Weight Tying](../知识库/概念/词表嵌入与权重共享.md#输入为什么乘根号dxavier又能说明多少) |
| 74 | 缩放与Xavier关系 | [Embedding与Weight Tying](../知识库/概念/词表嵌入与权重共享.md#输入为什么乘根号dxavier又能说明多少) |
| 75 | Xavier是否总方差1/d | [Embedding与Weight Tying](../知识库/概念/词表嵌入与权重共享.md#输入为什么乘根号dxavier又能说明多少) |
| 76 | 为何非所有Embedding都缩放 | [Embedding与Weight Tying](../知识库/概念/词表嵌入与权重共享.md#输入为什么乘根号dxavier又能说明多少) |
| 77 | LN实现 | [LayerNorm定义](../知识库/概念/LayerNorm与残差梯度.md#对每个token的特征求统计量) |
| 78 | 是否跨batch | [LayerNorm定义](../知识库/概念/LayerNorm与残差梯度.md#对每个token的特征求统计量) |
| 79 | 归一化轴 | [LayerNorm定义](../知识库/概念/LayerNorm与残差梯度.md#对每个token的特征求统计量) |
| 80 | B/S/D计算过程 | [LayerNorm定义](../知识库/概念/LayerNorm与残差梯度.md#对每个token的特征求统计量) |
| 81 | 为何不改形状 | [LayerNorm定义](../知识库/概念/LayerNorm与残差梯度.md#对每个token的特征求统计量) |
| 82 | gamma/beta与输出统计 | [LayerNorm定义](../知识库/概念/LayerNorm与残差梯度.md#对每个token的特征求统计量) |
| 83 | LN有哪些参数 | [LayerNorm参数与反传](../知识库/概念/LayerNorm与残差梯度.md#哪些是参数哪些只是当前输入的统计量) |
| 84 | 可训练量与实时统计 | [LayerNorm参数与反传](../知识库/概念/LayerNorm与残差梯度.md#哪些是参数哪些只是当前输入的统计量) |
| 85 | gamma/beta作用 | [LayerNorm参数与反传](../知识库/概念/LayerNorm与残差梯度.md#哪些是参数哪些只是当前输入的统计量) |
| 86 | 所有Token为何共享参数 | [LayerNorm参数与反传](../知识库/概念/LayerNorm与残差梯度.md#哪些是参数哪些只是当前输入的统计量) |
| 87 | LN怎样训练 | [LayerNorm参数与反传](../知识库/概念/LayerNorm与残差梯度.md#哪些是参数哪些只是当前输入的统计量) |
| 88 | LN是否独立Loss | [LayerNorm参数与反传](../知识库/概念/LayerNorm与残差梯度.md#哪些是参数哪些只是当前输入的统计量) |
| 89 | gamma/beta梯度 | [LayerNorm参数与反传](../知识库/概念/LayerNorm与残差梯度.md#哪些是参数哪些只是当前输入的统计量) |
| 90 | 统计量如何参与反传 | [LayerNorm参数与反传](../知识库/概念/LayerNorm与残差梯度.md#哪些是参数哪些只是当前输入的统计量) |
| 91 | LN推理流程 | [LayerNorm推理与BN](../知识库/概念/LayerNorm与残差梯度.md#推理仍重算统计量bn的行为取决于约定) |
| 92 | 推理是否重算 | [LayerNorm推理与BN](../知识库/概念/LayerNorm与残差梯度.md#推理仍重算统计量bn的行为取决于约定) |
| 93 | 使用哪份统计 | [LayerNorm推理与BN](../知识库/概念/LayerNorm与残差梯度.md#推理仍重算统计量bn的行为取决于约定) |
| 94 | 训练推理差异 | [LayerNorm推理与BN](../知识库/概念/LayerNorm与残差梯度.md#推理仍重算统计量bn的行为取决于约定) |
| 95 | LN与BN | [LayerNorm推理与BN](../知识库/概念/LayerNorm与残差梯度.md#推理仍重算统计量bn的行为取决于约定) |
| 96 | 结构差异 | [Pre-LN与Post-LN](../知识库/概念/LayerNorm与残差梯度.md#pre-ln的恒等梯度项从哪里来) |
| 97 | Pre-LN直接梯度路径 | [Pre-LN与Post-LN](../知识库/概念/LayerNorm与残差梯度.md#pre-ln的恒等梯度项从哪里来) |
| 98 | Identity Mapping | [Pre-LN与Post-LN](../知识库/概念/LayerNorm与残差梯度.md#pre-ln的恒等梯度项从哪里来) |
| 99 | 单位矩阵I | [Pre-LN与Post-LN](../知识库/概念/LayerNorm与残差梯度.md#pre-ln的恒等梯度项从哪里来) |
| 100 | Post-LN梯度路径 | [Pre-LN与Post-LN](../知识库/概念/LayerNorm与残差梯度.md#pre-ln的恒等梯度项从哪里来) |
| 101 | 能否完全避免消失 | [Pre-LN与Post-LN](../知识库/概念/LayerNorm与残差梯度.md#pre-ln的恒等梯度项从哪里来) |
| 102 | 多层恒等路径 | [Pre-LN与Post-LN](../知识库/概念/LayerNorm与残差梯度.md#pre-ln的恒等梯度项从哪里来) |

## 上传笔记中额外的内容

笔记还涉及FFN、复杂度、KV Cache、RMSNorm和FlashAttention。FFN沿用原精读，复杂度/缓存/FlashAttention归入[计算与存储](../知识库/概念/Attention计算与存储.md)，RMSNorm归入[归一化](../知识库/概念/LayerNorm与残差梯度.md#rmsnorm省去了哪一步)。ALiBi、长上下文扩展、GQA质量对比与SwiGLU仍未开展对应方法的完整学习，不能因本轮提及就更新为全面覆盖。

本轮新增9份来源卡均记录实际定向阅读范围，其中8份论文HTML与1份固定代码；这些不是8篇新论文的翻译交付。已有Transformer原文和中文译后源码用于对照，未修改原件/PDF。数值检查只验证小矩阵机制，不是训练或性能复现。

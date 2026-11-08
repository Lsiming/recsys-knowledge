---
id: "transformer-training-translation"
title: "Transformer机器翻译如何训练并逐步生成"
type: "concept"
status: "reviewed"
updated: "2026-11-08"
summary: "串起右移监督、因果并行、Token损失、交叉注意力反传与增量解码"
aliases: ["Teacher Forcing", "目标序列右移", "Decoder训练", "交叉注意力梯度", "Loss", "训练并行推理串行", "Encoder单独Loss"]
sources: {"SRC-TRANSFORMER": "2f1f9bf5db06a169aa117374ef34952e2b94e55aae46648e6f0d1280b4055d3e", "SRC-ANNOTATED-TRANSFORMER": "beeb95223c4b6291a6731ea8154535c34d236a83e1b35b47636be38504caba28", "SRC-LLAMA-CACHE-CODE": "e55e955775dd72fa548253694315647318567770485176edf06ac92b4beb54dc"}
related: ["self-attention-context", "pretraining-task-transfer", "attention-mask-padding", "embedding-weight-tying"]
---
# Transformer机器翻译如何训练并逐步生成

机器翻译中的编码器读取源句，解码器在源句条件下预测目标前缀的下一个Token。编码器和解码器由同一目标损失联合训练；目标右移定义监督对齐，因果mask保证信息不泄漏，两者让训练能按位置并行，而生成仍需逐步得到未知Token。

## 编码源序列，解码目标序列

设源Token为$x_{1:n_s}$，编码器输出$H_{enc}\in\mathbb R^{B\times n_s\times d}$。编码器自注意力通常读取整句有效源Token。解码器各层先对目标前缀做因果自注意力，再用该子层输出作为交叉注意力Query；每层的Key与Value由编码器顶层输出各自投影。因此源长$n_s$与目标长$n_t$可以不同，交叉注意力分数形状为$[B,H,n_t,n_s]$。[Transformer §3.1–3.2.3，PDF第3–5页](https://arxiv.org/pdf/1706.03762v7#page=3)

源和目标不必用同一词表；连续表示的特征宽度及投影要兼容即可。源目标ID甚至同数字异义也不构成错误。词表、Embedding和三方绑定条件另见[词表嵌入与权重共享](词表嵌入与权重共享.md)。

## 右移监督与Teacher Forcing

目标为`我 爱 猫 EOS`，加起始符后形成完整样本`BOS 我 爱 猫 EOS`；切片得到：

| 位置 | Decoder输入 | 这一行可见的目标输入前缀 | 监督标签 |
|---|---|---|---|
| 0 | BOS | BOS | 我 |
| 1 | 我 | BOS 我 | 爱 |
| 2 | 爱 | BOS 我 爱 | 猫 |
| 3 | 猫 | BOS 我 爱 猫 | EOS |

输入右移一位后，目标$y_t$在下一输入位置出现；如果不做因果遮罩，较早位置仍可能从右侧直接读到它。反过来，若输入不右移、同位置放待预测标签，即使mask含对角线也会泄漏。因此“右移”与“限制只读当前及左侧输入位置”必须配合。[Transformer §3.1](https://arxiv.org/pdf/1706.03762v7#page=3)

Teacher Forcing指训练时输入真实历史Token，优化$\prod_t p_\theta(y_t\mid y_{<t},x)$，而不是先从模型采样一个Token再作为下一位置输入。训练语料提供全部正确前缀，可直接计算每个条件分布；若逐步喂模型自己的输出，条件历史会改变，也不再是这里的一次标准前向。训练输入是真实前缀、推理输入是生成前缀，这种条件差异也意味着训练并行本身不保证生成不会累计错误；此处是目标分布的解释，不声称原文实测过该误差。

## 全词表logits怎样变成一个loss

Decoder输出$H\in\mathbb R^{B\times T\times d}$，线性层得到$Z\in\mathbb R^{B\times T\times V_t}$，Softmax沿词表轴产生$p_{btv}$。这与Attention沿Key位置Softmax是两处不同归一化。无标签平滑时，一种按有效Token平均的交叉熵为

$$L=-\frac1N\sum_{b,t}m_{bt}\log p_{bt,y_{bt}},\qquad m_{bt}=\mathbf1[y_{bt}\ne PAD],\quad N=\sum_{b,t}m_{bt}.$$

把$[B,T,V_t]$变成$[BT,V_t]$、标签变$[BT]$只是常见接口组织，不改变监督含义；数值稳定的交叉熵通常直接接收logits。原Transformer §5.4实际采用0.1标签平滑，因此上述one-hot目标是解释基式，具体训练loss还需把one-hot换为平滑分布，不能说原文只用这个未平滑公式。[原论文训练说明](../../来源/SRC-TRANSFORMER/阅读笔记.md#原论文怎样训练与评估)；[教学代码Batch.ntokens与LabelSmoothing](../../来源/SRC-ANNOTATED-TRANSFORMER/阅读笔记.md#遮罩与标签平滑要连着看)。原文§5.1讲分批Token数，并未给出这套PAD loss归一化公式。

## 一个翻译loss怎样把梯度传回Encoder

把一层交叉注意力简写为$C=A V$，$A=softmax(QK^\top/\sqrt{d_k})$，$K=H_{enc}W_K,V=H_{enc}W_V$。若$G=\partial L/\partial C$，仅看Value通路已有

$$\frac{\partial L}{\partial V}=A^\top G,\qquad \left.\frac{\partial L}{\partial H_{enc}}\right|_V=(A^\top G)W_V^\top.$$

另外还有经过$A$、$K$回到编码器的Key通路；各Decoder交叉注意力层的贡献会累加，再通过编码器反传。Query通路则更新解码器前序状态与参数。只要计算图连通而未人为`detach`/冻结，编码器便能从目标预测loss训练，不需要额外生成源语言的loss。这里是对Transformer §3.2.3结构的链式法则展开，不是新实验。

## 为什么mask与训练并行不冲突

在某一层，所有Token的输入来自上一层，已经同时已知。Attention每一行从这些已知输入算Q/K/V并聚合，不把同层前一行的输出再喂给后一行。下三角mask只删掉禁止信息边，所以训练仍可一次算全部目标位置。层之间与若干子层之间仍有先后顺序，不能把“序列维可并行”解释为整网所有层同时执行。[遮罩的实现与广播](Attention遮罩与填充.md#因果依赖为何不阻止训练并行)

## 生成时哪些可以重用

推理先对固定源句运行一次Encoder，从BOS开始逐步选Token，直到EOS或长度上限。未来Token尚未知，所以目标侧仍自回归；greedy或beam决定如何选/扩展候选，不改变这个依赖。未用缓存的教学实现每步重算整个已生成前缀；用缓存的实现只处理新增位置，在各层复用历史K/V。[Annotated Transformer的greedy_decode边界](../../来源/SRC-ANNOTATED-TRANSFORMER/阅读笔记.md#论文文字和实际代码的差异)

训练时交叉注意力Query覆盖全部目标位置；增量推理时通常只算新位置（或beam批）的Query，编码器memory固定，每层的交叉Key/Value投影也可缓存。不同层通常有不同投影，不能把它理解成全Decoder共一份投影后的K/V。因果自注意力的历史状态在后续Token加入后不变，这是历史缓存成立的条件；双向注意力的旧状态可能改变，不能直接照搬。[位置偏移与旋转Key的固定实现](../../来源/SRC-LLAMA-CACHE-CODE/阅读笔记.md)。一般推理不计算监督loss或参数更新；评估时如提供真实目标，也可以另外计算loss，这并不等于已知了生成结果。

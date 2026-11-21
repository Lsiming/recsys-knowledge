---
id: "transformer-position"
title: "Transformer的位置编码：正弦、学习表与RoPE"
type: "concept"
status: "reviewed"
updated: "2026-11-21"
summary: "比较正弦、学习位置表与 RoFormer 的相对旋转，解释旋转键缓存及长度外推的条件"
aliases: ["正弦位置编码", "Sinusoidal PE", "pos和i", "高低频", "偶数维奇数维", "旋转矩阵", "RoPE", "KV Cache", "旋转Key"]
sources: {"SRC-TRANSFORMER": "2f1f9bf5db06a169aa117374ef34952e2b94e55aae46648e6f0d1280b4055d3e", "SRC-ROFORMER": "a83a7bdb16a8b48f55940315b3808f519552a41623ecfbe5e19cb219fc11fdb8", "SRC-LLAMA-CACHE-CODE": "e55e955775dd72fa548253694315647318567770485176edf06ac92b4beb54dc", "SRC-GPT1": "346378979c197abef55857af94342a537f9401868d4cac993cf0d3aab8260bee", "SRC-SASREC": "4d1a1790276a3327439223472a93ed9610e6da82fe26979fdd9c2f3f1f01432b", "SRC-SASREC-CODE": "823147e3d84a55fb68b603db06eda3adb8da208e69a03ba8c14d11f0347656ff"}
related: ["self-attention-context", "transformer-training-translation"]
---
# Transformer的位置编码：正弦、学习表与RoPE

不带位置机制的全可见自注意力对序列置换等变，逐位置FFN也不会主动编码Token次序；因而原始架构另需位置表示来区分顺序。原始Transformer把位置向量加到Token嵌入上，RoPE则在每层投影后旋转Q/K。位置机制和可见性mask是独立选择：RoPE既能用于因果注意力，也能用于双向注意力。

## 正弦公式中的位置、维度与频率

原文§3.5定义

$$PE(p,2i)=\sin(p\omega_i),\quad PE(p,2i+1)=\cos(p\omega_i),\quad \omega_i=10000^{-2i/d}.$$

$p$是Token在序列中的位置，$i=0,\ldots,d/2-1$索引**特征维度对**，不是Token编号。每对维度使用一个频率；$i$越大，频率越低、变化越慢。以$d=4$为例：

$$PE(p)=[\sin p,\cos p,\sin(p/100),\cos(p/100)].$$

所以第二组分母是100。高低频提供不同变化尺度，不能把它们解释成“高频负责近邻，低频负责远邻”的固定语义分工；单个周期分量也不能唯一表示所有位置。离散公式的最大波长为$2\pi10000^{(d-2)/d}$，原文把整体范围概述为$2\pi$到$10000\cdot2\pi$，后一个端点是尺度概述，有限$d$下不严格取到。[Transformer §3.5，PDF第6页](https://arxiv.org/pdf/1706.03762v7#page=6)

固定正弦PE没有需要优化的位置Embedding参数。实现可以预先算表作为buffer，也可按需计算；算出的表不等于可学习表。Token Embedding本身仍是可训练参数，原版输入是$\sqrt d E[token]+PE(p)$。

## 为什么sin与cos成对能表达偏移

对固定频率$\omega$，令$u_p=[\sin(p\omega),\cos(p\omega)]^\top$。由和角公式：

$$u_{p+k}=\underbrace{\begin{bmatrix}\cos(k\omega)&\sin(k\omega)\\-\sin(k\omega)&\cos(k\omega)\end{bmatrix}}_{T_\omega(k)}u_p.$$

变换只依赖偏移$k$，不依赖起点$p$。正弦与余弦在平移下构成一个封闭的二维函数空间；只保留sin时一般无法仅用一个常数倍表达任意偏移。这解释了使用成对基函数的数学便利。偶数维放sin、奇数维放cos是一种坐标排列；若一致地交换，核心性质不变。不是偶数Token和奇数Token使用不同公式。

纯位置向量还满足

$$u_p^\top u_{p+k}=\cos(k\omega),\qquad PE(p)^\top PE(q)=\sum_i\cos((p-q)\omega_i).$$

但实际Attention中$Q=(X+P)W_Q,K=(X+P)W_K$还包含内容、交叉项和学习投影，不能据此说实际分数只依赖位置差。这些等式是对§3.5的数学展开；作者以固定偏移可线性表达为设计假设，并未证明网络一定学会相对位置算法。表3(E)仅显示该机器翻译开发协议中学习式PE与正弦PE表现接近，也未证明长度外推必然可靠。[§3.5；表3，PDF第9页](https://arxiv.org/pdf/1706.03762v7#page=9)

## 学习位置表为什么不能直接保证长度外推

学习式绝对位置表为$P\in\mathbb R^{L_{\max}\times d}$，位置$i$直接取$P_i$。通常仅将位置表用于输入查表时，训练只覆盖前$L_{train}$个位置，其余行便没有经位置查表收到这些样本的梯度；若同一张表还被其他路径使用，须另计那些梯度。超出表长则不能直接查表。扩表、插值、重新训练或改变位置方案都是额外设计，不能由“参数可学习”自动完成。

GPT初代在512 Token上下文训练，并使用学习式位置表；原文没有给出与正弦位置的隔离对照，也没证明长序列外推能力。[GPT §4.1，第5页](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf#page=5)。即使每个位置都有定义，序列长度变化仍可能改变注意力分布，因而正弦或RoPE“可以算更大索引”也不等于效果必然保持。位置公式的可计算范围与训练后模型的可靠范围应分别讨论。

SASRec主要设置与初代GPT一样，使用可学习的绝对位置表；SASRec的位置编号对应当前定长行为窗口的槽位。两者的输入和训练流程不同：SASRec按物品ID查找Embedding，直接用用户行为序列从头训练下一物品预测模型；初代GPT按文本Token查找Embedding，先预训练语言模型，再用预训练参数初始化下游任务并微调。GPT的预训练本身也从随机初始化开始，见[GPT训练起点与参数迁移](../../来源/SRC-GPT1/阅读笔记.md#预训练改变参数的起点微调改变参数的用途)。

SASRec作者称固定位置编码在其设置更差；这不等于学习表普遍优于正弦，也不同于表IV中直接去掉位置表示的消融。具体输入、共享范围和左填充槽位见[SASRec位置说明](../../来源/SRC-SASREC/阅读笔记.md#位置是共享槽位不是用户专属编号)，原始比较见[§III-A，第3页](https://arxiv.org/pdf/1808.09781v1#page=3)。

## 共享位置表怎样广播和累积梯度

学习位置表$P\in\mathbb R^{n\times d}$通常没有用户或batch参数轴。令批量输入$H^0_{bt}=M_{s_{bt}}+P_t$，广播只是让每个样本引用相同的$P_t$，不是复制出独立可训练变量。用$G^0_{bt}=\partial\mathcal L/\partial H^0_{bt}$表示已经包含目标遮罩、归约和整网反传的输入梯度，则位置查表路径给出

$$\frac{\partial\mathcal L}{\partial P_t}=\sum_b G^0_{bt}.$$

例如两个样本同一槽位贡献$(1,2)$和$(-0.5,3)$，这一路相加为$(0.5,5)$，不是分别更新用户专属位置。若Loss已平均，不再额外除一次batch；PAD清零位置的该输入路径梯度为零。正则项或其他共享用途仍须另加。物品表则按物品ID累加，不按窗口槽位：同一物品在不同位置、不同样本出现时也汇到同一行。这个结果来自共享查表与加法的链式法则。

位置ID是数据构造的决定，不能从“绝对位置”推出永远不变。SASRec的定长左填充中，窗口长5时历史ABCD为[PAD,A,B,C,D]，追加E变为[A,B,C,D,E]；A由零基槽位1移到0，仍共享同一张P表，但查用的行从$P_1$改为$P_0$。推理时参数没有更新，向量也可因换行而变化。原论文的填充与学习表见[SASRec §III-A，第3页](https://arxiv.org/pdf/1808.09781v1#page=3)，固定脚本的range/tile见[位置表实现](../../来源/SRC-SASREC-CODE/阅读笔记.md#共享物品表与窗口位置表)；它对[KV缓存有效性](Attention计算与存储.md#因果缓存成立需要固定哪些条件)有直接影响。

## 从加性位置向量到RoPE

对**投影后**的列向量$q_m,k_n\in\mathbb R^{d_k}$，按两维一组定义

$$R_i(m)=\begin{bmatrix}\cos(m\theta_i)&-\sin(m\theta_i)\\\sin(m\theta_i)&\cos(m\theta_i)\end{bmatrix},\quad R(m)=\operatorname{diag}(R_0(m),\ldots),$$

$$q'_m=R(m)q_m,\qquad k'_n=R(n)k_n.$$

原始RoPE取$\theta_i=10000^{-2i/d_k}$，$i$从0开始；经典完整旋转要求头维度为偶数。旋转保持向量模长，且

$$R(m)^\top R(n)=R(n-m),\qquad (q'_m)^\top k'_n=q_m^\top R(n-m)k_n.$$

于是位置差直接进入内容点积。这是“按绝对位置各自旋转，匹配时形成相对位移”的含义；实际数值仍取决于$q_m,k_n$。旋转号和行列向量约定可以让式中写成$m-n$，不能只据正负号判定公式错。[RoFormer v5 §3.1–3.2、式(11)–(16)](https://arxiv.org/html/2104.09864v5#S3.SS2)；公式(16)右侧的内容投影应按左侧展开理解为$x_m^\top W_q^\top R(n-m)W_kx_n$，不可漏掉$W_q$的转置。

相较于输入加性PE，RoPE在打分结构中直接规定相对旋转；它不需要传统的可学习绝对位置表，也不需要显式构造一整张相对位置向量矩阵。可计算任意位置的旋转并不保证超出训练长度后任务效果可靠；也不能从这条等式推出Attention权重随距离严格单调递减。双向、翻译和自回归任务都可采用位置旋转，可见范围由mask与任务决定。论文提及的自回归/线性Attention兼容性是适用方式，不是只能用于自回归的限制。[RoFormer §3.3](https://arxiv.org/html/2104.09864v5#S3.SS3)

| 方法 | 位置在哪里进入 | 需要学习什么 | 长度边界 |
|---|---|---|---|
| 正弦绝对PE | 输入嵌入加固定向量 | 无位置表参数 | 公式可算更长位置，效果需验证 |
| 学习式绝对PE | 输入嵌入加位置查表 | 每个位置的向量 | 未训练/未建表的位置需额外处理 |
| RoPE | 每层投影后旋转Q/K | 原始频率预设，无传统位置表 | 旋转可算更长位置，效果需验证 |

“相对位置编码”是方法族：例如T5使用相对距离桶给Attention logits加可学习偏置，与RoPE旋转内容向量不同，不能一概而论。具体方法见[T5精读](../../来源/SRC-T5/阅读笔记.md)。

### 频率衰减、线性注意力和长度外推

对每组复数坐标，把内容乘积记为 $h_i$，以 $\Delta=m-n$ 记位置差。RoPE 的分数是 $\Re\sum_i h_i e^{\mathrm{i}\Delta\theta_i}$。令 $S_j(\Delta)=\sum_{i<j} e^{\mathrm{i}\Delta\theta_i}$，$h_{d/2}=0$。Abel 变换把复数和改写为 $-\sum_i S_{i+1}(h_{i+1}-h_i)$。不同角频率的部分和在较大位移处会更多相消，作者图 2 展示了 $\sum_j |S_j|$ 相关量的下降趋势和局部振荡。具体分数还取决于 $h_i$，注意力权重又取决于整行 Softmax 的其他分数。这个结论不意味着每对词的权重随距离均单调下降。

采用可因式分解的线性注意力时，可以对查询与键的特征映射分别应用旋转，再先聚合旋转键的外积和值。原论文公式（19）的分母沿用未旋转的非负特征，以避免旋转后符号相消。分子权重因而可以为负，其和也不保证等于分母。中文 CAIL2019-SCM 长度 512 与 1024 的结果说明给同一模型更多文本可能有益，表 5 没有同长 1024 的 WoBERT，而且 RoFormer 训练覆盖过 1536。检验长度外推时，还要固定训练覆盖、比较方法与有效输入长度。[RoFormer §3.3–3.4、§4.5](../../来源/SRC-ROFORMER/阅读笔记.md)

## 为什么缓存已经旋转的Key

在固定参数、固定位置规则的因果解码中，历史位置$m$的该层输入状态不受未来Token影响，所以$k'_m=R(m)k_m$可复用。每步仅计算新位置的Q/K/V，旋转新Q/K，把新$k'_m$与未旋转的$v_m$追加到该层缓存，再用新Query读取全部缓存。缓存未旋转Key并在读取时逐个旋转也能得到同一打分，但反复旋转所有历史Key会增加工作。

这一“通常如此”有直接代码依据：Llama 2官方实现先在`Attention.forward`中调用`apply_rotary_emb(xq,xk)`，再将`xk`写入`cache_k`，`xv`直接写入`cache_v`；`Transformer.forward`按`start_pos:start_pos+seqlen`取旋转频率，不能把每个新Token都从位置0开始。它是逐层缓存，不是原始Embedding的缓存。[固定代码与阅读说明](../../来源/SRC-LLAMA-CACHE-CODE/阅读笔记.md)。若动态修改频率、重设滑窗位置或改变可见上下文，缓存等价条件需重新核对；此处不把这些变体的行为当作已验证。

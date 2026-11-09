---
id: "transformer-position"
title: "Transformer的位置编码：正弦、学习表与RoPE"
type: "concept"
status: "reviewed"
updated: "2026-11-08"
summary: "解释频率与成对维度、偏移的线性变换、RoPE相对点积及旋转Key缓存"
aliases: ["正弦位置编码", "Sinusoidal PE", "pos和i", "高低频", "偶数维奇数维", "旋转矩阵", "RoPE", "KV Cache", "旋转Key"]
sources: {"SRC-TRANSFORMER": "2f1f9bf5db06a169aa117374ef34952e2b94e55aae46648e6f0d1280b4055d3e", "SRC-ROFORMER": "d6c0d9c59c5151fab8c5a0febd7f9901b4391991480e4a49a7bc4957f80036c4", "SRC-LLAMA-CACHE-CODE": "e55e955775dd72fa548253694315647318567770485176edf06ac92b4beb54dc"}
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

## 为什么缓存已经旋转的Key

在固定参数、固定位置规则的因果解码中，历史位置$m$的该层输入状态不受未来Token影响，所以$k'_m=R(m)k_m$可复用。每步仅计算新位置的Q/K/V，旋转新Q/K，把新$k'_m$与未旋转的$v_m$追加到该层缓存，再用新Query读取全部缓存。缓存未旋转Key并在读取时逐个旋转也能得到同一打分，但反复旋转所有历史Key会增加工作。

这一“通常如此”有直接代码依据：Llama 2官方实现先在`Attention.forward`中调用`apply_rotary_emb(xq,xk)`，再将`xk`写入`cache_k`，`xv`直接写入`cache_v`；`Transformer.forward`按`start_pos:start_pos+seqlen`取旋转频率，不能把每个新Token都从位置0开始。它是逐层缓存，不是原始Embedding的缓存。[固定代码与阅读说明](../../来源/SRC-LLAMA-CACHE-CODE/阅读笔记.md)。若动态修改频率、重设滑窗位置或改变可见上下文，缓存等价条件需重新核对；此处不把这些变体的行为当作已验证。

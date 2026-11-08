---
id: "layernorm-residual"
title: "LayerNorm如何归一化、训练并传递残差梯度"
type: "concept"
status: "reviewed"
updated: "2026-11-08"
summary: "以逐Token公式、反向传播和训练推理对照解释LN与Pre/Post-LN"
aliases: ["Layer Normalization", "LayerNorm", "LN", "gamma", "beta", "均值方差", "Pre-LN", "Post-LN", "Identity Mapping", "恒等映射", "RMSNorm", "BatchNorm"]
sources: {"SRC-LAYERNORM": "c94757daf3ae1e3a6cd0b58db86620bd653012b2d55ebdecf5ed5415df086739", "SRC-TRANSFORMER": "2f1f9bf5db06a169aa117374ef34952e2b94e55aae46648e6f0d1280b4055d3e", "SRC-PRELN": "d44f072ece3dcb69ba2cd12843e41390c0c3020650a7019175c0947d075cc3b3", "SRC-RMSNORM": "3a1391ca35d1d0b8071ea812709837449ce0b0404d72bfb751654f45b91c61f0", "SRC-LLAMA-CACHE-CODE": "e55e955775dd72fa548253694315647318567770485176edf06ac92b4beb54dc"}
related: ["self-attention-context"]
---
# LayerNorm如何归一化、训练并传递残差梯度

Transformer中的Layer Normalization（LN）对每个Token的特征向量重新计算统计量，再施加共享的可学习缩放和偏移。统计量属于当前输入的计算结果，参数属于模型；区分这两者，就能同时解释LN的训练、推理与反向传播。LN放在残差分支内还是相加后，又决定了梯度路径经过哪些算子。

## 对每个Token的特征求统计量

对$X\in\mathbb R^{B\times S\times D}$，常规Transformer设归一化轴为最后的$D$维。固定样本$b$和位置$t$：

$$\mu_{bt}=\frac1D\sum_{r=1}^D X_{btr},\quad v_{bt}=\frac1D\sum_{r=1}^D(X_{btr}-\mu_{bt})^2,$$

$$\hat X_{btr}=\frac{X_{btr}-\mu_{bt}}{\sqrt{v_{bt}+\epsilon}},\qquad Y_{btr}=\gamma_r\hat X_{btr}+\beta_r.$$

$\mu,v$可以保留形状$[B,S,1]$，经广播作用于$[B,S,D]$；$\gamma,\beta$各为$[D]$，也在样本和位置轴广播。每个Token有自己的统计量，同一LN层的所有Token共享一组按特征排列的参数，所以输入输出都是$[B,S,D]$，不会压缩掉特征轴。各子层的LN通常各有自己的参数，并非全模型共享。

例如$x=[2,4,6,8]$，$\mu=5,v=5$，忽略epsilon得到$\hat x\approx[-1.342,-0.447,0.447,1.342]$。严格地说，$\hat x$的特征均值为0、方差是$v/(v+\epsilon)$，不总是恰好1；原向量恒定时$v=0$，标准化结果为0。逐维$\gamma,\beta$进一步改变最终输出，故LN不要求最终$Y$保持均值0、方差1，也不把所有元素限制在$[-1,1]$。

LN原论文§3、式(3)支持单个training case的层内统计，§3.1说明时间步分别计算；上述$[B,S,D]$是应用到Transformer的具体轴展开。稳定常数放在平方根内是此处采用的常见计算约定，教学版`std+eps`与它不同。[Layer Normalization v1 §3](https://arxiv.org/html/1607.06450v1#S3)；[教学实现差异](../../来源/SRC-ANNOTATED-TRANSFORMER/阅读笔记.md#论文文字和实际代码的差异)。

## 哪些是参数，哪些只是当前输入的统计量

| 对象 | 标准带仿射LN的数量 | 是否由优化器更新 | 推理时来源 |
|---|---|---|---|
| $\gamma,\beta$ | 各$D$，共$2D$ | 是 | 训练后的参数 |
| $\mu,v$ | 每Token各一个 | 否 | 根据当前Token重算 |
| $\epsilon$ | 一个设定常数 | 通常否 | 相同数值稳定设置 |

$D=512$时，一个标准带仿射LN有1024个可训练参数。共享$\gamma,\beta$是“对所有位置应用相同特征变换”的设计，与共享FFN类似；不是数学上禁止设计逐位置参数。去仿射、去bias等接口变体需另按定义核算。

LN无需单独loss。设任务损失的上游梯度为$g_{btr}=\partial L/\partial Y_{btr}$，链式法则给出

$$\frac{\partial L}{\partial\gamma_r}=\sum_{b,t}g_{btr}\hat X_{btr},\qquad \frac{\partial L}{\partial\beta_r}=\sum_{b,t}g_{btr}.$$

求和来自共享参数的所有使用位置；任务loss是否平均、排除PAD，已经体现在$g$中。优化器用这些梯度更新参数。若示意$\gamma\leftarrow\gamma-\eta\nabla_\gamma L$，这是普通SGD更新，不能称作Adam完整公式；Adam另有一阶/二阶矩与偏差校正。

统计量不是参数，仍然依赖输入。对单个Token，令$a_r=g_r\gamma_r,s=\sqrt{v+\epsilon}$，用横线表示特征维平均，则

$$\frac{\partial L}{\partial x_r}=\frac1s\left[a_r-\overline a-\hat x_r\,\overline{a\hat x}\right].$$

这条推导把$\mu(x),v(x)$的依赖一起计入，展示了梯度如何传回Attention/FFN等前序模块；不把中间统计量误当作停止梯度的常数。它是对LN公式的链式法则展开，并非原论文额外实验。

## 推理仍重算统计量，BN的行为取决于约定

标准LN在训练和推理都按当前Token重算$\mu,v$，使用同一组$\gamma,\beta$；常规推理只前向，不反传和更新。`eval()`本身并不是禁用自动微分的开关。LN层的计算规则相同，也不等于整个Transformer在训练与推理行为相同：Dropout等模块仍会变化。[LN原文摘要、§3](https://arxiv.org/html/1607.06450v1#abstract1)

BN通常按某个特征/通道汇总多个样本的统计。对$[B,S,D]$若按特征在$B,S$轴归约，训练统计会混入其他样本和位置，需要处理PAD，因果任务还须防止跨未来位置聚合。标准跟踪运行统计的BN在训练前向用当前批次统计、同时更新running statistics，在推理用运行统计；关闭跟踪的接口可以不同。不能把“BN总是只沿batch一轴”或“任何BN推理都固定运行统计”当作所有接口的定义。

## Pre-LN的恒等梯度项从哪里来

忽略Dropout，把一个Attention或FFN子层记作$f$，采用列向量Jacobian：

$$y_{pre}=x+f(\operatorname{LN}(x)),\quad J_{pre}=I+J_fJ_{LN};$$

$$y_{post}=\operatorname{LN}(x+f(x)),\quad J_{post}=J_{LN}(I+J_f).$$

恒等映射是残差支路直接把$x$送到相加处，$\partial x_i/\partial x_j=\mathbf1_{i=j}$组成单位矩阵$I$。Pre-LN的直接支路绕开子层LN与$f$；Post-LN的相加结果还经过LN，所以直接支路梯度也要乘$J_{LN}$。反传给列梯度时使用这些Jacobian的转置，不能混淆乘法次序。[原版Post-LN结构](https://arxiv.org/pdf/1706.03762v7#page=3)；[后续Pre/Post-LN结构，§3.3、表1](https://arxiv.org/html/2002.04745v2#S3.SS3)

多残差子层堆叠时，令$A_l=J_{f_l}J_{LN_l}$，内部堆叠的Jacobian为

$$J= (I+A_{L-1})\cdots(I+A_0).$$

展开包含一直选取恒等支路的一项$I$，也包含大量其他项，整体可以放大、衰减或在某方向抵消，不能保证每个奇异值都有正下界。实际模型在最后预测前还可能有final LN和输出投影，它们也会作用于最终梯度。因此“有一条直接路径”不等于“全网络梯度恒为1”，更不等于“完全避免梯度消失”。

Xiong等人的初始化分析给出更专门的支持：在其单头、简化权重形状、Q/K零初始化等假设下，分析Post-LN输出附近较大梯度及Pre-LN的尺度差异，并在指定翻译/BERT设置讨论移除warmup。该理论和实验不能推广成所有Pre-LN训练全程都不需要warmup、或任务质量一定优于Post-LN；本轮未复现这些实验。[§3.3–3.4、§4，原文与阅读边界](../../来源/SRC-PRELN/阅读笔记.md)。

## RMSNorm省去了哪一步

常见不带bias的实现采用

$$\operatorname{RMSNorm}(x)_r=\gamma_r\frac{x_r}{\sqrt{D^{-1}\sum_jx_j^2+\epsilon}}.$$

它不减均值，分母是均方根而非去均值后的标准差；输入均值非零时，两者不同，不能把RMSNorm说成省掉$\beta$的LN。原RMSNorm论文§4还给出带网络bias的一般式，所以“RMSNorm数学上绝不允许bias”也不对。上述常见无bias形式可直接核对Llama 2代码中的`RMSNorm`，不据此承诺任意硬件上的固定加速比例。[原文§4](https://arxiv.org/html/1910.07467v1#S4)；[固定实现](../../来源/SRC-LLAMA-CACHE-CODE/阅读笔记.md)。

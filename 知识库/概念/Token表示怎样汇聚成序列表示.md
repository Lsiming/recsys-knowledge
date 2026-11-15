---
id: "sequence-representation-pooling"
title: "Token表示怎样汇聚成序列表示"
type: "concept"
status: "reviewed"
updated: "2026-11-15"
summary: "比较因果末状态、专用提取Token、均值和注意力池化的信息范围、梯度路径及填充处理"
aliases: ["EXTRACT", "_classify_", "句子表示", "句向量", "Last Token Pooling", "Mean Pooling", "Attention Pooling", "CLS"]
sources: {"SRC-GPT1": "346378979c197abef55857af94342a537f9401868d4cac993cf0d3aab8260bee", "SRC-GPT1-CODE": "7cd5d15bf083af358d280a6b681bf3d17c1069301589081bd501543e662147f9", "SRC-BERT": "c6a7d8a52b8f422d4e8e9db2dab86dee349c31f2d91170511513e3bc41fd5331"}
related: ["pretraining-task-transfer", "self-attention-context", "attention-mask-padding", "layernorm-residual", "language-model-loss-gradient"]
---
# Token表示怎样汇聚成序列表示

Transformer输出的是一组位置状态，而分类、匹配或检索通常需要一个序列表示。读出某个位置、对多位置平均、再学一层注意力，都是从$H=[h_1,\ldots,h_T]$得到向量$z$的办法。选择时要同时看骨干的信息可见范围、训练信号和输出用途；同一池化公式并不保证不同预训练模型得到同样适用的句向量。

## 先区分可见输入和最终保留的信息

因果骨干的$h_i=f_i(x_1,\ldots,x_i)$，较早位置没有右侧Token，$h_T$可依赖整段有效输入。因此对整段已有文本做Mean Pooling，不会增加末位置在结构上不可见的新原始Token；它会提供其他位置的不同变换结果，而这些结果未必都被固定宽度的$h_T$保留下来。

“可读取全部输入”与“已经充分表示所有内容”不是一回事。例如最后状态经训练只保留某个类别相关特征，它不必能重建每一个词。反过来，平均多个状态也不保证补回所需信息。在因果模型里，平均值混合了不同前缀长度的表示，并不是把每个Token在完整上下文下的表示平均。信息范围由[因果遮罩](Attention遮罩与填充.md#因果依赖为何不阻止训练并行)决定。

## 专用提取位置与最后真实Token

若输入为`[Start, 文本, Extract]`，末尾专用Token的位置能读取全部前文，微调时用其状态接任务头。GPT图1的Extract是这一角色；官方代码实际用`_classify_`，不是新增名为EXTRACT的网络层。[GPT §3.2–3.3与图1，第3–4页](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf#page=4)；[代码中的提取操作](../../来源/SRC-GPT1-CODE/阅读笔记.md#分类token怎样定位)。

专用位置提供固定的Token身份和明确的监督落点，输入长度不同时位置编号仍会变，并非一个固定绝对位置。其嵌入与骨干要通过任务训练才学会有用读出；仅在文本后追加一个陌生Token，不会自动得到高质量句向量。

直接使用最后一个真实文本Token也可定义模型，只需把分类监督施加在该状态。区别是该位置还对应某个具体词及其位置；专用Token使读出角色一致。GPT没有用隔离消融证明专用Token一定优于真实末Token，因此两者效果不能由这个机制单独判定。追加了Extract时，“最后有效Token”通常是Extract，而“最后真实文本Token”在它前面；必须先明确想取哪一个。

## 残差为何不等于强制保留词义

输入$h_i^{(0)}=E[x_i]+P_i$本来就包含自身Token。GPT的Post-LN子层为

$$h_i'=LN(h_i+Attention_i(H)),\qquad h_i''=LN(h_i'+FFN(h_i')).$$

自身输入既参与残差，也参与Query以及可见的Key/Value，所以末状态可以依赖自身词和位置。“可以依赖”不等于一定被自身语义主导；变换、LN、参数学习和路径抵消都能改变甚至抹去某些信息。残差并不保证原词义在最终表示里原样可恢复，也不构成专用Token效果必优的证明。[LN与残差路径](LayerNorm与残差梯度.md#pre-ln的恒等梯度项从哪里来)。

因此，对“最后真实Token是否受自身影响”的准确解释是：计算图保留这种依赖通路，但依赖的强度、是否造成任务损害，要由具体参数与数据验证。

## GPT的Extract与BERT的CLS

| 维度 | GPT初代提取Token | BERT的`[CLS]` |
|---|---|---|
| 位置 | 有效序列末尾 | 序列开头 |
| 为什么能汇聚全输入 | 因果mask下末位置可读此前内容 | 双向注意力允许首位置读取后续有效Token |
| 原训练角色 | 下游新增边界/提取Token嵌入与任务头微调 | 预训练NSP用CLS，微调再接任务输出 |
| 表示用途 | 任务分类或候选评分 | 依任务使用序列或Token级状态 |

若在因果GPT开头直接放一个CLS，它读不到后文，不能只照搬BERT的位置。BERT原文也提醒未经微调的CLS不是现成有意义的句向量：任务分类可用不等于直接余弦检索好用。[BERT §3–3.1与脚注6，第3–4页](https://arxiv.org/pdf/1810.04805v2#page=4)；[BERT序列表示笔记](../../来源/SRC-BERT/阅读笔记.md#nsp与边界标记一起训练文本对表示)。

BERT的词恢复与CLS关系分类分别从不同位置进入损失，但共享骨干；CLS读出不是把每词表示先求平均。可沿[同一条BERT样本](../../来源/SRC-BERT/阅读笔记.md#nsp与边界标记一起训练文本对表示)核对读出、目标与反传的区别。

## Last与Mean究竟改变了什么

令$m_i\in\{0,1\}$选择参与池化的位置，$n=\sum_im_i>0$，$t_*$是指定的有效末位置：

$$z_{last}=h_{t_*},\qquad z_{mean}=\frac1n\sum_im_ih_i.$$

Last把直接读出放在一个状态上，学习把任务需要的信息汇入该状态；Mean直接使用多个状态的各特征均值，让信息从多个位置进入读出。特征维度都仍是$d$，Mean不会因为用了更多状态就增加输出维度。

Mean在多个位置都承载相近任务信息、个别状态噪声较大时，可能通过平均形成更合适的表示。这是机制上的可能性，不是GPT论文的比较结果；若噪声强相关，平均也未必降低它。反之，若仅一个位置携带关键特征$a$、其他位置该特征为0，平均后变成$a/n$；长序列会稀释这个特征。学习到的后续头可能补偿一部分尺度，但不保证恢复被平均抵消的信息。

选择还取决于训练是否针对该读出方式优化：只按下一Token训练的骨干、为句对分类微调的骨干、为检索对比学习的骨干，输出几何性质可能不同。不能脱离训练目标，把一种Pooling列成普遍最优。

## 池化怎样分配梯度

令$g=\partial\mathcal L/\partial z$，先把顶层各位置$h_i$作为独立中间变量，则

$$\left.\frac{\partial\mathcal L}{\partial h_i}\right|_{last}=\mathbf1[i=t_*]g,\qquad\left.\frac{\partial\mathcal L}{\partial h_i}\right|_{mean}=\frac{m_i}{n}g.$$

这说的是池化算子对顶层输出的**直接梯度**。Last的直接梯度只进被读出的顶层行，但该状态依赖较低层的前文状态，继续经过Attention后，前文Token和共享参数仍能收到梯度。不能说“Last只训练最后Token”；辅助LM目标也会另外提供梯度。[LM头与骨干反传](语言模型的词表预测与交叉熵.md#梯度怎样穿过lm头和共享embedding)。

Mean给所选顶层行相同的直接权重，但每个位置回到参数的Jacobian不同，参数更新并不均匀；序列越长，每行$1/n$越小，也不能单凭这个因子断言整网梯度更弱。

## Attention Pooling怎样学习读出权重

一种独立于骨干注意力的读出定义是

$$s_i=v^\top\tanh(Wh_i+b),\qquad\alpha_i=\frac{m_ie^{s_i}}{\sum_jm_je^{s_j}},\qquad z=\sum_i\alpha_ih_i.$$

它按学习到的分数选择各位置权重；Mean则是所选位置固定$1/n$。实现应在Softmax前屏蔽无效位置。该式用于比较读出机制，不是GPT初代新增了这层Attention Pooling。

当$\alpha$依赖$h$，梯度除了直接值路径$\alpha_ig$，还经过权重路径；对于上式每个$s_i$只依赖$h_i$的情形，

$$\frac{\partial\mathcal L}{\partial s_i}=\alpha_i g^\top(h_i-z),\quad\frac{\partial\mathcal L}{\partial h_i}=\alpha_i g+\alpha_i g^\top(h_i-z)\nabla_{h_i}s_i.$$

更多可学习参数提供了选择能力，也增加优化和过拟合的可能；有效性仍取决于训练目标与数据。对整段已知输入做句级池化可以使用全部有效状态；若输出用于某个中间时刻的预测，池化选择也必须限制到当时已知前缀，不能只给骨干加因果mask却池化未来行。

## 右填充时怎样取末位置和做均值

若mask严格形如`[1,1,1,0,0]`、有效Token从索引0连续排列，零基末有效索引为$\sum_im_i-1$。有左填充或内部空洞时不成立，可用$\max\{i:m_i=1\}$。每条至少一个有效Token是这些公式的前提，空序列必须另行处理。

例如`[Start,A,B,Extract,PAD,PAD]`的末有效索引为3，最后文本索引为2。官方代码直接按`_classify_`的ID定位，避免把末数组列当末有效Token；使用argmax前还须保证目标标记确实存在且符合预期次数。[固定代码定位](../../来源/SRC-GPT1-CODE/阅读笔记.md#分类token怎样定位)。

均值时使用$\sum_im_ih_i/\sum_im_i$，不能除以填充后的统一长度。池化mask可以进一步排除Start、分隔符和Extract；它表示“哪些状态参与读出”，不必等于Attention Key mask或LM Loss mask。PAD状态即使非零也可以安全排除，但已产生NaN时乘0不能修复，需先保证前向数值合法。[填充状态与监督](Attention遮罩与填充.md#pad输出和pad监督分别处理)。

## 从GPT疑问返回论文

[GPT学习思考](../../来源/SRC-GPT1/学习思考.md#extract与句子级表示)保留围绕提取位置的原始追问；[GPT任务适配](../../来源/SRC-GPT1/阅读笔记.md#用输入变换适配任务而非为每种关系重建架构)说明这些表示怎样接到具体分类、相似性与多选评分。

---
id: "attention-compute-memory"
title: "Attention的平方矩阵、KV缓存与FlashAttention"
type: "concept"
status: "reviewed"
updated: "2026-11-21"
summary: "区分分数元素数、算量、逐层缓存与FlashAttention的IO节省"
aliases: ["Attention Score存储", "平方复杂度", "KV Cache", "FlashAttention", "online softmax", "FP16显存", "prefill", "decode"]
sources: {"SRC-TRANSFORMER": "2f1f9bf5db06a169aa117374ef34952e2b94e55aae46648e6f0d1280b4055d3e", "SRC-FLASHATTENTION": "12fc356b011202b581abd7a8aff9c9e237f7636fab0e7216cd452054c2e77616", "SRC-LLAMA-CACHE-CODE": "e55e955775dd72fa548253694315647318567770485176edf06ac92b4beb54dc", "SRC-SASREC": "4d1a1790276a3327439223472a93ed9610e6da82fe26979fdd9c2f3f1f01432b", "SRC-SASREC-CODE": "823147e3d84a55fb68b603db06eda3adb8da208e69a03ba8c14d11f0347656ff"}
related: ["self-attention-context", "transformer-position"]
---
# Attention的平方矩阵、KV缓存与FlashAttention

普通自注意力将$n$个Query逐一与$n$个Key匹配，所以分数有$n^2$个；单次匹配再沿头特征维求和，才得到位置混合的算术成本。缓存历史状态和不物化分数矩阵解决不同问题，不能仅凭“省显存”就断定算量也变成线性。

## 二维分数为何有平方个元素

单头$Q\in\mathbb R^{n_q\times d_k},K\in\mathbb R^{n_k\times d_k}$，$QK^\top\in\mathbb R^{n_q\times n_k}$；两个保留轴来自Query位置与Key位置，共同的特征轴被求和。自注意力$n_q=n_k=n$，分数有$n^2$个；交叉注意力则为$n_tn_s$个。批量多头的显式分数形状$[B,H,n_q,n_k]$，元素数$BHn_qn_k$，缩放与Softmax不改变该形状。[Transformer §3.2、§4](https://arxiv.org/pdf/1706.03762v7#page=4)

例如$B=2,H=8,n=1024$，一份显式分数有16,777,216个元素；假设确实以FP16存储，每元素2字节，则为33,554,432字节，即32 MiB。Score与Probability若同时保留还要各计一份；框架可能用FP32计算Softmax或融合算子，实际峰值还包括其他激活、梯度、参数和优化器状态，不能把此数当整模型显存。

因果连接只保留下三角的$n(n+1)/2$项，仍是平方阶；朴素实现还可能照算整张稠密矩阵。固定总宽$d=Hd_k$，位置混合计算为$O(Bn^2d)$，完整块另含投影与FFN的$O(Bnd^2)$项。固定$d$增加head数可不改变主要算量/投影参数阶数，却增加显式Score的head轴元素数。

## KV Cache是逐层历史状态缓存

在固定因果可见性与位置规则下，历史Token的该层K/V不因新Token到来而改变，可逐层保存，仅计算新增输入。固定头维$d_k=d_v=d_h$、KV头数$H_{kv}$、层数$L$时，缓存$T$个位置的K/V元素数为

$$2LBT H_{kv}d_h,$$

再乘实际每元素字节数。MHA取$H_{kv}=H$；GQA/MQA的KV头更少，不能用Query头数代替KV头数估存储。代码可静态核对Llama的`n_kv_heads`与`cache_k/cache_v`形状；此处未核验不同头共享方式的模型质量。

无缓存重算完整前缀时，每步不仅重算旧K/V，还重算旧位置的多层状态、投影和FFN。缓存后每层新Query仍读取历史Key：给定长度$P$的固定前缀，再逐步处理$N$个新位置，匹配数按$\sum_{t=1}^N(P+t)=NP+N(N+1)/2$增长；它没有消除位置匹配的累计平方项。Prefill可并行编码已知前缀，decode依赖新Token逐步到来。[静态缓存实现](../../来源/SRC-LLAMA-CACHE-CODE/阅读笔记.md)

## 因果缓存成立需要固定哪些条件

“当前用户状态变了”通常指新的末端状态$h_{t+1}$，不等于所有旧位置$h_i$都变了。设参数固定、Dropout关闭、旧Token及其位置ID不变、每行的可见Key集合不变，且LN/FFN等操作逐位置进行。对层数归纳：旧输入$h_i^0$不变；如果上一层旧状态不变，位置$i$只读$j\le i$，追加新位置不会改变它的Q/K/V、Softmax分母或输出。因此所有旧层状态以及由它们投影的K/V均可复用。这是计算图性质，实际浮点核的计算次序可能产生微小差异。因果结构依据[原始Transformer笔记](../../来源/SRC-TRANSFORMER/阅读笔记.md)；缓存代码实例见[固定Llama实现](../../来源/SRC-LLAMA-CACHE-CODE/阅读笔记.md)。

新增第$t+1$个位置时，在第$l$层先由该层输入$h_{t+1}^{l-1}$按该实现的归一化/投影规则计算$q_{t+1}^l,k_{t+1}^l,v_{t+1}^l$；把新K/V加入该层缓存，Query读取旧缓存和自身K/V，得到本层新输出，再交给下一层。新K/V一经该层投影即可写入，整个位置也可结束后统一提交缓存以保证请求一致性；无需等全部层完成才在数学上定义它。每层有自己的缓存，新Query通常不需要重算旧Query。只有最末层状态不足以还原其他层的历史K/V。

这些前提失效时，因果mask本身不能挽救缓存：

- **改写第j个历史输入**：在位置与更早上下文均不变时，j之前可保留，j及之后的有关层状态/缓存需重算；即使改写后序列末项相同，也不能只更新末项。删除还可能移动后续位置ID。
- **定长左填充重新对齐**：SASRec窗口[PAD,A,B,C,D]追加E后成为[A,B,C,D,E]，旧物品都换了位置向量，不能直接把原K/V接到E前。即使尚未发生真实历史淘汰，这种槽位移动已足以破坏等价。
- **滑动窗口淘汰旧输入**：即便保留剩余Token的原位置ID，多层历史状态也可能含被淘汰输入的信息。仅删除最早K/V，不等于从剩余窗口重新编码；第一层原始输入投影与高层上下文缓存要分开判断。
- **模型或表示更新**：权重、物品表、位置表、可见规则、跨时间归一化或适配器改变后，相关缓存需按模型/规则版本失效；普通训练Dropout也不满足确定性复用前提。

SASRec与GPT共有因果前缀的这一性质，但SASRec通常等待真实新行为到来、输出物品分数，GPT生成时把选出的Token继续追加。原SASRec的学习窗口位置与左填充会频繁重新对齐；现代GPT常在一次生成中固定旧位置、递增新位置，但其滑窗或位置重设也须重新核对。SASRec作者脚本没有KV缓存接口，不能把这段可行性推导当作论文已实现的优化或速度结论。[原输入构造与推理](../../来源/SRC-SASREC/阅读笔记.md#训练完后怎样给这位用户推荐)；[固定实现边界](../../来源/SRC-SASREC-CODE/阅读笔记.md#填充遮罩与末位置切片)。

若改为不移动旧Token的位置方案、按合适条件缓存，单步每层主要计算可由完整前缀的$O(t^2d+td^2)$减少到$O(td+d^2)$，仍需读取历史KV；参数、位置语义与训练部署一致性需要重新验证，不能直接声称等价于原SASRec窗口模型。候选打分和ANN成本另计。

## FlashAttention为什么不必保存完整概率矩阵

FlashAttention在数学上仍计算$softmax(QK^\top/\sqrt{d_k}+M)V$。它把Q/K/V分块搬入片上存储，计算块分数后立即归约，并保存每行的小量统计，减少完整Score/Probability在高带宽显存HBM中的写入和读取。所谓exact指未换成低秩、稀疏等近似Attention；浮点归约次序变化不保证逐位完全相同。[FlashAttention 初版论文 arXiv v2 §2–3.1](https://arxiv.org/html/2205.14135v2#S3.SS1)

以一行Query为例，对已处理块记录最大值$m$、归一化分母$\ell=\sum_j e^{s_j-m}$和未归一化输出$u=\sum_j e^{s_j-m}v_j$。新块的统计为$(m_b,\ell_b,u_b)$，合并为

$$m'=\max(m,m_b),$$
$$\ell'=e^{m-m'}\ell+e^{m_b-m'}\ell_b,\qquad u'=e^{m-m'}u+e^{m_b-m'}u_b.$$

处理完所有Key块后取$o=u/\ell$。两个块的贡献先换到共同最大值再相加，所以等价于整行Softmax，而非“每块单独Softmax后再平均”。这个合并式是原文在线归一化的逐行展开；全mask行仍需安全语义。[§3.1；附录B.1](https://arxiv.org/html/2205.14135v2#A2.SS1)

## 反向只重算当前块，整行修正量来自前向输出

无 dropout 时，$P_{ij}=\exp(S_{ij}-m_i)/\ell_i$，可用前向保存的每行统计量从当前分数块重建。给定上游 $dO$，有 $dP=dO V^\top$，Softmax 的行修正量 $D_i=\sum_j P_{ij}dP_{ij}$ 可化为 $dO_i\cdot O_i$。每块计算 $dS_{ij}=P_{ij}(dP_{ij}-D_i)$ 后累加对 $Q,K,V$ 的梯度。训练中若有 dropout，原算法在反向恢复前向的同一伪随机掩码。这样把概率块的生命周期缩短到片上计算。推理只走前向。KV Cache 保存历史投影，FlashAttention 管理一次注意力计算的访存，两者可以同时使用。[FlashAttention 附录 B.2–B.4](../../来源/SRC-FLASHATTENTION/阅读笔记.md#反向如何重算概率)

## IO 复杂度与算术复杂度分别由什么决定

论文定理 1 的 $O(N^2d)$ FLOPs 来自计算所有查询与键的配对，额外全局存储为 $O(N)$，另有 $O(Nd)$ 输入与输出。定理 2 在两级存储模型下按 SRAM 可容纳元素数 $M$ 计。键值每块放 $O(M/d)$ 行，一共 $O(Nd/M)$ 块。每块扫描 $O(Nd)$ 个查询、输出和统计量，因此有 $\Theta(N^2d^2/M)$ 次 HBM 访问。固定 $M,d$ 时仍为二次，但 $M\gg d^2$ 时搬运量明显更小。命题 3 的下界约束整个 SRAM 容量区间上的同时改进，证明在 $M=\Theta(Nd)$ 处使用输入规模下界。块稀疏版跳过预先设为不可见的块，IO 主项乘非零块占比 $s$，并保留输入输出 $\Theta(Nd)$ 项。全量注意力的速度、显存与启用更长上下文后的任务结果应分开读图和评估。[FlashAttention §3.2–4.3](../../来源/SRC-FLASHATTENTION/阅读笔记.md#算力hbm-和训练收益怎样区分)

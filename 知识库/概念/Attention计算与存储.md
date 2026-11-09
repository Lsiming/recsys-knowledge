---
id: "attention-compute-memory"
title: "Attention的平方矩阵、KV缓存与FlashAttention"
type: "concept"
status: "reviewed"
updated: "2026-11-08"
summary: "区分分数元素数、算量、逐层缓存与FlashAttention的IO节省"
aliases: ["Attention Score存储", "平方复杂度", "KV Cache", "FlashAttention", "online softmax", "FP16显存", "prefill", "decode"]
sources: {"SRC-TRANSFORMER": "2f1f9bf5db06a169aa117374ef34952e2b94e55aae46648e6f0d1280b4055d3e", "SRC-FLASHATTENTION": "d82bb31c05732b818284a36e271c544cecf564128f219a7357d0f8bf7ca9bcfa", "SRC-LLAMA-CACHE-CODE": "e55e955775dd72fa548253694315647318567770485176edf06ac92b4beb54dc"}
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

## FlashAttention为什么不必保存完整概率矩阵

FlashAttention在数学上仍计算$softmax(QK^\top/\sqrt{d_k}+M)V$。它把Q/K/V分块搬入片上存储，计算块分数后立即归约，并保存每行的小量统计，减少完整Score/Probability在高带宽显存HBM中的写入和读取。所谓exact指未换成低秩、稀疏等近似Attention；浮点归约次序变化不保证逐位完全相同。[FlashAttention v2 §2–3.1](https://arxiv.org/html/2205.14135v2#S3.SS1)

以一行Query为例，对已处理块记录最大值$m$、归一化分母$\ell=\sum_j e^{s_j-m}$和未归一化输出$u=\sum_j e^{s_j-m}v_j$。新块的统计为$(m_b,\ell_b,u_b)$，合并为

$$m'=\max(m,m_b),$$
$$\ell'=e^{m-m'}\ell+e^{m_b-m'}\ell_b,\qquad u'=e^{m-m'}u+e^{m_b-m'}u_b.$$

处理完所有Key块后取$o=u/\ell$。两个块的贡献先换到共同最大值再相加，所以等价于整行Softmax，而非“每块单独Softmax后再平均”。这个合并式是原文在线归一化的逐行展开；全mask行仍需安全语义。[§3.1；附录B.1](https://arxiv.org/html/2205.14135v2#A2.SS1)

原文定理1仍给出$O(n^2d_k)$ FLOPs；节省的是中间物化和IO，反传还可重算概率块而不保存整矩阵，不能宣传成dense Attention算术变为$O(n)$。本轮未运行kernel、显存或吞吐测试，未据论文硬件数字估计本机速度。KV Cache减少生成重复状态计算，FlashAttention减少一次Attention的IO，两者可以同时使用，不能互相替代。

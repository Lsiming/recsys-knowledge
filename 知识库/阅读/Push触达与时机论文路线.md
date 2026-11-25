---
id: "push-timing-reading-path"
title: "Push触达与时机：2022—2026年工业论文路线"
type: "map"
status: "reviewed"
updated: "2026-11-25"
summary: "从日内时槽分配、发送或等待到自触发调度，筛选大厂Push时机与长期收益论文"
aliases: ["Push", "触达时机", "通知推荐", "send time optimization", "notification", "STEPS", "TIM", "DeepPvisit", "FairNotification"]
sources: {"SRC-TIM": "7e73df972b74f7b7b888353975a737296196afba65d0623bfdb242ea4620bf8f", "SRC-TSIL": "40312e0e4785536c1e1f37dd1c65e2db4354fcb35b9f952f7448e468938afcdc", "SRC-DEEPPVISIT": "aa6d1ae3ebfa9bd10e9bbb91c3fa3a72dd8b4d55883eb93fb57a1c9c7909b643", "SRC-LINKEDIN-NOTIFICATION-DT": "fc6bb3e6f9d1c6e37e985c4e476ba04d4ebe7cd98b06cc2c86306487d440bb37", "SRC-LINKEDIN-NOTIFICATION-RL": "ef357491d3cab9d1ef0b5c7ae57c02e90fde83a37d16638834449bd9faafba25", "SRC-LINKEDIN-NOTIFICATION-MORL": "9e68931195cc0bfabac0c1f987ac7d43fbf7a58e0a65d9f097b120d0546140f7", "SRC-TWITTER-NOTIFICATION-RL": "27524dfa0cb734e161ae9ce60d0726bdc11adc2483feb827e63eac349dac5bed", "SRC-PUSHGEN": "da350c1c4d588497fc7de289b6cce848cc4e1c07e62d188ca9b5e47e34939dde", "SRC-LINKEDIN-NOTIFICATION-GNN": "ea9fda755ec78e5cd7cd1243d0c3859cad700e0901f759b2b3e4f100558bae44", "SRC-STEPS": "5f1c750c574a8f91ccf7c0b97915fe08186334c1150ad3850bba3bea3c184d95", "SRC-FAIR-NOTIFICATION": "6af872de1b2ea319ea8b0d97d922004b70a1d3b44774eddb44952777023ae122", "SRC-HGENPUSH": "88b0601665bc07fe5d2584541b62dd20c6dc1643c87b49f232f596216eded5b6", "SRC-ALERT-NOW-OR-NEVER": "57e095823e9ffce7048f304c7abe43f3ebf49f66e3be4c88f599cf90d4a73e45"}
related: ["paper-candidates", "exploration-longterm", "evaluation-bias", "multitask-objectives", "user-sequence", "serving-efficiency", "push-offer-contact", "notification-quota-timing"]
---
# Push触达与时机：2022—2026年工业论文路线

Push的关键约束是用户没有主动打开推荐流：系统要决定是否打扰、何时打扰，以及发送多少。内容点击率高不代表此刻发送有增量收益，用户本来就可能回访；连续通知还会影响后续响应、权限关闭和计算成本。因此，时机论文应先按决策对象区分，再比较模型与实验。

截至2026-11-09，本轮筛出13篇互联网公司参与的相关论文，正式题名、公司、年份、出版入口和阅读范围集中在[候选表P75—P87](候选论文.md#push触达与时机)。最贴近发送时机的是快手TIM和字节STEPS；LinkedIn的CIKM2022、KDD2022与2025年Decision Transformer工作则提供“发送或等待”的长期决策路线。推荐顺序按问题贴合度与证据可读性选择，不表示跨平台效果排名。

若关注的是月初一次性为用户选本月优惠发送日，先进入[优惠信息Push触达场景页](../总览/优惠信息Push触达场景.md)：其中区分用款需求峰值、发送响应和相对不触达的增量收益，并给出按该决策粒度调整后的阅读顺序。

## 日内时槽、发送或等待、自触发调度

| 实际要决定什么 | 优先阅读 | 决策接口与约束 |
|---|---|---|
| 今天已有配额，分配到哪些时段？ | [P76 · TIM](候选论文.md#p76)，快手，ICMR2024 | 预测全天分槽CTR，再按预测值分配给定日配额；时机与配额是分开的 |
| 队列里的通知现在发还是再等等？ | [P77 · Offline RL](候选论文.md#p77)，LinkedIn，CIKM2022 | 非强时效通知，每隔几小时检查候选，学习SEND/NOT-SEND及通知间隔 |
| 事件到达时，怎样兼顾回访、点击和发送量？ | [P78 · 多目标Offline RL](候选论文.md#p78)，LinkedIn，KDD2022 | 近实时通知，用保守Q学习优化多目标长期奖励；决策时点由外部事件提供 |
| 怎样用序列监督学习替代Q学习式策略？ | [P79 · 多目标DT](../../来源/SRC-LINKEDIN-NOTIFICATION-DT/阅读笔记.md)，LinkedIn，2025预印本 | 历史轨迹与目标回报条件化的发送/跳过；仍不直接生成最佳连续时间 |
| 下一次何时再调用系统，届时是否发送？ | [STEPS 精读](../../来源/SRC-STEPS/阅读笔记.md)，字节/抖音，RecSys2026 | 规划代理预测下次调用时间，执行代理决定是否发送；另有轻过滤与业务事件触发 |

### TIM：先学一天中哪些时段更适合触达

TIM把长期通知接收、点击、观看等交互组织成“天×时槽”，用Temporal Attention Unit先跨天聚合相同时槽，再用旋转位置编码融合时槽；日期类型嵌入区分工作日与休息日。输出是全天各槽响应概率，而不是只预测当前时刻。给定日配额后，再把额度分配到各槽并控制累计发送节奏。这适合“配额规则相对稳定，但统一时刻发送太粗”的业务起点。依据为[固定v1全文](https://arxiv.org/html/2406.07067v1)§2—3；它主要预测响应，不直接估计发送相对不发送的因果增量。

作者在§3.4 Table 3报告：相同配额分配算法下，以均匀发送为对照，CTR相对提升1.217%、DAU提升0.100%。观看时长提升0.066%的p值为0.11；权限关闭变化也未显著，不能据此证明打扰下降或两策略等效。正式出版是[ICMR2024](https://doi.org/10.1145/3652583.3657614)，不能误记为KDD/SIGIR。

已完成[TIM全文精读](../../来源/SRC-TIM/阅读笔记.md)，机制、KKT条件和累计pacing边界统一见[问题页](../问题/给定配额怎样安排通知发送时机.md)。它的比例分配依赖特定正则系数，配额由外部给定，原概率式还需补足负值边界；不能等同于月初整数选日或因果增量模型。

### LinkedIn：把等待当作可以学习的动作

[LinkedIn CIKM 2022 精读](../../来源/SRC-LINKEDIN-NOTIFICATION-RL/阅读笔记.md)针对非强时效的批量通知：在预定检查点读取用户近期访问、历史通知数、badge等状态，从队列候选中选择发送或让候选回队；到期另行发送或丢弃。Double DQN 学习跨轮访问价值，再用状态边缘化权重校正目标策略与日志策略的状态、动作分布，筛选进线上 A/B 的候选。与TIM的全天配额分配相比，它让当前少发与后续状态联系起来；仍依赖检查时刻与日志动作覆盖。[固定v1全文](https://arxiv.org/html/2202.03867v1)§V-B Table I的一周线上A/B，相对生存分析监督基线，报告Sessions +0.30%、通知卡片量−3.49%、CTR +4.53%、取消关注通知动作−4.37%，作者报告均p<0.05。这是短周期策略实验，不等同长期留存已经充分验证。

[LinkedIn KDD 2022 多目标精读](../../来源/SRC-LINKEDIN-NOTIFICATION-MORL/阅读笔记.md)把决策扩展到近实时事件和批量队列。不发近实时候选会丢弃，不发批量候选可以回队。会话、点击和发送量合成标量奖励，下一状态的价值按真实事件间隔折扣。CQL 在训练时压低日志支持薄弱动作的高估；一步重要性采样保留日志状态分布，用来筛选候选。固定 v1 表 1 的线上 A/B 中，DDQN + CQL 相对同目标监督 MOO 基线报告会话 +0.24%、WAU +0.18%、发送量 −1.73%、CTR +2.26%。相同论文表 2 另比较预测与观测会话奖励，使用另一对照。

2025年[多目标 Decision Transformer 精读](../../来源/SRC-LINKEDIN-NOTIFICATION-DT/阅读笔记.md)把轨迹中的状态、动作和目标回报作为序列训练，用状态相关的回报提示驱动动作选择。“Generative”生成的是决策动作，不是通知文案。§6.3 Table 1在2%用户、每次一周的A/B中，报告所选最佳DT策略相对CQL的Sessions +0.72%、发送量−1.68%，CTR无统计显著变化；特征与工程链路也有变化，不能将全部收益归于DT结构。固定v1写明Under review，本轮未核实其正式会议身份。

### Twitter：由连续响应状态求发送门槛

[Twitter 基于模型的通知过滤](../../来源/SRC-TWITTER-NOTIFICATION-RL/阅读笔记.md)在定期挑出候选后比较发与不发的折扣打开数。历史通知连续打开或忽略形成状态，打开率经验倍数朝 1 收缩后进入打开概率；离线解出各状态的门槛，线上用校准分查表。确定性日志缺未发记录，不能识别状态变化的因果效应。33 天 A/B 中，收缩参数 0.2、上限加 2 的组合相对分位数启发式基线发送量 −5.79%、打开率 +7.96%、DAU +0.20%，可触达用户数变化未达显著。实验没有穷举上限与收缩参数的组合，不能拆分发送上限和收缩参数的影响。

[通知候选到达后怎样决定发送或等待](../问题/通知候选到达后怎样决定发送或等待.md)把生存曲线、离线价值、显式用户模型与待获回报提示放在同一决策点比较。

### STEPS：连下次何时决策也一起学习

STEPS把固定轮询改为自触发闭环：基于Decision Transformer的规划代理通过门控序数回归预测下一次调用时间，执行代理按轨迹奖励判断是否发送。轻量过滤器在昂贵召回/排序前筛掉低价值请求，并限制不合理规划；直播等业务事件仍可触发系统，因此并非完全取消外部事件。完整时间解码、执行价值和成本分母见[STEPS 精读](../../来源/SRC-STEPS/阅读笔记.md)。出版身份见[RecSys 2026 DOI](https://doi.org/10.1145/3773078.3831932)。

作者在§4.1 Table 1的抖音14天、设备随机A/B中，相对预先规划频次的生产基线，报告User Active Days +0.2843%、关闭Push权限的用户数−1.9089%、资源消耗−79.42%。资源下降主要来自轻量过滤器，不能解释成单纯“更准地预测时机就省了79%”。这一方向最直接覆盖“何时再决策+届时是否发”，但需要轨迹数据、执行与规划协调、过滤和事件兜底，工程投入高于单独替换时槽预测器。

## 补足生存模型、分配与打扰视角

[DeepPvisit](../../来源/SRC-DEEPPVISIT/阅读笔记.md)以同一个未来访问窗比较两条路径：继续等待沿用原状态已过时长，立即发送重新起算。下一条通知先于访问到来时，似然用到已知的未访问时长。作者在一周实验中仅替换旧 AFT 效用模型，报告卡片数下降和通知 CTR 上升，Macrosessions 与 WAU 变化未显著。

[Fair Notification Optimization 精读](../../来源/SRC-FAIR-NOTIFICATION/阅读笔记.md)把通知类型当作虚拟买家，用预算、节奏乘数和逐用户价格分配容量。生成时刻来自上游，候选到达后过价即发。两次线上 A/B 分别检验集中拍卖和计价规则，具体基线见[通知配额问题](../问题/给定配额怎样安排通知发送时机.md#多个通知类型怎样共享同一用户的容量)。

[Alert Now or Never](../../来源/SRC-ALERT-NOW-OR-NEVER/阅读笔记.md)通过一周 Android 体验采样收集通知栏送达和声音提醒的偏好。525 条训练标签里，静默送达占 26%，立即送达后延迟提醒占 6.3%。行为模型聚合同一用户历史相似通知的动作和响应时间，在 79 条共同覆盖测试样本上的 ROC AUC 为 0.749。它比较的是主观偏好预测，和生产策略 A/B 的活跃、打扰指标口径不同。

[TSIL](../../来源/SRC-TSIL/阅读笔记.md)是 STEPS 预规划基线引用的活跃建模工作。它用端点分类和中间天数分布估计 14 日活跃期望，比较零推送与预设频次，并据效用重新分配容量。原文实验按频次干预，具体发送日的选择还需日期级别的动作和对照。

一个容易混淆的背景来源是[《A State Transition Model for Mobile Notifications via Survival Analysis》](https://doi.org/10.1145/3289600.3290981)：尽管[arXiv版本](https://arxiv.org/abs/2207.03099v1)在2022年上传，正式发表是WSDM2019，不计入2022—2026年的新论文。

## 内容推荐与发送时机分别看

[HGenPush 精读](../../来源/SRC-HGENPUSH/阅读笔记.md)，快手 KDD 2026，共享行为主干分别生成视频码与作者混合码，生成候选跳过粗排进入精排；[PushGen](../../来源/SRC-PUSHGEN/阅读笔记.md)，快手 WSDM 2026，用视频事实和风格条件生成文案，再以同视频 A/B 胜负训练判别器做替换筛选；[LinkedIn 跨域 GNN](../../来源/SRC-LINKEDIN-NOTIFICATION-GNN/阅读笔记.md)，CIKM 2025，把动态、邮件与通知的行为合入异构图，每日批产会员表示供第二阶段排序器判断发送资格和排序。时序聚合编码已有事件，触发时刻由下游链路决定。固定 v1 表 5 的 14 天 A/B 比较 SPR 接入向量前后的完整变化，站内 CTR +0.62%、Push CTR +0.30%、WAU +0.10%。三个方法在内容链路里分别改变候选、文案和排序输入。

如果要从业务问题选择第一篇：已有每日配额、先改善日内分发，读TIM；主要痛点是疲劳和频控，读LinkedIn的两篇2022论文；希望进一步统一长期轨迹、唤醒时间与调用成本，再读2025 DT和STEPS。多业务配额冲突补Fair Notification，用户打扰偏好补TOCHI。评估时同时报告活跃/回访、发送量、权限关闭或投诉与总成本，CTR仅是其中一项；不同平台、基线、随机化单位与实验周期的相对提升不能直接排序。相关基础见[长期策略模块](../模块/探索、长期收益与策略学习.md)、[多目标模块](../模块/多任务学习与多目标决策.md)、[序列建模](../模块/用户兴趣与序列建模.md)、[服务效率](../模块/在线服务、更新与计算效率.md)与[因果评估](../模块/评估、偏差与因果收益.md)。

## 已核实的GitHub实现

Meta官方[facebookresearch/FairNotification](https://github.com/facebookresearch/FairNotification/tree/5f37544360a20df9fc3a462a196bc71427d240d3)的README明确关联Fair Notification论文，包含模拟、指标分析、派生数据notebook及Julia的Eisenberg–Gale求解文件；README提供[Instagram通知数据入口](https://socialmediaarchive.org/record/55?&ln=en)。代码许可为CC-BY-NC-4.0，复用时需核对非商业限制。本轮只静态核对固定commit的README与目录，未下载数据、运行notebook或验证可复现性。TIM、STEPS及LinkedIn核心策略论文，本轮未找到能够确认对应的官方实现；这不表示它们一定没有开源。

检索截至 2026-11-25。采用版本、阅读范围及正文中文 PDF 见各篇精读。未运行模型实验。

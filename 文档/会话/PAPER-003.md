# PAPER-003：生成式推荐论文与跨模块梳理

用户要求按论文工作流依次读相关论文，下载可并行并支持断点；全部解读完成后，从全局重新整理相关知识页。此前综述与微信正文已读，DMT综述中文PDF及私有备份已完成；不能据此认定后续逐篇流程完成。

## 范围与完成证据

主队列沿用候选P60–P71：ColdLLM、Agent4Rec、LETTER、LLaRA、TokenRec、LatentR³、OneMall、MDGR、FedCGR、UniGCRec、DreamRec、PENS。补充此前已列出的OneSug（P42）、OneRec V2（P44）、OneReason（P45）、PreferDiff及OneRec-Think；OneRec-Think已核对综述题名与标识，和OneReason为不同论文，固定版本原文仍待取得。

每篇完成条件均为：固定版本原件/阅读范围、正文中文PDF与逐页验收、原文及译文私有备份和首次认证下载哈希核验、独立精读、问题合并与整合收据、检索检查。公开译文另核实逐篇许可，不以私有保存代替公开授权。未运行算法实验，作者报告与分析推断分别表述。

最终复核生成式专题、数据/样本、表征编码、训练对齐、生成解码、多场景/冷启动、级联、服务成本与评估等页面的接口、公式、协议与引用范围，修正旧候选状态和重复/过强结论。保留本任务前已有的LightGCN、POUL、TaQFormer待整合问题；不借批量替换指纹掩盖未复核项。

## 2026-10-29已核实进度

- 分支`codex/generative-recommendation-survey`，main/origin/main的4a9f1e6是祖先；已有综述提交79c5fa7，无upstream。普通正文只本地提交，私有附件目录按持续授权推送。
- ColdLLM：10页v2原文、源码正文精读与7页正文中文PDF已完成；中文7页全部逐页渲染目视，清理前后逐页文字/像素一致。原文/中文PDF均已私有上传、核对远端digest并真实登录下载验证大小及完整SHA256。已修正冷物品随机抽取、细化停止策略和21.69%出处的过度表述，补齐LoRA、采样标签、BPR与耦合损失边界；数据模块/合成反馈问题页及整合收据已更新。
- Agent4Rec：11页v3采用PDF、源码正文精读和8页中文PDF已完成；8页逐页目视、清理前后文字/像素一致，原文/译文私有上传与真实登录下载核验完成。已纠正画像≥3与策略>3的阈值差异、从众平方差方向、未交互负类、表3真实离线/模拟评价、DAG因果边界；相关五页整合收据已刷新。源码gzip CRC/tar完整，但实际SHA与服务器ETag不同；包内PDF与采用PDF仅页边标记不同，未另登记。
- TokenRec：已有正文笔记、来源卡与模块整合收据；15页原文已私有备份并真实登录下载核验。中文PDF仍未完成。
- DreamRec：15页正文中文PDF已完成并逐页目视；字体/环绕图公式重叠/算法锚点问题已修复，14块显示公式与原表1单元格和原源码一致。附录A–C、参考文献、图内英文与出版说明保留；清理前后15页文字和1.5倍像素一致。独立精读已补全文公式/伪代码差异、表1对照和协议边界，扩散问题页与生成模块已自查整合。原文与译文均已私有上传，核对远端digest并首次实际认证下载验证大小与完整SHA256。
- LETTER、LLaRA、LatentR³、OneMall、MDGR、FedCGR已有本地PDF和解压源码，仍须逐篇核验和精读。PENS已有PDF，无源码；UniGCRec仅DOI/题名核对，正式全文待取得。
- 断点下载进程已终止成功，PreferDiff、OneSug、OneRec V2、OneReason的PDF和源码均完整；状态在本地`.local/papers/PAPER-003/download-status.json`。Agent源码状态残留validation-failed仅为ETag断言差异，已按上述独立完整性证据处理，不重启下载。
- OneRec-Think的综述bib标识为2510.11639，题名为OneRec-Think: In-Text Reasoning for Generative Recommendation；与OneReason 2606.06260不同，尚待固定版本全文获取与精读。
- 私有库目录现为50份原文、49篇中文PDF，共99份、1382页。ColdLLM与Agent4Rec译文、四篇新增原文的成功收据和认证副本均保留本地；私有目录/README/阅读目录已中文提交c8a081f并推送main。此前98份目录检查、7项下载器测试通过；本轮6份新增附件本地verify-only通过，匿名仓库及ColdLLM译文返回404，private/仅所有者/无邀请已核实。
- 公开PDF许可/范围盘点、正式Markdown未发布原因及工具说明已同步49译文/50原文；普通正文尚未推送。全队列完成后的跨模块全局复核尚未执行。
- 保留用户未提交的治理目录改动及两个未命名画布，不纳入本任务暂存。LightGCN指纹旧漏字符已按来源卡核实修正，不是来源升级；POUL/TaQFormer既有待整合项保留。

## 下一步与恢复位置

DreamRec译文已完成私有上传/登录下载与目录同步，私有目录中文提交df0cd88已推送main；99份、1382页，新增DreamRec原文/译文verify-only通过，译文匿名访问404。本轮check_context通过193篇/2724链接，wiki lint为0错误、3个既有警告（POUL争议与POUL/TaQFormer未整合）；DreamRec已不再待整合，译文/PDF目录检查通过。继续TokenRec及其他主队列。DreamRec译文已逐页验收，最终PDF位于本地`translation/Generate_What_You_Prefer_Reshaping_Sequential_Recommendation_via_Guided_Diffusion_中文.pdf`，验收记录在`qa/final-qa.json`；最终SHA256为9f2c2647aa2983335c87a815e1f3f048ece4ab3d4adf2ae46d0252f85f5f438e。当前来源指纹103201cb187a23b2ae5a56f64c7f926a64ac332ee84a499e288c05300e9d46d2，已明确附录C可视化范围；旧原文备份指纹合法保留，不重复上传相同原文。DreamRec采用源码主文件为本地`original/source-work/main.tex`，参与正文为0_abs_new、1_intro_new、2_related、2A_preliminary、3_method2、4_exp、5_conclusion，另嵌入9_alg/9_tab_main；6_appendix按默认保留英文，7_rebuttal未参与。

DreamRec预备知识后验均值式(7)的第二项分子写1−ᾱ_t、分母亦为1−ᾱ_t，与后文采样式(16)的1−ᾱ_(t−1)不同；方法KL条件下标、噪声符号、重参数化及损失权重也须保留原式并加译注，不能以标准DDPM公式静默替换。表1的SASRec标准差原写002，YooChoose NDCG的第二名下划线与数值不一致，翻译保留数值、另解释，精读比较须以实际数字判断。

本文件记录执行状态；领域解释继续写入各来源笔记与对应问题页。

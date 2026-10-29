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
- TokenRec：15页v3原文与11页正文中文PDF已完成私有备份和真实登录下载核验；最终11页全部渲染目视，18块align公式、6表67个数字行核对一致，清理前后逐页文字/像素一致。修正无附录、P5耗时范围、式20分段损失、User ID Only含历史协同信号与unseen-user更新GNN的信息边界；正式出版版与代码未独立核对，未运行模型。
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

## TokenRec收尾与LETTER续读

TokenRec最终中文PDF为本地`translation/TokenRec_Learning_to_Tokenize_ID_for_LLM_based_Generative_Recommendations_中文.pdf`，SHA256为a9be8d4b0ad9f4e71948ac2b01a5f52eae5c6f3652e113243ca755db4efcfc46，11页、6,371,003字节。新来源指纹e89ee023097e56881954f27f3cabaca20ce1610a7b411734593f46d153cba878；旧原件备份指纹保留，原文原哈希未变。私有目录当前50原文/50译文、100份、1393页，TokenRec新增译文已核对远端digest及首次真实认证下载。

LETTER已核对10页arXiv:2405.07314v3固定PDF与CIKM2024/DOI，读取引言、任务和方法；引言与物品Token化章节初译保存在本地`translation/translated-sources/`，其余仍为英文，不称已完成翻译或精读。上游原始源码包未保留，本轮将既有未改源码重新打包为`original/LETTER.2405.07314v3.source-local-repacked.tar.gz`（SHA256 a286ec5ee0c0ac33908c6180c601a41bae3563c70a7eddc97b3b4fb991ad2289），明确不是上游压缩包原字节。方法中CF/Div目标未写log，后续保留公式并回查附录/官方实现，不能静默改成InfoNCE；排序温度在Token级定义，其到物品级排名的理论条件亦待核对。

OneRec-Think元数据已核实当前v2（2025-11-11），固定采用2510.11639v2；原文与源码并行断点下载现均完成、进程已终止成功。PDF为6,072,213字节、SHA256 8fbd181d6084d247637aa2d626b52fecb079fb794308ac37f6a67b6202aa6540；源码gzip/CRC及tar内容检查通过，为5,451,621字节、SHA256 3a82674615a0585ab0e3b5eb114b57f8b85e75fd641eba30a93004acec50ae7e。状态在本地`onerec-think-download-status.json`，尚未精读，不重启下载。全队列完成后的跨模块全局复核仍未执行。

TokenRec私有目录中文提交4c1df86；本轮公开库check_context通过193篇/2730链接，wiki lint为0错误、3个既有警告，plan只余POUL/TaQFormer，索引/译文/PDF盘点及本任务diff检查通过。匿名仓库与TokenRec译文均404，原/译verify-only通过；完整历史公开扫描通过16提交598对象。普通知识正文只本地提交，用户治理目录和两个画布未触碰。

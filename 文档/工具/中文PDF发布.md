# 原文与中文 PDF 私有维护

原文与中文PDF统一存入独立私有附件库 `Lsiming/recsys-knowledge-attachments` 的Releases；公开知识库不再托管PDF。该决定替代此前按逐篇许可公开中文PDF的流程，原9篇已迁入私有库并撤下公开附件。路径保留用于兼容旧入口。

公开Git保存知识正文、来源记录、许可核实的正式Markdown译文、[PDF许可/范围盘点](../../译文/PDF目录.md)、规则和工具；私有Git保存完整附件目录、类型、版本、哈希与登录下载工具。两库Git均不存PDF字节。LaTeX、图表源文件、渲染、日志、其他来源快照和环境不因本规则自动上传。

## 登录下载

需Python 3.9+、GitHub CLI与有权访问私有库的GitHub账号。当前仅所有者Lsiming有访问权限，没有邀请其他账号。登录后可从[私有仓库](https://github.com/Lsiming/recsys-knowledge-attachments)浏览；无权限访问返回404。

```bash
gh auth login
gh repo clone Lsiming/recsys-knowledge-attachments
cd recsys-knowledge-attachments
python3 download.py
```

独立阅读时，默认获取全部原文与中文 PDF，分别保存到私有克隆的 `.local/pdfs/<来源ID>/original.pdf` 和 `.local/pdfs/<来源ID>/中文.pdf`。知识库维护使用已有正式文件位置，核验时运行下方的验证命令。96篇中文PDF与96份已登记原文分别保存；2026-10-29追加DMT综述、Agent4Rec、ColdLLM、DreamRec、TokenRec、LETTER与LLaRA中文PDF及对应原文。2026-10-30再追加LatentR³的19页采用原文和17页正文中文PDF，以及OneMall的11页采用原文和9页正文中文PDF，随后追加MDGR的11页采用原文与9页正文中文PDF，以及FedCGR的13页采用原文与10页正文中文PDF。随后追加PENS正式11页原文与14页正文中文重排本，论文CC BY 4.0与数据MSR许可分开记录；再追加OneSug v1的11页原文与8页正文中文PDF，固定arXiv页CC BY 4.0与原PDF的ACM模板权利栏并存保留，不以模板确认正式发表。再追加OneRec-V2 v4的28页原文/24页正文中文PDF、PreferDiff v2的38页原文/37页正文中文PDF；两篇附录、参考文献及图内英文保留，公开全文翻译许可未确认。随后追加OneRec-Think固定v2的17页采用原文与16页正文中文PDF，26位作者署名及非独占分发许可保留，附录/参考文献/图内原文字保留。随后追加OneReason固定v1的108页采用原文与96页正文中文PDF；正文§1–11及图表说明翻译，作者表姓名、参考文献、附录和图内原文字保留，96页全部逐页目视。随后追加UniGCRec正式10页原文与18页正文中文重排PDF，13编号公式、5表数值、6图及参考文献对照，原/译PDF均逐页目视；首页CC BY 4.0与八位作者署名保留。2026-11-09追加TIM固定v1的5页采用原文与4页正文中文PDF：原文5页、译文4页全部逐页目视，保留原式、图内英文与24条参考文献，全部表内小数对照；未确认公开全文译文许可。2026-11-16追加TG-DIPricingNets正式5页原文与7页正文中文重排PDF：原文和译文全部逐页目视；前5页中文，末2页保留参考文献/附录/表3及结论英文末段，未取得作者LaTeX、未确认公开译文许可。2026-11-18追加RankMixer固定v3原文9页与正文中文译本7页，全部逐页目视；公式/表数保留，译后清理副本与编译版逐页像素一致，两份均完成首次认证下载和完整SHA256核验。同日追加AMEN固定v2原文6页/正文中文5页、User Personas固定v2原文9页/正文中文7页、RecGPT-V3固定v2原文32页/正文中文27页；相应范围正文翻译及全部新PDF逐页目视、公式/表数/字体与清理像素检查完成，原/译均首次真实认证下载。2026-11-21 追加第 02 批 Transformer 基础的 8 份采用原文与 8 份正文中文 PDF，译文逐页目视，16 份均实际认证下载并核对完整 SHA-256。2026-11-21 追加第 03–04 批的 9 份采用原文与 9 份正文中文 PDF。译文共 96 页，已逐页目视。18 份均核对远端 digest 并登录下载校验页数、大小与完整 SHA-256。另重新认证下载 BPR、YouTube DNN 与 MIND 的 6 份既有附件。2026-11-22 追加第 05–06 批的 7 份采用原文与 7 份正文中文 PDF。译文共 83 页，均已逐页渲染目视。14 份均核对 Release 摘要，并真实认证下载校验页数、大小和完整 SHA-256。另重新核对 LightGCN、Wide & Deep 和 DeepFM 的 6 份认证下载附件。2026-11-22 首先追加第 07–10 批的 DCN v1。DCN v1 的 7 页采用版原文和 6 页中文正文译本均完成私有备份及首次认证下载核验。译文逐页目视，核对公式、四表、三图和引文，支持中文提取。随后追加 AutoInt v2。AutoInt v2 的 10 页采用版原文和 8 页中文正文与致谢译本均完成私有备份和首次认证下载核验。译文逐页目视，核对 10 个编号公式、五张表、七张图和引文。随后追加 CAN v3。CAN v3 的 9 页采用版原文和 7 页中文正文译本均完成私有备份和首次认证下载核验。译文逐页目视，核对 13 个编号公式、六张表、五张图和引文。新增附件均核对远端digest并实际登录下载校验PDF类型、大小与完整SHA256。STAR未核实镜像及BERT额外出版版已按用户要求删除，当前仅保留实际采用的登记原件。

```bash
python3 download.py --kind translation
python3 download.py --kind original
python3 download.py --source SRC-BERT
python3 download.py --list
python3 download.py --verify-only
python3 download.py --kind original --dest ~/Downloads/recsys-originals
```

`git pull --ff-only`只更新私有目录与工具，之后运行下载器取得新增版本；`git clone`/`git pull`不自动下载PDF。下载器使用已有 gh 认证，联网前确认仓库仍为私有。保存时核对 PDF 类型、大小和完整 SHA-256 后原子替换稳定文件名，之后清理该类型旧版下载文件。正确已有文件直接复用，失败时保留原文件。`--list` 和 `--verify-only` 离线运行。

维护者验证远端时在私有克隆运行以下命令。已登记附件使用 `--verify-remote`，刚上传的候选用 `--verify-candidate` 对照本地正式文件。两种模式都执行实际认证下载，成功、失败或超时时自动清理该次临时目录和下载文件。核对新增 PDF 类型、大小、完整 SHA-256 与远端 digest，页数以该哈希对应的已验收本地 PDF 为准。只保留文字或 JSON 收据，凭证与临时签名链接由 gh 管理。

```bash
python3 download.py --source SRC-ESMM --verify-remote
python3 download.py --verify-candidate TAG ASSET_NAME LOCAL_PDF
python3 download.py --check-releases
```

公开旧入口`python3 scripts/download_translations.py --list`只列公开盘点；实际下载需先克隆私有库，并传`--attachments-root <私有克隆路径>`转交私有下载器。新使用优先直接运行私有库的`download.py`。原准备脚本`prepare_pdf_release.py`已停用，不再生成公开资产元数据。

## 新论文与修订

1. 按[论文标准流程](../../维护/工作流.md#论文知识沉淀标准流程)固定原文身份/版本，冻结采用版原文并核验 SHA-256。私有库只备份每篇当前实际采用的登记原文。原文按原字节备份，不清理元数据、重排、加封面或改写页面；即使上游原文件包含作者构建路径，也须区分上游公开信息与维护者隐私。发现凭证、个人路径或非公开数据先排查，不能静默清洗后仍称原件。需清理的派生副本另列，不能覆盖证据原件。
2. 完成中文PDF及原文对照，保留作者署名、既有权利声明、译文范围和修改说明。核查固定版本的许可页面与原PDF声明；私有存储状态与公开再分发权利分别记录，不把arXiv可下载或私有备份记为公开译文授权。新译文副本可清理维护者路径、嵌入附件和本地/执行动作，但不得改写原件；处理后核查正文、页数和渲染，将通过验收的发布用 PDF 定为正式版。
3. 盘点按来源ID、类型（`original`/`translation`）、完整SHA256区分，不凭文件名/论文名去重。原文资产命名`<ID>.original.<SHA256前16位>.pdf`；译文用`<ID>.zh-CN.private.<版本>.pdf`。原文记录采用版本、原文件名、来源指纹/原哈希、是否已登记；镜像或待核实版本单独标注，不冒充当前来源。译文记录翻译范围、输入/备份哈希、许可依据、页数及实际QA。
4. 上传前执行`gh api repos/Lsiming/recsys-knowledge-attachments --jq .private`确认true，核对协作者及待处理邀请。保持仅本人访问，不自动邀请账号、启用Pages、修改可见性或公开分享。用草稿Release承接新批次；译文标签`private-zh-pdfs-YYYYMMDD`，原文标签`private-original-pdfs-YYYYMMDD`。同日已存在其他批次的正式 Release 时，可加两位批号后缀 `-batch-03-04`。上传仅限核实的PDF及必要许可文本，不将目录中其他文件一并上传，不用`--clobber`覆盖旧字节。
5. 在私有仓库内启用 Release。用 `--verify-candidate` 核对远端摘要和字节数，认证下载核验 PDF 类型、大小与完整 SHA-256，工具随即清理核验副本。只有真实成功才在私有`附件目录.json`记录`verified_download_sha256`及日期；失败如实保留，不伪造验证字段。已有正确副本可离线复核，不能替代首次远端下载验证。匿名访问仓库和抽样附件应返回404；检查不是新的授权。
6. 私有目录采用schema_version=2、visibility=private、policy=private-only；附件身份为 `<ID>:<kind>:<sha256>`，当前目录的 `(来源 ID, kind)` 唯一。私有`附件目录.json`是完整账本，`附件目录.md`为阅读入口。公开`译文/PDF目录.json`只维护逐篇中文PDF盘点、许可/范围及备份摘要（status=private/local-only/failed）；不放需登录的逐篇下载链接，也不保留published/release字段。正式Markdown译文按独立目录与许可规则管理。
7. 更新相关笔记文末的访问说明，保留固定版本公开原文入口，运行plan并复核导航变化涉及的来源收据；不借附件迁移改写科研结论。仅改附件与配套目录时不触发处理语义升版。检查实际差异与完整待推历史后按明确文件中文提交，两库分别推送本任务增量；不得夹带其他会话未完成知识、旧私人历史或凭证。

## 单正式版与替换顺序

每篇论文在知识库本地及私有 Releases 各保留一份采用版原文与一份正式中文 PDF。原文唯一实体是来源卡登记的 `.local/sources/<ID>/<sha256>/<原文件名>`。原先在 `.local/papers/<ID>/original/` 的查阅入口可改为指向它的相对符号链接。中文正式文件留在 `.local/papers/<ID>/translation/` 的交付位置，既有链接可引用同一实体。此前已验收并登记的隐私清理或加封面前后的 PDF，可分别担当本地与私有正式件。新译文验收后，本地采用与私有备份相同的发布字节。

重新翻译或更新采用原文时，先校验新本地成品，再以新资产名上传并用 `--verify-candidate` 登录核验。成功后替换正式文件、同步私有目录与公开盘点，再撤下同来源同类型的旧 Release 资产。核对新资产、引用和恢复入口可用后清理已被替代的本地成品、缓存和上传暂存。运行 `--check-releases` 对照实际资产和账本，确认没有额外 PDF。替换失败时保留当前正式版，回查目录与实际资产后继续可恢复的环节。历史身份、版本、范围及哈希保留在来源卡和 Git，仍支撑独有历史引用的证据先按原文查证并明确恢复入口。

恢复原文时核对来源卡的原始 SHA-256，把认证下载且校验通过的文件原子落到登记位置。恢复中文译文时核对私有目录的记录，再落到现行中文 PDF 位置。恢复下载直接形成正式文件，同机其他旧路径只链接该文件。仅核验时用临时模式。

本任务及后续同类PDF的私有备份、登录下载验证和必要目录更新已获用户授权；此前公开PDF持续发布授权已被替代。其他远端写入、邀请、公开分发或设置变化按[AGENTS](../../AGENTS.md)的具体授权处理。

## 撤回与访问边界

需要撤回时先核实原件、本地备份与受影响来源，再撤下指定资产并同步目录和失败原因，不删除无关版本。已下载的副本无法保证收回；删除公开附件不会改写第三方已有许可，也不能收回外部缓存或副本。本次原9篇公开资产删除后，旧Git中的URL仅为历史记录，不是当前下载入口。

私有备份不授予公开分发、翻译再许可或转发权，既有CC署名/非商业/相同方式共享等条件保留，详见[LICENSE](../../LICENSE)。普通贡献者不需要私有库访问权或原件；仍可通过原文公开入口参与知识共建。

## 验证

公开PR/CI不联网取附件，也不需要gh或私有凭证：

```bash
python3 scripts/wiki.py plan
python3 scripts/wiki.py index --check
python3 scripts/wiki.py lint
python3 scripts/translations.py check
python3 scripts/pdf_releases.py check
python3 scripts/download_translations.py --list
python3 scripts/check_context.py
python3 scripts/check_public.py
python3 -m unittest discover -s tests -p 'test_*.py'
git diff --check
```

私有库运行其下载器测试、`download.py --list`与本地`--verify-only`，发布时另执行真实登录下载、临时目录清理、`--check-releases` 和匿名拒绝访问检查。工具只验证结构/哈希/访问，不证明翻译质量、全部原文范围、科研结论或永久授权。原字节迁移无需重新翻译/排版，但必须说明采用的既有QA及本次检查范围。

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

默认获取全部原文与中文PDF，保存到私有克隆的`.local/pdfs/<来源ID>/`。45篇中文PDF与45份已登记原文分别保存；2026-10-28追加TaQFormer七页译文与九页正式原文，两份均已实际登录下载核验。STAR未核实镜像及BERT额外出版版已按用户要求删除，当前仅保留实际采用的登记原件。

```bash
python3 download.py --kind translation
python3 download.py --kind original
python3 download.py --source SRC-BERT
python3 download.py --list
python3 download.py --verify-only
python3 download.py --kind original --dest ~/Downloads/recsys-originals
```

`git pull --ff-only`只更新私有目录与工具，之后运行下载器取得新增版本；`git clone`/`git pull`不自动下载PDF。下载器使用gh现有认证，联网前确认仓库仍为私有；只在PDF类型、大小和SHA256一致后原子替换目标文件，正确已有文件跳过，失败保留旧文件，重跑即可重试。目录、Git、日志和命令参数不保存令牌或临时签名链接；`--list`和`--verify-only`离线运行。

公开旧入口`python3 scripts/download_translations.py --list`只列公开盘点；实际下载需先克隆私有库，并传`--attachments-root <私有克隆路径>`转交私有下载器。新使用优先直接运行私有库的`download.py`。原准备脚本`prepare_pdf_release.py`已停用，不再生成公开资产元数据。

## 新论文与修订

1. 按[论文标准流程](../../维护/工作流.md#论文知识沉淀标准流程)固定原文身份/版本，保存来源快照并核验SHA256。默认只备份来源登记中实际采用的原文，不自动加入未采用镜像或额外出版版本；用户另有要求时单独核实。原文按原字节备份，不清理元数据、重排、加封面或改写页面；即使上游原文件包含作者构建路径，也须区分上游公开信息与维护者隐私。发现凭证、个人路径或非公开数据先排查，不能静默清洗后仍称原件。需清理的派生副本另列，不能覆盖证据原件。
2. 完成中文PDF及原文对照，保留作者署名、既有权利声明、译文范围和修改说明。核查固定版本的许可页面与原PDF声明；私有存储状态与公开再分发权利分别记录，不把arXiv可下载或私有备份记为公开译文授权。新译文副本可清理维护者路径、嵌入附件和本地/执行动作，但不得改写原件；处理后核查正文、页数和渲染，原始成品另留。
3. 盘点按来源ID、类型（`original`/`translation`）、完整SHA256区分，不凭文件名/论文名去重。原文资产命名`<ID>.original.<SHA256前16位>.pdf`；译文用`<ID>.zh-CN.private.<版本>.pdf`。原文记录采用版本、原文件名、来源指纹/原哈希、是否已登记；镜像或待核实版本单独标注，不冒充当前来源。译文记录翻译范围、输入/备份哈希、许可依据、页数及实际QA。
4. 上传前执行`gh api repos/Lsiming/recsys-knowledge-attachments --jq .private`确认true，核对协作者及待处理邀请。保持仅本人访问，不自动邀请账号、启用Pages、修改可见性或公开分享。用草稿Release承接新批次；译文标签`private-zh-pdfs-YYYYMMDD`，原文标签`private-original-pdfs-YYYYMMDD`。上传仅限核实的PDF及必要许可文本，不将目录中其他文件一并上传，不用`--clobber`覆盖旧字节。
5. 核对GitHub远端资产大小与SHA256，然后在私有仓库内启用Release，以有权账号实际下载每份新资产，再核对PDF类型、大小及完整哈希。只有真实成功才在私有`附件目录.json`记录`verified_download_sha256`及日期；失败如实保留，不伪造验证字段。已有正确副本可离线复核，不能替代首次远端下载验证。匿名访问仓库和抽样附件应返回404；检查不是新的授权。
6. 私有目录采用schema_version=2、visibility=private、policy=private-only；附件身份为`<ID>:<kind>:<sha256>`，同论文不同类型/版本可共存。私有`附件目录.json`是完整账本，`附件目录.md`为阅读入口。公开`译文/PDF目录.json`只维护逐篇中文PDF盘点、许可/范围及备份摘要（status=private/local-only/failed）；不放需登录的逐篇下载链接，也不保留published/release字段。正式Markdown译文按独立目录与许可规则管理。
7. 更新相关笔记文末的访问说明，保留固定版本公开原文入口，运行plan并复核导航变化涉及的来源收据；不借附件迁移改写科研结论。仅改附件与配套目录时不触发处理语义升版。检查实际差异与完整待推历史后按明确文件中文提交，两库分别推送本任务增量；不得夹带其他会话未完成知识、旧私人历史或凭证。

原文恢复时，在有权账号下载后逐个校验来源卡的原始SHA256，再复制到对应`.local/sources/<ID>/<sha256>/<原文件名>`；拒绝用私有目录的镜像或清理后的译文替换原件。Git和哈希不能代替附件，LaTeX等其他原件仍需单独备份。

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

私有库运行其下载器测试、`download.py --list`与本地`--verify-only`，发布时另执行真实登录下载和匿名拒绝访问检查。工具只验证结构/哈希/访问，不证明翻译质量、全部原文范围、科研结论或永久授权。原字节迁移无需重新翻译/排版，但必须说明采用的既有QA及本次检查范围。

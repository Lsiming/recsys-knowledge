# 中文 PDF 发布与下载

中文 PDF 按论文固定版本逐篇核实许可，允许分发的发布到 [GitHub Releases](https://github.com/Lsiming/recsys-knowledge/releases)。Git 保存 [PDF目录.json](../../译文/PDF目录.json)、[可读目录](../../译文/PDF目录.md)、版本、翻译范围、许可证据和下载工具。PDF、LaTeX、原件与渲染仍不进入 Git 历史。Markdown 译文独立登记在 [正式译文目录](../../译文/目录.md)，一种格式获准不代表另一种已经制作完成。

## 克隆后获取中文 PDF

需要 Python 3.9+ 与网络，无需 GitHub 登录、LaTeX 或论文原件：

```bash
git clone https://github.com/Lsiming/recsys-knowledge.git
cd recsys-knowledge
python3 scripts/download_translations.py
```

默认保存到 `.local/translations/<来源ID>/<资产名>.pdf`，不改写翻译工作工程。每个 PDF 首页有署名、许可与翻译范围；CC BY-NC-SA 项限制非商业使用并要求相同方式共享。

```bash
python3 scripts/download_translations.py --list
python3 scripts/download_translations.py --source SRC-HSTU-PAPER
python3 scripts/download_translations.py --source SRC-T5 --dest ~/Downloads/recsys-pdfs
python3 scripts/download_translations.py --verify-only
```

工具只下载登记为 published 且许可受支持的资产，检查 PDF 文件头、字节数与 SHA256，正确的已有文件会跳过。下载采用临时文件与原子替换，失败不覆盖原文件；逐篇报告，任一失败返回非零状态。网络错误可原命令重试。`git pull` 只更新目录与工具，之后再运行下载命令取得新版本；旧版本按版本化文件名保留。

## 每篇新论文的发布流程

1. 按 [论文标准流程](../../维护/工作流.md#论文知识沉淀标准流程) 确认原文版本、制作译文并核查最终 PDF。盘点 `translation/` 中的最终文件；同内容别名按 SHA256 去重，不把原文、图表、旧构建和诊断当成译文成品。
2. 同时查固定版本页面、原始 PDF 自带许可与必要的出版商登记。arXiv 非独占分发许可不授予公众译文分发权；ND 禁止分享改编作品；没有明确许可/授权就保留本地，并登记原因、日期和失败入口。作品内明确的 CC 许可也是依据，不能只读 arXiv 页面而漏掉它。另一出版版许可只有在确认所译内容属于该许可版本时才能使用；不能把新版许可直接套到不同旧稿。
3. 在 `译文/PDF目录.json` 追加/更新同一个 source_id。固定 original_url、revision、input_sha256、input_pages、scope，以及 rights 内的作者、许可、核实日期、证据 URL/字节哈希和判断依据。原件字节保持不变；有注册来源时必须与其当前版本一致。没有公开精读的附件可以只作盘点登记，不能据此声称全文精读已合入。新论文尚无 PDF 时在笔记说明，不虚构 PDF 登记。
4. 许可允许后在独立目录准备发布副本。维护者需要可用 Python 中的 `pypdf` 与 `reportlab`，并准备允许嵌入的中文 TrueType 字体（例如遵循 OFL 的 Noto Sans SC）；普通读者和 CI 不需要这两个包。原译文不被修改。准备工具增加一页中文署名/许可/范围说明，保留已有权利声明，重设元数据，移除文件附件与本地/可执行链接动作；发现本机路径、内网地址或凭证候选时拒绝；邮箱与哈希绑定的原文 PDF 对照，拒绝译文新增的非 noreply 邮箱。原论文公开作者的署名/机构邮箱属于原文内容，保留与原文一致的项目；人工仍需确认来源公开与内容适合分发。

```bash
python3 scripts/prepare_pdf_release.py --source SRC-PAPER --input .local/papers/SRC-PAPER/translation/中文译文.pdf --original .local/papers/SRC-PAPER/original/原文.pdf --tag zh-pdfs-YYYYMMDD --version YYYYMMDD.1 --output-dir .local/releases/zh-pdfs-YYYYMMDD --font .local/fonts/中文字体.ttf
```

5. 准备命令输出 release 字段候选，不修改登记或上传。逐页渲染最终发布副本，检查署名页、中文缺字、裁切、公式/图表与引用；保存 QA 在 `.local/`。确认翻译范围与文件相符，不能因有封面/哈希就声称完成翻译审核。许可声明、第三方材料、隐私和质量需维护者真实判断。
6. 使用 `gh release create ... --draft` 创建草稿，上传经检查的 PDF 与适用许可文本。资产名固定为 `<来源ID>.zh-CN.<译文版本>.pdf`。完成后公开 Release，在**无认证**环境用公开下载 URL 下载全部新资产并核验大小与 SHA256；只有成功才把状态记为 published，保存 tag、资产名、URL、译文版本、大小、页数、哈希、译者/修改、实际 QA 和 verified_download_sha256。失败则保持 local-only 或 failed 并记录具体原因。
7. 生成两个译文目录，更新该论文笔记的公开 PDF 下载入口（笔记有原先失败记录时注明是后续补齐），运行 plan 并更新仅导航变化的整合收据；知识内容、原件版本与科研结论不因附件发布而改写。按明确文件提交并推送本篇目录/入口增量，等待 GitHub CI 完成，最后报告实际发布及未许可/失败结果。

本轮用户已授权此批及后续新论文沿用此发布流程；持续授权限于该仓库逐篇合规的中文 PDF 和配套目录/下载入口。不要发布其他会话未完成内容、绕过逐篇许可和 QA，或顺带推送无关知识改动。其他远端操作遵循 [AGENTS](../../AGENTS.md) 的具体授权边界。

## 修订与撤回

译文修订后重新核对范围、许可和最终 PDF，使用新译文版本及新资产名，保留旧版本的可追踪性。不得以 `--clobber` 静默替换同一公开 URL。当前目录指向最新已验证版本，读者再次运行下载工具获取；原文升级必须重新核实权利与内容绑定，不能只改哈希。

许可或质量存在实质问题时，先从目录撤下下载入口并说明原因，再由有权限维护者按实际问题撤回相应 Release 资产。已下载副本无法保证收回。状态记录不是额外授权。

## 自动与人工检查的边界

```bash
python3 scripts/translations.py index
python3 scripts/pdf_releases.py index
python3 scripts/translations.py check
python3 scripts/pdf_releases.py check
python3 scripts/download_translations.py --list
python3 scripts/check_context.py
python3 scripts/check_public.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

PR/CI 离线核对目录、逐篇许可声明、当前来源版本、资产命名、固定下载 URL、哈希格式与下载校验记录，并验证下载器的完整性校验/失败保护行为；不下载整库 PDF，不要求本地原件。机器不能证明真实授权、译文正确、全部原文范围或外链永久可用。发布时的真实公开下载与渲染由维护者执行。

# 本地知识工具

只依赖 Python 3.9+ 标准库，无服务器、模型 API 或新增全局配置。默认根路径由脚本位置确定，可从任意目录运行。源码 [wiki.py](wiki.py)，上下文链接检查 [check_context.py](check_context.py)，行为验收见 [test_wiki.py](../tests/test_wiki.py)。环境约定见 [CONFIG](CONFIG.md)。

```bash
python3 scripts/wiki.py search "增量摄入"
python3 scripts/wiki.py plan
python3 scripts/wiki.py index
python3 scripts/wiki.py index --check
python3 scripts/wiki.py lint
python3 scripts/wiki.py lint --local
python3 scripts/check_context.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

`search` 检索标题、summary、aliases、正文以及问题页的模块/方案/论文题名与 ID；可由论文反查解决的问题。query 用空格分词；中文复合词请用具体词或分开查询，也可用 rg。回查原文用来源目录。没有向量语义搜索或经测定的召回率。

`index` 自动发现 type=map 且有 module 的模块导读；普通 map 列为总览、专题与阅读路线。同模块的 problem 另列“问题 / 解决方案 / 核心思路 / 对应论文”，来源目录反链相关知识页。只有候选与模块导读时也有可用导航，不会将候选误列为已支持方案。Agent 维护页面元数据和正文，无需手填第二份知识地图；字段见 SCHEMA。

`plan` 输出需重新整合的来源、原因、直接引用页和一跳关联候选。当前版本、阅读笔记、处理语义版本未变，且收据中的页面存在并绑定来源，才认为可跳过摄入。仅修改说明/索引/工具结构不触发全部旧来源重处理。它不检查每条陈述真假，也不因正文正常积累而要求重读所有旧来源。

## GitHub 与正式译文

PR 自动检查运行于全新克隆，不要求 `.local/`。正式译文在 `译文/目录.json` 登记；`python3 scripts/translations.py index` 生成目录，`python3 scripts/translations.py check` 离线核对论文身份/版本、逐篇许可声明、署名/范围、文件哈希、目录与未登记文件。该工具不自动判定真实授权或翻译质量；维护者须核实公开许可入口。支持 CC BY 4.0 与 CC BY-NC-SA 4.0，其他许可需先扩展规则。

共建步骤见 [CONTRIBUTING](../CONTRIBUTING.md)。公开附件链接不能指向 `.local/`；只有本机可用的路径写成行内代码。

## 登记来源

先把原件下载到临时位置或使用已有文件；固定来源与版本，再执行。下列命令是形式示例，不是已读论文：

```bash
python3 scripts/wiki.py register --id SRC-DEMO --title "资料题目" --kind paper \
  --locator "https://example.org/paper" --revision "v1" \
  --read-scope "已读的实际范围" --file /absolute/path/to/paper.pdf
```

`--file` 可多次提供；快照按哈希写入 `.local/sources/`，JSON 版本追加进 `来源/<ID>/来源.json`。重复登记相同身份/字节/阅读范围不增加版本；更新原件用相同 ID 和新 revision。read_scope 应在真实阅读后登记或以新阅读范围重新登记，不因下载成功写“全文已读”。CLI 不联网、不提取 PDF，不自动生成笔记。

写好 阅读笔记.md、合并所有直接引用页、核对证据后，用页面路径记录自查；参数随实际来源和页面替换：

```bash
python3 scripts/wiki.py integrate SRC-DEMO --pages 知识库/概念/示例.md \
  --review-note "说明核对的证据、合并结果和未覆盖范围"
python3 scripts/wiki.py index
```

工具拒绝 draft/contested 输出、错误版本绑定、引用该来源却未覆盖的页面，以及缺失/过短的阅读笔记；这只是结构保护，不能识别伪造阅读。收据标为 agent-self-review。不存在程序自动批准或必须让用户逐页批准的门禁。

## 原件与恢复

Git 中仅有来源账本/笔记和知识，不含 `.local/sources/`。本机已有知识系统参考与九份推荐资源的实际快照；其中 nashsu 只保存定向阅读的文件，推荐资源主要保存固定版本 README，不镜像上游。恢复公开资料时按 来源.json 的 locator + revision 获取每个 artifacts.name 对应文件，核对 SHA256 后放回 snapshot 指定位置。路径重名时须对照笔记中的原文件路径。不可公开恢复的本地 skill 需单独备份。

`lint` 默认允许原件不在本机，存在时仍核验哈希；`lint --local` 进一步要求所有登记版本的原件存在。损坏/变更不要覆盖旧快照，重新获取或登记新版本。撤回来源按 SCHEMA 手工标 withdrawn、记录原因并运行 plan，不自动删知识正文。

## 检查边界

`index --check` 验证自动目录未漂移。`lint` 检查元数据、重复 ID/模块主导读、来源账本指纹、关联页、来源版本绑定、原件哈希、索引及解法的论文/方法引用；draft/contested、孤页、长页和待整合只提示，故 PASS 可能带 warnings，收尾必须阅读输出和 plan。

`check_context.py` 检查当前入口、Markdown 相对链接及 Git 分发目标、模板标记泄漏和误入分发的附件/环境文件；允许配置 remote，不验证外链、锚点、科研结论或并发。单个来源账本采用原子替换，多文件更新/索引不具备事务或锁，写入串行由整合者负责。

## 公开发布前的隐私检查

`python3 scripts/check_public.py` 扫描当前分发文件与 HEAD 的完整历史，检查作者/提交者邮箱是否为 GitHub noreply，以及凭证、用户绝对路径、内网地址、邮箱与附件候选。CI 完整拉取历史再检查；浅克隆需要先补齐历史。启用本机预推送钩子：`git config --local core.hooksPath .githooks`。钩子检查实际待推送的每个本地 ref，而非只查当前分支，防止误推旧私人分支。

检查器只输出问题类别与文件/提交位置，不打印匹配到的凭证或个人信息；无法判断任意业务文字是否来自公司，人工审核仍需确认来源为公开材料。自动检查不能证明此前短暂公开的内容未被访问；远端旧仓库已按用户要求清除并重建，不保存原始历史。

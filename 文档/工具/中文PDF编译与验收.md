# 中文PDF编译与验收

本页提供[论文标准流程](../../维护/工作流.md#论文知识沉淀标准流程)第3步的操作细节。默认交付约定范围的正文中文PDF；失败后先定位并修复，再切换可用链路。原件、译后工程、构建输出分别保存，日志和渲染留在忽略的 `.local/papers/<ID>/qa/`，不入Git。附件备份另按[私有维护](中文PDF发布.md)执行。

## TaQFormer为何第一次失败、重试后成功

2026-10-28，TaQFormer第一次处理完成正文翻译和精读，但远程编译超时、本地编译启动失败后就交付了PDF缺项。后续重试使用完整译后工程，保留`acmart`双栏排版，成功生成7页中文PDF，见[论文笔记](../../来源/SRC-TAQFORMER/阅读笔记.md)。

| 现象与证据 | 可以得出的结论 | 本次有效处理 |
|---|---|---|
| 首轮记录远程服务多次30秒超时；后续XeLaTeX请求实际返回PDF | 当时远程链路未完成；没有证据证明论文模板本身不能编译，也未隔离服务恢复的原因 | 改用适配XeLaTeX的CJK配置重试，同时继续已有本地工具链 |
| 默认PATH下找不到`lualatex`；受管TeX Live目录实际已有引擎和BibTeX | 未加入PATH，不等于没有安装 | 搜索已知安装目录，显式设置编译子进程PATH |
| 同一中文最小文档在`C.UTF-8`下退出1，无PDF、无TeX日志，控制台为`Unable to read locale data`；在`en_US.UTF-8`下退出0并产生1页PDF | 本机不支持所继承locale，失败发生在处理正文之前；此前笼统归因为`acmart/luatexja`问题不准确 | 依据`locale -a`选择可用UTF-8 locale，仅修改编译子进程环境 |
| 完整工程指定本机Songti SC/Heiti SC后由LuaLaTeX完成多遍编译和BibTeX | 本机字体及完整工具链可用；字体选择是环境适配，未单独证明它是首轮根因 | 保留正文、公式、原图及参考文献，使用完整译后工程编译 |
| 内置`compile_latex_document`报告成功，却没有在附件路径生成PDF | 工具提供编译诊断，不导出成品 | 继续使用能写出文件的编译链路，检查实际输出路径 |
| `simple.tex`只有摘要级解读 | 其编译成功也不能满足正文翻译要求 | 交付完整译后工程的PDF，摘要入口不计为论文译文 |

本次复盘再次进行了locale对照：只改变`LC_ALL`/`LANG`，使用相同引擎、中文字体、源码和参数，复现上述失败/成功；诊断留在 `.local/papers/2610.26199/qa/locale-recheck/`。`lualatex --version`在两种locale下都退出0，所以仅查版本会漏掉此问题。最终7页产物的检查范围和SHA256见[PDF盘点](../../译文/PDF目录.md)及[日志](../../log.md)。

流程上的遗漏是没有完成本地工具探测和启动错误定位，就结束了PDF生成阶段。继续精读可以保留有效进展，但不能解除中文PDF交付要求。

## 先验证环境，再编译完整工程

探测已有安装，不自动安装庞大环境。除PATH外，检查`/Library/TeX/texbin`、`/usr/local/texlive/*/bin/*`和`~/.cache/codex-runtimes/codex-texlive/*/bin/*`；其他平台按当前宿主的实际安装位置探测。受管运行库通常不在默认PATH中，不能只用`command -v`判断。

下面的只读探测从仓库根目录运行，输出本机实际结果；不要把运行输出中的个人路径提交到Git：

```bash
python3 - <<'PY'
from pathlib import Path
import glob, locale, os, shutil

print('继承的locale:', {k: os.environ.get(k) for k in ('LANG', 'LC_ALL', 'LC_CTYPE')})
for name in ('C.UTF-8', 'en_US.UTF-8', 'zh_CN.UTF-8'):
    try:
        locale.setlocale(locale.LC_ALL, name)
        print('可用locale:', name)
    except locale.Error:
        print('不可用locale:', name)
roots = ['/Library/TeX/texbin']
roots += glob.glob('/usr/local/texlive/*/bin/*')
roots += glob.glob(str(Path.home() / '.cache/codex-runtimes/codex-texlive/*/bin/*'))
for tool in ('latexmk', 'lualatex', 'xelatex', 'bibtex', 'biber'):
    found = {shutil.which(tool)}
    found.update(str(Path(root) / tool) for root in roots if (Path(root) / tool).is_file())
    print(tool, sorted(p for p in found if p))
PY
```

根据结果设置编译子进程环境，不更改用户全局shell配置。本次宿主可用`en_US.UTF-8`；其他机器需实际探测，不能盲目照抄。例如已探测到上述受管目录时：

```bash
# 先把工作目录设为完整译后工程目录；路径和主文件名按实际探测结果填写。
TEX_BIN="$HOME/.cache/codex-runtimes/codex-texlive/full/bin/universal-darwin"
env PATH="$TEX_BIN:$PATH" LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 \
  "$TEX_BIN/latexmk" -lualatex -interaction=nonstopmode -halt-on-error \
  -outdir=build main.tex > build-console.log 2>&1
```

先用一份含“中文字体验证”和数学公式的最小文档实际编译。启动失败时读控制台；缺少`.log`常说明尚未进入TeX处理阶段，不应先大改论文源码。只有最小文档通过后，再用同样环境编译完整论文。记录选用的引擎、locale、字体和主文件；不重设`HOME`或`CODEX_HOME`。

## 按错误切换可用链路

| 失败位置 | 处理方式 |
|---|---|
| 远程超时或不可用 | 遵守skill同配置重试上限，读取响应/日志；转向已安装本地链路。更改引擎或CJK配置时在副本操作，不无限重复同一请求 |
| 引擎启动前退出、locale报错、没有TeX日志 | 对照可用locale，以修正后的子进程环境重做中文最小编译；先排环境，再排源码 |
| 字体找不到或初始化失败 | 探测实际字体；LuaLaTeX搭配`luatexja-fontspec`等对应栈，XeLaTeX搭配`xeCJK`。不要同时混用两套栈；切换后重新验收映射和渲染 |
| `Undefined control sequence` | 对照报错行定位缺失宏包或误改命令，例如`\mathbb`需要提供该命令的数学宏包；保留原数学语义 |
| 引用显示`?`、`??`或文献缺失 | 运行BibTeX/Biber与后续TeX遍次，优先用`latexmk`管理依赖；检查主文件与图表路径，不以单遍生成文件判定完成 |
| 原出版模板持续失败 | 在副本中切换简化中文排版，保留同一份完整正文、公式、表格、图片、引用及权利声明，注明重排。不能用精读、摘要或删去复杂章节换取成功 |
| 无LaTeX源码 | 从固定正式PDF翻译成章节可核对的正文，用已有LaTeX或其他排版工具生成PDF，明确非作者源码重排及未能恢复的内容 |
| 只有编译成功诊断或预览 | 继续导出/本地构建。检查输出文件真实存在、为本次源码对应产物，避免误取上次或其他入口的PDF |

每次有针对性的修复后读取新日志；同一错误原样重复没有诊断价值。更换工具不得缩小翻译范围。确实缺依赖、源码资源或编译服务全部不可用时，保留已完成产物、具体错误与下一条可执行恢复动作；依赖安装仍遵守授权和成本边界。

## 验收的是最终PDF文件

逐项核对后才能登记PDF已完成：

1. 最终附件路径存在，文件头/解析结果为PDF、页数非零；记录最终SHA256、页数及实际编译主文件。检查该文件对应当前译文，不能沿用旧文件的验收记录。
2. 对照原文确认约定正文的章节、图表、公式和结论均已保留；说明附录、图内文字与参考文献的翻译范围。摘要版不能通过此项。
3. 使用Poppler或已有PDFium等渲染器渲染所有页面，逐页目视中文、数学、表格、图片、换行和页边界；修订后重渲染最终文件，复查所有受影响页，分页变化则扩大检查范围。
4. 提取正文核对中文可读性、关键结果及未解析引用；检查编译缺字日志和渲染器字体错误。保留的版面警告按具体页面判断，不把工具零警告当视觉验收。
5. 核查中文字体嵌入和Unicode映射，尤其是换引擎后。既有[字体修复案例](../会话/PAPER-002.md#2026-10-27修复前四篇中文显示)显示，中文可提取、字体可渲染、视觉可读需要分别验证；公式和英文可见不代表中文正常。可用`pdffonts`或现有PDF库递归检查页面/Form资源，不把缺少检查工具写成检查通过。
6. 保存可继续编译的完整译后工程及图片、样式、参考文献；阅读笔记和PDF目录同步最终范围、QA与存储状态。最终答复提供实际中文PDF入口，区分本地交付和私有备份；只有尚存真实阻塞时明确说明PDF缺项。

结构lint、Markdown检查和编译成功诊断均不代替这些文件检查。本地生成、视觉验收、翻译准确性复核、许可核实和远端备份是不同事实，各自按真实完成范围报告。

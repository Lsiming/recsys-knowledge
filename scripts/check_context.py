#!/usr/bin/env python3
"""Check active Markdown entry points, inline link targets and template leaks.

Uses Git's tracked/non-ignored file list. Historical snapshots are excluded;
their directory index remains active. Does not check anchors, external URL reachability,
reference-style links, scientific claims or concurrent session ownership.
Local attachments belong in inline code, never in published relative links.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "AGENTS.md", "CLAUDE.md", "README.md", "PROJECT_MEMORY.md", "SESSION.md",
    "TODO.md", "SCHEMA.md", "知识库/知识地图.md", "来源/来源目录.md", "log.md",
    "维护/上下文路由.md", "维护/工作流.md", "维护/审核台.md",
    "维护/架构决定.md", "scripts/README.md", "scripts/CONFIG.md",
    "文档/项目背景.md", "文档/目录.md",
    "文档/规范/上下文与多会话协作.md", "文档/规范/研究工作流.md",
    "文档/会话/目录.md", "文档/历史归档/目录.md",
    "CONTRIBUTING.md", "LICENSE", "LICENSES/CC-BY-4.0.txt",
    "LICENSES/MIT.txt", "译文/目录.md", "译文/目录.json",
)
LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^)\n]+?)\s*\)")
PLACEHOLDER = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
PRIVATE_DIRS = {".local", ".obsidian", ".venv", "venv", "node_modules", ".worktrees",
                "papers", "data", "datasets", "outputs", "artifacts", "checkpoints",
                "models", "logs", "tmp", "cache", "__pycache__"}
ATTACHMENT_SUFFIXES = {".pdf", ".tex", ".bib", ".bbl", ".bst", ".cls", ".sty", ".aux",
                       ".log", ".gz", ".zip", ".tgz", ".pt", ".pth", ".ckpt", ".safetensors",
                       ".pem", ".key", ".parquet", ".pkl", ".pickle", ".onnx", ".h5", ".hdf5"}


def check_distribution(names: set[str]) -> list[str]:
    errors = []
    for name in sorted(names):
        path = Path(name)
        private_env = path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example")
        if path.parts[0] in PRIVATE_DIRS or path.suffix.lower() in ATTACHMENT_SUFFIXES or private_env:
            errors.append(f"不应进入 Git 分发的附件/环境文件：{name}")
    return errors


def check_markdown(root: Path, relative: str, visible: set[str] | None = None) -> tuple[list[str], int]:
    path = root / relative
    if not path.is_file():
        return [f"{relative}: 文件不存在"], 0
    content = path.read_text(encoding="utf-8")
    errors = []
    if not relative.startswith("文档/模板/") and PLACEHOLDER.search(content):
        errors.append(f"{relative}: 活跃文档中仍有模板占位符")
    # Link-like text inside fenced examples and inline code is not a real link.
    prose = re.sub(r"(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1\s*$", "", content)
    prose = re.sub(r"(`+)[^`\n]*\1", "", prose)
    count = 0
    for match in LINK.finditer(prose):
        target = re.sub(r'\s+"[^"\n]*"$', '', match.group(1)).strip("<>")
        try:
            parsed = urlsplit(target)
        except ValueError:
            errors.append(f"{relative}: 无法解析链接 {target}")
            continue
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        count += 1
        destination = (path.parent / unquote(parsed.path)).resolve()
        try:
            local = destination.relative_to(root.resolve()).as_posix()
        except ValueError:
            errors.append(f"{relative}: 本地链接超出仓库 {target}")
            continue
        if local.split("/")[0] in {".local", ".git"}:
            errors.append(f"{relative}: 公开链接指向本地附件 {target}；请改为公开原文或行内代码路径")
            continue
        if not destination.exists():
            errors.append(f"{relative}: 链接目标不存在 {target}")
        elif visible is not None and local != "." and local not in visible and not (
            destination.is_dir() and any(name.startswith(local + "/") for name in visible)
        ):
            errors.append(f"{relative}: 链接目标未纳入 Git 分发 {target}")
    return errors, count


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.PIPE,
    )


def main() -> int:
    try:
        names = git("ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0")
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: 无法读取本地 Git 状态：{exc}")
        return 1
    errors = [f"缺少必需入口：{name}" for name in REQUIRED if not (ROOT / name).is_file()]
    visible = set(filter(None, names))
    errors.extend(check_distribution(visible))
    files = sorted({
        name for name in names if name.endswith(".md")
        and (not name.startswith("文档/历史归档/") or name == "文档/历史归档/目录.md")
    })
    links = 0
    for name in files:
        findings, count = check_markdown(ROOT, name, visible)
        errors.extend(findings)
        links += count
    if errors:
        print("FAIL\n" + "\n".join(f"- {error}" for error in errors))
        return 1
    print(f"PASS: {len(files)} 份活跃 Markdown，{links} 个本地链接目标；入口/占位符/公开链接检查通过。")
    print("范围：不检查锚点、引用式链接、外部网址可访问性、科研结论或并发锁。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

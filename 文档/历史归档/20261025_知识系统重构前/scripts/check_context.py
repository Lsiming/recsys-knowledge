#!/usr/bin/env python3
"""Check active Markdown entry points, inline link targets and template leaks.

Uses Git's tracked/non-ignored file list. Historical snapshots are excluded;
their README remains active. Does not check anchors, external URL reachability,
reference-style links, scientific claims or concurrent session ownership.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "AGENTS.md", "CLAUDE.md", "README.md", "PROJECT_MEMORY.md", "SESSION.md",
    "TODO.md", "docs/PROJECT_BACKGROUND.md", "docs/README.md",
    "docs/规范/上下文与多会话协作.md", "docs/规范/研究工作流.md",
    "docs/研究/README.md", "docs/实验/README.md", "docs/会话/README.md",
    "docs/模板/任务交接模板.md", "docs/模板/论文笔记模板.md",
    "docs/模板/实验记录模板.md", "docs/历史归档/README.md",
)
LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+\"[^\"\n]*\")?\s*\)")
PLACEHOLDER = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")


def check_markdown(root: Path, relative: str) -> tuple[list[str], int]:
    path = root / relative
    if not path.is_file():
        return [f"{relative}: 文件不存在"], 0
    content = path.read_text(encoding="utf-8")
    errors = []
    if not relative.startswith("docs/模板/") and PLACEHOLDER.search(content):
        errors.append(f"{relative}: 活跃文档中仍有模板占位符")
    # Link-like text inside fenced examples and inline code is not a real link.
    prose = re.sub(r"(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1\s*$", "", content)
    prose = re.sub(r"(`+)[^`\n]*\1", "", prose)
    count = 0
    for match in LINK.finditer(prose):
        target = match.group(1).strip("<>")
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
            destination.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{relative}: 本地链接超出仓库 {target}")
            continue
        if not destination.exists():
            errors.append(f"{relative}: 链接目标不存在 {target}")
    return errors, count


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.PIPE,
    )


def main() -> int:
    try:
        names = git("ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0")
        remotes = git("remote").strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: 无法读取本地 Git 状态：{exc}")
        return 1
    errors = [f"缺少必需入口：{name}" for name in REQUIRED if not (ROOT / name).is_file()]
    if remotes:
        errors.append("仓库配置了 remote，与仅本地 Git 约定不符；请核实最新用户决定")
    files = sorted({
        name for name in names if name.endswith(".md")
        and (not name.startswith("docs/历史归档/") or name == "docs/历史归档/README.md")
    })
    links = 0
    for name in files:
        findings, count = check_markdown(ROOT, name)
        errors.extend(findings)
        links += count
    if errors:
        print("FAIL\n" + "\n".join(f"- {error}" for error in errors))
        return 1
    print(f"PASS: {len(files)} 份活跃 Markdown，{links} 个本地链接目标；入口/占位符/无远端检查通过。")
    print("范围：不检查锚点、引用式链接、外部网址可访问性、科研结论或并发锁。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

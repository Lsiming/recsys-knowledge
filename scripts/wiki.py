#!/usr/bin/env python3
"""Local evidence bookkeeping; semantic reading and merging remain Agent work."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9-]*\Z")
TYPES = {"map", "concept", "method", "synthesis", "problem", "question"}
STATES = {"draft", "reviewed", "contested"}


def today():
    return datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def within(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"路径超出仓库：{relative}")
    return path


def protocol(root):
    # Navigation/code refactoring must not force all papers through ingestion again.
    schema = (root / "SCHEMA.md").read_text(encoding="utf-8")
    revision = re.search(r"^处理语义版本：([1-9]\d*)$", schema, re.MULTILINE)
    if not revision:
        raise ValueError("SCHEMA.md 缺少有效的处理语义版本")
    return digest(f"ingest-semantics:{revision.group(1)}".encode())


def records(root):
    result = {}
    for path in sorted((root / "来源").glob("*/来源.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["id"] != path.parent.name or record["id"] in result:
            raise ValueError(f"来源 ID 与目录不符或重复：{path}")
        result[record["id"]] = record
    return result


def current(record):
    return next(v for v in record["versions"] if v["fingerprint"] == record["current"])


def read_page(path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        raise ValueError(f"{path}: 缺少 frontmatter")
    end = lines[1:].index("---") + 1
    meta = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(":")
        if not separator or key in meta:
            raise ValueError(f"{path}: 元数据重复或格式错误：{line}")
        meta[key] = json.loads(value.strip())
    for key, kind in {"id": str, "title": str, "type": str, "status": str,
                      "updated": str, "summary": str, "aliases": list,
                      "sources": dict, "related": list}.items():
        if key not in meta or not isinstance(meta[key], kind):
            raise ValueError(f"{path}: 缺少或无效字段 {key}")
    if not ID.fullmatch(meta["id"]) or meta["type"] not in TYPES or meta["status"] not in STATES:
        raise ValueError(f"{path}: 无效 ID/type/status")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["updated"]):
        raise ValueError(f"{path}: 日期格式无效")
    if not all(isinstance(item, str) for item in meta["aliases"] + meta["related"]):
        raise ValueError(f"{path}: aliases/related 必须为字符串数组")
    if not all(isinstance(k, str) and isinstance(v, str) for k, v in meta["sources"].items()):
        raise ValueError(f"{path}: sources 必须为来源 ID → 指纹映射")
    if "module" in meta and (not isinstance(meta["module"], str) or not meta["module"].strip()):
        raise ValueError(f"{path}: module 必须为非空字符串")
    if meta["type"] == "problem":
        if not meta.get("module") or not isinstance(meta.get("solutions"), list) or not meta["solutions"]:
            raise ValueError(f"{path}: 问题页需要 module 和非空 solutions")
        names = set()
        for solution in meta["solutions"]:
            if not isinstance(solution, dict) or not all(
                isinstance(solution.get(key), str) and solution[key].strip() for key in ("name", "idea")
            ):
                raise ValueError(f"{path}: 每种解法需要 name 和 idea")
            papers = solution.get("papers")
            if not isinstance(papers, list) or not papers or not all(isinstance(p, str) for p in papers):
                raise ValueError(f"{path}: 每种解法需要非空 papers 来源 ID 数组")
            if "method" in solution and not isinstance(solution["method"], str):
                raise ValueError(f"{path}: method 必须为知识页 ID")
            name = solution["name"].casefold()
            if name in names:
                raise ValueError(f"{path}: 重复解法 {solution['name']}，请合并论文引用")
            names.add(name)
    elif "solutions" in meta:
        raise ValueError(f"{path}: solutions 只用于 problem 页")
    return meta, "\n".join(lines[end + 1:])


def pages(root):
    result = {}
    for path in sorted((root / "知识库").rglob("*.md")):
        if path == root / "知识库/知识地图.md":
            continue
        meta, body = read_page(path)
        if meta["id"] in result:
            raise ValueError(f"页面 ID 重复：{meta['id']}")
        result[meta["id"]] = (path, meta, body)
    return result


def register(root, args):
    if not ID.fullmatch(args.id):
        raise ValueError("来源 ID 只能使用字母、数字和连字符")
    artifacts = []
    for filename in args.file:
        source = Path(filename).expanduser().resolve()
        data = source.read_bytes()
        sha = digest(data)
        target = root / ".local/sources" / args.id / sha / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != data:
            raise ValueError(f"不可覆盖已有快照：{target}")
        if not target.exists():
            target.write_bytes(data)
        artifacts.append({"name": source.name, "sha256": sha,
                          "snapshot": target.relative_to(root).as_posix()})
    version = {"locator": args.locator, "revision": args.revision,
               "read_scope": args.read_scope, "artifacts": artifacts}
    fingerprint = digest(canonical(version))
    version.update(fingerprint=fingerprint, retrieved_on=args.date or today(), integration=None)
    path = root / "来源" / args.id / "来源.json"
    if path.exists():
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["title"] != args.title or record["kind"] != args.kind:
            raise ValueError("同一来源的 title/kind 不同；请核对身份后手工迁移，或使用新 ID")
    else:
        record = {"id": args.id, "title": args.title, "kind": args.kind,
                  "state": "active", "current": fingerprint, "versions": []}
    if not any(v["fingerprint"] == fingerprint for v in record["versions"]):
        record["versions"].append(version)
    record["current"] = fingerprint
    write_json(path, record)
    print(json.dumps({"id": args.id, "fingerprint": fingerprint,
                      "note": "已登记；尚需阅读、合并、审核并 integrate"}, ensure_ascii=False))


def pending(root):
    all_pages = pages(root)
    result = []
    for sid, record in records(root).items():
        version = current(record)
        receipt = version.get("integration")
        reasons = []
        if record["state"] != "active":
            reasons.append("来源已撤回；保留证据，逐条复核结论")
        if not receipt:
            reasons.append("当前版本未完成整合")
        else:
            if receipt["protocol"] != protocol(root):
                reasons.append("处理语义版本已变更")
            notes = root / "来源" / sid / "阅读笔记.md"
            if not notes.is_file() or receipt["notes_sha256"] != digest(notes.read_bytes()):
                reasons.append("阅读笔记已变更")
            for pid in receipt["pages"]:
                if pid not in all_pages or all_pages[pid][1]["sources"].get(sid) != record["current"]:
                    reasons.append(f"输出缺失或来源绑定变更：{pid}")
                elif all_pages[pid][1]["status"] != "reviewed":
                    reasons.append(f"输出进入待复核状态：{pid}")
        affected = [pid for pid, (_, meta, _) in all_pages.items() if sid in meta["sources"]]
        if receipt and set(affected) - set(receipt["pages"]):
            reasons.append("新增引用页尚未记录整合自查")
        if any(all_pages[pid][1]["sources"][sid] != record["current"] for pid in affected):
            reasons.append("知识页仍引用旧来源版本")
        if reasons:
            candidates = sorted(pid for pid, (_, meta, _) in all_pages.items()
                                if (set(meta["related"]) | {s["method"] for s in meta.get("solutions", []) if s.get("method")})
                                & set(affected) and pid not in affected)
            result.append({"id": sid, "reasons": reasons, "affected": affected,
                           "review_candidates": candidates})
    return result


def integrate(root, args):
    registry = records(root)
    record = registry[args.id]
    if record["state"] != "active":
        raise ValueError("撤回来源不能标记为完成整合")
    all_pages = pages(root)
    selected = []
    for relative in args.pages:
        path = within(root, relative)
        meta, _ = read_page(path)
        if meta["id"] not in all_pages or all_pages[meta["id"]][0] != path:
            raise ValueError(f"不属于 Wiki 的输出：{relative}")
        if meta["sources"].get(args.id) != record["current"]:
            raise ValueError(f"{relative}: 未绑定当前来源指纹")
        if meta["status"] != "reviewed":
            raise ValueError(f"{relative}: 尚未自查为 reviewed")
        selected.append(meta["id"])
    bound = {pid for pid, (_, meta, _) in all_pages.items() if args.id in meta["sources"]}
    if not bound.issubset(selected):
        raise ValueError(f"仍有引用该来源的页面未复核：{sorted(bound - set(selected))}")
    notes = root / "来源" / args.id / "阅读笔记.md"
    if not notes.is_file() or len(notes.read_text(encoding="utf-8").strip()) < 80:
        raise ValueError("先保存有实质内容的 阅读笔记.md；工具不判断阅读是否真实")
    current(record)["integration"] = {
        "protocol": protocol(root), "notes_sha256": digest(notes.read_bytes()),
        "pages": sorted(set(selected)), "reviewed_on": today(),
        "review_method": "agent-self-review", "review_note": args.review_note}
    write_json(root / "来源" / args.id / "来源.json", record)
    print(f"已记录 {args.id} 的整合自查；不代表独立审核或科研验证")


def table_text(value):
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]").replace("\n", " ")


def generated(root):
    all_pages, registry = pages(root), records(root)
    wiki = ["# 知识地图", "", "<!-- 由 python3 scripts/wiki.py index 生成，请维护知识页元数据。 -->", "",
            "沿模块 → 问题 → 解法 → 论文学习。模块导读组织问题与候选阅读，已精读方案另列论文依据。", ""]
    maps = [(p, m) for p, m, _ in all_pages.values() if m["type"] == "map"]
    overview = [(p, m) for p, m in maps if not m.get("module")]
    if overview:
        wiki += ["## 总览、专题与阅读路线", ""]
        for path, meta in overview:
            state = {"draft": "（初稿）", "contested": "（存在未解分歧）"}.get(meta["status"], "")
            wiki.append(f"- [{table_text(meta['title'])}]({path.relative_to(root / '知识库').as_posix()}) — {meta['summary']}{state}")
        wiki.append("")
    guides = [(p, m) for p, m in maps if m.get("module")]
    wiki += ["## 按模块学习", ""]
    problems = [(p, m) for p, m, _ in all_pages.values() if m["type"] == "problem"]
    if not problems and not guides:
        wiki += ["尚无模块导读与论文方案；已有支持知识见下方。", ""]
    for module in sorted({m["module"] for _, m in problems + guides}):
        wiki += [f"### {table_text(module)}", ""]
        for path, meta in guides:
            if meta["module"] == module:
                state = {"draft": "（初稿）", "contested": "（存在未解分歧）"}.get(meta["status"], "")
                wiki += [f"[{table_text(meta['title'])}]({path.relative_to(root / '知识库').as_posix()}) — {meta['summary']}{state}", ""]
        if not any(m["module"] == module for _, m in problems):
            continue
        wiki += ["已有论文依据的问题与解法：", "", "| 问题 | 解决方案 | 核心思路 | 对应论文 |", "|---|---|---|---|"]
        for path, meta in problems:
            if meta["module"] != module:
                continue
            problem_link = f"[{table_text(meta['title'])}]({path.relative_to(root / '知识库').as_posix()})"
            for solution in meta["solutions"]:
                name = table_text(solution["name"])
                if solution.get("method") in all_pages:
                    method_path = all_pages[solution["method"]][0].relative_to(root / "知识库").as_posix()
                    name = f"[{name}]({method_path})"
                papers = "、".join(
                    f"[{table_text(registry[sid]['title'])}](../来源/{sid}/阅读笔记.md)" if sid in registry else table_text(sid)
                    for sid in solution["papers"])
                wiki.append(f"| {problem_link} | {name} | {table_text(solution['idea'])} | {papers} |")
        wiki.append("")
    wiki += ["## 概念、方法与支持知识", ""]
    labels = {"concept": "概念", "method": "方法", "synthesis": "综合比较", "question": "待研究问题"}
    for kind in sorted(TYPES - {"problem", "map"}):
        group = [(p, m) for p, m, _ in all_pages.values() if m["type"] == kind]
        if group:
            wiki += [f"### {labels[kind]}", ""]
            for path, meta in group:
                state = {"draft": "（初稿）", "contested": "（存在未解分歧）"}.get(meta["status"], "")
                wiki.append(f"- [{table_text(meta['title'])}]({path.relative_to(root / '知识库').as_posix()}) — {meta['summary']}{state}")
            wiki.append("")
    source = ["# 来源目录", "", "<!-- 由 python3 scripts/wiki.py index 生成。 -->", "",
              "进入单份资料的解读，再沿相关知识链接查看概念、问题与方法比较。实际阅读范围见各篇笔记。", ""]
    for sid, record in registry.items():
        state = "（已撤回，结论需复核）" if record["state"] != "active" else ""
        source.append(f"- [{table_text(record['title'])}]({sid}/阅读笔记.md) · [来源与版本]({sid}/来源.json){state}")
        backrefs = [f"[{table_text(meta['title'])}](../{path.relative_to(root).as_posix()})"
                    for path, meta, _ in all_pages.values() if sid in meta["sources"]]
        if backrefs:
            source.append("  相关知识：" + "、".join(backrefs))
    source.append("")
    return {root / "知识库/知识地图.md": "\n".join(wiki), root / "来源/来源目录.md": "\n".join(source)}


def index(root, check=False):
    errors = []
    for path, text in generated(root).items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                errors.append(f"索引待更新：{path.relative_to(root)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    return errors


def lint(root, local=False):
    errors, warnings = [], []
    registry, all_pages = records(root), pages(root)
    for sid, record in registry.items():
        if not (root / "来源" / sid / "阅读笔记.md").is_file():
            errors.append(f"{sid}: 缺少 阅读笔记.md")
        for version in record["versions"]:
            content = {k: version[k] for k in ("locator", "revision", "read_scope", "artifacts")}
            if digest(canonical(content)) != version["fingerprint"]:
                errors.append(f"{sid}: 来源指纹不符")
            for artifact in version["artifacts"]:
                path = within(root, artifact["snapshot"])
                if path.exists():
                    if digest(path.read_bytes()) != artifact["sha256"]:
                        errors.append(f"{sid}: 原件哈希不符 {artifact['snapshot']}")
                elif local:
                    errors.append(f"{sid}: 本地原件缺失 {artifact['snapshot']}")
        if record["state"] not in {"active", "withdrawn"}:
            errors.append(f"{sid}: 未知来源状态")
    inbound = {pid: 0 for pid in all_pages}
    module_guides = {}
    for pid, (path, meta, body) in all_pages.items():
        if meta["type"] == "map" and meta.get("module"):
            module = meta["module"]
            if module in module_guides:
                errors.append(f"{pid}: 模块 {module} 存在重复导读 {module_guides[module]}")
            module_guides[module] = pid
        for target in meta["related"]:
            if target not in all_pages:
                errors.append(f"{pid}: 未知关联页 {target}")
            elif target != pid:
                inbound[target] += 1
        for sid, fingerprint in meta["sources"].items():
            if sid not in registry:
                errors.append(f"{pid}: 未知来源 {sid}")
            elif fingerprint != registry[sid]["current"] or registry[sid]["state"] != "active":
                errors.append(f"{pid}: 来源版本过时或已撤回 {sid}")
        for solution in meta.get("solutions", []):
            for sid in solution["papers"]:
                if sid not in meta["sources"]:
                    errors.append(f"{pid}: 解法论文未绑定来源版本 {sid}")
                if sid not in registry or registry[sid]["kind"] != "paper":
                    errors.append(f"{pid}: 解法需要已登记的 paper 来源 {sid}")
            target = solution.get("method")
            if target:
                if target not in all_pages or all_pages[target][1]["type"] != "method":
                    errors.append(f"{pid}: 未知或无效方法页 {target}")
                else:
                    inbound[target] += 1
        if not meta["sources"] and meta["type"] not in {"map", "question"}:
            errors.append(f"{pid}: 缺少来源证据")
        if meta["status"] != "reviewed":
            warnings.append(f"{pid}: {meta['status']}，作答时保留此状态")
        if len(body.splitlines()) > 200:
            warnings.append(f"{pid}: 正文超过 200 行，考虑摘要或拆页")
    warnings += [f"{pid}: 无其他知识页关联，可检查是否孤立" for pid, count in inbound.items() if not count]
    errors += index(root, check=True)
    for item in pending(root):
        warnings.append(f"{item['id']}: {'；'.join(item['reasons'])}")
    return errors, warnings


def search(root, query, limit):
    tokens = query.casefold().split()
    matches = []
    registry = records(root)
    for path, meta, body in pages(root).values():
        solutions = meta.get("solutions", [])
        solution_terms = [s[key] for s in solutions for key in ("name", "idea")]
        paper_ids = sorted({sid for s in solutions for sid in s["papers"]})
        paper_terms = [registry[sid]["title"] for sid in paper_ids if sid in registry]
        heading = " ".join([meta["title"], *meta["aliases"], meta["summary"], meta.get("module", ""),
                            *solution_terms, *paper_ids, *paper_terms]).casefold()
        terms = list(tokens)
        for token in tokens:
            if any(token in alias.casefold() for alias in meta["aliases"]):
                terms.extend(alias.casefold() for alias in meta["aliases"])
        score = sum(8 * (term in heading) + min(body.casefold().count(term), 5) for term in set(terms))
        if score:
            snippet = next((line for line in body.splitlines() if any(t in line.casefold() for t in tokens)), meta["summary"])
            matches.append({"path": path.relative_to(root).as_posix(), "title": meta["title"],
                            "status": meta["status"], "score": score, "snippet": snippet[:200],
                            **({"papers": paper_ids} if paper_ids else {})})
    return sorted(matches, key=lambda item: (-item["score"], item["path"]))[:limit]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="验收或迁移时指定独立仓库根")
    subs = parser.add_subparsers(dest="command", required=True)
    reg = subs.add_parser("register", help="快照原件并登记版本，不生成知识正文")
    for name in ("id", "title", "kind", "locator", "revision", "read-scope"):
        reg.add_argument("--" + name, required=True)
    reg.add_argument("--file", action="append", required=True)
    reg.add_argument("--date")
    subs.add_parser("plan", help="列出增量摄入及受影响页面候选")
    complete = subs.add_parser("integrate", help="记录当前 Agent 已完成的阅读/整合自查")
    complete.add_argument("id")
    complete.add_argument("--pages", nargs="+", required=True)
    complete.add_argument("--review-note", required=True)
    idx = subs.add_parser("index")
    idx.add_argument("--check", action="store_true")
    check = subs.add_parser("lint")
    check.add_argument("--local", action="store_true", help="另要求忽略目录中的原件存在")
    query = subs.add_parser("search")
    query.add_argument("query")
    query.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "register":
            register(root, args)
        elif args.command == "integrate":
            integrate(root, args)
        elif args.command == "plan":
            print(json.dumps(pending(root), ensure_ascii=False, indent=2))
        elif args.command == "search":
            print(json.dumps(search(root, args.query, args.limit), ensure_ascii=False, indent=2))
        elif args.command == "index":
            errors = index(root, args.check)
            if errors:
                print("\n".join(errors))
                return 1
            print("PASS: 知识与来源索引" if args.check else "已更新知识与来源索引")
        elif args.command == "lint":
            errors, warnings = lint(root, args.local)
            for warning in warnings:
                print("WARN: " + warning)
            for error in errors:
                print("ERROR: " + error)
            print(f"{'FAIL' if errors else 'PASS'}: {len(errors)} errors, {len(warnings)} warnings；结构检查不验证研究事实")
            return int(bool(errors))
    except (ValueError, KeyError, OSError, StopIteration) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

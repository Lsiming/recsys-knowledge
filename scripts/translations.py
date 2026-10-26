#!/usr/bin/env python3
"""Offline publication checks for licensed, canonical Markdown translations."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LICENSES = {
    'CC-BY-4.0': 'https://creativecommons.org/licenses/by/4.0/',
    'CC-BY-NC-SA-4.0': 'https://creativecommons.org/licenses/by-nc-sa/4.0/',
}


def load(root):
    return json.loads((root / '译文/目录.json').read_text(encoding='utf-8'))


def render(entries):
    lines = ['# 正式 Markdown 译文', '',
             '<!-- 由 python3 scripts/translations.py index 生成，请维护目录.json。 -->', '',
             '仅发布已核实允许译文再分发、并保留署名与许可的正式版本。原文、PDF、LaTeX、编译和核查附件留本地；来源阅读范围与科研证据见各篇笔记。', '',
             '“待授权”不表示没有译文，而是全文未公开；公开原文可读不等于获得全文翻译发布授权。CC BY-NC-SA 译文须遵守非商业和相同方式共享条件，详见 [许可规则](../LICENSE)。', '',
             '| 论文 | 正式译文 | 原文与许可 | 状态/范围 |', '|---|---|---|---|']
    for e in entries:
        title = e['title'].replace('|', '\\|')
        note = f"[{title}](../来源/{e['source_id']}/阅读笔记.md)"
        translation = f"[中文译文]({e['source_id']}/中文译文.md)" if e['status'] == 'published' else '本地保留'
        license_link = f" · [原文许可]({e['license_url']})" if e.get('license_url') else ''
        state = f"已公开，{e['license_id']}；{e['scope']}" if e['status'] == 'published' else e['reason']
        lines.append(f"| {note} | {translation} | [固定原文]({e['original_url']}){license_link} | {state.replace('|', '、')} |")
    return '\n'.join(lines) + '\n'


def check(root, entries):
    errors, ids, declared = [], set(), set()
    for e in entries:
        sid = e.get('source_id', '')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*', sid) or sid in ids:
            errors.append(f'无效或重复来源 ID：{sid}')
            continue
        ids.add(sid)
        source = root / '来源' / sid / '来源.json'
        if not source.is_file():
            errors.append(f'{sid}: 来源未登记')
            continue
        record = json.loads(source.read_text(encoding='utf-8'))
        version = next(v for v in record['versions'] if v['fingerprint'] == record['current'])
        if record['kind'] != 'paper' or e.get('original_url') != version['locator'] or e.get('revision') != version['revision']:
            errors.append(f'{sid}: 译文身份/版本与当前来源不符，需复核许可和译文版本')
        if e.get('status') not in {'published', 'local-only'}:
            errors.append(f'{sid}: 无效公开状态')
        if not e.get('reason') or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', e.get('checked_on', '')):
            errors.append(f'{sid}: 缺少核实日期或状态原因')
        if e.get('status') != 'published':
            if e.get('file'):
                errors.append(f'{sid}: 非公开项不能声明分发文件')
            continue
        expected = f'译文/{sid}/中文译文.md'
        declared.add(expected)
        if e.get('file') != expected:
            errors.append(f'{sid}: 正式译文路径不符')
            continue
        license_id = e.get('license_id')
        expected_url = LICENSES.get(license_id)
        if expected_url is None or e.get('license_url', '').replace('http://', 'https://').rstrip('/') + '/' != expected_url:
            errors.append(f'{sid}: 不支持或不匹配的译文许可')
        if e.get('evidence_url') != e.get('original_url') or not re.fullmatch(r'[0-9a-f]{64}', e.get('evidence_sha256', '')):
            errors.append(f'{sid}: 缺少固定版本许可核实记录')
        for key in ('authors', 'translator', 'scope', 'changes'):
            if not e.get(key):
                errors.append(f'{sid}: 缺少署名/派生说明 {key}')
        path = root / expected
        if not path.is_file():
            errors.append(f'{sid}: 正式译文缺失')
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != e.get('sha256'):
            errors.append(f'{sid}: 正式译文哈希不符')
        text = path.read_text(encoding='utf-8')
        if '<!-- translation-body -->' not in text:
            errors.append(f'{sid}: 缺少译文与授权说明分界')
        header = text.split('<!-- translation-body -->')[0]
        for required in [e['original_url'], expected_url or 'INVALID-LICENSE', *e.get('authors', []),
                         e.get('translator', ''), e.get('scope', ''), e.get('changes', '')]:
            if required not in header:
                errors.append(f'{sid}: 文件开头缺少许可/署名/范围说明 {required}')
    papers = {p.parent.name for p in (root / '来源').glob('*/来源.json')
              if json.loads(p.read_text(encoding='utf-8'))['kind'] == 'paper'}
    if papers != ids:
        errors.append('译文目录与已登记论文不一致：' + ', '.join(sorted(papers ^ ids)))
    actual = {p.relative_to(root).as_posix() for p in (root / '译文').rglob('*')
              if p.is_file() and p.name not in {'目录.md', '目录.json'}}
    if actual != declared:
        errors.append('存在未登记或缺失的译文文件：' + ', '.join(sorted(actual ^ declared)))
    index = root / '译文/目录.md'
    if not index.exists() or index.read_text(encoding='utf-8') != render(entries):
        errors.append('译文目录待更新：运行 python3 scripts/translations.py index')
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['index', 'check'])
    args = parser.parse_args(argv)
    try:
        entries = load(ROOT)
        if args.command == 'index':
            (ROOT / '译文/目录.md').write_text(render(entries), encoding='utf-8')
            return 0
        errors = check(ROOT, entries)
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print(f'FAIL: 无法读取译文记录：{exc}')
        return 1
    if errors:
        print('FAIL\n' + '\n'.join('- ' + e for e in errors))
        return 1
    print(f"PASS: {len(entries)} 篇论文，{sum(e['status'] == 'published' for e in entries)} 篇正式译文；身份/许可声明/哈希/目录检查通过。")
    print('范围：离线核对登记与文件一致性，不自动判断真实授权、译文质量或外链可用性。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check and index the per-paper PDF release registry without local attachments."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from translations import LICENSES

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'Lsiming/recsys-knowledge'
MANIFEST = '译文/PDF目录.json'
INDEX = '译文/PDF目录.md'


def load(root=ROOT):
    data = json.loads((root / MANIFEST).read_text(encoding='utf-8'))
    if data['schema_version'] != 1 or data['repository'] != REPOSITORY:
        raise ValueError('不支持的 PDF 目录版本或仓库')
    return data


def asset_url(tag, name):
    return f'https://github.com/{REPOSITORY}/releases/download/{tag}/{name}'


def valid_id(value):
    return isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*', value)


def check(data, root=ROOT):
    errors, ids, assets = [], set(), set()
    for e in data['entries']:
        sid = e.get('source_id')
        if not valid_id(sid) or sid in ids:
            errors.append(f'无效或重复 PDF 来源：{sid}')
            continue
        ids.add(sid)
        for key in ('title', 'original_url', 'revision', 'scope', 'reason', 'input_sha256'):
            if not e.get(key):
                errors.append(f'{sid}: 缺少 {key}')
        if not re.fullmatch(r'[0-9a-f]{64}', e.get('input_sha256', '')):
            errors.append(f'{sid}: 输入文件哈希无效')
        source = root / '来源' / sid / '来源.json'
        if source.exists():
            record = json.loads(source.read_text(encoding='utf-8'))
            version = next(v for v in record['versions'] if v['fingerprint'] == record['current'])
            if (e['original_url'], e['revision']) != (version['locator'], version['revision']):
                errors.append(f'{sid}: 原文版本变化，需重新核实 PDF 与许可')
        if e.get('status') not in {'published', 'local-only', 'failed'}:
            errors.append(f'{sid}: 无效 PDF 状态')
        rights = e.get('rights', {})
        if rights.get('decision') not in {'allowed', 'not-permitted', 'unverified'} or not rights.get('notes'):
            errors.append(f'{sid}: 缺少逐篇许可判断及说明')
        original_hash = rights.get('original_pdf_sha256')
        if original_hash is not None:
            if not re.fullmatch(r'[0-9a-f]{64}', original_hash):
                errors.append(f'{sid}: 原 PDF 许可证据哈希无效')
            elif source.exists() and original_hash not in {a['sha256'] for a in version['artifacts']}:
                errors.append(f'{sid}: 作品内许可证据未绑定当前来源原件')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', rights.get('checked_on', '')):
            errors.append(f'{sid}: 缺少许可核实日期')
        release = e.get('release')
        if e.get('status') != 'published':
            if release:
                errors.append(f'{sid}: 未发布项不能提供下载资产')
            continue
        if rights.get('decision') != 'allowed' or rights.get('license_id') not in LICENSES or rights.get('license_url') != LICENSES.get(rights.get('license_id')):
            errors.append(f'{sid}: 发布许可不支持或不匹配')
        for key in ('authors', 'evidence_url', 'evidence_sha256'):
            if not rights.get(key):
                errors.append(f'{sid}: 缺少许可证据/署名 {key}')
        if not re.fullmatch(r'[0-9a-f]{64}', rights.get('evidence_sha256', '')):
            errors.append(f'{sid}: 许可证据哈希无效')
        if not isinstance(release, dict):
            errors.append(f'{sid}: 缺少 release')
            continue
        tag, name = release.get('tag', ''), release.get('asset_name', '')
        version = release.get('translation_version', '')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', tag) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]*', version):
            errors.append(f'{sid}: release tag/译文版本无效')
        if name != f'{sid}.zh-CN.{version}.pdf' or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*\.pdf', name):
            errors.append(f'{sid}: PDF 资产名无效')
        if release.get('url') != asset_url(tag, name):
            errors.append(f'{sid}: 下载 URL 必须属于指定仓库且与 tag/资产名一致')
        if (tag, name) in assets:
            errors.append(f'{sid}: 重复资产')
        assets.add((tag, name))
        if not re.fullmatch(r'[0-9a-f]{64}', release.get('sha256', '')):
            errors.append(f'{sid}: PDF 哈希无效')
        for key in ('size_bytes', 'pages'):
            if type(release.get(key)) is not int or release[key] <= 0:
                errors.append(f'{sid}: {key} 无效')
        for key in ('translator', 'changes', 'qa'):
            if not release.get(key):
                errors.append(f'{sid}: 缺少发布说明 {key}')
        if release.get('verified_download_sha256') != release.get('sha256'):
            errors.append(f'{sid}: 缺少公开下载校验证据')
    return errors


def render(data):
    entries = data['entries']
    count = sum(e['status'] == 'published' for e in entries)
    lines = ['# 中文 PDF 目录与下载', '',
             '<!-- 由 python3 scripts/pdf_releases.py index 生成，请维护 PDF目录.json。 -->', '',
             f'截至 {data["updated"]}，逐篇处理 {len(entries)} 篇现有中文 PDF，公开 {count} 篇。PDF 存放于 GitHub Releases，不进入 Git 历史；克隆或拉取仓库不会自动下载 PDF。', '',
             '在仓库根目录执行（仅 Python 3.9+ 标准库，无需 GitHub 登录）：', '',
             '```bash', 'python3 scripts/download_translations.py',
             'python3 scripts/download_translations.py --source SRC-HSTU-PAPER',
             '```', '',
             '默认下载到 `.local/translations/<来源ID>/`，校验大小与 SHA256；已有正确文件会跳过。使用 `--verify-only` 检查本地文件，`--list` 列出可下载项，`--dest` 指定目录。下载失败返回非零状态并逐篇报告。', '',
             '每份公开 PDF 首页附原作者、固定版本、许可、译者、修改与范围说明。CC BY-NC-SA 4.0 项仅限非商业使用并须相同方式共享。未经许可的全文译文不随下载工具分发；原文可下载不代表允许公开译文。许可与代码见 [共享规则](../LICENSE)、[发布流程](../文档/工具/中文PDF发布.md)。', '',
             '本表按论文与最终 PDF 去重；同内容别名不重复计数，旧构建、原文和拆出的图表不是独立译文。未登记为公开知识来源的论文仅列附件盘点，不代表其精读已合入。', '',
             '| 论文 / 稳定 ID | 中文 PDF / 版本 | 许可与核实 | 翻译范围及处理结果 |', '|---|---|---|---|']
    for e in entries:
        sid = e['source_id']
        title = e['title'].replace('|', '、')
        rights = e['rights']
        release = e.get('release')
        link = f'[{title}]({e["original_url"]}) · `{sid}`'
        pdf = (f'[下载]({release["url"]}) · {release["translation_version"]} · {release["pages"]}页'
               if release else '未公开' if e['status'] == 'local-only' else '处理失败')
        license = rights.get('license_id') or rights['decision']
        evidence = f'[{license}]({rights["evidence_url"]})' if rights.get('evidence_url') else license
        result = f'{e["scope"]}；{e["reason"]}'.replace('|', '、').replace('\n', ' ')
        lines.append(f'| {link} | {pdf} | {evidence} | {result} |')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['index', 'check'])
    args = parser.parse_args(argv)
    try:
        data = load()
        errors = check(data)
        if errors:
            raise ValueError('\n'.join(errors))
        content = render(data)
        if args.command == 'index':
            (ROOT / INDEX).write_text(content, encoding='utf-8')
        elif not (ROOT / INDEX).exists() or (ROOT / INDEX).read_text(encoding='utf-8') != content:
            raise ValueError('PDF 目录待生成：python3 scripts/pdf_releases.py index')
        print(f'PASS: {len(data["entries"])} 篇 PDF 登记；许可声明/版本/下载入口/目录一致。离线检查不证明真实授权或远端资产可用。')
        return 0
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print(f'FAIL: {exc}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check the PDF inventory and private storage policy without local attachments."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from translations import LICENSES

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'Lsiming/recsys-knowledge'
PRIVATE_REPOSITORY = 'Lsiming/recsys-knowledge-attachments'
MANIFEST = '译文/PDF目录.json'
INDEX = '译文/PDF目录.md'


def load(root=ROOT):
    data = json.loads((root / MANIFEST).read_text(encoding='utf-8'))
    if (data.get('schema_version'), data.get('repository'), data.get('storage_policy'), data.get('attachment_repository')) != (2, REPOSITORY, 'private-only', PRIVATE_REPOSITORY):
        raise ValueError('PDF目录必须采用统一私有存储策略')
    return data


def asset_url(tag, name):
    return f'https://github.com/{PRIVATE_REPOSITORY}/releases/download/{tag}/{name}'


def valid_id(value):
    return isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*', value)


def check(data, root=ROOT):
    errors, ids, assets = [], set(), set()
    if (data.get('schema_version'), data.get('repository'), data.get('storage_policy'), data.get('attachment_repository')) != (2, REPOSITORY, 'private-only', PRIVATE_REPOSITORY):
        errors.append('PDF目录必须采用统一私有存储策略')
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
        if e.get('status') not in {'private', 'local-only', 'failed'}:
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
        if 'release' in e:
            errors.append(f'{sid}: 不允许公开PDF资产')
        release = e.get('private_copy')
        if e.get('status') != 'private':
            if release:
                errors.append(f'{sid}: 未发布项不能提供下载资产')
            continue
        if rights.get('decision') == 'allowed':
            if rights.get('license_id') not in LICENSES or rights.get('license_url') != LICENSES.get(rights.get('license_id')):
                errors.append(f'{sid}: 许可不支持或不匹配')
            if not rights.get('authors') or not rights.get('evidence_url') or not re.fullmatch(r'[0-9a-f]{64}', rights.get('evidence_sha256', '')):
                errors.append(f'{sid}: 缺少署名或许可证据')
        if not isinstance(release, dict):
            errors.append(f'{sid}: 缺少私有副本记录')
            continue
        tag, name = release.get('tag', ''), release.get('asset_name', '')
        version = release.get('translation_version', '')
        if not re.fullmatch(r'private-zh-pdfs-[0-9]{8}', tag) or not re.fullmatch(r'[0-9]+\.[0-9]+', version):
            errors.append(f'{sid}: release tag/译文版本无效')
        if name != f'{sid}.zh-CN.private.{version}.pdf' or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*\.pdf', name):
            errors.append(f'{sid}: PDF 资产名无效')
        if release.get('repository') != PRIVATE_REPOSITORY or release.get('visibility') != 'private' or 'url' in release:
            errors.append(f'{sid}: 必须使用指定私有仓库；公开目录不放需登录的逐篇链接')
        if (tag, name) in assets:
            errors.append(f'{sid}: 重复资产')
        assets.add((tag, name))
        if not re.fullmatch(r'[0-9a-f]{64}', release.get('sha256', '')):
            errors.append(f'{sid}: PDF 哈希无效')
        for key in ('size_bytes', 'pages'):
            if type(release.get(key)) is not int or release[key] <= 0:
                errors.append(f'{sid}: {key} 无效')
        if release.get('verified_download_sha256') != release.get('sha256'):
            errors.append(f'{sid}: 缺少登录下载校验证据')
    return errors


def render(data):
    entries = data['entries']
    count = sum(e['status'] == 'private' for e in entries)
    lines = ['# 中文 PDF 目录与访问范围', '',
             '<!-- 由 python3 scripts/pdf_releases.py index 生成，请维护 PDF目录.json。 -->', '',
             f'截至{data["updated"]}，盘点{len(entries)}篇中文PDF，{count}篇已私有备份，其余逐篇记录。公开仓库不再托管PDF；原有9篇公开附件已撤下，许可判断保留。', '',
             '原文和中文PDF统一由独立私有附件仓库维护，需有权账号登录。公开克隆、Fork与PR不附带这些文件或访问权限。', '',
             '访问方法见[PDF私有维护流程](../文档/工具/中文PDF发布.md)：在私有克隆运行`python3 download.py --kind translation`；原文用`--kind original`，不带类型则获取全部。私有目录是附件版本、哈希和登录下载校验记录的唯一完整账本。', '',
             '本表只保留中文PDF盘点、许可依据、范围及备份摘要，不承诺公开下载。原文公开入口仍可使用；私有备份不新增公开分发或翻译授权。正式Markdown译文继续按[共享规则](../LICENSE)逐篇核实后公开。', '',
             '| 论文 / 稳定 ID | 中文PDF存储 / 版本 | 许可与核实 | 翻译范围及处理结果 |', '|---|---|---|---|']
    for e in entries:
        sid, rights, copy = e['source_id'], e['rights'], e.get('private_copy')
        title = e['title'].replace('|', '、')
        pdf = (f'私有，需登录 · {copy["translation_version"]} · {copy["pages"]}页' if copy else
               '仅本地，未纳入私有库' if e['status'] == 'local-only' else '处理失败')
        license = rights.get('license_id') or rights['decision']
        evidence = f'[{license}]({rights["evidence_url"]})' if rights.get('evidence_url') else license
        result = f'{e["scope"]}；{e["reason"]}'.replace('|', '、').replace('\n', ' ')
        lines.append(f'| [{title}]({e["original_url"]}) · `{sid}` | {pdf} | {evidence} | {result} |')
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
        print(f'PASS: {len(data["entries"])} 篇 PDF 登记；私有策略/许可声明/版本/目录一致。离线检查不证明远端资产可用。')
        return 0
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print(f'FAIL: {exc}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

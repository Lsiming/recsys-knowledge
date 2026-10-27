#!/usr/bin/env python3
"""Download licensed Chinese PDFs from the pinned GitHub Releases registry."""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import tempfile
import urllib.error
import urllib.request

from pdf_releases import ROOT, check, load


def verify(path, release):
    if not path.is_file() or path.stat().st_size != release['size_bytes']:
        return False
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        if stream.read(5) != b'%PDF-':
            return False
        stream.seek(0)
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest() == release['sha256']


def download(entry, dest, verify_only=False):
    release = entry['release']
    folder = dest / entry['source_id']
    path = folder / release['asset_name']
    if verify(path, release):
        return '已有文件校验通过', path
    if verify_only:
        raise ValueError('文件缺失或大小/哈希不符')
    folder.mkdir(parents=True, exist_ok=True)
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=folder, suffix='.part', delete=False) as output:
            tmp_path = Path(output.name)
            req = urllib.request.Request(release['url'], headers={'User-Agent': 'recsys-knowledge-pdf/1.0'})
            with urllib.request.urlopen(req, timeout=60) as response:
                size = 0
                for chunk in iter(lambda: response.read(1024 * 1024), b''):
                    size += len(chunk)
                    if size > release['size_bytes']:
                        raise ValueError('远端文件超过登记大小')
                    output.write(chunk)
        if not verify(tmp_path, release):
            raise ValueError('PDF 类型、大小或 SHA256 校验失败')
        os.replace(tmp_path, path)
        return '下载并校验通过', path
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', action='append', help='只下载指定来源，可重复指定')
    parser.add_argument('--dest', type=Path, default=ROOT / '.local/translations')
    parser.add_argument('--verify-only', action='store_true', help='只核对本地 PDF，不联网')
    parser.add_argument('--list', action='store_true', help='列出已许可并发布的 PDF，不联网')
    args = parser.parse_args(argv)
    try:
        data = load()
        errors = check(data)
        if errors:
            raise ValueError('; '.join(errors))
        published = {e['source_id']: e for e in data['entries'] if e['status'] == 'published'}
        requested = set(args.source or published)
        missing = requested - published.keys()
        if missing:
            raise ValueError('未许可/未发布或未知来源：' + ', '.join(sorted(missing)))
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print(f'FAIL: {exc}')
        return 1
    failures = 0
    for sid in sorted(requested):
        e = published[sid]
        if args.list:
            print(f'{sid}\t{e["release"]["translation_version"]}\t{e["rights"]["license_id"]}\t{e["release"]["url"]}')
            continue
        try:
            message, path = download(e, args.dest, args.verify_only)
            print(f'PASS {sid}: {message} → {path}')
        except (OSError, ValueError, urllib.error.URLError) as exc:
            failures += 1
            print(f'FAIL {sid}: {exc}')
    print(f'{len(requested)} 篇公开 PDF；失败 {failures} 篇。')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())

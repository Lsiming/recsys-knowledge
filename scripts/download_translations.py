#!/usr/bin/env python3
"""旧下载入口：列公开盘点，或转交本机私有附件库；不从公开Releases下载PDF。"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

from pdf_releases import ROOT, PRIVATE_REPOSITORY, check, load


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', action='append', help='指定中文PDF来源，可重复指定')
    parser.add_argument('--attachments-root', type=Path, default=ROOT / '.local/attachments', help='已克隆的私有附件库目录')
    parser.add_argument('--dest', type=Path)
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--list', action='store_true', help='离线列出公开盘点及访问范围')
    args = parser.parse_args(argv)
    try:
        data = load()
        errors = check(data)
        if errors:
            raise ValueError('; '.join(errors))
        entries = {e['source_id']: e for e in data['entries']}
        selected = set(args.source or entries)
        if selected - entries.keys():
            raise ValueError('未知来源：' + ', '.join(sorted(selected - entries.keys())))
        if args.list:
            for sid in sorted(selected):
                print(f'{sid}\t{entries[sid]["status"]}\t{entries[sid]["title"]}')
            print('PDF统一私有维护，公开克隆不附带附件或访问权限。')
            return 0
        unavailable = [sid for sid in selected if entries[sid]['status'] != 'private']
        if args.source and unavailable:
            raise ValueError('未纳入私有备份：' + ', '.join(sorted(unavailable)))
        private_script = args.attachments_root.resolve() / 'download.py'
        if not private_script.is_file():
            print('PDF已改为私有维护。请用有权账号执行：')
            print('gh auth login')
            print(f'gh repo clone {PRIVATE_REPOSITORY}')
            print('cd recsys-knowledge-attachments')
            print('python3 download.py --kind translation')
            print('已有克隆可传 --attachments-root；原文PDF在私有库用 --kind original 获取。')
            return 1
        command = [sys.executable, str(private_script), '--kind', 'translation']
        for sid in sorted(selected):
            if entries[sid]['status'] == 'private':
                command += ['--source', sid]
        if args.dest:
            command += ['--dest', str(args.dest.resolve())]
        if args.verify_only:
            command += ['--verify-only']
        return subprocess.run(command).returncode
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print(f'FAIL: {exc}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

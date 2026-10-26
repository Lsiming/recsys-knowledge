#!/usr/bin/env python3
"""Check public files and full reachable Git history without printing matched secrets."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
NOREPLY = re.compile(r'(?:[0-9]+\+)?[A-Za-z0-9-]+@users\.noreply\.github\.com\Z', re.I)
PATTERNS = {
    '凭证候选': re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    '本机用户绝对路径': re.compile(r'/(?:Users|home)/[^/\s`"<>]+/'),
    '内网地址': re.compile(r'(?<![\d.])(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?![\d.])'),
}
EMAIL = re.compile(r'(?<![\w.])[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PRIVATE_DIRS = {'.local', '.obsidian', '.venv', 'venv', '.worktrees', 'node_modules', 'data',
                'datasets', 'papers', 'outputs', 'artifacts', 'checkpoints', 'models', 'logs', 'tmp', 'cache'}
ATTACHMENTS = {'.pdf', '.tex', '.bib', '.bbl', '.bst', '.cls', '.sty', '.aux', '.gz', '.zip', '.tgz',
               '.log', '.pem', '.key', '.pt', '.pth', '.ckpt', '.safetensors', '.parquet', '.pkl', '.pickle', '.onnx'}


def findings(text):
    result = [label for label, pattern in PATTERNS.items() if pattern.search(text)]
    if any(not NOREPLY.fullmatch(email) for email in EMAIL.findall(text)):
        result.append('非 GitHub noreply 邮箱')
    return result


def private_path(name):
    p = Path(name)
    return bool(p.parts and (p.parts[0] in PRIVATE_DIRS or p.suffix.lower() in ATTACHMENTS
                or p.name == '.env' or (p.name.startswith('.env.') and p.name != '.env.example')))


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.PIPE)


def check_history(root, ref='HEAD'):
    errors = set()
    if git(root, 'rev-parse', '--is-shallow-repository').strip() == b'true':
        return ['浅克隆无法审查完整历史；请补齐历史或在 CI 使用 fetch-depth: 0'], 0, 0
    commits = git(root, 'log', ref, '--format=%H%x00%an%x00%ae%x00%cn%x00%ce').decode().splitlines()
    for line in commits:
        oid, author, author_email, committer, committer_email = line.split('\0')
        for role, name, email in [('作者', author, author_email), ('提交者', committer, committer_email)]:
            if not NOREPLY.fullmatch(email) or findings(name):
                errors.add(f'{oid[:12]}: {role}应使用 GitHub 账号身份和 noreply 邮箱')
        message = git(root, 'show', '-s', '--format=%B', oid).decode(errors='replace')
        for label in findings(message):
            errors.add(f'{oid[:12]}: 提交说明含{label}')
    rows = git(root, 'rev-list', '--objects', ref).decode().splitlines()
    blobs = 0
    process = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=root,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for row in rows:
            oid, _, name = row.partition(' ')
            process.stdin.write((oid + '\n').encode())
            process.stdin.flush()
            header = process.stdout.readline().split()
            size = int(header[2])
            data = process.stdout.read(size)
            process.stdout.read(1)
            if header[1] != b'blob':
                continue
            blobs += 1
            label_path = name or oid[:12]
            if private_path(name):
                errors.add(f'{label_path}: 历史含本地附件/环境文件')
            for label in findings(data.decode(errors='replace')):
                errors.add(f'{label_path}: 历史内容含{label}')
    finally:
        process.stdin.close()
        process.wait()
        process.stdout.close()
        process.stderr.close()
    return sorted(errors), len(commits), blobs


def check_files(root):
    errors = []
    names = git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').decode().split('\0')
    for name in filter(None, names):
        if private_path(name):
            errors.append(f'{name}: 本地附件/环境文件不应分发')
        p = root / name
        if p.is_file():
            for label in findings(p.read_text(encoding='utf-8', errors='replace')):
                errors.append(f'{name}: 当前文件含{label}')
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref', default='HEAD', help='实际待发布的本地 ref 或提交')
    args = parser.parse_args(argv)
    try:
        errors = check_files(ROOT)
        history_errors, commits, blobs = check_history(ROOT, args.ref)
        errors += history_errors
    except (OSError, ValueError, subprocess.CalledProcessError):
        print('FAIL: 无法完成公开历史检查；请确认 Git 状态、历史与 ref。')
        return 1
    if errors:
        print('FAIL\n' + '\n'.join('- ' + e for e in sorted(set(errors))))
        return 1
    print(f'PASS: 当前分发文件及完整历史（{commits}个提交、{blobs}个文件对象）的身份/凭证/路径/地址/附件检查通过。')
    print('范围：规则扫描不能证明不存在未知隐私或非公开业务文字，仍须人工核实资料来源。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

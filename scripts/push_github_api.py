#!/usr/bin/env python3
"""Publish existing linear Git commits through GitHub's Git Database API."""
from __future__ import annotations

import argparse
import base64
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args, root=ROOT):
    return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.PIPE)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def api(repo, endpoint, data=None, method=None):
    command = ['gh', 'api', '--hostname', 'github.com', '--method',
               method or ('POST' if data is not None else 'GET'),
               f'repos/{repo}{endpoint}']
    if data is not None:
        command += ['--input', '-']
    result = subprocess.run(command, input=json.dumps(data).encode() if data is not None else None,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    require(result.returncode == 0, f'GitHub API失败：{endpoint}；请核对认证、网络及远端ref后重试。')
    return json.loads(result.stdout)


def identity(raw):
    match = re.fullmatch(r'(.*) <([^<>]+)> (\d+) ([+-]\d{4})', raw)
    require(match is not None, '提交身份格式不支持；未更新ref。')
    name, email, stamp, zone = match.groups()
    require(email.endswith('@users.noreply.github.com'), '提交身份须使用GitHub noreply邮箱。')
    minutes = (int(zone[1:3]) * 60 + int(zone[3:])) * (1 if zone[0] == '+' else -1)
    tz = datetime.timezone(datetime.timedelta(minutes=minutes))
    return {'name': name, 'email': email,
            'date': datetime.datetime.fromtimestamp(int(stamp), tz).isoformat()}


def prepare(base, head, root=ROOT):
    require(subprocess.run(['git', 'merge-base', '--is-ancestor', base, head], cwd=root,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0,
            '远端基线必须已在本地且为HEAD祖先；先保留工作并整合远端，禁止强推。')
    commits = []
    for oid in git('rev-list', '--reverse', f'{base}..{head}', root=root).decode().splitlines():
        raw = git('cat-file', 'commit', oid, root=root).decode('utf-8')
        headers, _, message = raw.partition('\n\n')
        fields = {}
        for line in headers.splitlines():
            key, _, value = line.partition(' ')
            require(key in {'tree', 'parent', 'author', 'committer'} and key not in fields,
                    '仅支持普通单父提交；合并、签名或额外头字段须单独处理，未上传。')
            fields[key] = value
        require(set(fields) == {'tree', 'parent', 'author', 'committer'}, '提交头字段不完整。')
        payload = {'message': message, 'tree': fields['tree'], 'parents': [fields['parent']],
                   'author': identity(fields['author']), 'committer': identity(fields['committer'])}
        paths = list(filter(None, git('diff', '--name-only', '--no-renames', '-z',
                                     fields['parent'], oid, root=root).decode().split('\0')))
        entries = []
        for path in paths:
            require(not path.startswith(('.local/', '.obsidian/')), '不得上传本地附件或个人配置。')
            row = git('ls-tree', '-z', oid, '--', path, root=root).decode().rstrip('\0')
            if not row:
                entries.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': None})
                continue
            info, _, actual_path = row.partition('\t')
            mode, kind, blob = info.split()
            require(actual_path == path and kind == 'blob' and mode in {'100644', '100755'},
                    '仅支持普通文件/可执行文件；子模块和符号链接须单独处理。')
            entries.append({'path': path, 'mode': mode, 'type': kind, 'sha': blob})
        commits.append({'sha': oid, 'payload': payload, 'entries': entries,
                        'base_tree': git('rev-parse', fields['parent'] + '^{tree}', root=root).decode().strip()})
    return commits


def check_local(head, branch, root=ROOT):
    require(git('branch', '--show-current', root=root).decode().strip() == branch,
            '当前本地分支须与目标分支相同；不自动切分支。')
    require(git('rev-parse', 'HEAD', root=root).decode().strip() == head, 'HEAD已变化；重新审查发布范围。')
    require(not git('diff', '--cached', '--name-only', root=root).strip(), '暂存区须为空；先完成明确范围的本地提交。')


def publish(repo, branch, base, head, commits, root=ROOT):
    ref = '/git/ref/heads/' + branch
    check_local(head, branch, root=root)
    tracking = 'refs/remotes/origin/' + branch
    previous = git('rev-parse', '--verify', tracking, root=root).decode().strip()
    require(api(repo, ref)['object']['sha'] == base, '远端已变化；未上传，重新读取并整合远端。')
    uploaded = set()
    for commit in commits:
        for entry in commit['entries']:
            blob = entry['sha']
            if blob is None or blob in uploaded:
                continue
            data = git('cat-file', 'blob', blob, root=root)
            result = api(repo, '/git/blobs', {'content': base64.b64encode(data).decode(), 'encoding': 'base64'})
            require(result['sha'] == blob, 'blob SHA不一致；未更新ref。')
            uploaded.add(blob)
        if commit['entries']:
            tree = api(repo, '/git/trees', {'base_tree': commit['base_tree'], 'tree': commit['entries']})
            require(tree['sha'] == commit['payload']['tree'], 'tree SHA不一致；未更新ref。')
        result = api(repo, '/git/commits', commit['payload'])
        require(result['sha'] == commit['sha'], 'commit SHA不一致；未更新ref。')
        print('已核验提交对象：', commit['sha'], flush=True)
    check_local(head, branch, root=root)
    require(api(repo, ref)['object']['sha'] == base, '上传期间远端已变化；对象已上传，未更新ref。')
    result = api(repo, '/git/refs/heads/' + branch, {'sha': head, 'force': False}, method='PATCH')
    require(result['object']['sha'] == head and api(repo, ref)['object']['sha'] == head,
            '远端更新结果需重新核实；不要强推或回退。')
    git('update-ref', tracking, head, previous, root=root)
    print('本地分支、origin跟踪ref与GitHub目标ref一致：', head)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, help='GitHub owner/repo，与origin对应')
    parser.add_argument('--branch', default='main')
    parser.add_argument('--base', required=True, help='经API读取并已审查的远端完整SHA')
    parser.add_argument('--publish', action='store_true', help='执行已获用户授权的发布；默认只预览')
    args = parser.parse_args(argv)
    try:
        require(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', args.repo), 'repo格式不正确。')
        require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]*', args.branch)
                and not args.branch.startswith('archive/'), '禁止发布归档分支或无效分支名。')
        git('check-ref-format', 'refs/heads/' + args.branch)
        require(re.fullmatch(r'[0-9a-f]{40}', args.base), 'base须为完整40位SHA。')
        origin = git('remote', 'get-url', 'origin').decode().strip()
        ssh_origin = 'git' + '@' + f'github.com:{args.repo}.git'
        require(origin in {f'https://github.com/{args.repo}.git', f'https://github.com/{args.repo}',
                           ssh_origin}, 'origin与指定GitHub仓库不一致。')
        head = git('rev-parse', 'HEAD').decode().strip()
        check_local(head, args.branch)
        require(git('rev-parse', '--abbrev-ref', '@{upstream}').decode().strip() == 'origin/' + args.branch,
                '当前分支须已跟踪origin的同名分支；首次建库/分支单独处理。')
        subprocess.run([sys.executable, str(ROOT / 'scripts/check_public.py'), '--ref', head],
                       cwd=ROOT, check=True)
        remote = api(args.repo, '/git/ref/heads/' + args.branch)['object']['sha']
        require(remote == args.base, '远端与base不一致；重新读取并审查，不自动改写基线。')
        commits = prepare(args.base, head)
        print(f'目标：{args.repo}:{args.branch}；{args.base} → {head}；{len(commits)}个提交')
        for commit in commits:
            print(commit['sha'], ', '.join(e['path'] for e in commit['entries']))
        if args.publish and commits:
            publish(args.repo, args.branch, args.base, head, commits)
        elif not args.publish:
            print('只读预览；已有发布授权并审查范围后使用同参数加--publish。')
        else:
            print('目标已一致，无需上传。')
        return 0
    except ValueError as exc:
        print('FAIL:', str(exc), file=sys.stderr)
        return 1
    except (OSError, KeyError, subprocess.SubprocessError):
        # Avoid emitting command payloads or authentication output in exceptions.
        print('FAIL: 发布未完成。核对origin/upstream、完整基线SHA、提交结构、公开检查及API认证/网络；'
              'API超时后先读取远端ref判断是否已生效。详情按GitHub共建流程处理。', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

"""Exercise publication integrity and refusal paths without network access."""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('push_github_api', Path(__file__).resolve().parents[1] / 'scripts/push_github_api.py')
push = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(push)


class ApiPushTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@users.noreply.github.com')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('config', 'core.autocrlf', 'false')
        (self.root / '删除.md').write_text('old\n')
        self.git('add', '删除.md')
        self.git('commit', '-qm', '基线')
        self.base = self.git('rev-parse', 'HEAD').decode().strip()
        self.git('update-ref', 'refs/remotes/origin/main', self.base)
        self.git('rm', '-q', '删除.md')
        (self.root / '二进制.bin').write_bytes(b'\x00\xff\n')
        (self.root / '中文.md').write_text('中文内容\n')
        self.git('add', '二进制.bin', '中文.md')
        self.git('commit', '-qm', '新增并删除文件')
        self.head = self.git('rev-parse', 'HEAD').decode().strip()
        self.commits = push.prepare(self.base, self.head, root=self.root)
        self.calls = []
        self.remote = self.base

    def git(self, *args, data=None):
        return subprocess.check_output(['git', '-C', str(self.root), *args], input=data, stderr=subprocess.PIPE)

    def fake_api(self, repo, endpoint, data=None, method=None):
        self.calls.append((endpoint, data, method))
        if endpoint == '/git/refs/heads/main':
            self.assertEqual(method, 'PATCH')
            self.assertIs(data['force'], False)
            self.remote = data['sha']
            return {'object': {'sha': self.remote}}
        if endpoint == '/git/ref/heads/main':
            return {'object': {'sha': self.remote}}
        if endpoint == '/git/blobs':
            import base64
            blob = self.git('hash-object', '--stdin', data=base64.b64decode(data['content'])).decode().strip()
            return {'sha': blob}
        if endpoint == '/git/trees':
            # Read the real final tree to verify that the requested changes reconstruct it.
            expected = self.commits[0]
            self.assertEqual(data['base_tree'], expected['base_tree'])
            paths = {e['path'] for e in data['tree']}
            self.assertEqual(paths, {'删除.md', '二进制.bin', '中文.md'})
            self.assertIsNone(next(e['sha'] for e in data['tree'] if e['path'] == '删除.md'))
            return {'sha': expected['payload']['tree']}
        if endpoint == '/git/commits':
            # Rebuild commit bytes from the API payload and compare Git's actual hash.
            import datetime
            def raw_identity(person):
                date = datetime.datetime.fromisoformat(person['date'])
                return f"{person['name']} <{person['email']}> {int(date.timestamp())} {date.strftime('%z')}"
            raw = (f"tree {data['tree']}\nparent {data['parents'][0]}\n"
                   f"author {raw_identity(data['author'])}\ncommitter {raw_identity(data['committer'])}\n\n"
                   + data['message']).encode()
            return {'sha': self.git('hash-object', '-t', 'commit', '--stdin', data=raw).decode().strip()}
        self.fail('Unexpected API endpoint')

    def publish(self, api):
        with patch.object(push, 'api', side_effect=api), patch('builtins.print'):
            push.publish('owner/repo', 'main', self.base, self.head, self.commits, root=self.root)

    def test_exact_commit_and_uncommitted_work_preserved(self):
        (self.root / '中文.md').write_text('未提交的用户改动\n')
        self.publish(self.fake_api)
        self.assertEqual(self.remote, self.head)
        self.assertEqual(self.git('rev-parse', 'origin/main').decode().strip(), self.head)
        self.assertEqual((self.root / '中文.md').read_text(), '未提交的用户改动\n')
        self.assertFalse(self.git('diff', '--cached', '--name-only').strip())

    def test_mismatched_blob_never_updates_ref(self):
        def api(repo, endpoint, data=None, method=None):
            result = self.fake_api(repo, endpoint, data, method)
            return {'sha': '0' * 40} if endpoint == '/git/blobs' else result
        with self.assertRaisesRegex(ValueError, 'blob SHA'):
            self.publish(api)
        self.assertEqual(self.remote, self.base)
        self.assertFalse(any(method == 'PATCH' for _, _, method in self.calls))

    def test_remote_changes_during_upload_never_updates_ref(self):
        def api(repo, endpoint, data=None, method=None):
            if endpoint == '/git/commits':
                self.remote = '1' * 40
            return self.fake_api(repo, endpoint, data, method)
        with self.assertRaisesRegex(ValueError, '远端已变化'):
            self.publish(api)
        self.assertFalse(any(method == 'PATCH' for _, _, method in self.calls))

    def test_merge_refused_before_upload(self):
        self.git('checkout', '-qb', 'side', self.base)
        (self.root / 'side.md').write_text('side\n')
        self.git('add', 'side.md')
        self.git('commit', '-qm', 'side')
        self.git('checkout', '-q', 'main')
        self.git('merge', '--no-ff', '-qm', 'merge', 'side')
        with self.assertRaisesRegex(ValueError, '单父提交'):
            push.prepare(self.base, 'HEAD', root=self.root)


if __name__ == '__main__':
    unittest.main()

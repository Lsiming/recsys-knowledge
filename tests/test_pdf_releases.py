"""Private PDF policy, version binding and the offline public download entry."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import pdf_releases as registry
import download_translations as downloader
import prepare_pdf_release as retired


class PDFReleases(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.entry = dict(source_id='SRC-TEST', title='Example', original_url='https://example.org/paper',
                          revision='v1', scope='Body', reason='Personal private backup', status='private', input_sha256='a'*64,
                          rights=dict(decision='not-permitted', notes='No public permission', checked_on='2026-10-27'),
                          private_copy=dict(repository=registry.PRIVATE_REPOSITORY, visibility='private',
                                            tag='private-zh-pdfs-20261027', asset_name='SRC-TEST.zh-CN.private.20261027.1.pdf',
                                            translation_version='20261027.1', sha256='b'*64,
                                            verified_download_sha256='b'*64, size_bytes=32, pages=2))
        self.data = dict(schema_version=2, repository=registry.REPOSITORY, storage_policy='private-only',
                         attachment_repository=registry.PRIVATE_REPOSITORY, updated='2026-10-27', entries=[self.entry])

    def test_private_storage_does_not_invent_public_permission_or_require_originals(self):
        self.assertEqual(registry.check(self.data, self.root), [])
        for decision in ['not-permitted', 'unverified']:
            self.entry['rights']['decision'] = decision
            self.assertEqual(registry.check(self.data, self.root), [])
        content = registry.render(self.data)
        self.assertNotIn('/releases/download/', content)
        self.assertIn('需登录', content)

    def test_rejects_public_status_assets_and_visibility(self):
        for changes in [dict(status='published'), dict(release={}), dict(status='public')]:
            data = deepcopy(self.data);data['entries'][0].update(changes)
            self.assertTrue(registry.check(data, self.root))
        for changes in [dict(visibility='public'), dict(repository=registry.REPOSITORY), dict(url='https://example.org/a.pdf')]:
            data = deepcopy(self.data);data['entries'][0]['private_copy'].update(changes)
            self.assertTrue(registry.check(data, self.root))
        self.data['storage_policy'] = 'public'
        self.assertTrue(registry.check(self.data, self.root))

    def test_local_only_cannot_claim_backup(self):
        self.entry['status'] = 'local-only'
        self.assertTrue(registry.check(self.data, self.root))
        del self.entry['private_copy']
        self.assertEqual(registry.check(self.data, self.root), [])

    def test_rejects_path_escape_and_unverified_download(self):
        for changes in [dict(asset_name='../bad.pdf'), dict(tag='../../escape'),
                        dict(tag='zh-pdfs-20261027'), dict(verified_download_sha256='0'*64)]:
            data = deepcopy(self.data);data['entries'][0]['private_copy'].update(changes)
            self.assertTrue(registry.check(data, self.root))

    def test_source_version_and_embedded_license_bind_to_original(self):
        folder = self.root/'来源/SRC-TEST';folder.mkdir(parents=True)
        record = dict(current='fp', versions=[dict(fingerprint='fp', locator=self.entry['original_url'],
                                                  revision='v2', artifacts=[dict(sha256='d'*64)])])
        path = folder/'来源.json';path.write_text(json.dumps(record))
        self.assertTrue(any('版本' in e for e in registry.check(self.data, self.root)))
        record['versions'][0]['revision']='v1';path.write_text(json.dumps(record))
        self.entry['rights']['original_pdf_sha256']='c'*64
        self.assertTrue(any('原件' in e for e in registry.check(self.data, self.root)))
        self.entry['rights']['original_pdf_sha256']='d'*64
        self.assertEqual(registry.check(self.data, self.root), [])

    def test_list_is_offline_and_missing_private_clone_fails_with_instructions(self):
        with patch.object(downloader, 'load', return_value=self.data), patch.object(downloader, 'check', return_value=[]), \
             patch.object(subprocess, 'run', side_effect=AssertionError('must be offline')), patch('builtins.print'):
            self.assertEqual(downloader.main(['--list']), 0)
            self.assertEqual(downloader.main(['--attachments-root', str(self.root)]), 1)

    def test_delegate_only_selected_private_translation_to_explicit_clone(self):
        script=self.root/'download.py';script.write_text('# local private tool')
        with patch.object(downloader, 'load', return_value=self.data), patch.object(downloader, 'check', return_value=[]), \
             patch.object(subprocess, 'run', return_value=subprocess.CompletedProcess([], 7)) as run:
            self.assertEqual(downloader.main(['--attachments-root', str(self.root), '--source', 'SRC-TEST', '--verify-only']), 7)
            command = run.call_args.args[0]
            self.assertEqual(command[:4], [sys.executable, str(script.resolve()), '--kind', 'translation'])
            self.assertIn('--verify-only', command)
            self.assertIn('SRC-TEST', command)

    def test_old_prepare_command_cannot_generate_public_asset(self):
        with patch('builtins.print'):
            self.assertEqual(retired.main([]), 1)


if __name__ == '__main__':
    unittest.main()

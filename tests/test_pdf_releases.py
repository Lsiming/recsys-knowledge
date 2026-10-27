"""Release permission gates and atomic, verified PDF downloads."""
from copy import deepcopy
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import pdf_releases as registry
import download_translations as downloader

PDF = b'%PDF-1.7\nexample test bytes\n%%EOF\n'


class PDFReleases(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        tag, name = 'zh-pdfs-20261027', 'SRC-TEST.zh-CN.20261027.1.pdf'
        digest = hashlib.sha256(PDF).hexdigest()
        self.entry = dict(source_id='SRC-TEST', title='Example', original_url='https://example.org/paper',
                          revision='v1', scope='Body', reason='Licensed', status='published', input_sha256='a'*64,
                          rights=dict(decision='allowed', notes='Confirmed on original', checked_on='2026-10-27',
                                      license_id='CC-BY-4.0', license_url=registry.LICENSES['CC-BY-4.0'],
                                      authors=['Author'], evidence_url='https://example.org/paper', evidence_sha256='b'*64),
                          release=dict(tag=tag, asset_name=name, translation_version='20261027.1',
                                       url=registry.asset_url(tag, name), sha256=digest,
                                       verified_download_sha256=digest, size_bytes=len(PDF), pages=2,
                                       translator='Translator', changes='Chinese', qa='Rendered'))
        self.data = dict(schema_version=1, repository=registry.REPOSITORY, updated='2026-10-27', entries=[self.entry])

    def test_registry_is_offline_and_accepts_licensed_assets_without_originals(self):
        self.assertEqual(registry.check(self.data, self.root), [])
        self.assertIn(self.entry['release']['url'], registry.render(self.data))

    def test_nd_unknown_and_unverified_permission_cannot_be_published(self):
        for changes in [dict(license_id='CC-BY-NC-ND-4.0'), dict(license_id=None, license_url=None),
                        dict(decision='unverified')]:
            with self.subTest(changes=changes):
                data = deepcopy(self.data)
                data['entries'][0]['rights'].update(changes)
                self.assertTrue(registry.check(data, self.root))

    def test_local_only_entry_must_not_expose_release(self):
        self.entry['status'] = 'local-only'
        self.assertTrue(registry.check(self.data, self.root))
        del self.entry['release']
        self.assertEqual(registry.check(self.data, self.root), [])

    def test_path_escape_foreign_urls_missing_download_verification_rejected(self):
        for changes in [dict(asset_name='../bad.pdf'), dict(tag='../../escape'),
                        dict(url='https://example.org/file.pdf'), dict(verified_download_sha256='0'*64)]:
            with self.subTest(changes=changes):
                data = deepcopy(self.data)
                data['entries'][0]['release'].update(changes)
                self.assertTrue(registry.check(data, self.root))

    def test_source_version_drift_reopens_pdf_review(self):
        folder = self.root / '来源/SRC-TEST'
        folder.mkdir(parents=True)
        (folder/'来源.json').write_text(json.dumps(dict(current='fp', versions=[dict(
            fingerprint='fp', locator=self.entry['original_url'], revision='v2')])))
        self.assertTrue(any('版本' in e for e in registry.check(self.data, self.root)))

    def test_embedded_license_evidence_must_match_registered_original(self):
        folder = self.root / '来源/SRC-TEST'
        folder.mkdir(parents=True)
        self.entry['rights']['original_pdf_sha256'] = 'c'*64
        record = dict(current='fp', versions=[dict(
            fingerprint='fp', locator=self.entry['original_url'], revision=self.entry['revision'],
            artifacts=[dict(sha256='d'*64)])])
        (folder/'来源.json').write_text(json.dumps(record))
        self.assertTrue(any('原件' in e for e in registry.check(self.data, self.root)))
        self.entry['rights']['original_pdf_sha256'] = 'd'*64
        self.assertEqual(registry.check(self.data, self.root), [])

    def test_download_verifies_then_skips_existing_file_without_network(self):
        with patch.object(downloader.urllib.request, 'urlopen', return_value=BytesIO(PDF)) as request:
            message, path = downloader.download(self.entry, self.root)
            self.assertTrue(downloader.verify(path, self.entry['release']))
            self.assertEqual(request.call_count, 1)
        with patch.object(downloader.urllib.request, 'urlopen', side_effect=AssertionError('must be offline')):
            downloader.download(self.entry, self.root)
            downloader.download(self.entry, self.root, verify_only=True)

    def test_corrupt_response_never_overwrites_an_existing_file(self):
        release = self.entry['release']
        path = self.root / 'SRC-TEST' / release['asset_name']
        path.parent.mkdir()
        path.write_bytes(b'keep existing bytes')
        for content in [b'X'*len(PDF), PDF+b'oversize']:
            with patch.object(downloader.urllib.request, 'urlopen', return_value=BytesIO(content)):
                with self.assertRaises(ValueError):
                    downloader.download(self.entry, self.root)
            self.assertEqual(path.read_bytes(), b'keep existing bytes')
            self.assertEqual(list(path.parent.glob('*.part')), [])

    def test_verify_only_never_fetches_missing_file(self):
        with patch.object(downloader.urllib.request, 'urlopen', side_effect=AssertionError('must be offline')):
            with self.assertRaises(ValueError):
                downloader.download(self.entry, self.root, verify_only=True)


if __name__ == '__main__':
    unittest.main()

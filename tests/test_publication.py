"""Public clones must work without attachments and reject accidental private uploads."""
from contextlib import redirect_stdout
from io import StringIO
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


context = module('check_context')
translations = module('translations')


class PublicLinks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_optional_attachment_is_text_and_real_links_remain_checked(self):
        p = self.root / 'README.md'
        p.write_text('本地附件：`.local/paper.pdf`\n[原文](https://arxiv.org/pdf/1234.5678v1#page=2)\n[知识](知识.md)\n')
        (self.root / '知识.md').write_text('# 知识')
        self.assertEqual(context.check_markdown(self.root, 'README.md', {'README.md', '知识.md'})[0], [])
        (self.root / '知识.md').unlink()
        self.assertTrue(any('不存在' in e for e in context.check_markdown(self.root, 'README.md')[0]))

    def test_local_attachment_link_fails_even_when_it_exists(self):
        (self.root / '.local').mkdir()
        (self.root / '.local/paper.pdf').write_bytes(b'local')
        (self.root / 'README.md').write_text('[附件](.local/paper.pdf#page=2)')
        self.assertTrue(any('本地附件' in e for e in context.check_markdown(self.root, 'README.md')[0]))

    def test_unshared_target_space_paths_and_escape_are_detected(self):
        (self.root / 'space name.md').write_text('# Shared')
        p = self.root / 'README.md'
        p.write_text('[有空格](<space name.md>)\n[越界](../outside.md)')
        errors, count = context.check_markdown(self.root, 'README.md', {'README.md'})
        self.assertEqual(count, 2)
        self.assertTrue(any('未纳入 Git' in e for e in errors))
        self.assertTrue(any('超出仓库' in e for e in errors))
        p.write_text('[有空格](space%20name.md)')
        self.assertEqual(context.check_markdown(self.root, 'README.md', {'README.md', 'space name.md'})[0], [])

    def test_adding_a_remote_does_not_break_an_attachment_free_clone(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', '-C', str(self.root), 'remote', 'add', 'origin', 'https://example.org/repo.git'], check=True)
        (self.root / 'README.md').write_text('# Public clone')
        with patch.object(context, 'ROOT', self.root), patch.object(context, 'REQUIRED', ()), redirect_stdout(StringIO()):
            self.assertEqual(context.main(), 0)

    def test_force_added_attachments_and_secrets_are_rejected(self):
        for name in ['.local/paper.md', '.obsidian/workspace.json', 'paper.pdf', 'source.tex', '.env', '.env.production']:
            self.assertTrue(context.check_distribution({name}), name)
        self.assertEqual(context.check_distribution({'译文/SRC-A/中文译文.md', '.env.example', '图示/机制.png'}), [])


class TranslationPublication(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root / '来源/SRC-TEST/来源.json'
        source.parent.mkdir(parents=True)
        source.write_text(json.dumps({'kind': 'paper', 'current': 'v1', 'versions': [
            {'fingerprint': 'v1', 'locator': 'https://arxiv.org/abs/1234.5678v1', 'revision': 'v1'}]}))
        self.entry = dict(source_id='SRC-TEST', title='Example paper', original_url='https://arxiv.org/abs/1234.5678v1',
                          revision='v1', status='local-only', reason='待授权', checked_on='2026-10-26')
        (self.root / '译文').mkdir()
        self.refresh()

    def refresh(self):
        (self.root / '译文/目录.md').write_text(translations.render([self.entry]))

    def publish(self):
        self.entry.update(status='published', file='译文/SRC-TEST/中文译文.md', license_id='CC-BY-4.0',
                          license_url=translations.LICENSES['CC-BY-4.0'], authors=['Original Author'], translator='Translator',
                          scope='Body only', changes='Translated', evidence_url=self.entry['original_url'], evidence_sha256='a' * 64)
        self.path = self.root / self.entry['file']
        self.path.parent.mkdir()
        self.path.write_text('\n'.join([self.entry[k] for k in ['original_url', 'license_url', 'translator', 'scope', 'changes']]) +
                             '\nOriginal Author\n<!-- translation-body -->\nTranslated body')
        self.entry['sha256'] = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.refresh()

    def test_pending_entries_require_no_local_originals_or_translation(self):
        self.assertEqual(translations.check(self.root, [self.entry]), [])

    def test_published_translation_has_attribution_and_cannot_drift(self):
        self.publish()
        self.assertEqual(translations.check(self.root, [self.entry]), [])
        self.path.write_text(self.path.read_text().replace('Original Author', ''))
        errors = translations.check(self.root, [self.entry])
        self.assertTrue(any('哈希' in e for e in errors))
        self.assertTrue(any('署名' in e for e in errors))

    def test_nonexclusive_arxiv_license_is_not_public_translation_permission(self):
        self.publish()
        self.entry['license_url'] = 'https://arxiv.org/licenses/nonexclusive-distrib/1.0/'
        self.refresh()
        self.assertTrue(any('许可' in e for e in translations.check(self.root, [self.entry])))

    def test_source_version_change_reopens_permission_review(self):
        self.publish()
        self.entry['revision'] = 'v2'
        self.refresh()
        self.assertTrue(any('版本' in e for e in translations.check(self.root, [self.entry])))

    def test_unregistered_full_text_cannot_bypass_manifest(self):
        (self.root / '译文/extra.md').write_text('Undeclared full translation')
        self.assertTrue(any('未登记' in e for e in translations.check(self.root, [self.entry])))

public = module('check_public')


class PublicHistory(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.git('config', 'user.name', 'ExampleUser')
        self.git('config', 'user.email', '123+ExampleUser@users.noreply.github.com')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.PIPE)

    def commit(self, content):
        (self.root / 'note.md').write_text(content)
        self.git('add', 'note.md')
        self.git('commit', '-qm', '知识更新')

    def test_clean_history_and_noreply_identity_pass(self):
        self.commit('# Public paper analysis')
        self.assertEqual(public.check_history(self.root)[0], [])

    def test_private_email_in_git_identity_is_detected_without_echoing_it(self):
        email = 'person' + '@' + 'company.example'
        self.git('config', 'user.email', email)
        self.commit('# Content is public, identity is private')
        errors, _, _ = public.check_history(self.root)
        self.assertTrue(any('noreply' in e for e in errors))
        self.assertFalse(any(email in e for e in errors))

    def test_removing_sensitive_text_from_tip_does_not_hide_it_in_history(self):
        path = '/' + 'Users' + '/private-user/project/'
        self.commit('Personal machine: ' + path)
        self.commit('Generic machine: ~/project/')
        self.assertTrue(any('本机用户绝对路径' in e for e in public.check_history(self.root)[0]))

    def test_specific_ref_cannot_bypass_old_identity_history(self):
        self.commit('# Safe')
        safe = self.git('rev-parse', 'HEAD').decode().strip()
        self.git('config', 'user.email', 'person' + '@' + 'company.example')
        self.commit('# Another branch to publish')
        self.assertEqual(public.check_history(self.root, safe)[0], [])
        self.assertTrue(public.check_history(self.root)[0])

    def test_credentials_addresses_and_forced_attachments_are_caught(self):
        secret = 'ghp_' + 'a' * 36
        address = '.'.join(['10', '8', '1', '2'])
        self.assertIn('凭证候选', public.findings(secret))
        self.assertIn('内网地址', public.findings(address))
        self.commit('# Public')
        self.git('config', 'user.email', '123+ExampleUser@users.noreply.github.com')
        (self.root / 'paper.pdf').write_bytes(b'Attachment')
        self.git('add', 'paper.pdf')
        self.git('commit', '-qm', '误加附件')
        self.assertTrue(any('附件' in e for e in public.check_history(self.root)[0]))


if __name__ == '__main__':
    unittest.main()

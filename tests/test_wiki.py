"""Behavior checks for incremental evidence bookkeeping, isolated from real data."""
from contextlib import redirect_stdout
from io import StringIO
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("wiki", Path(__file__).parents[1] / "scripts/wiki.py")
wiki = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wiki)


class EvidenceLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="知识库验收-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ["SCHEMA.md", "维护/工作流.md", "scripts/wiki.py"]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(wiki.ROOT / name, target)
        self.source = self.root / "资料原件.txt"
        self.source.write_text("Original evidence", encoding="utf-8")
        self.register()
        self.note = self.root / "来源/SRC-TEST/阅读笔记.md"
        self.note.write_text("Reading scope and evidence location; " * 6, encoding="utf-8")
        self.page = self.root / "知识库/概念/证据测试.md"
        self.page.parent.mkdir(parents=True)
        self.make_page()

    def register(self, revision="v1"):
        self.run_cli("register", "--id", "SRC-TEST", "--title", "Test source", "--kind", "reference",
                     "--locator", "https://example.org/reference", "--revision", revision,
                     "--read-scope", "full text", "--file", str(self.source))

    def run_cli(self, *args):
        with redirect_stdout(StringIO()):
            result = wiki.main(["--root", str(self.root), *args])
        self.assertEqual(result, 0)

    def make_page(self, status="reviewed", fingerprint=None):
        fingerprint = fingerprint or wiki.records(self.root)["SRC-TEST"]["current"]
        meta = {"id": "evidence", "title": "Evidence page", "type": "concept", "status": status,
                "updated": "2026-10-25", "summary": "Source scope and conditions", "aliases": ["证据范围"],
                "sources": {"SRC-TEST": fingerprint}, "related": []}
        self.page.write_text("---\n" + "\n".join(k + ": " + json.dumps(v, ensure_ascii=False)
                             for k, v in meta.items()) + "\n---\nEvidence body.\n", encoding="utf-8")

    def integrate(self):
        self.run_cli("integrate", "SRC-TEST", "--pages", "知识库/概念/证据测试.md",
                     "--review-note", "Checked original evidence, scope and citation")
        self.run_cli("index")

    def test_full_cycle_skip_unchanged_source_and_retrieve_alias(self):
        self.assertTrue(wiki.pending(self.root))
        self.integrate()
        self.register()
        self.assertEqual(len(wiki.records(self.root)["SRC-TEST"]["versions"]), 1)
        self.assertEqual(wiki.pending(self.root), [])
        self.assertEqual(wiki.lint(self.root, local=True)[0], [])
        self.assertEqual(wiki.search(self.root, "证据范围", 3)[0]["title"], "Evidence page")

    def test_source_revision_preserves_history_and_invalidates_old_claims(self):
        self.integrate()
        old = wiki.records(self.root)["SRC-TEST"]["current"]
        self.source.write_text("Corrected evidence", encoding="utf-8")
        self.register("v2")
        record = wiki.records(self.root)["SRC-TEST"]
        self.assertEqual(len(record["versions"]), 2)
        self.assertNotEqual(record["current"], old)
        self.assertEqual(wiki.pending(self.root)[0]["affected"], ["evidence"])
        self.assertTrue(any("过时" in error for error in wiki.lint(self.root)[0]))
        with self.assertRaises(ValueError):
            wiki.integrate(self.root, type("Args", (), {"id": "SRC-TEST", "pages": ["知识库/概念/证据测试.md"]})())
        self.make_page()
        self.integrate()
        self.assertEqual(wiki.pending(self.root), [])

    def test_missing_output_reopens_ingestion(self):
        self.integrate()
        self.page.unlink()
        self.assertTrue(any("输出缺失" in s for s in wiki.pending(self.root)[0]["reasons"]))

    def test_rule_change_reopens_ingestion(self):
        self.integrate()
        schema = self.root / "SCHEMA.md"
        schema.write_text(schema.read_text().replace("处理语义版本：1", "处理语义版本：2"))
        self.assertIn("处理语义版本已变更", wiki.pending(self.root)[0]["reasons"])

    def test_navigation_edits_do_not_reopen_ingestion(self):
        self.integrate()
        for name in ["SCHEMA.md", "维护/工作流.md", "scripts/wiki.py"]:
            path = self.root / name
            path.write_text(path.read_text() + "\n# Navigation or formatting change\n")
        self.assertEqual(wiki.pending(self.root), [])

    def test_chinese_page_move_preserves_identity_receipt_and_backlinks(self):
        self.integrate()
        record = wiki.records(self.root)["SRC-TEST"]
        old_path = self.page.relative_to(self.root).as_posix()
        new_page = self.root / "知识库/问题/证据与适用条件.md"
        new_page.parent.mkdir(parents=True)
        self.page.rename(new_page)
        self.assertEqual(wiki.pending(self.root), [])
        self.run_cli("index")
        hit = wiki.search(self.root, "证据范围", 1)[0]
        self.assertEqual(hit["path"], "知识库/问题/证据与适用条件.md")
        self.assertEqual(wiki.records(self.root)["SRC-TEST"], record)
        self.assertIn("问题/证据与适用条件.md", (self.root / "知识库/知识地图.md").read_text())
        source_index = (self.root / "来源/来源目录.md").read_text()
        self.assertIn("../知识库/问题/证据与适用条件.md", source_index)
        self.assertNotIn(old_path, source_index)
        self.assertTrue((self.root / "来源/SRC-TEST/来源.json").is_file())
        self.assertTrue((self.root / "来源/SRC-TEST/阅读笔记.md").is_file())
        self.assertEqual(wiki.lint(self.root, local=True)[0], [])

    def test_notes_change_or_loss_reopens_ingestion(self):
        self.integrate()
        self.note.write_text(self.note.read_text() + "\nCorrection\n")
        self.assertIn("阅读笔记已变更", wiki.pending(self.root)[0]["reasons"])
        self.note.unlink()
        self.assertIn("阅读笔记已变更", wiki.pending(self.root)[0]["reasons"])

    def test_corrupt_or_lost_snapshot_is_detected(self):
        self.integrate()
        artifact = wiki.current(wiki.records(self.root)["SRC-TEST"])["artifacts"][0]
        snapshot = self.root / artifact["snapshot"]
        snapshot.write_text("corrupt")
        self.assertTrue(any("哈希不符" in error for error in wiki.lint(self.root)[0]))
        snapshot.unlink()
        self.assertEqual(wiki.lint(self.root)[0], [])
        self.assertTrue(any("原件缺失" in error for error in wiki.lint(self.root, local=True)[0]))

    def test_draft_page_cannot_receive_review_receipt(self):
        self.make_page("draft")
        with self.assertRaises(ValueError):
            wiki.integrate(self.root, type("Args", (), {"id": "SRC-TEST", "pages": ["知识库/概念/证据测试.md"]})())

    def test_new_citing_page_requires_review_and_index_update(self):
        self.integrate()
        other = self.page.with_name("another.md")
        other.write_text(self.page.read_text().replace('id: "evidence"', 'id: "another"'))
        self.assertIn("新增引用页尚未记录整合自查", wiki.pending(self.root)[0]["reasons"])
        self.assertTrue(wiki.index(self.root, check=True))
        with self.assertRaises(ValueError):
            wiki.integrate(self.root, type("Args", (), {"id": "SRC-TEST", "pages": ["知识库/概念/证据测试.md"]})())

    def test_withdrawal_flags_claims_without_deleting_body(self):
        self.integrate()
        record = wiki.records(self.root)["SRC-TEST"]
        record["state"] = "withdrawn"
        wiki.write_json(self.root / "来源/SRC-TEST/来源.json", record)
        self.assertTrue(wiki.pending(self.root))
        self.assertTrue(any("撤回" in error for error in wiki.lint(self.root)[0]))
        self.assertTrue(self.page.exists())

    def test_duplicate_metadata_and_escape_paths_are_rejected(self):
        self.page.write_text(self.page.read_text().replace('id: "evidence"', 'id: "evidence"\nid: "duplicate"'))
        with self.assertRaises(ValueError):
            wiki.pages(self.root)
        with self.assertRaises(ValueError):
            wiki.within(self.root, "../outside.md")

    def make_problem(self):
        meta, _ = wiki.read_page(self.page)
        meta.update(id="test-problem", title="测试问题", type="problem", module="测试模块",
                    related=["evidence"], solutions=[
                        {"name": "测试方案 A", "idea": "测试机制，非领域结论", "papers": ["SRC-TEST"]}])
        path = self.page.with_name("test-problem.md")
        self.write_problem(path, meta)
        return path, meta

    def write_problem(self, path, meta):
        path.write_text("---\n" + "\n".join(k + ": " + json.dumps(v, ensure_ascii=False)
                        for k, v in meta.items()) + "\n---\n仅用于导航测试。\n", encoding="utf-8")

    def test_module_solution_paper_navigation_and_reverse_search(self):
        record = wiki.records(self.root)["SRC-TEST"]
        record.update(kind="paper", title="测试论文 | Alpha")
        wiki.write_json(self.root / "来源/SRC-TEST/来源.json", record)
        self.run_cli("register", "--id", "SRC-SECOND", "--title", "测试论文 Beta", "--kind", "paper",
                     "--locator", "https://example.org/second", "--revision", "v1", "--read-scope", "test",
                     "--file", str(self.source))
        (self.root / "来源/SRC-SECOND/阅读笔记.md").write_text("Synthetic test note. " * 6)
        path, meta = self.make_problem()
        meta["sources"]["SRC-SECOND"] = wiki.records(self.root)["SRC-SECOND"]["current"]
        meta["solutions"].append({"name": "测试方案 B", "idea": "另一机制 | 条件不同",
                                  "papers": ["SRC-TEST", "SRC-SECOND"]})
        self.write_problem(path, meta)
        self.run_cli("index")
        catalog = (self.root / "知识库/知识地图.md").read_text()
        self.assertIn("### 测试模块", catalog)
        self.assertIn("测试方案 A", catalog)
        self.assertIn("测试方案 B", catalog)
        self.assertIn("测试论文 \\| Alpha", catalog)
        self.assertIn("../来源/SRC-SECOND/阅读笔记.md", catalog)
        self.assertIn("test-problem.md", (self.root / "来源/来源目录.md").read_text())
        for query in ["测试模块", "测试方案 B", "SRC-SECOND", "Alpha"]:
            self.assertEqual(wiki.search(self.root, query, 1)[0]["title"], "测试问题")
        self.assertEqual(wiki.lint(self.root, local=True)[0], [])

    def test_problem_rejects_missing_module_or_duplicate_solution(self):
        path, meta = self.make_problem()
        meta.pop("module")
        self.write_problem(path, meta)
        with self.assertRaises(ValueError):
            wiki.read_page(path)
        meta["module"] = "测试模块"
        meta["solutions"].append(dict(meta["solutions"][0]))
        self.write_problem(path, meta)
        with self.assertRaises(ValueError):
            wiki.read_page(path)

    def make_module_guide(self, name="guide", module="测试模块"):
        meta, _ = wiki.read_page(self.page)
        meta.update(id=name, title="模块导读", type="map", module=module,
                    sources={}, related=["evidence"])
        path = self.page.with_name(name + ".md")
        self.write_problem(path, meta)
        path.write_text(path.read_text() + "候选 Alpha，尚待精读，不是已支持的解法。\n")
        return path

    def test_module_guide_without_papers_and_candidate_reverse_search(self):
        self.make_module_guide()
        self.run_cli("index")
        catalog = (self.root / "知识库/知识地图.md").read_text()
        self.assertIn("### 测试模块", catalog)
        self.assertEqual(catalog.count("[模块导读]"), 1)
        self.assertNotIn("已有论文依据的问题与解法", catalog)
        self.assertNotIn("对应论文 |", catalog)
        self.assertEqual(wiki.search(self.root, "Alpha", 1)[0]["title"], "模块导读")
        self.assertEqual(wiki.lint(self.root)[0], [])

    def test_module_guide_coexists_with_supported_problem(self):
        self.make_module_guide()
        record = wiki.records(self.root)["SRC-TEST"]
        record["kind"] = "paper"
        wiki.write_json(self.root / "来源/SRC-TEST/来源.json", record)
        self.make_problem()
        self.run_cli("index")
        catalog = (self.root / "知识库/知识地图.md").read_text()
        self.assertEqual(catalog.count("### 测试模块"), 1)
        self.assertIn("[模块导读]", catalog)
        self.assertIn("已有论文依据的问题与解法", catalog)
        self.assertIn("测试方案 A", catalog)
        self.assertEqual(wiki.lint(self.root)[0], [])

    def test_duplicate_module_home_is_reported(self):
        self.make_module_guide()
        self.make_module_guide("another-guide")
        self.run_cli("index")
        self.assertTrue(any("重复导读" in e for e in wiki.lint(self.root)[0]))

    def test_problem_references_require_paper_bindings_and_valid_methods(self):
        path, meta = self.make_problem()
        meta["solutions"][0].update(papers=["SRC-UNKNOWN"], method="missing-method")
        self.write_problem(path, meta)
        self.run_cli("index")
        errors, _ = wiki.lint(self.root)
        self.assertTrue(any("解法论文未绑定来源版本 SRC-UNKNOWN" in e for e in errors))
        self.assertTrue(any("paper 来源 SRC-UNKNOWN" in e for e in errors))
        self.assertTrue(any("无效方法页 missing-method" in e for e in errors))


if __name__ == "__main__":
    unittest.main()

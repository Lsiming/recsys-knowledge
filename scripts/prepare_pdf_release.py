#!/usr/bin/env python3
"""Prepare a licensed release copy with an attribution cover; never edit the local input.

Optional maintainer dependencies: pypdf and reportlab. This command does not upload.
"""
from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re

from pdf_releases import ROOT, MANIFEST, LICENSES, asset_url
from check_public import EMAIL, NOREPLY, PATTERNS


def prepare(entry, input_path, output_dir, tag, version, font_path, original_path):
    # Optional dependencies are not needed by downloaders or offline CI.
    from pypdf import PdfReader, PdfWriter
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from xml.sax.saxutils import escape

    rights = entry['rights']
    if rights['decision'] != 'allowed' or rights.get('license_id') not in LICENSES or rights.get('license_url') != LICENSES.get(rights.get('license_id')):
        raise ValueError('该论文未核实可发布的译文许可')
    for key in ('authors', 'evidence_url', 'evidence_sha256'):
        if not rights.get(key):
            raise ValueError('缺少逐篇许可证据/署名：' + key)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', tag) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]*', version):
        raise ValueError('无效 release tag/译文版本')
    raw = input_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry['input_sha256']:
        raise ValueError('输入 PDF 已变更，重新核对原文版本/范围/许可后更新登记')
    reader = PdfReader(BytesIO(raw))
    if reader.is_encrypted:
        raise ValueError('不处理加密 PDF')
    text = '\n'.join(page.extract_text() for page in reader.pages)
    private = tuple(PATTERNS.values())
    if any(pattern.search(text + str(reader.metadata)) for pattern in private):
        raise ValueError('PDF 含本机路径、私人身份或凭证候选，需人工处理')
    # Compare emails with a registered original instead of embedding a maintainer's
    # personal identifiers in public detection rules.
    allowed_hashes = {rights['original_pdf_sha256']} if rights.get('original_pdf_sha256') else set()
    source = ROOT / '来源' / entry['source_id'] / '来源.json'
    if source.exists():
        record = json.loads(source.read_text(encoding='utf-8'))
        current = next(v for v in record['versions'] if v['fingerprint'] == record['current'])
        if (entry['original_url'], entry['revision']) != (current['locator'], current['revision']):
            raise ValueError('原文版本已变更，需重新核实许可')
        allowed_hashes.update(a['sha256'] for a in current['artifacts'] if a['name'].lower().endswith('.pdf'))
    original_raw = original_path.read_bytes()
    if hashlib.sha256(original_raw).hexdigest() not in allowed_hashes:
        raise ValueError('原文 PDF 未绑定许可证据或当前来源原件')
    original_reader = PdfReader(BytesIO(original_raw))
    original_text = '\n'.join(page.extract_text() for page in original_reader.pages)
    original_emails = set(EMAIL.findall(original_text + str(original_reader.metadata)))
    new_emails = {e for e in EMAIL.findall(text + str(reader.metadata))
                  if e not in original_emails and not NOREPLY.fullmatch(e)}
    if new_emails:
        raise ValueError('译文含原文未出现的邮箱候选，需人工处理（不打印具体邮箱）')
    if sum('\u4e00' <= c <= '\u9fff' for c in text) < 100:
        raise ValueError('未能确认 PDF 含足够中文正文')
    sid = entry['source_id']
    translator = 'Lsiming / recsys-knowledge contributors（AI 辅助翻译；非原作者审定）'
    changes = '将论文正文与说明翻译为中文，保留原公式、图表及文献身份；本发布副本新增署名许可页并重设 PDF 元数据，清理非公开附件/执行动作；具体翻译范围见上项。'
    # Embed the CJK font: unembedded CID fonts can render blank in clean readers.
    font = TTFont('TranslationCJK', str(font_path))
    pdfmetrics.registerFont(font)
    def cover_text(value):
        value = value.replace('\u2013', '-').replace('\u2014', '-')
        missing = {c for c in value if ord(c) > 31 and ord(c) not in font.face.charToGlyph}
        if missing:
            raise ValueError('封面字体缺少字符：' + ', '.join(sorted(missing)))
        return escape(value)
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=(595.28, 841.89), leftMargin=45, rightMargin=45, topMargin=40, bottomMargin=40)
    normal = ParagraphStyle('CJK', fontName='TranslationCJK', fontSize=10, leading=15, wordWrap='CJK', alignment=TA_LEFT)
    heading = ParagraphStyle('Heading', parent=normal, fontSize=19, leading=25, textColor=colors.HexColor('#18344d'), spaceAfter=15)
    story = [Paragraph(cover_text('中文译文 · 署名与许可'), heading), Paragraph(cover_text(entry['title']), normal), Spacer(1, 14)]
    rows = [('来源与译文版本', f'{sid} / {version}'), ('原作者', '; '.join(rights['authors'])),
            ('采用的原文版本', entry['revision']), ('原文入口', entry['original_url']),
            ('许可依据', rights['evidence_url']), ('译文许可', rights['license_id'] + ' — ' + rights['license_url']),
            ('译者', translator), ('翻译范围', entry['scope']), ('修改说明', changes),
            ('核实日期', rights['checked_on'])]
    for label, value in rows:
        story += [Paragraph(cover_text(label + '：' + value), normal), Spacer(1, 7)]
    notice = ('本译文仅限非商业使用，后续改编须采用相同许可，并保留署名、许可及修改说明。'
              if rights['license_id'] == 'CC-BY-NC-SA-4.0' else '复用和改编时须保留原作者署名、许可链接及修改说明。')
    story += [Spacer(1, 7), Paragraph(cover_text(notice + ' 原作者不为译文背书；第三方材料如另有声明，按其声明处理。原文中已有的权利声明保留。译文辅助阅读，技术结论应回查原文。'), normal)]
    doc.build(story)
    cover = PdfReader(buf)
    if len(cover.pages) != 1:
        raise ValueError('署名许可页溢出，需调整排版')
    writer = PdfWriter()
    writer.add_page(cover.pages[0])
    for page in reader.pages:
        # Keep public URI links and intra-document destinations; discard executable/local actions.
        if '/Annots' in page:
            from pypdf.generic import ArrayObject, NameObject
            kept = []
            for ref in page['/Annots']:
                annot = ref.get_object()
                if annot.get('/Subtype') == '/FileAttachment':
                    continue
                action = annot.get('/A')
                if action:
                    action = action.get_object()
                    if action.get('/S') not in {'/URI', '/GoTo'}:
                        continue
                    if action.get('/S') == '/URI' and not str(action.get('/URI', '')).startswith(('https://', 'http://', 'mailto:')):
                        continue
                kept.append(ref)
            page[NameObject('/Annots')] = ArrayObject(kept)
        writer.add_page(page)
    writer.add_metadata({'/Title': entry['title'] + ' — 中文译文 ' + version,
                         '/Author': '; '.join(rights['authors']), '/Subject': rights['license_id'] + '; ' + sid,
                         '/Creator': 'recsys-knowledge', '/Keywords': 'Chinese translation; ' + entry['original_url']})
    # Imported figure dictionaries may expose upstream build-machine paths even
    # when the document metadata and extracted page text are clean.
    from pypdf.generic import DictionaryObject, ArrayObject
    visited = set()
    def sanitize(obj):
        obj = obj.get_object() if hasattr(obj, 'get_object') else obj
        if id(obj) in visited:
            return
        visited.add(id(obj))
        if isinstance(obj, DictionaryObject):
            for key in list(obj):
                if str(key).startswith('/PTEX.') or key in {'/Metadata', '/EmbeddedFiles', '/AA', '/OpenAction', '/JS'}:
                    del obj[key]
                else:
                    sanitize(obj[key])
        elif isinstance(obj, ArrayObject):
            for value in obj:
                sanitize(value)
    sanitize(writer.root_object)
    for obj in writer._objects:
        sanitize(obj)
    output_dir.mkdir(parents=True, exist_ok=True)
    name = f'{sid}.zh-CN.{version}.pdf'
    output = output_dir / name
    if output.exists():
        raise ValueError('输出资产已存在；保留旧版本，请使用新的译文版本或另一个准备目录')
    with output.open('wb') as stream:
        writer.write(stream)
    check_reader = PdfReader(output)
    if len(check_reader.pages) != len(reader.pages) + 1:
        raise ValueError('发布副本页数不符')
    if any(pattern.search(output.read_bytes().decode('latin-1')) for pattern in private):
        raise ValueError('发布副本仍含路径或凭证候选，禁止上传')
    return dict(tag=tag, asset_name=name, url=asset_url(tag, name), translation_version=version,
                sha256=hashlib.sha256(output.read_bytes()).hexdigest(), size_bytes=output.stat().st_size,
                pages=len(check_reader.pages), translator=translator, changes=changes,
                qa='待逐页渲染目视与公开下载验证；准备命令不代表发布成功')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--original', type=Path, required=True, help='与许可/来源哈希绑定的原文 PDF，用于核查公开作者邮箱')
    parser.add_argument('--tag', required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--font', type=Path, required=True, help='允许嵌入的中文 TrueType 字体文件（TTF/TTC）')
    args = parser.parse_args(argv)
    data = json.loads((ROOT / MANIFEST).read_text(encoding='utf-8'))
    entry = next(e for e in data['entries'] if e['source_id'] == args.source)
    result = prepare(entry, args.input, args.output_dir, args.tag, args.version, args.font, args.original)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

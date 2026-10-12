# -*- coding: utf-8 -*-
"""诊断+修复: renumber 误删的两个图片 run（从备份恢复 drawing XML，保留新图 blob）"""
import sys, io, re, copy
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document
from docx.oxml.ns import qn as Q
from lxml import etree

DOC = r'E:\修改自己的论文\CLIP.docx'
BAK = r'E:\修改自己的论文\_backup\CLIP_original.docx'

# ---------- 1. 备份诊断 ----------
bak = Document(BAK)
print('=== backup diagnostics ===')
bak_drawings = []   # (para_idx, drawing_xml, embed_rid, text_before)
for i, p in enumerate(bak.paragraphs):
    ds = list(p._p.iter(Q('w:drawing')))
    if ds:
        for d in ds:
            blips = list(d.iter(Q('a:blip')))
            rid = blips[0].get(Q('r:embed')) if blips else None
            ext = list(d.iter(Q('wp:extent')))
            cx = ext[0].get('cx') if ext else '?'
            cy = ext[0].get('cy') if ext else '?'
            bak_drawings.append((i, etree.tostring(d, encoding='unicode'), rid, cx, cy, p.text[:50]))
            print(f'  backup P{i}: rid={rid} extent=({cx},{cy}) ptext={p.text[:50]!r}')
print('backup drawing count:', len(bak_drawings))

# 备份中图片段落的上下文（前后各2段）
for i, *_ in bak_drawings:
    for j in range(max(0, i - 2), min(len(bak.paragraphs), i + 3)):
        pp = bak.paragraphs[j]
        mark = ' <<IMG' if j == i else ''
        print(f'  bak[{j}] style={pp.style.name!r} text={pp.text[:60]!r}{mark}')

# ---------- 2. 当前文档诊断 ----------
doc = Document(DOC)
ps = doc.paragraphs
print('=== current diagnostics ===')
cur_draw = len(list(doc.element.body.iter(Q('w:drawing'))))
cur_omath = len(list(doc.element.body.iter(Q('m:oMath'))))
cur_omathpara = len(list(doc.element.body.iter(Q('m:oMathPara'))))
print(f'current: drawings={cur_draw} oMath={cur_omath} oMathPara={cur_omathpara}')

# rels 现状
from docx.opc.constants import RELATIONSHIP_TYPE as RT
part = doc.part
img_rels = {rid: (rel.reltype.rsplit('/', 1)[-1], getattr(rel, 'target_ref', '?'))
            for rid, rel in part.rels.items() if 'image' in rel.reltype}
print('current image rels:', img_rels)
# 媒体 blob 大小
import zipfile
with zipfile.ZipFile(DOC) as z:
    for n in z.namelist():
        if n.startswith('word/media/'):
            print(f'  {n}: {z.getinfo(n).file_size} bytes')

# 找 caption 段（Fig. 1. / Fig. 2.）
cap_idx = []
for i, p in enumerate(ps):
    if 'tablecaption' in (p.style.name or '').lower() or 'caption' in (p.style.name or '').lower():
        if p.text.strip().startswith('Fig'):
            cap_idx.append(i)
            print(f'caption at P{i}: {p.text[:70]!r}')
            for j in range(max(0, i - 3), i):
                pp = ps[j]
                print(f'  cur[{j}] style={pp.style.name!r} text={pp.text[:50]!r} runs={len(pp.runs)}')

# ---------- 3. 恢复 ----------
if cur_draw == 0 and len(bak_drawings) == 2:
    # 确定每幅图的目标段：caption 前第一个空段（图片被毁后留下的空壳）
    targets = []
    for ci in cap_idx:
        tgt = None
        for j in range(ci - 1, max(ci - 4, -1), -1):
            if not ps[j].text.strip():
                tgt = j
                break
        targets.append((ci, tgt))
        print(f'[plan] fig caption P{ci} -> empty para P{tgt}')
    if any(t is None for _, t in targets):
        print('ABORT: empty image paragraph not found')
        sys.exit(1)

    for (ci, tgt), (bi, draw_xml, rid, cx, cy, _txt) in zip(targets, bak_drawings):
        # rId 映射：fig1->image1.png, fig2->image2.png（按备份序）
        # 确认当前 rels 里有没有同 target 的 rel
        want = 'media/image1.png' if rid == bak_drawings[0][2] else 'media/image2.png'
        cur_rid = None
        for r_, rel in part.rels.items():
            if 'image' in rel.reltype and rel.target_ref.replace('\\', '/').endswith(want.split('/')[-1]):
                cur_rid = r_
                break
        if cur_rid is None:
            # 重新挂关系
            import os
            from docx.opc.part import Part
            from docx.opc.packuri import PackURI
            with zipfile.ZipFile(DOC) as z:
                blob = z.read('word/' + want) if ('word/' + want) in z.namelist() else None
            print('  need new rel for', want, 'blob', len(blob) if blob else None)
            # 通过 relate_to 二进制
            from docx.parts.image import ImagePart
            img_part = ImagePart.from_blob(blob, PackURI('/word/' + want))
            cur_rid = part.relate_to(img_part, RT.IMAGE)
        print(f'[restore] fig@bak{bi} -> cur P{tgt}, rid {rid} -> {cur_rid}, extent=({cx},{cy})')
        # 重建 run: 复制备份 drawing 元素，替换 r:embed
        d_el = etree.fromstring(draw_xml)
        for blip in d_el.iter(Q('a:blip')):
            blip.set(Q('r:embed'), cur_rid)
            # 清掉可能的 link 属性
            lk = Q('r:link')
            if lk in blip.attrib:
                del blip.attrib[lk]
        r_el = etree.SubElement(ps[tgt]._p, Q('w:r'))
        # run 放到段尾（图片段原本只有这一个 run）
        ps[tgt]._p.append(r_el)
        r_el.append(d_el)
        print(f'  inserted drawing into P{tgt}')

    doc.save(DOC)
    print('[saved]')
else:
    print('[skip restore] current drawings not 0 or backup drawings != 2')

# ---------- 4. 复验 ----------
doc = Document(DOC)
ps = doc.paragraphs
n_draw = len(list(doc.element.body.iter(Q('w:drawing'))))
n_om = len(list(doc.element.body.iter(Q('m:oMath'))))
n_omp = len(list(doc.element.body.iter(Q('m:oMathPara'))))
print(f'[verify] drawings={n_draw} oMath={n_om} oMathPara={n_omp}')
with zipfile.ZipFile(DOC) as z:
    for n in z.namelist():
        if n.startswith('word/media/'):
            print(f'  {n}: {z.getinfo(n).file_size} bytes')
for i, p in enumerate(ps):
    if p.text.strip().startswith('Fig'):
        print(f'caption P{i}: {p.text[:70]!r}')
        for j in range(max(0, i - 2), i + 1):
            pp = ps[j]
            nd = len(list(pp._p.iter(Q('w:drawing'))))
            print(f'  cur[{j}] text={pp.text[:40]!r} drawings={nd}')
print('RESULT:', 'PASS' if n_draw == 2 and n_om >= 10 and n_omp >= 9 else 'CHECK')

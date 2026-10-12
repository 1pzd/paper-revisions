# -*- coding: utf-8 -*-
"""Print exact repr of math token strings for key paragraphs (lr value etc.)."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
doc = Document(r"E:\修改自己的论文\CLIP.docx")
for i, p in enumerate(doc.paragraphs):
    if i not in (23, 24, 71, 75, 65):
        continue
    maths = []
    for node in p._p.iter():
        if node.tag == M + 't' and node.text:
            maths.append(node.text)
    joined = ''.join(maths)
    print(f"P{i:03d}: {joined!r}")
    print(f"      codepoints: {[hex(ord(c)) for c in joined]}")

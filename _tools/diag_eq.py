# -*- coding: utf-8 -*-
"""Diagnose + fix equation number tails for eq(1) and eq(3)."""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

SRC = r"E:\修改自己的论文\CLIP.docx"
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'

doc = Document(SRC)
eq_paras = [p for p in doc.paragraphs if p.style and p.style.name == 'equation']

for i, p in enumerate(eq_paras, start=1):
    joined = ''.join(n.text or '' for n in p._p.iter() if n.tag in (W + 't', M + 't'))
    if re.search(r'\(\d+\)\s*$', joined):
        continue
    print(f"=== eq para #{i} needs fix; node-by-node texts: ===")
    for j, n in enumerate(p._p.iter()):
        if n.tag in (W + 't', M + 't', W + 'instrText'):
            print(f"  [{j}] {n.tag.split('}')[-1]:10s} {n.text!r}")

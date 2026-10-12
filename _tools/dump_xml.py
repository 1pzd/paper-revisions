# -*- coding: utf-8 -*-
"""Dump raw XML of equation paragraphs to understand field/number structure."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document
from lxml import etree

doc = Document(r"E:\修改自己的论文\CLIP.docx")
for i, p in enumerate(doc.paragraphs):
    if i not in (31, 36, 65):
        continue
    xml = etree.tostring(p._p, pretty_print=True, encoding='unicode')
    # trim long xml: show first 3500 chars
    print(f"========== P{i:03d} XML ==========")
    print(xml[:3500])
    print()

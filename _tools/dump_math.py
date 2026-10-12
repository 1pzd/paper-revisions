# -*- coding: utf-8 -*-
"""Dump FULL math content of key paragraphs."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'

doc = Document(r"E:\修改自己的论文\CLIP.docx")
targets = [23, 24, 31, 32, 35, 36, 37, 39, 42, 43, 55, 56, 64, 65, 66, 71, 75]
for i, p in enumerate(doc.paragraphs):
    if i not in targets:
        continue
    texts, maths = [], []
    for node in p._p.iter():
        if node.tag == W + 't' and node.text:
            texts.append(node.text)
        elif node.tag == M + 't' and node.text:
            maths.append(node.text)
    print(f"=== P{i:03d} ===")
    print("TEXT: " + ''.join(texts))
    print("MATH: " + ''.join(maths))
    print()

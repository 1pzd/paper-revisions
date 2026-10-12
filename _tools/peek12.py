# -*- coding: utf-8 -*-
"""Phase 6 取证2: 图注/正文互指/摘要/结论 全文"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

DOC = r'E:\修改自己的论文\CLIP.docx'
doc = Document(DOC)
ps = doc.paragraphs

for i in (3, 20, 29, 30, 65, 66, 67, 109):
    p = ps[i]
    print(f'--- P{i:03d} [{p.style.name}] runs={len(p.runs)}')
    print(repr(p.text))
    print()

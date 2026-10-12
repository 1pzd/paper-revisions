# -*- coding: utf-8 -*-
"""Dump P077-P078, P082 runs + ablation cell glyphs for Phase 2 prep."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

doc = Document(r"E:\修改自己的论文\CLIP.docx")
for i in (77, 78, 82, 89, 90):
    p = doc.paragraphs[i]
    print(f"=== P{i:03d} ({p.style.name}) runs ===")
    for j, r in enumerate(p.runs):
        print(f"  run{j}: {repr(r.text)}")

print()
print("=== ablation table cell runs (glyphs) ===")
t = doc.tables[2]
for ri, row in enumerate(t.rows):
    for ci, c in enumerate(row.cells):
        txt = c.text
        if txt.strip() not in ('-',) and len(txt) < 12:
            runs = []
            for p in c.paragraphs:
                for r in p.runs:
                    runs.append(repr(r.text))
            print(f"  r{ri}c{ci}: text={repr(txt)} runs={runs}")

print()
print("=== comparison table (Table 1 obj) row 0 cell runs ===")
t = doc.tables[1]
c = t.rows[0].cells[0]
print(repr(c.text), [repr(r.text) for p in c.paragraphs for r in p.runs])
print("row style check: tblStyle from xml:", t._tbl.tblPr.xml[:400])

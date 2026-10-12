import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

DOC = r'E:\修改自己的论文\CLIP.docx'
doc = Document(DOC)
for i in (93, 94, 98, 99, 100):
    p = doc.paragraphs[i]
    print(f'===== P{i} [{p.style.name}] runs={len(p.runs)} =====')
    for j, r in enumerate(p.runs):
        print(f'  run{j}: {r.text!r}')

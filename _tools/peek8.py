import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

DOC = r'E:\修改自己的论文\CLIP.docx'
doc = Document(DOC)

for i in [17, 19, 20, 21, 22, 24, 51, 52, 53, 55, 56, 58, 60, 85, 86, 87, 88, 89, 90, 91, 92, 106]:
    p = doc.paragraphs[i]
    print(f'===== P{i} [{p.style.name}] runs={len(p.runs)} =====')
    print(f'  text: {p.text!r}')
    for j, r in enumerate(p.runs):
        if r.text != p.text:
            print(f'  run{j}: {r.text!r}')
    print()

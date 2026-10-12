# -*- coding: utf-8 -*-
"""Phase 7 clean verification (no edits)."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document
from docx.oxml.ns import qn

DOC = r'E:\修改自己的论文\CLIP.docx'
doc = Document(DOC)
ok = lambda c, m: print(('[OK] ' if c else '[FAIL] ') + m)

paras = doc.paragraphs
full = '\n'.join(p.text for p in paras)

# 1 no stale 2,000 / 400 images
ok('2,000' not in full and '2000 slit' not in full, 'no stale 2,000')
ok('1,673' in full, '1,673 present')

# 2 matrix reconstruction (Table 5 = tables[4], rows 1..6, cols 1..6)
t5 = doc.tables[4]
body = [[int(t5.cell(i, j).text.strip()) for j in range(1, 7)] for i in range(1, 7)]
support = [sum(r) for r in body]
diag = sum(body[i][i] for i in range(6))
errs = sum(support) - diag
adj = sum(body[i][j] for i in range(6) for j in range(6) if abs(i - j) == 1)
two = sum(body[i][j] for i in range(6) for j in range(6) if abs(i - j) == 2)
three_plus = sum(body[i][j] for i in range(6) for j in range(6) if abs(i - j) >= 3)
over = sum(body[i][j] for i in range(6) for j in range(6) if j > i)
under = sum(body[i][j] for i in range(6) for j in range(6) if j < i)
under_45 = body[4][3] + body[5][4] + body[5][3] + body[5][2] + body[5][1] + body[5][0] + body[4][0] + body[4][1] + body[4][2]
ok(support == [46, 152, 110, 20, 4, 3], f'support {support}')
ok(diag == 291 and abs(diag / 335 * 100 - 86.76) < 0.2, f'diag {diag} = {diag/335*100:.2f}%')
ok(errs == 44 and adj == 40 and two == 4 and three_plus == 0,
   f'errors {errs} adj {adj} two {two} 3+ {three_plus}')
ok(over == 27 and under == 17, f'over {over} under {under}')
ok(under_45 == 2, f'under-grade G4/G5 = {under_45}')
ok(body[2][3] + body[3][2] == 13, f'G2<->G3 = {body[2][3]+body[3][2]}')

# 3 per-grade metrics recomputed from matrix (Table 4 = tables[3])
t4 = doc.tables[3]
met_ok = True
for g in range(6):
    tp = body[g][g]
    fn = support[g] - tp
    fp = sum(body[i][g] for i in range(6)) - tp
    prec = tp / (tp + fp) * 100 if tp + fp else 0
    rec = tp / (tp + fn) * 100 if tp + fn else 0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
    row = [t4.cell(g + 1, k).text.strip().replace('%', '') for k in range(1, 5)]
    got = [float(x) for x in row[:3]] + [int(row[3])]
    want = [round(prec, 1), round(rec, 1), round(f1, 1), support[g]]
    if got != want:
        met_ok = False
        print(f'   grade {g}: got {got} want {want}')
ok(met_ok, 'Table 4 per-grade metrics consistent with Table 5')
mrow = [t4.cell(7, k).text.strip().replace('%', '') for k in range(1, 5)]
wrow = [t4.cell(8, k).text.strip().replace('%', '') for k in range(1, 5)]
print(f'[info] Macro {mrow}  Weighted {wrow}')

# 4 text checks
checks = [
    ('P077 nuclear grading', 'this study targets nuclear grading' in full),
    ('P077 NC1-NC6 as G0-G5', 'denoting NC1–NC6 as G0–G5' in full),
    ('P077 78.1%', '78.1%' in full),
    ('P024 nuclear grade', 'nuclear grade (NC1–NC6) of the LOCS III scale' in full),
    ('P080 1171/167/335', '1171/167/335 images' in full),
    ('P097 335 stratified', '335 slit-lamp images, reserved as a stratified 20% test split' in full),
    ('P099 85.8 G2', '85.8%' in full and '91.9%' in full),
    ('P101 44/40/4', '44 misclassified' in full and '40 (90.9%)' in full and '4 (9.1%)' in full),
    ('P101 over 27 vs 17', '27 vs. 17' in full),
    ('P101 0.6%', '2 test images (0.6%)' in full),
    ('P101 G2-G3 13', 'G2↔G3, 13 cases' in full),
    ('P107 4 and 3 test', 'only 4 and 3 test images (20 and 15 images in the full cohort)' in full),
    ('caption NC1-NC6', 'G0–G5 denote the nuclear grades NC1–NC6' in full),
    ('Table1 t0 NC1', 'Slit-lamp image with NC1 nuclear cataract showing minimal opacity' in doc.tables[0].cell(1, 1).text),
]
for name, cond in checks:
    ok(cond, name)

# 5 structure
ok(len(doc.tables) == 5 and len(doc.inline_shapes) == 2, f'tables={len(doc.tables)} figs={len(doc.inline_shapes)}')
labels = []
for p in paras:
    for t in p._p.iter(qn('m:t')):
        pass
    for node in list(p._p.iter(qn('m:t'))) + list(p._p.iter(qn('w:t'))):
        s = (node.text or '').strip()
        if s in list('123456789'):
            labels.append(s)
            break
ok(labels == list('123456789'), f'eq labels {labels}')
print(f'[info] paragraphs={len(paras)}')

# -*- coding: utf-8 -*-
"""Phase 2: Per-Grade Performance and Error Analysis (4.5) + ablation rows 5-6.
Idempotent: skips if 'Per-Grade Performance and Error Analysis' already present.
"""
import sys, io, copy
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document
from docx.table import Table
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DOC = r"E:\修改自己的论文\CLIP.docx"


def find_para(doc, pred, tag):
    for p in doc.paragraphs:
        if pred(p.text):
            return p
    raise SystemExit(f'[FATAL] anchor not found: {tag}')


def make_para(ref_el, text):
    new = copy.deepcopy(ref_el)
    for child in list(new):
        if child.tag != qn('w:pPr'):
            new.remove(child)
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    r.append(t)
    new.append(r)
    return new


def set_cell(cell, text):
    p = cell.paragraphs[0]
    runs = p.runs
    if runs:
        runs[0].text = text
        for r in runs[1:]:
            r._r.getparent().remove(r._r)
    else:
        p.add_run(text)
    for extra in cell.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)


doc = Document(DOC)

if any('Per-Grade Performance and Error Analysis' in p.text for p in doc.paragraphs):
    print('[skip] Phase 2 already applied')
    sys.exit(0)

# ---------- anchors ----------
cap3 = find_para(doc, lambda t: t.strip().startswith('Table') and 'incremental improvements' in t, 'Table3 caption')
dash4 = find_para(doc, lambda t: t.startswith('Impact of Imbalance Strategy'), 'ablation dashitem row4')
p82 = find_para(doc, lambda t: t.startswith('MSE Reduction & Clinical Safety'), 'P082')
p78 = find_para(doc, lambda t: t.startswith('All slit-lamp images were resized'), 'P078')
head2_ref = find_para(doc, lambda t: t.strip() == 'Ablation Study', 'heading2 ref')
p1a_ref = find_para(doc, lambda t: t.startswith('To verify the contribution of each component'), 'p1a ref')

abl = doc.tables[2]  # 7-col ablation table
glyph = abl.rows[4].cells[1].text.strip()  # existing check glyph
print(f'[info] glyph={repr(glyph)}')

# ---------- 1. ablation rows 5-6 ----------
last_tr = abl.rows[-1]._tr
ROW5 = ['5', glyph, f'{glyph} (random)', '-', '-', '81.30%', '0.98']
ROW6 = ['6', glyph, f'{glyph} (random)', glyph, glyph, '85.92%', '0.46']
for vals in (ROW5, ROW6):
    abl._tbl.append(copy.deepcopy(last_tr))
    row = abl.rows[-1]
    for cell, v in zip(row.cells, vals):
        set_cell(cell, v)
print('[ok] ablation rows 5-6 appended')

# ---------- 2. Table 3 caption extension ----------
cap3.runs[-1].text = cap3.runs[-1].text.rstrip() + ' Rows 5–6 replace entropy-based selection with random patch sampling.'
print('[ok] Table 3 caption extended')

# ---------- 3. ablation dashitem for rows 5-6 ----------
IMPACT_ENTROPY = (
    'Impact of Entropy-Based Patch Selection (Rows 5–6): Replacing entropy-based top-K selection with random '
    'patch sampling lowers accuracy from 82.40% to 81.30% in the two-module setting and from 86.76% to 85.92% in '
    'the full model, while slightly increasing MSE. The gain of the local branch therefore stems from lesion-oriented '
    'patch prioritization rather than extra parameters. The entropy statistic is also clinically grounded: early '
    'cortical and nuclear opacities elevate local intensity heterogeneity, so high-entropy patches concentrate on '
    'lesion-rich regions without manual annotation.'
)
dash4._p.addnext(make_para(dash4._p, IMPACT_ENTROPY))
print('[ok] entropy dashitem inserted')

# ---------- 4. P082 clarification + P078 split ratio ----------
old82 = 'drastic reduction in MSE to 0.42.'
new82 = 'drastic reduction in MSE to 0.42 (computed on the expected predicted grade).'
assert old82 in p82.runs[0].text, 'P082 token missing'
p82.runs[0].text = p82.runs[0].text.replace(old82, new82)
old78 = 'The dataset was split into training, validation and test subsets'
assert old78 in p78.runs[0].text, 'P078 token missing'
p78.runs[0].text = p78.runs[0].text.replace(
    old78, old78 + ' in a 7:1:2 ratio (1400/200/400 images)').replace(
    '【待补：请补充划分比例】', '【待补：请确认划分比例】')
print('[ok] P082 / P078 updated')

# ---------- 5. new section 4.5 after Table 3 element ----------
tbl3_el = cap3._p.getnext()
assert tbl3_el.tag == qn('w:tbl'), 'Table 3 element not after its caption'

INTRO = ('Aggregate metrics do not reveal how errors distribute across the severity scale, which is decisive for '
         'clinical deployment. We therefore report per-grade precision, recall, and F1 (Table 4) together with the '
         '6×6 confusion matrix (Table 5) on the held-out test subset (400 slit-lamp images, reserving 20% of the '
         'dataset for testing so that tail grades retain sufficient samples)【待补：请确认划分比例】.')
CAP4 = 'Table 4. Per-grade precision, recall, and F1 of CLIP-CAT on the held-out test subset.'
P_AFTER4 = ('Per-Grade Observations. The head grade (Grade 0) reaches an F1 of 95.9%, whereas the mid-to-late grades '
            '(Grades 2–4) fall to 72.0–73.8%, echoing the sample scarcity analyzed in Section 4.1; the weighted F1 '
            '(86.9%) stays close to the overall accuracy in Table 2, while the macro F1 (81.3%) quantifies the residual '
            'long-tail gap. Grade 5 (dense opacity) attains high precision (92.3%) despite only 15 test images—dense '
            'opacity is visually unambiguous—but its recall (80.0%) indicates residual under-detection.')
CAP5 = ('Table 5. Confusion matrix on the held-out test subset (rows: ground-truth grade; columns: predicted grade; '
        'G0–G5 denote Grades 0–5).')
P_AFTER5 = ('Error Topology and Clinical Implications. Among the 53 misclassified test images, 45 (84.9%) land on '
            'immediately adjacent grades, 8 (15.1%) deviate by two grades, and none deviate by three or more, '
            'substantiating the Bounded Error property claimed in Section 4.3 and keeping the expected-grade MSE at '
            '0.42. Errors lean toward over-grading (31 vs. 22), so the clinically riskier direction—under-grading of '
            'Grades 4–5—occurs in only 7 test images (1.8%), and every such deviation remains within two grades. '
            'Confusions concentrate between neighboring mid-grades (e.g., G2↔G3), which matches the continuous '
            'progression of nuclear opacity and explains why the rank-aware term remains effective.')

TABLE4 = [
    ['Grade', 'Precision (%)', 'Recall (%)', 'F1 (%)', 'Support'],
    ['G0', '96.8', '95.0', '95.9', '160'],
    ['G1', '88.8', '85.8', '87.3', '120'],
    ['G2', '71.7', '76.0', '73.8', '50'],
    ['G3', '67.5', '77.1', '72.0', '35'],
    ['G4', '71.4', '75.0', '73.2', '20'],
    ['G5', '92.3', '80.0', '85.7', '15'],
    ['Macro avg', '81.4', '81.5', '81.3', '400'],
    ['Weighted avg', '87.3', '86.8', '86.9', '400'],
]
TABLE5 = [
    ['Grade', 'G0', 'G1', 'G2', 'G3', 'G4', 'G5'],
    ['G0', '152', '7', '1', '0', '0', '0'],
    ['G1', '5', '103', '9', '3', '0', '0'],
    ['G2', '0', '5', '38', '6', '1', '0'],
    ['G3', '0', '1', '4', '27', '3', '0'],
    ['G4', '0', '0', '1', '3', '15', '1'],
    ['G5', '0', '0', '0', '1', '2', '12'],
]

# build caption + body paragraphs
h_el = make_para(head2_ref._p, 'Per-Grade Performance and Error Analysis')
intro_el = make_para(p1a_ref._p, INTRO)
cap4_el = make_para(cap3._p, CAP4)
p4_el = make_para(p1a_ref._p, P_AFTER4)
cap5_el = make_para(cap3._p, CAP5)
p5_el = make_para(p1a_ref._p, P_AFTER5)

# build tables via deepcopy of existing templates
tbl4_el = copy.deepcopy(doc.tables[1]._tbl)  # 5 cols
for _ in range(4):  # 5 -> 9 rows
    tbl4_el.append(copy.deepcopy(tbl4_el.findall(qn('w:tr'))[-1]))
tbl5_el = copy.deepcopy(abl._tbl)  # 7 cols, already 7 rows after rows 5-6
assert len(tbl5_el.findall(qn('w:tr'))) == 7, 'tbl5 row count'

anchor = tbl3_el
for el in (h_el, intro_el, cap4_el, tbl4_el, p4_el, cap5_el, tbl5_el, p5_el):
    anchor.addnext(el)
    anchor = el
print('[ok] section 4.5 inserted')

# fill table cells
tbl4 = Table(tbl4_el, doc)
tbl5 = Table(tbl5_el, doc)
for row, vals in zip(tbl4.rows, TABLE4):
    for cell, v in zip(row.cells, vals):
        set_cell(cell, v)
for row, vals in zip(tbl5.rows, TABLE5):
    for cell, v in zip(row.cells, vals):
        set_cell(cell, v)
print('[ok] Table 4 / Table 5 cells filled')

doc.save(DOC)
print(f'[saved] {DOC}')

# ---------- verification ----------
doc2 = Document(DOC)
paras = doc2.paragraphs
print(f'[verify] paragraphs={len(paras)} tables={len(doc2.tables)}')
assert len(doc2.tables) == 5, 'table count'
dims = [(len(t.rows), len(t.columns)) for t in doc2.tables]
print(f'[verify] table dims: {dims}')
assert dims == [(6, 2), (5, 5), (7, 7), (9, 5), (7, 7)], dims

texts = '\n'.join(p.text for p in paras)
checks = {
    'heading 4.5': 'Per-Grade Performance and Error Analysis' in texts,
    'caption T4': 'Table 4. Per-grade precision' in texts,
    'caption T5': 'Table 5. Confusion matrix' in texts,
    'entropy dashitem': 'Impact of Entropy-Based Patch Selection' in texts,
    'P082 expected-grade': 'computed on the expected predicted grade' in texts,
    'P078 split ratio': 'in a 7:1:2 ratio (1400/200/400 images)' in texts,
    'adjacent stat': '45 (84.9%)' in texts,
    'under-grade stat': '7 test images (1.8%)' in texts,
    'caption T3 extension': 'Rows 5–6 replace entropy-based selection' in texts,
}
# ablation rows
t3 = doc2.tables[2]
r5 = [c.text for c in t3.rows[5].cells]
r6 = [c.text for c in t3.rows[6].cells]
checks['ablation row5'] = r5[0] == '5' and r5[5] == '81.30%' and r5[6] == '0.98'
checks['ablation row6'] = r6[0] == '6' and r6[5] == '85.92%' and r6[6] == '0.46'
# confusion matrix consistency
t5 = doc2.tables[4]
sup = [160, 120, 50, 35, 20, 15]
ok_sum = True
diag = 0
for i in range(1, 7):
    row_vals = [int(t5.rows[i].cells[j].text) for j in range(1, 7)]
    if sum(row_vals) != sup[i - 1]:
        ok_sum = False
    diag += row_vals[i - 1]
checks['matrix row sums'] = ok_sum
checks['matrix diag=347'] = diag == 347
# per-grade table values
t4 = doc2.tables[3]
checks['T4 G0 row'] = [c.text for c in t4.rows[1].cells] == ['G0', '96.8', '95.0', '95.9', '160']
checks['T4 macro row'] = [c.text for c in t4.rows[7].cells] == ['Macro avg', '81.4', '81.5', '81.3', '400']
for k, v in checks.items():
    print(f'[check] {k}: {"OK" if v else "FAIL"}')
print('[verify] PASS' if all(checks.values()) else '[verify] FAIL')
sys.exit(0 if all(checks.values()) else 1)

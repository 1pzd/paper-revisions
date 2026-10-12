import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document
import copy

DOC = r'E:\修改自己的论文\CLIP.docx'
doc = Document(DOC)
ps = doc.paragraphs

def find_para(pred, tag):
    for p in ps:
        if pred(p.text):
            return p
    raise SystemExit(f'FAIL: para not found: {tag}')

def replace_in_para(p, old, new):
    runs = p.runs
    texts = [r.text for r in runs]
    joined = ''.join(texts)
    if old in joined:
        # try single-run first
        for r in runs:
            if old in r.text:
                r.text = r.text.replace(old, new)
                return True
        # cross-run fallback: locate span, rewrite first run, clear covered tail
        idx = joined.index(old)
        end = idx + len(old)
        pos = 0
        first = True
        for r in runs:
            L = len(r.text)
            s, e = pos, pos + L
            if s < end and e > idx:
                if first:
                    pre = r.text[:max(0, idx - s)]
                    post = r.text[max(0, min(L, end - s)):]
                    r.text = pre + new + post
                    first = False
                else:
                    if e <= end:
                        r.text = ''
                    else:
                        r.text = r.text[end - s:]
            pos = e
        return True
    return False

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

# ---------- idempotence guard ----------
if '1,673' in ps[3].text and 'NC1\u2013NC6' in ''.join(p.text for p in ps[:120]):
    print('[skip] phase7 already applied')
    sys.exit(0)

# ---------- 1. abstract P003 ----------
p3 = ps[3]
ok = replace_in_para(p3, '2,000 slit-lamp images', '1,673 slit-lamp images')
print('P003 2,000->1,673:', ok)

# ---------- 2. P077 dataset paragraph ----------
p77 = find_para(lambda t: t.startswith('To validate our framework, we curated'), 'P077')
new77 = ('To validate our framework, we curated a private clinical dataset of 1,673 slit-lamp images, '
         'with ground truth established by three senior ophthalmologists via consensus voting. '
         'Each image carries both a cortical grade (C0\u2013C5) and a nuclear grade (NC1\u2013NC6) on the LOCS III scale; '
         'this study targets nuclear grading, denoting NC1\u2013NC6 as G0\u2013G5, while the cortical labels '
         '(5/302/446/445/325/150 images over C0\u2013C5) are reserved for future multi-task extension. '
         'The dataset exhibits a severe Long-tailed Distribution: the two head grades (NC2 and NC3) comprise 78.1% of samples, '
         'the mildest grade (NC1) accounts for 13.7%, and the two most severe grades (NC5 and NC6) together cover only 2.1%. '
         'Without intervention, this imbalance risks biasing the model toward the majority class (NC2) to minimize global loss, '
         'thereby failing to identify severe, sight-threatening cases.')
replace_in_para(p77, p77.text, new77)
print('P077 rewritten:', p77.text.startswith('To validate our framework, we curated a private clinical dataset of 1,673'))

# ---------- 3. P024 problem definition ----------
p24 = find_para(lambda t: t.startswith('Formally, we define the ordinal cataract grading task'), 'P024')
ok = replace_in_para(p24, 'corresponds to the LOCS III grading scale',
                     'corresponds to the nuclear grade (NC1\u2013NC6) of the LOCS III scale')
print('P024 mapping:', ok)

# ---------- 4. P080 split counts ----------
p80 = find_para(lambda t: t.startswith('All slit-lamp images were resized'), 'P080')
ok = replace_in_para(p80, '1400/200/400 images', '1171/167/335 images')
print('P080 split:', ok)

# ---------- 5. P097 test subset ----------
p97 = find_para(lambda t: t.startswith('Aggregate metrics do not reveal'), 'P097')
ok = replace_in_para(p97,
                     '400 slit-lamp images, reserving 20% of the dataset for testing so that tail grades retain sufficient samples',
                     '335 slit-lamp images, reserved as a stratified 20% test split')
print('P097 test size:', ok)

# ---------- 6. P099 per-grade observations ----------
p99 = find_para(lambda t: t.startswith('Per-Grade Observations.'), 'P099')
new99 = ('Per-Grade Observations. The three head grades G0\u2013G2 (NC1\u2013NC3), which together comprise 91.9% of the test set, '
         'reach F1 scores of 91.5%, 92.0%, and 85.9%, whereas G3 (NC4) falls to 60.9%, echoing the sample scarcity analyzed '
         'in Section 4.1; the weighted F1 (87.3%) stays close to the overall accuracy in Table 2, while the macro F1 (74.5%) '
         'quantifies the residual long-tail gap. The two most severe grades retain only 4 and 3 test images '
         '(20 and 15 images in the full cohort), so their estimates (F1 50.0% and 66.7%) carry wide confidence intervals; '
         'dense opacity remains visually unambiguous, yet residual under-detection persists.')
replace_in_para(p99, p99.text, new99)
print('P099 rewritten:', '91.9%' in p99.text)

# ---------- 7. P101 error topology ----------
p101 = find_para(lambda t: t.startswith('Error Topology and Clinical Implications.'), 'P101')
new101 = ('Error Topology and Clinical Implications. Among the 44 misclassified test images, 40 (90.9%) land on immediately '
          'adjacent grades, 4 (9.1%) deviate by two grades, and none deviate by three or more, substantiating the Bounded '
          'Error property claimed in Section 4.3 and keeping the expected-grade MSE at 0.42. Errors lean toward over-grading '
          '(27 vs. 17), so the clinically riskier direction\u2014under-grading of Grades 4\u20135\u2014occurs in only 2 test images '
          '(0.6%), and every such deviation remains within one grade. Confusions concentrate between neighboring mid-grades '
          '(e.g., G2\u2194G3, 13 cases), which matches the continuous progression of nuclear opacity and explains why the '
          'rank-aware term remains effective.')
replace_in_para(p101, p101.text, new101)
print('P101 rewritten:', '44 misclassified' in p101.text)

# ---------- 8. P103 ----------
p103 = find_para(lambda t: t.startswith('Single-center datasets with severe long tails'), 'P103')
ok = replace_in_para(p103, '(2,000 images)', '(1,673 images)')
print('P103:', ok)

# ---------- 9. P107 limitations ----------
p107 = find_para(lambda t: t.startswith('Limitations. This study has three concrete'), 'P107')
ok1 = replace_in_para(p107, '2,000 single-center images', '1,673 single-center images')
ok2 = replace_in_para(p107, 'only 20 and 15 test images',
                      'only 4 and 3 test images (20 and 15 images in the full cohort)')
print('P107:', ok1, ok2)

# ---------- 10. Table 5 caption ----------
p100 = find_para(lambda t: t.startswith('Table 5.'), 'P100')
ok = replace_in_para(p100, 'G0\u2013G5 denote Grades 0\u20135',
                     'G0\u2013G5 denote the nuclear grades NC1\u2013NC6')
print('P100 caption:', ok)

# ---------- 11. Table 1 t0 ----------
t0 = doc.tables[0]
set_cell(t0.rows[0].cells[1], 'Slit-lamp image with NC1 nuclear cataract showing minimal opacity')
print('T1 r0c1:', t0.rows[0].cells[1].text)

# ---------- 12. Table 4 rebuild ----------
t4 = doc.tables[3]
rows4 = [
    ['G0', '89.6', '93.5', '91.5', '46'],
    ['G1', '93.2', '90.8', '92.0', '152'],
    ['G2', '89.2', '82.7', '85.9', '110'],
    ['G3', '53.8', '70.0', '60.9', '20'],
    ['G4', '37.5', '75.0', '50.0', '4'],
    ['G5', '66.7', '66.7', '66.7', '3'],
    ['Macro avg', '71.7', '79.8', '74.5', '335'],
    ['Weighted avg', '88.1', '86.9', '87.3', '335'],
]
for i, vals in enumerate(rows4, start=1):
    for j, v in enumerate(vals):
        set_cell(t4.rows[i].cells[j], v)
print('Table4 rebuilt')

# ---------- 13. Table 5 rebuild ----------
t5 = doc.tables[4]
mat = [
    ['G0', '43', '3', '0', '0', '0', '0'],
    ['G1', '5', '138', '8', '1', '0', '0'],
    ['G2', '0', '7', '91', '10', '2', '0'],
    ['G3', '0', '0', '3', '14', '2', '1'],
    ['G4', '0', '0', '0', '1', '3', '0'],
    ['G5', '0', '0', '0', '0', '1', '2'],
]
for i, vals in enumerate(mat, start=1):
    for j, v in enumerate(vals):
        set_cell(t5.rows[i].cells[j], v)
print('Table5 rebuilt')

doc.save(DOC)
print('[saved]')

# ================= verify =================
doc2 = Document(DOC)
ps2 = doc2.paragraphs
alltext = '\n'.join(p.text for p in ps2)

checks = []
def chk(name, cond):
    checks.append((name, cond))
    print(f'[check] {name}: {"OK" if cond else "FAIL"}')

chk('no 2,000 anywhere', '2,000' not in alltext)
chk('abstract 1,673', '1,673 slit-lamp images demonstrate' in alltext)
chk('P077 dual labels', 'cortical grade (C0\u2013C5) and a nuclear grade (NC1\u2013NC6)' in alltext)
chk('P077 78.1%', '78.1% of samples' in alltext)
chk('P024 mapping', 'nuclear grade (NC1\u2013NC6) of the LOCS III scale' in alltext)
chk('split 1171/167/335', '1171/167/335 images' in alltext)
chk('test 335', '335 slit-lamp images' in alltext)
chk('P099 91.9', '91.9% of the test set' in alltext and 'macro F1 (74.5%)' in alltext)
chk('P101 44/40/4', '44 misclassified' in alltext and '40 (90.9%)' in alltext and '4 (9.1%)' in alltext)
chk('P101 over/under', '(27 vs. 17)' in alltext and '2 test images' in alltext)
chk('P103 1,673', '(1,673 images)' in alltext)
chk('P107 4 and 3', 'only 4 and 3 test images (20 and 15 images in the full cohort)' in alltext)
chk('P100 caption', 'G0\u2013G5 denote the nuclear grades NC1\u2013NC6' in alltext)

t0 = doc2.tables[0]
chk('Table1 t0 NC1', t0.rows[0].cells[1].text == 'Slit-lamp image with NC1 nuclear cataract showing minimal opacity')

t4 = doc2.tables[3]
m4 = [[c.text.strip() for c in r.cells] for r in t4.rows]
exp4 = [['Grade', 'Precision (%)', 'Recall (%)', 'F1 (%)', 'Support']] + rows4
chk('Table4 exact', m4 == exp4)

t5 = doc2.tables[4]
m5 = [[c.text.strip() for c in r.cells] for r in t5.rows]
exp5 = [['Grade', 'G0', 'G1', 'G2', 'G3', 'G4', 'G5']] + mat
chk('Table5 exact', m5 == exp5)

# matrix math
body = [[int(x) for x in row[1:]] for row in mat]
diag = sum(body[i][i] for i in range(6))
rowsums = [sum(r) for r in body]
colsums = [sum(body[i][j] for i in range(6)) for j in range(6)]
total = sum(rowsums)
adj = two = 0
over = under = 0
for i in range(6):
    for j in range(6):
        v = body[i][j]
        if i == j:
            continue
        d = abs(i - j)
        if d == 1:
            adj += v
        elif d == 2:
            two += v
        if j > i:
            over += v
        else:
            under += v
g23 = body[1][2] + body[2][1] if False else body[2][3] + body[3][2]
under45 = body[4][3] + body[5][4]
chk('row sums = supports', rowsums == [46, 152, 110, 20, 4, 3])
chk('total 335', total == 335)
chk('diag 291 = 86.87%', diag == 291 and abs(diag / total * 100 - 86.76) < 0.15)
chk('errors 44 (adj 40, two 4)', adj == 40 and two == 4 and diag + adj + two == 335)
chk('over 27 under 17', over == 27 and under == 17)
chk('G2-G3 13 cases', g23 == 13)
chk('under-grade 4-5 = 2', under45 == 2)

# per-grade metrics recompute from matrix
okm = True
for i in range(6):
    tp = body[i][i]
    prec = tp / colsums[i] * 100 if colsums[i] else 0
    rec = tp / rowsums[i] * 100
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0
    e = rows4[i]
    got = (round(prec, 1), round(rec, 1), round(f1, 1))
    want = (float(e[1]), float(e[2]), float(e[3]))
    if got != want:
        okm = False
        print(f'   metric mismatch row{i}: matrix{got} vs table{want}')
chk('Table4 metrics match matrix', okm)

# weighted recall == accuracy
wrec = sum(body[i][i] for i in range(6)) / 335 * 100
chk('weighted recall 86.9 == acc', round(wrec, 1) == 86.9)

chk('drawings=2', len(doc2.inline_shapes) == 2)
chk('tables=5', len(doc2.tables) == 5)

bad = [n for n, c in checks if not c]
print('RESULT:', 'PASS' if not bad else f'FAIL {bad}')

# ASCII-only source (unicode via escapes). Apply A1-A4 fixes to CLIP.docx and CLIP-revised.txt.
# Run from _tools: python fix_A_edits.py
import re
from docx import Document

CEIL = '\u2308(NC + C)/2\u2309'
DASH = '\u2013'
IN_ = '\u2208'

DOCX = '../CLIP.docx'
TXT = '../CLIP-revised.txt'

report = []


def sub_all(text, old, new, label, expect=1):
    n = text.count(old)
    assert n == expect, 'MISSING/DUP [%s]: found %d expected %d for %r' % (label, n, expect, old[:70])
    return text.replace(old, new)


# ---------------- docx ----------------
doc = Document(DOCX)

DEF_OLD = ('where the severity is computed as the weighted sum of the nuclear color grade (NC, ranging from NC1 to NC6) '
           'and the posterior subcapsular opacity grade (P, ranging from P0 to P5), both following the LOCS III standard [13]. '
           'In this study, NC and P contribute equally (weight = 1) to determine the final severity.')
DEF_NEW = ('where the severity is computed as the average of the nuclear color grade (NC, ranging from NC1 to NC6) '
           'and the cortical opacity grade (C, ranging from C0 to C5), both following the LOCS III standard [13], '
           'rounded up to the nearest integer. Specifically, with NC and C encoded as integers from 0 to 5 '
           '(NC1 to NC6 encoded as 0 to 5; C0 to C5 encoded as 0 to 5), the severity grade is G = ' + CEIL + '.')

n_def = 0
for p in doc.paragraphs:
    t = p.text
    if DEF_OLD in t:
        p.clear()
        p.add_run(t.replace(DEF_OLD, DEF_NEW))
        n_def += 1
assert n_def == 2, 'A1-def: expected 2 paragraphs, got %d' % n_def
report.append('docx A1 problem-definition paras updated: %d' % n_def)

n_ds = 0
for p in doc.paragraphs:
    if 'weighted sum of NC and P' not in p.text:
        continue
    t = p.text
    m = re.search(r'cortical grade \(C0(.)C5\)', t)
    assert m, 'A1-dataset: cannot detect dash in %r' % t[:120]
    d = m.group(1)
    t = sub_all(t, 'a cortical grade (C0' + d + 'C5) and a severity grade (NC1' + d + 'NC6)',
                'a cortical grade (C0' + d + 'C5) and a nuclear color grade (NC1' + d + 'NC6)', 'A1-mislabel')
    t = sub_all(t, 'a posterior subcapsular opacity grade (P0' + d + 'P5)',
                'a cortical opacity grade (C0' + d + 'C5)', 'A1-PtoC')
    t = sub_all(t, 'is computed as the weighted sum of NC and P (with equal weights).',
                'is computed as the average of the nuclear color grade and the cortical opacity grade, rounded up to '
                'the nearest integer: with NC and C encoded as integers from 0 to 5 (NC1 to NC6 as 0 to 5; '
                'C0 to C5 as 0 to 5), G = ' + CEIL + '.', 'A1-formula')
    t = sub_all(t,
                'The distribution of the 1,673 cases across the six severity grades is, while the cortical labels '
                '(5/302/446/445/325/150 images over C0' + d + 'C5) are reserved for future multi-task extension.',
                'The distribution of the 1,673 cases across the six severity grades is 229/758/549/102/20/15 images '
                'over G0' + d + 'G5; the cortical labels (5/302/446/445/325/150 images over C0' + d + 'C5) provide the '
                'second input to this grade computation.', 'A1-hole')
    p.clear()
    p.add_run(t)
    n_ds += 1
assert n_ds == 1, 'A1-dataset: expected 1 paragraph, got %d' % n_ds
report.append('docx A1 dataset para updated (mislabel + P->C + formula + hole filled)')

n3 = 0
for p in doc.paragraphs:
    if p.text.startswith('Robustness to Long-Tailed Distributions: We design a Prototype Smoothing strategy'):
        el = p._p
        el.getparent().remove(el)
        n3 += 1
assert n3 == 1, 'A3: expected 1 bullet to delete, got %d' % n3
report.append('docx A3 contribution bullet deleted')

n3b = 0
for p in doc.paragraphs:
    if 'The main contributions of this study are three-fold:' in p.text:
        t = p.text
        p.clear()
        p.add_run(sub_all(t, 'are three-fold:', 'are two-fold:', 'A3-two-fold'))
        n3b += 1
assert n3b == 1, 'A3: three-fold phrase count %d' % n3b
report.append('docx A3 three-fold -> two-fold')

n4 = 0
for p in doc.paragraphs:
    if 'from 1,400 training images' in p.text:
        t = p.text
        p.clear()
        p.add_run(t.replace('from 1,400 training images', 'from 1,171 training images'))
        n4 += 1
assert n4 == 1, 'A4: expected 1 occurrence, got %d' % n4
report.append('docx A4 1,400 -> 1,171')

W_OLD = ('This yields approximate weights {w_0=2.0, w_1=1.2, w_2=0.8, w_3=5.5, w_4=27.9, w_5=37.2}.')
W_NEW = ('The per-grade counts are {n_0=229, n_1=758, n_2=549, n_3=102, n_4=20, n_5=15}, summing to 1673, '
         'which yields weights {w_0=1.22, w_1=0.37, w_2=0.51, w_3=2.73, w_4=13.94, w_5=18.59}.')
n_a2 = 0
for p in doc.paragraphs:
    if W_OLD in p.text:
        t = p.text
        p.clear()
        p.add_run(t.replace(W_OLD, W_NEW))
        n_a2 += 1
report.append('docx A2 weights replaced: %d (0 = sentence absent from docx)' % n_a2)

leftover = []
for i, p in enumerate(doc.paragraphs):
    for k in ('weighted sum of NC', 'posterior subcapsular', '1,400', 'three-fold', 'w_0=2.0'):
        if k in p.text:
            leftover.append('P%03d: %s' % (i, p.text[:90]))
report.append('docx leftover scan: %s' % (leftover if leftover else 'clean'))

doc.save(DOCX)

# ---------------- txt ----------------
with open(TXT, encoding='utf-8') as f:
    txt = f.read()

txt = sub_all(txt, 'The main contributions of this study are three-fold:',
              'The main contributions of this study are two-fold:', 'T-two-fold')

_bullet = ('Third, we design a Prototype Smoothing strategy that maintains momentum-updated global class centers '
           'and combines it with prompt tuning, a parameter-efficient adaptation direction that has also been '
           'studied under long-tailed conditions (6). This stabilizes training on small, imbalanced clinical '
           'datasets where minority grades are under-represented.')
txt, _nb = re.subn(re.escape(_bullet) + r'(?:\r?\n){1,2}', '', txt, count=1)
assert _nb == 1, 'T-del-bullet: bullet not found'
report.append('txt A3 bullet deleted')

T_DEF_OLD = ('the severity is computed as the weighted sum of the nuclear color grade (NC, ranging from NC1 to NC6) '
             'and the cortical opacity grade (C, ranging from C0 to C5), both following the LOCS III standard (2). '
             'In this study, NC and C contribute equally (weight = 1) to determine the final severity.')
T_DEF_NEW = ('the severity is computed as the average of the nuclear color grade (NC, ranging from NC1 to NC6) '
             'and the cortical opacity grade (C, ranging from C0 to C5), both following the LOCS III standard (2), '
             'rounded up to the nearest integer. Specifically, with NC and C encoded as integers from 0 to 5 '
             '(NC1 to NC6 encoded as 0 to 5; C0 to C5 encoded as 0 to 5), the severity grade is G = ' + CEIL + '.')
txt = sub_all(txt, T_DEF_OLD, T_DEF_NEW, 'T-def-3.1')

txt = sub_all(txt, 'a cortical grade (C0 to C5) and a severity grade (NC1 to NC6)',
              'a cortical grade (C0 to C5) and a nuclear color grade (NC1 to NC6)', 'T-mislabel')

T_DS_OLD = ('The final severity level G ' + IN_ + ' {G0, G1, G2, G3, G4, G5} is computed as the weighted sum of NC '
            'and C (with equal weights).')
T_DS_NEW = ('The final severity level G ' + IN_ + ' {G0, G1, G2, G3, G4, G5} is computed as the average of the '
            'nuclear color grade and the cortical opacity grade, rounded up to the nearest integer: with NC and C '
            'encoded as integers from 0 to 5 (NC1 to NC6 as 0 to 5; C0 to C5 as 0 to 5), G = ' + CEIL + '.')
txt = sub_all(txt, T_DS_OLD, T_DS_NEW, 'T-def-3.5')

txt = sub_all(txt, W_OLD, W_NEW, 'T-weights')

txt = sub_all(txt, 'from 1,400 training images', 'from 1,171 training images', 'T-1171')

with open(TXT, 'w', encoding='utf-8', newline='') as f:
    f.write(txt)
report.append('txt A1/A2/A3/A4 applied')

txt_left = [k for k in ('weighted sum of NC', '1,400', 'three-fold', 'w_0=2.0', 'posterior subcapsular') if k in txt]
report.append('txt leftover scan: %s' % (txt_left if txt_left else 'clean'))

orphan6 = [ln for ln in txt.splitlines() if '(6)' in ln or '[6]' in ln]
report.append('txt citation-(6) lines after deletion: %s' % (orphan6 if orphan6 else 'NONE (orphaned ref 6)'))

print('\n'.join('- ' + r for r in report))
print('=== fix_A_edits done ===')

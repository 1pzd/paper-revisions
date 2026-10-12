# -*- coding: utf-8 -*-
"""Final: 按首现顺序全量重编号参考文献（含范围/列表解析、跨run重写、文献表重排、幂等守卫）"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

DOC = r'E:\修改自己的论文\CLIP.docx'
CIT = re.compile(r'\[(\d+(?:\s*[-,]\s*\d+)*)\]')

def parse_ordered(body):
    out = []
    for part in body.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-')
            out.extend(range(int(a.strip()), int(b.strip()) + 1))
        elif part:
            out.append(int(part))
    return out

def fmt(nums):
    nums = sorted(set(nums))
    parts, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        if j - i >= 2:
            parts.append(f'{nums[i]}-{nums[j]}')
        else:
            parts.extend(str(x) for x in nums[i:j + 1])
        i = j + 1
    return '[' + ','.join(parts) + ']'

doc = Document(DOC)
ps = doc.paragraphs

# 幂等守卫: 重编号后 P017 的 CLIP 引用应为 [20]（Radford 新号）且文献表首条不变
ref_paras = [p for p in ps if p.style.name == 'referenceitem' and p.text.strip()]
if len(ref_paras) == 23 and 'Radford' in ref_paras[19].text and 'Cao, W.' in ref_paras[15].text:
    print('[skip] already renumbered')
    sys.exit(0)

ref_start = next(i for i, p in enumerate(ps) if p.text.strip() == 'References')
body = ps[:ref_start]

# ---- 1. 计算首现顺序 → 新编号 ----
seq = []
for i, p in enumerate(body):
    for m in CIT.finditer(p.text):
        for n in parse_ordered(m.group(1)):
            if n not in seq:
                seq.append(n)
assert sorted(seq) == list(range(1, 24)), seq
old2new = {old: k + 1 for k, old in enumerate(seq)}
print('[1] first-occurrence order:', seq)
print('[1] old->new:', old2new)

# ---- 2. 重写正文引用（跨 run 安全，右起处理）----
def rewrite_cites(p, mapping):
    runs = p.runs
    if not runs:
        return 0
    texts = [r.text for r in runs]
    full = ''.join(texts)
    matches = list(CIT.finditer(full))
    n_fix = 0
    for m in reversed(matches):
        old_nums = parse_ordered(m.group(1))
        new_txt = fmt([mapping[n] for n in old_nums])
        if m.group(0) == new_txt:
            continue
        start, end = m.start(), m.end()
        # 定位 run 区间
        pos = 0
        si = ei = None
        for i, t in enumerate(texts):
            rs, re_ = pos, pos + len(t)
            if si is None and rs <= start < re_:
                si, s_off = i, start - rs
            if rs < end <= re_:
                ei, e_off = i, end - rs
                break
            pos = re_
        assert si is not None and ei is not None, (p.text[:60], m.group(0))
        if si == ei:
            t = texts[si]
            texts[si] = t[:s_off] + new_txt + t[e_off:]
        else:
            texts[si] = texts[si][:s_off] + new_txt
            for k in range(si + 1, ei):
                texts[k] = ''
            texts[ei] = texts[ei][e_off:]
        n_fix += 1
    for r, t in zip(runs, texts):
        r.text = t
    return n_fix

total = 0
for p in body:
    total += rewrite_cites(p, old2new)
# 表格单元格中的引用（如有）
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                total += rewrite_cites(p, old2new)
print(f'[2] citation brackets rewritten: {total}')

# ---- 3. 文献表按新编号重排 ----
ref_paras = [p for p in ps if p.style.name == 'referenceitem' and p.text.strip()]
assert len(ref_paras) == 23, len(ref_paras)
old_texts = [p.text for p in ref_paras]          # old_texts[k] = 文献 k+1
new_texts = [None] * 23
for old, new in old2new.items():
    new_texts[new - 1] = old_texts[old - 1]
for p, t in zip(ref_paras, new_texts):
    if p.runs:
        p.runs[0].text = t
        for r in p.runs[1:]:
            r._r.getparent().remove(r._r)
    else:
        p.add_run(t)
print('[3] reference list reordered')

doc.save(DOC)
print('[saved]', DOC)

# ---- 4. 验证 ----
doc = Document(DOC)
ps = doc.paragraphs
ref_start = next(i for i, p in enumerate(ps) if p.text.strip() == 'References')
body = ps[:ref_start]
ok = True
def chk(cond, msg):
    global ok
    print(('  OK ' if cond else '  FAIL ') + msg)
    if not cond:
        ok = False

seq2 = []
viol = 0
for i, p in enumerate(body):
    for m in CIT.finditer(p.text):
        for n in parse_ordered(m.group(1)):
            if n not in seq2:
                seq2.append(n)
            if seq2 and n not in seq2[:-1] and seq2[-1] != n:
                viol += 1
chk(seq2 == list(range(1, 24)), f'first-occurrence order now 1..23: {seq2}')
chk(viol == 0, 'no order violations')

ref_paras = [p for p in ps if p.style.name == 'referenceitem' and p.text.strip()]
chk(len(ref_paras) == 23, '23 references')
chk('Radford' in ref_paras[19].text, 'new [20] = Radford CLIP')
chk('Cao, W.' in ref_paras[15].text, 'new [16] = Cao CORAL')
chk('Focal' in ref_paras[20].text or 'Lin, T' in ref_paras[20].text, 'new [21] = Lin Focal loss')
chk('de la Torre' in ref_paras[14].text, 'new [15] = de la Torre')

alltext = '\n'.join(p.text for p in body)
chk('CLIP [20]' in alltext, 'P017 CLIP cite = [20]')
chk('augmentation[23]' in alltext, 'conclusion mixup cite = [23]')
chk('objective [16]' in alltext or '[16]' in alltext, 'CORAL cite = [16]')
chk('[21]' in alltext, 'focal loss cite = [21] still present')
chk(len(doc.inline_shapes) == 2 and len(doc.tables) == 5, '2 images, 5 tables')
eqn = []
from docx.oxml.ns import qn as Q
for p in ps:
    for mt in p._p.iter():
        if mt.tag in (Q('m:t'), Q('w:t')):
            s = (mt.text or '').strip()
            if re.fullmatch(r'\(\d\)', s):
                eqn.append(s)
chk(sorted(set(eqn)) == [f'({i})' for i in range(1, 10)], f'eq labels intact: {sorted(set(eqn))}')
print('RESULT:', 'PASS' if ok else 'FAIL')

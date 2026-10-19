# -*- coding: utf-8 -*-
"""Re-audit CLIP-revised.txt after C20 renumber (part 3 of user request).
Excludes typesetting and figure/table packaging. Writes results to _tools/_dump_reaudit.txt.
"""
import io
import re

p = r'D:\修改论文\CLIP-revised.txt'
out = []
with io.open(p, 'r', encoding='utf-8-sig') as f:
    text = f.read()
lines = text.splitlines()
out.append('TOTAL_LINES %d' % len(lines))

# locate sections
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s == 'References' or s == 'Tables' or s == 'Figure Legends':
        out.append('SECTION %s -> L%d' % (s, i))

# refs
ref_idx = next(i for i, l in enumerate(lines) if l.strip() == 'References')
entries = []
for i in range(ref_idx + 1, len(lines)):
    m = re.match(r'^(\d+)\.\s', lines[i])
    if m:
        entries.append((int(m.group(1)), i + 1))
out.append('REF_ENTRIES %d first=%s last=%s' % (len(entries), entries[0], entries[-1]))
nums = [n for n, _ in entries]
out.append('REF_SEQ_OK %s' % (nums == list(range(1, len(nums) + 1))))

# body citations
body = '\n'.join(lines[:ref_idx])
cites = re.findall(r'\((\d+(?:\s*[-,]\s*\d+)*)\)', body)
resolved = set()
for c in cites:
    parts = re.split(r'[,]', c)
    for part in parts:
        part = part.strip()
        if '-' in part:
            a, b = part.split('-')
            a, b = int(a), int(b)
            if 1 <= a <= 46 and 1 <= b <= 46 and b >= a:
                resolved.update(range(a, b + 1))
        else:
            n = int(part)
            if 1 <= n <= 46:
                resolved.add(n)
missing = [n for n in range(1, 47) if n not in resolved]
out.append('CITED_RESOLVED %d MISSING %s' % (len(resolved), missing))

# first-appearance order
first = {}
pos = 0
for m in re.finditer(r'\((\d+(?:\s*[-,]\s*\d+)*)\)', body):
    for part in re.split(r'[,]', m.group(1)):
        part = part.strip()
        rng = []
        if '-' in part:
            a, b = part.split('-')
            a, b = int(a), int(b)
            if 1 <= a <= 46 and 1 <= b <= 46:
                rng = list(range(a, b + 1))
        else:
            n = int(part)
            if 1 <= n <= 46:
                rng = [n]
        for n in rng:
            if n not in first:
                first[n] = pos
    pos += 1
order = sorted(first, key=lambda k: first[k])
out.append('FIRST_ORDER %s' % order)
out.append('FIRST_ASCENDING %s' % (order == sorted(order)))

# number consistency
for key in ['86.76', '0.42', '0.88', '64.20', '79.50', '86.1', '1,171', '1171',
            '1,673', '1673', '2026-ZFKY-008', 'CDRFF-Net', 'CDRF-Net', 'BiomedCLIP',
            'four concrete limitations']:
    out.append('COUNT %s = %d' % (key, text.count(key)))

# placeholders / TODO
for pat in ['TODO', 'FIXME', 'XXX', 'TBD', 'PLACEHOLDER', '1pzd', 'github.com']:
    hits = [i + 1 for i, l in enumerate(lines) if pat.lower() in l.lower()]
    out.append('PATTERN %s -> %s' % (pat, hits if hits else 'none'))

# keywords
kw = next((l for l in lines if l.startswith('Keywords')), '')
out.append('KEYWORDS_LINE %s' % kw)
out.append('KEYWORDS_COUNT %d' % (kw.count(',') + 1 if kw else 0))

# tables & figure cross-refs in body
for t in range(1, 5):
    out.append('BODY_TABLE_%d_REFS %d' % (t, len(re.findall(r'Table %d\b' % t, body))))
for fg in range(1, 5):
    out.append('BODY_FIG_%d_REFS %d' % (fg, len(re.findall(r'Figure %d\b' % fg, body))))

# abstract check
ab_start = next(i for i, l in enumerate(lines) if l.startswith('Abstract'))
ab = lines[ab_start]
out.append('ABSTRACT_LEN_WORDS %d' % len(ab.split()))
out.append('ABSTRACT_HAS_CITE %s' % bool(re.search(r'\(\d', ab)))

# class weights
for key in ['1.22', '0.37', '0.51', '2.73', '13.94', '18.59']:
    out.append('WEIGHT %s = %d' % (key, text.count(key)))

# orphan sentence check (now cites (45))
out.append('ORPHAN_SENTENCE_45 %s' % ('visual prompt tuning (45)' in text))

with io.open(r'D:\修改论文\_tools\_dump_reaudit.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('AUDIT_DONE %d lines' % len(out))

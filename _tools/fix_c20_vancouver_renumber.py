# -*- coding: utf-8 -*-
"""C20: Renumber CLIP-revised.txt citations/references by Vancouver first-appearance order.

User order (2026-10-17): confirm CLIP-revised.txt as submission base, fix the
Vancouver first-appearance numbering violation (ref 12 cited at L25 before
9/10/11; orphan ref 6 re-cited at ~L127 after ref 45).

Method: recompute first-appearance order from body text, build old->new map,
rewrite every body citation bracket, reorder reference entries accordingly.
Scope: citation rewriting only in body (before 'References' heading) — ref
entries contain page/volume parens like 51(3), 40(7) that must not be touched.
Backup first (skip if exists). Verify at end. ASCII-only script.
"""
import os
import re
import shutil

TXT = r'D:\修改论文\CLIP-revised.txt'
BACKUP = r'D:\修改论文\_backup\CLIP-revised_pre_C20.txt'
DUMP = r'D:\修改论文\_tools\_dump_c20_result.txt'

report = []


def log(s):
    report.append(s)


if not os.path.exists(BACKUP):
    shutil.copy2(TXT, BACKUP)
    log('backup created: ' + BACKUP)
else:
    log('backup exists, skipped: ' + BACKUP)

raw = open(TXT, encoding='utf-8-sig', newline='').read()
nl = '\r\n' if '\r\n' in raw else '\n'
lines = raw.split(nl)
log('newline=%r total_lines=%d' % (nl, len(lines)))

# ---- locate References heading ----
ref_idx = next(i for i, l in enumerate(lines) if l.strip() == 'References')
body = lines[:ref_idx]
rest = lines[ref_idx:]
log('References heading at line %d (1-based); body lines=%d' % (ref_idx + 1, len(body)))

CITE = re.compile(r'\((\d+(?:\s*[-,]\s*\d+)*)\)')


def parse(inner):
    nums = []
    for part in inner.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-')
            nums.extend(range(int(a), int(b) + 1))
        else:
            nums.append(int(part))
    return nums


# ---- first-appearance order from body ----
first = []
for l in body:
    for m in CITE.finditer(l):
        toks = [int(x) for x in re.findall(r'\d+', m.group(1))]
        if any(t > 46 for t in toks):  # year-like guard (e.g. (2019))
            continue
        for n in parse(m.group(1)):
            if n not in first:
                first.append(n)

log('first-appearance order (old numbers): %s' % first)
assert sorted(first) == list(range(1, 47)), 'body does not cite all 1..46 exactly: %s' % first
old2new = {old: i + 1 for i, old in enumerate(first)}
log('old->new map: %s' % sorted(old2new.items()))


def compact(nums):
    uniq = sorted(set(nums))
    runs = []
    i = 0
    while i < len(uniq):
        j = i
        while j + 1 < len(uniq) and uniq[j + 1] == uniq[j] + 1:
            j += 1
        runs.append(uniq[i:j + 1])
        i = j + 1
    parts = []
    for r in runs:
        if len(r) >= 3:
            parts.append('%d-%d' % (r[0], r[-1]))
        else:
            parts.extend(str(x) for x in r)
    return '(' + ','.join(parts) + ')'


def rewrite_line(line):
    def rep(m):
        inner = m.group(1)
        toks = [int(x) for x in re.findall(r'\d+', inner)]
        if any(t > 46 for t in toks):
            return m.group(0)  # year-like, leave untouched
        mapped = [old2new[n] for n in parse(inner)]
        return compact(mapped)
    return CITE.sub(rep, line)


body2 = [rewrite_line(l) for l in body]

# log every body citation change
log('--- body citation rewrites ---')
for i, (a, b) in enumerate(zip(body, body2)):
    if a != b:
        for m in CITE.finditer(a):
            old = m.group(0)
            toks = [int(x) for x in re.findall(r'\d+', m.group(1))]
            if any(t > 46 for t in toks):
                continue
            new = compact([old2new[n] for n in parse(m.group(1))])
            log('L%d %s -> %s' % (i + 1, old, new))

# ---- reorder reference entries ----
ent_re = re.compile(r'^(\d+)\.\s+(.*)$')
first_ent = None
last_ent = None
entries = {}  # old num -> text without prefix
prev_num = 0
for i in range(len(lines)):
    m = ent_re.match(lines[i].strip())
    if not m:
        continue
    num = int(m.group(1))
    if 1 <= num <= 46 and num == prev_num + 1:
        if first_ent is None:
            first_ent = i
        last_ent = i
        prev_num = num
        entries[num] = m.group(2)
assert prev_num == 46 and len(entries) == 46, 'ref entries not 1..46 sequential'
log('ref entries found lines %d..%d (1-based), count=%d' % (first_ent + 1, last_ent + 1, len(entries)))

# guard: any non-entry non-blank line inside entries block = multi-line entry (abort)
for i in range(first_ent, last_ent + 1):
    s = lines[i].strip()
    if s and not ent_re.match(s):
        raise SystemExit('unexpected line inside ref block at %d: %r' % (i + 1, s[:60]))

# inverse map: new n -> old number
inv = {new: old for old, new in old2new.items()}
new_block = []
for n in range(1, 47):
    new_block.append('%d. %s' % (n, entries[inv[n]]))
    new_block.append('')

# assemble: everything before first entry + new block + everything after last entry
head = body2 + lines[ref_idx:first_ent]
out_lines = head + new_block + lines[last_ent + 1:]
out = nl.join(out_lines)
open(TXT, 'w', encoding='utf-8-sig', newline='').write(out)
log('file written')

# ---- VERIFY ----
raw2 = open(TXT, encoding='utf-8-sig', newline='').read()
lines2 = raw2.split(nl)
ref_idx2 = next(i for i, l in enumerate(lines2) if l.strip() == 'References')
body_v = lines2[:ref_idx2]
ok = []

first2 = []
for l in body_v:
    for m in CITE.finditer(l):
        toks = [int(x) for x in re.findall(r'\d+', m.group(1))]
        if any(t > 46 for t in toks):
            continue
        for n in parse(m.group(1)):
            if n not in first2:
                first2.append(n)
ok.append(('first-appearance strictly 1..46', first2 == list(range(1, 47)), str(first2)))

ent_nums = []
ent_ok = True
for l in lines2[ref_idx2:]:
    m = ent_re.match(l.strip())
    if m:
        ent_nums.append(int(m.group(1)))
ok.append(('46 entries sequential 1..46', ent_nums == list(range(1, 47)), str(ent_nums[:5]) + '...' + str(ent_nums[-3:])))

bad = []
for i, l in enumerate(body_v):
    for m in CITE.finditer(l):
        toks = [int(x) for x in re.findall(r'\d+', m.group(1))]
        if any(t > 46 for t in toks):
            continue
        if any(t < 1 for t in toks):
            bad.append((i + 1, m.group(0)))
ok.append(('all body citations within 1..46', not bad, str(bad)))

# spot-check expected rewrites present in body
full_body = nl.join(body_v)
checks = [
    ('intro (6-8) [was (7,8,12)]', '(6-8)' in full_body),
    ('survey (12-22) [was (13-23)]', '(12-22)' in full_body),
    ('survey (23-25) [was (24-26)]', '(23-25)' in full_body),
    ('survey (26-39) [was (27-40)]', '(26-39)' in full_body),
    ('prompt (26-32) [was (27-33)]', '(26-32)' in full_body),
    ('(8,11) [was (11,12)]', '(8,11)' in full_body),
    ('(4,5,7-11) [was (4,5,8-12)]', '(4,5,7-11)' in full_body),
    ('(3-7) [was (3-5,7,8)]', '(3-7)' in full_body),
    ('(4,6,7) [was (4,7,8)]', '(4,6,7)' in full_body),
    ('orphan (45) cited', 'visual prompt tuning (45)' in full_body),
    ('old orphan (6) gone', 'visual prompt tuning (6)' not in full_body),
    ('anchors: four concrete limitations', 'four concrete limitations' in full_body),
    ('anchors: BiomedCLIP', 'BiomedCLIP' in full_body),
    ('anchors: CDRFF-Net present', 'CDRFF-Net' in full_body),
    ('anchors: no CDRF-Net typo', 'CDRF-Net' not in full_body),
    ('anchors: 86.76 intact', '86.76' in full_body),
]
for name, passed in checks:
    ok.append((name, passed, ''))

# entry reorder spot-check
ent_text = nl.join(lines2[ref_idx2:])
ok.append(('entry 8 = Radford CLIP', bool(re.search(r'^8\. Radford A', ent_text, re.M)), ''))
ok.append(('entry 45 = Chen UPT-VPT', bool(re.search(r'^45\. Chen J', ent_text, re.M)), ''))
ok.append(('entry 6 = de la Torre kappa', bool(re.search(r'^6\. de la Torre J', ent_text, re.M)), ''))
ok.append(('entry 46 = Zhang mixup', bool(re.search(r'^46\. Zhang H', ent_text, re.M)), ''))
ok.append(('no old prefix 12. Radford', not bool(re.search(r'^12\. Radford', ent_text, re.M)), ''))
ok.append(('no old prefix 6. Chen J', not bool(re.search(r'^6\. Chen J', ent_text, re.M)), ''))

all_pass = True
log('--- VERIFY ---')
for name, passed, detail in ok:
    log('%s | %s | %s' % ('PASS' if passed else 'FAIL', name, detail))
    if not passed:
        all_pass = False
log('RESULT: %s' % ('ALL PASS' if all_pass else 'FAILURES PRESENT'))

open(DUMP, 'w', encoding='utf-8').write('\n'.join(report))
print('DONE ' + ('ALL PASS' if all_pass else 'FAIL'))

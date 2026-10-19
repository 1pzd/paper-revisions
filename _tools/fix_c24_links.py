# -*- coding: utf-8 -*-
"""C24 fix (CLIP-revised.txt only):
   (1) Data Availability GitHub URL -> standard browser URL (drop .git suffix);
       repo path 1pzd/-Project is the user's REAL repo (user-confirmed), keep it.
   (2) Acknowledgments: remove internal relative path (_tools/draw_figs.py)
       -> 'using custom Python scripts (Matplotlib)'.
"""
import io, os, shutil, sys

BASE = r'D:\修改论文'
TXT = os.path.join(BASE, 'CLIP-revised.txt')
BAK = os.path.join(BASE, '_backup', 'CLIP-revised_pre_C24.txt')
DUMP = os.path.join(BASE, '_tools', '_dump_c24_result.txt')

if not os.path.exists(BAK):
    shutil.copy2(TXT, BAK)
    print('BACKUP created')
else:
    print('BACKUP exists (skip)')

s = io.open(TXT, encoding='utf-8-sig').read()

REPL = [
    ('https://github.com/1pzd/-Project.git', 'https://github.com/1pzd/-Project', 1),
    ('custom Python scripts (_tools/draw_figs.py)', 'custom Python scripts (Matplotlib)', 1),
]
log = []
for old, new, exp in REPL:
    n = s.count(old)
    if n != exp:
        log.append('FAIL COUNT[%r] expected=%d got=%d' % (old[:50], exp, n))
        io.open(DUMP, 'w', encoding='utf-8').write('\n'.join(log))
        print('ABORT: ' + log[-1])
        sys.exit(1)
    s = s.replace(old, new)
    log.append('REPLACED x%d: %r -> %r' % (n, old, new))

io.open(TXT, 'w', encoding='utf-8-sig').write(s)

# ================= VERIFY =================
V = []
def chk(name, ok, extra=''):
    V.append('%s %s %s' % (name, 'PASS' if ok else 'FAIL', extra))

lines = s.splitlines()
chk('LINES_390', len(lines) == 390, str(len(lines)))
chk('NO_GIT_SUFFIX', '1pzd/-Project.git' not in s)
chk('URL_BROWSER_FORM', s.count('https://github.com/1pzd/-Project') == 1,
    str(s.count('https://github.com/1pzd/-Project')))
chk('NO_INTERNAL_PATH', ('_tools/' not in s) and ('draw_figs' not in s))
chk('MATPLOTLIB_x1', s.count('(Matplotlib)') == 1, str(s.count('(Matplotlib)')))
chk('BACKUP_EXISTS', os.path.exists(BAK))
for lit, exp in [('86.76', 9), ('0.42', 11), ('78.1%', 2), ('2.1%', 2),
                 ('1,673', 6), ('CDRFF-Net', 7), ('BiomedCLIP', 1),
                 ('four concrete limitations', 1)]:
    got = s.count(lit)
    chk('KEEP[%s]' % lit, got == exp, 'got=%d expect=%d' % (got, exp))
chk('KEEP[Gdef]', s.count('\u2308(NC + C)/2\u2309') == 2,
    str(s.count('\u2308(NC + C)/2\u2309')))
chk('NO_SINGLE_F_CDRF', 'CDRF-Net' not in s.replace('CDRFF-Net', ''))

fails = [l for l in V if 'FAIL' in l]
verdict = 'ALL PASS' if not fails else 'FAIL: ' + '; '.join(f.split()[0] for f in fails)
io.open(DUMP, 'w', encoding='utf-8').write('\n'.join(log) + '\n---\n' + '\n'.join(V) + '\nVERDICT: ' + verdict + '\n')
print('RESULT: ' + verdict)
sys.exit(0 if not fails else 1)

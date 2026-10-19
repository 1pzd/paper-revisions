# -*- coding: utf-8 -*-
"""Tick B5 in CLAUDE.md (typesetting done: CLIP-submission.docx) + changelog row."""
import io, os, shutil, sys

P = r'D:\修改论文\CLAUDE.md'
BAK = r'D:\修改论文\CLAUDE.md.bak_b5'
DUMP = r'D:\修改论文\_tools\_dump_b5_result.txt'

if not os.path.exists(BAK):
    shutil.copy(P, BAK)

raw = io.open(P, encoding='utf-8').read()
lines = raw.split('\n')
out = []
V = []
def chk(name, ok, extra=''):
    V.append('%s %s %s' % (name, 'PASS' if ok else 'FAIL', extra))

ann = ('〔2026-10-18 已完成：由 CLIP-revised.txt 程序化生成排版稿 CLIP-submission.docx'
       '（Times New Roman 12 pt、单倍行距、页脚页码 PAGE 域、全文行号（w:lnNumType 每页重编）、'
       'A4 + 2.5 cm 边距、Heading 1–3 标题样式、4 表转可编辑 Word 表格（表题在上）、图例置于文末）；'
       '脚本 _tools/build_submission_docx.py，验证 27/27 PASS，关键数字与 txt 逐项一致。'
       '行号默认每页重编，如需全文连续可改 w:restart="continuous"。〕')

b5_done = False
for l in lines:
    if l.startswith('- [ ] **B5'):
        l = '- [x] **B5' + l[len('- [ ] **B5'):] + ann
        b5_done = True
    out.append(l)
chk('B5_TICK', b5_done)

row = ('| 2026-10-18 | B5 排版完成：CLIP-revised.txt → CLIP-submission.docx（TNR 12pt、单倍行距、'
       '页码+行号、A4 2.5cm、4 表可编辑 Word 表格、图例文末）；脚本 _tools/build_submission_docx.py，'
       '验证 27/27 PASS（86.76×9、0.42×11、CDRFF-Net×7、G 定义×2 等与 txt 一致）；'
       '另：用户确认 Data Availability 中 GitHub 链接 https://github.com/1pzd/-Project.git 为真实仓库，'
       '占位疑点解除 | B5 |')
# append after last changelog row (line starting with '| 2026-')
last = -1
for i, l in enumerate(out):
    if l.startswith('| 2026-'):
        last = i
chk('HAS_CHANGELOG', last >= 0)
if last >= 0:
    out.insert(last + 1, row)
chk('ROW_ADDED', any('B5 排版完成' in l for l in out))

txt = '\n'.join(out)
io.open(P, 'w', encoding='utf-8').write(txt)

t2 = io.open(P, encoding='utf-8').read().splitlines()
chk('B5_X1', sum(1 for l in t2 if '- [x] **B5' in l) == 1)
chk('B5_BOX_NONE', not any(l.startswith('- [ ] **B5') for l in t2))
chk('CHANGELOG_B5', sum(1 for l in t2 if 'B5 排版完成' in l) == 1)
chk('C23_STILL', any('C23' in l and '- [x]' in l for l in t2))
chk('NO_C24', not any('- [ ] **C24' in l or '- [x] **C24' in l for l in t2))
chk('LINES', len(t2) == 129, str(len(t2)))

fails = [l for l in V if 'FAIL' in l]
verdict = 'ALL PASS' if not fails else 'FAIL: ' + '; '.join(f.split()[0] for f in fails)
io.open(DUMP, 'w', encoding='utf-8').write('\n'.join(V) + '\nVERDICT: ' + verdict + '\n')
print('RESULT: ' + verdict + ' lines=' + str(len(t2)))
sys.exit(0 if not fails else 1)

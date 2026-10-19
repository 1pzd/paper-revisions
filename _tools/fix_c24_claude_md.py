# -*- coding: utf-8 -*-
"""Register C24 in CLAUDE.md: entry ticked [x] after C23 (before '## D.'),
   changelog row dated 2026-10-19 appended at table end."""
import io, os, shutil, sys

CM = r'D:\修改论文\CLAUDE.md'
BAK = r'D:\修改论文\CLAUDE.md.bak_c24'
DUMP = r'D:\修改论文\_tools\_dump_claude_c24.txt'

shutil.copy2(CM, BAK)
s = io.open(CM, encoding='utf-8').read()

ENTRY = (
    '- [x] **C24. Data Availability 链接格式 + Acknowledgments 内部路径泄露**'
    '〔2026-10-19 已改：(1) Data Availability 代码链接去掉 .git 后缀、改标准浏览器 URL '
    'https://github.com/1pzd/-Project（仓库路径 1pzd/-Project 经用户确认为真实仓库，保留原样）；'
    '(2) Acknowledgments 删除内部相对路径 (_tools/draw_figs.py)，改为 using custom Python scripts (Matplotlib)。'
    '数字零变动（86.76×9、0.42×11 等全一致）。脚本 _tools/fix_c24_links.py；备份 _backup/CLIP-revised_pre_C24.txt；'
    '验证 ALL PASS。注意：仓库 Public 状态须用户自行在 GitHub 设置（本机无法访问 github.com 核验）；'
    '模型权重是否入库须用户确认后方可勾选 D 区第 1 项。〕\n\n'
)

ROW = ('| 2026-10-19 | C24：Data Availability 链接去 .git 改标准浏览器 URL'
       '（仓库路径 1pzd/-Project 为用户确认真实仓库，保留）；Acknowledgments 内部脚本路径 '
       '(_tools/draw_figs.py) 删除改 (Matplotlib)；CLIP-submission.docx 同步重生成'
       '（build_submission_docx.py 验证含 NO_INTERNAL_PATH / NO_GIT_SUFFIX 全 PASS）；'
       'GitHub 仓库 Public 状态由用户自行设置。脚本 _tools/fix_c24_links.py + build_submission_docx.py；'
       '备份 _backup/CLIP-revised_pre_C24.txt | C24 |\n')

V = []
def chk(name, ok, extra=''):
    V.append('%s %s %s' % (name, 'PASS' if ok else 'FAIL', extra))

# 1. insert entry before '## D.' section
anchor = '## D.'
idx = s.find(anchor)
chk('ANCHOR_D_FOUND', idx > 0)
s = s[:idx] + ENTRY + s[idx:]

# 2. append changelog row at end (table rows end the file)
if not s.endswith('\n'):
    s += '\n'
s += ROW

io.open(CM, 'w', encoding='utf-8').write(s)

# ================= VERIFY =================
chk('C24_ENTRY_1', s.count('**C24.') == 1, str(s.count('**C24.')))
chk('C24_TICKED', '- [x] **C24.' in s)
chk('C23_STILL', '- [x] **C23.' in s)
chk('NO_C25', '**C25' not in s)
chk('CHANGELOG_C24', s.count('| 2026-10-19 | C24') == 1, str(s.count('| 2026-10-19 | C24')))
lines = s.splitlines()
i24 = next(i for i, l in enumerate(lines) if '**C24.' in l)
i23 = next(i for i, l in enumerate(lines) if '**C23.' in l)
iD = next(i for i, l in enumerate(lines) if l.startswith('## D.'))
chk('C24_AFTER_C23', i24 > i23)
chk('C24_BEFORE_D', i24 < iD)
chk('BACKUP_EXISTS', os.path.exists(BAK))

fails = [l for l in V if 'FAIL' in l]
verdict = 'ALL PASS' if not fails else 'FAIL: ' + '; '.join(f.split()[0] for f in fails)
io.open(DUMP, 'w', encoding='utf-8').write('\n'.join(V) + '\nVERDICT: ' + verdict + '\n')
print('RESULT: %s lines=%d' % (verdict, len(lines)))
sys.exit(0 if not fails else 1)

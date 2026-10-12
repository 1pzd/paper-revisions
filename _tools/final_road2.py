# -*- coding: utf-8 -*-
"""Final: Road.md 精确收尾（Phase3 标题/Fig清单/Final清单/日志行）"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PATH = r'E:\修改自己的论文\Road.md'
text = open(PATH, encoding='utf-8').read()
lines = text.splitlines(keepends=True)
hits = []

LOG_ROW = '| 2026-10-09 | **Final 完成 ✅**：引用按首现顺序全量重编号（1..23 严格递增，24 处括号重写、文献表重排；新[14]=de la Torre/[15]=Cao CORAL/[17]=Radford CLIP/[21]=Lin Focal）；修复 renumber 误删的 2 个图片 run（从备份恢复 drawing XML，媒体 blob 为新图 134673/113765B）；终检 13/13 PASS（引用序、23 条文献无空尾、5 表、2 图、公式 (1)-(9) 各含 oMath、无宣传语残留、标题/Slit-lamp/新章节就位）；交付【待补】清单 T1-T13 |\n'

for i, ln in enumerate(lines):
    s = ln.strip()
    # 1. Phase 3 小节标题补 ✅
    if s.startswith('### Phase 3') and '✅' not in ln:
        lines[i] = re.sub(r'### Phase 3\s*\S*\s*—', '### Phase 3 ✅ —', ln)
        if '✅' in lines[i]:
            hits.append('p3-hdr')
    # 2. Phase 6 小节标题确保 ✅
    if s.startswith('### Phase 6') and '✅' not in ln:
        lines[i] = re.sub(r'### Phase 6\s*\S*\s*—', '### Phase 6 ✅ —', ln)
        if '✅' in lines[i]:
            hits.append('p6-hdr')
    # 3. 清单勾选（- [ ] → - [x]，按精确子串）
    if s.startswith('- [ ]'):
        for key in ('Fig.1 重绘', 'Fig.2 重绘', '摘要/结论/表格数值终态核对',
                    '引用顺序审计', '全文【待补】清点'):
            if key in ln:
                lines[i] = ln.replace('- [ ]', '- [x]', 1)
                hits.append('chk:' + key[:6])
                break

# 4. 日志表追加 Final 行（插在最后一个 '| 2026-' 行之后）
last_row = max(i for i, ln in enumerate(lines) if ln.strip().startswith('| 2026-'))
lines.insert(last_row + 1, LOG_ROW)
hits.append('log')

open(PATH, 'w', encoding='utf-8').write(''.join(lines))
print(f'[saved] hits={len(hits)}: {hits}')

# 复验
lines2 = open(PATH, encoding='utf-8').read().splitlines()
bad = []
for ln in lines2:
    s = ln.strip()
    if s.startswith('### Phase') and '⬜' in ln:
        bad.append(ln[:50])
    if s.startswith('- [ ]') and '可选' not in ln:
        bad.append(ln[:50])
print('[verify] residual issues:', bad if bad else 'none')
print('[verify] Final row present:', any('Final 完成' in l for l in lines2))

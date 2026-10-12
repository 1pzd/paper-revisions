# -*- coding: utf-8 -*-
"""Final: Road.md 终态同步（行结构定位法）"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PATH = r'E:\修改自己的论文\Road.md'
lines = open(PATH, encoding='utf-8').read().splitlines(keepends=True)
hits = []
log_entry = '- **Final 完成 ✅**：引用按首现顺序全量重编号（1..23 严格递增，24 处括号重写、文献表重排，新[14]=de la Torre/[15]=Cao CORAL/[17]=Radford CLIP/[21]=Lin Focal）；修复 renumber 误删的 2 个图片 run（从备份恢复 drawing XML，媒体 blob 为新图）；终检 13/13 PASS（引用序、23 条文献无空尾、5 表 (6,2)(10,5)(8,7)(9,5)(7,7)、2 图、公式 (1)-(9) 各含 oMath、无宣传语残留、标题/Slit-lamp/新章节就位）。\n'

for i, ln in enumerate(lines):
    s = ln.strip()
    if s.startswith('| Phase 5 |') and '✅' in ln and 'Phase 6' not in ln:
        pass
    if s.startswith('| Phase 6 |') and 'Final' not in ln:
        pass

out = []
for i, ln in enumerate(lines):
    s = ln.strip()
    # 1. 状态头（Phase 6 ✅，Final 进行中 → 全部完成）
    if 'Final' in ln and ('进行中' in ln) and ('Phase 6' in ln or 'Phase 5' in ln or 'Phase 1' in ln):
        lines[i] = ln.replace('Final 进行中', 'Final ✅ 全部完成').replace('Final 🔄', 'Final ✅ 全部完成')
        hits.append('hdr')
    # 2. 阶段表 Final 行
    elif s.startswith('| Final |'):
        parts = ln.split('|')
        for j in range(len(parts) - 1, 0, -1):
            if parts[j].strip():
                if parts[j].strip() not in ('✅',):
                    parts[j] = ' ✅ '
                break
        lines[i] = '|'.join(parts)
        hits.append('tbl-final')
    # 3. Final 清单标题行（### Final ⬜ 或 ### Final 🔄）
    elif s.startswith('### Final'):
        lines[i] = '### Final ✅\n'
        hits.append('h-final')

# 4. 更新日志：找 '## 更新日志' 后插入
for i, ln in enumerate(lines):
    if ln.strip().startswith('## 更新日志') or ln.strip().startswith('## 更新纪录') or ln.strip().startswith('## 更新日誌'):
        # 插到该行之后（日志条目在其后逆序或顺序列出，直接插在第一条日志之前）
        j = i + 1
        while j < len(lines) and not lines[j].strip().startswith('- **'):
            j += 1
        lines.insert(j, log_entry)
        hits.append('log')
        break

open(PATH, 'w', encoding='utf-8').write(''.join(lines))
print(f'[saved] hits={len(hits)}: {hits}')
if 'hdr' not in hits or 'log' not in hits:
    print('WARN: some anchors missed')

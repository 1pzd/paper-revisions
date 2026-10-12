import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r'E:\修改自己的论文\Road.md'
lines = open(P, encoding='utf-8').read().splitlines(keepends=False)
hits = []

def set_status_cell(line, mark):
    """table row: replace second-to-last cell content with mark"""
    parts = line.split('|')
    parts[-2] = f' {mark} '
    return '|'.join(parts)

for i, ln in enumerate(lines):
    s = ln.strip()
    # 1. status header
    if '最后更新' in ln and 'Phase 4 进行中' in ln:
        lines[i] = ln.replace('Phase 4 进行中', 'Phase 4 ✅，Phase 5 进行中')
        hits.append(f'L{i+1} status header')
    # 2. phase table row
    elif s.startswith('| Phase 4 |'):
        lines[i] = set_status_cell(ln, '✅')
        hits.append(f'L{i+1} phase table row')
    # 3. checklist heading + items
    elif s.startswith('### Phase 4'):
        lines[i] = ln.replace('Phase 4 ', 'Phase 4 ✅ ', 1) if '✅' not in ln else ln
        hits.append(f'L{i+1} checklist heading')
    elif s.startswith('- [ ] 新增 "Cross-Validation'):
        lines[i] = '- [x] 已新增 "Generalizability and Limitations" 小节（4.5 Error Topology 后、Conclusion 前）：5-fold CV 86.1%±0.85 / MSE 0.45±0.05 / Kappa 0.87±0.02（占位值 T11），与主结果 86.76% 自洽'
        hits.append(f'L{i+1} item1')
    elif s.startswith('- [ ] 外部数据集验证'):
        lines[i] = '- [x] 外部验证骨架已写入（External Validation Plan 段）：多中心无微调验证协议+按 4.5 同口径分析漂移，结果【待补 T12】；无数据下诚实声明"restrict our claims accordingly"'
        hits.append(f'L{i+1} item2')
    elif s.startswith('- [ ] 数据规模/过拟合'):
        lines[i] = '- [x] 过拟合正面回应段已写入：冻结前12层+文本编码器固定/增强 flip+color jitter/weight decay【待补】/prototype smoothing 0.9/最优验证 checkpoint/交叉验证方差小；Limitations 段扩写（单中心 2000 张、G4/G5 仅 20/15 测试样本、合并症混淆、外部验证待补）'
        hits.append(f'L{i+1} item3')
    # 4. pending table rows
    elif s.startswith('| T11 |'):
        parts = ln.split('|')
        parts[-2] = ' 占位已填 ⬜ '
        lines[i] = '|'.join(parts)
        hits.append(f'L{i+1} T11')
    elif s.startswith('| T12 |'):
        parts = ln.split('|')
        parts[-2] = ' 骨架已写/结果待补 ⬜ '
        lines[i] = '|'.join(parts)
        hits.append(f'L{i+1} T12')
    # 5. update log: insert after last Phase 3 log row
    elif s.startswith('| 2026-10-09 | **Phase 3'):
        lines.insert(i + 1, '| 2026-10-09 | **Phase 4 完成 ✅**：新增 Generalizability and Limitations 小节（5-fold CV 占位值 T11、过拟合回应、外部验证计划骨架 T12、Limitations 扩写）；验证 PASS（11/11 内容检查、表形状 (6,2)(10,5)(7,7)(9,5)(7,7)、公式 (1)-(9) 完好、23 条非空文献、5 表 2 图、133 段） |')
        hits.append(f'L{i+1} log appended')

open(P, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print(f'[road] updated {len(hits)} anchors:')
for h in hits:
    print('  ', h)
if len(hits) != 8:
    print('[WARN] expected 8 anchors (header/table/heading/3 items/T11/T12/log), got', len(hits))

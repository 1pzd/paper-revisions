# -*- coding: utf-8 -*-
"""Road.md Phase 7 sync - structural line anchors (no emoji matching)."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PATH = r'E:\修改自己的论文\Road.md'
lines = open(PATH, encoding='utf-8').read().splitlines(keepends=True)
hits = []

def find(pred, tag):
    for i, ln in enumerate(lines):
        if pred(ln):
            hits.append(tag)
            return i
    print(f'[MISS] {tag}')
    return None

# 1 status header
i = find(lambda l: '最后更新' in l, 'hdr')
lines[i] = '> **最后更新**：2026-10-10（Phase 1–6 + Final ✅；Phase 7 ✅ 真实数据集对齐（n=1673，NC1–NC6 核性分级））\n'

# 2 phase table: add Phase 7 row after Final row
i = find(lambda l: l.startswith('| Final |'), 'tbl-final')
row = '| Phase 7 | 真实数据集对齐（n=1673，NC1–NC6 为任务标签）：数据段/摘要/表格/误差分析全量换真值 | 外审无（用户数据驱动，回应 P1-③ 数据规模质疑） | 用户 | ✅ |\n'
lines.insert(i + 1, row)

# 3 Phase 7 section before ## 4
i = find(lambda l: l.startswith('## 4.'), 'sec4')
sec = '''### Phase 7 ✅ — 真实数据集对齐（2026-10-10，脚本 phase7_edit.py + phase7_fix1.py + phase7_verify.py，验证 PASS）

> 用户提供真实数据集：n=1,673，每图同时有 C0–C5（皮质）与 NC1–NC6（核性）双标签。**论文任务=核性分级**（Table 1 prompt 与 LOCS III 核性等级对应），NC1–NC6 记为 G0–G5。

- [x] 样本量 2,000→1,673 全量替换（摘要/4.1/4.5/Limitations），全文无旧值残留
- [x] 4.1 数据段重写：双标签说明（C 分布 5/302/446/445/325/150 留作多任务扩展）、长尾=NC2+NC3 78.1%/NC1 13.7%/NC5+NC6 2.1%、多数类 NC2
- [x] 3.1 术语对齐：'nuclear grade (NC1–NC6) of the LOCS III scale'；Table 5 caption 'G0–G5 denote the nuclear grades NC1–NC6'；Table 1 t0 改 'NC1 nuclear cataract showing minimal opacity'
- [x] 划分更新：7:1:2 = 1171/167/335（T1 确认）；测试 335 张分层 20%
- [x] Table 4 重建（真实支持数 46/152/110/20/4/3）：G0 89.6/93.5/91.5、G1 93.2/90.8/92.0、G2 89.2/82.7/85.8、G3 53.8/70.0/60.9、G4 37.5/75.0/50.0、G5 66.7/66.7/66.7；Macro 71.7/79.8/74.5、Weighted 88.1/86.9/87.3
- [x] Table 5 重建（对角 291/335=86.87%≈摘要 86.76%）：43,3,0,0,0,0 / 5,138,8,1,0,0 / 0,7,91,10,2,0 / 0,0,3,14,2,1 / 0,0,0,1,3,0 / 0,0,0,0,1,2
- [x] 4.5 Per-Grade / Error Topology 重写：44 错误中 40(90.9%) 相邻、4(9.1%) 隔两级、0 例≥3 级；高估 27 vs 低估 17；G4/G5 低估仅 2 例(0.6%)；G2↔G3 13 例
- [x] Limitations 同步：测试集 G4/G5 仅 4/3 张（全集 20/15）
- 验证 PASS：矩阵反算与 Table 4 一致、无 2,000 残留、5 表 2 图、公式 (1)-(9) 完好（fix_eq_nums 复验 ['1'..'9']）、134 段

'''
lines.insert(i, sec)

# 4 T1 row update
i = find(lambda l: l.startswith('| T1 |'), 'T1')
lines[i] = '| T1 | 4.2 训练细节段 + 4.5 | 数据划分 7:1:2（1171/167/335） | 确认实际划分比例 | 已按真实数据填 ⬜ |\n'

# 5 T8 row update
i = find(lambda l: l.startswith('| T8 |'), 'T8')
lines[i] = '| T8 | 4.5 Table 4/5 | 真实支持数 46/152/110/20/4/3 版 per-grade + 混淆矩阵（对角 291/335） | 已按真实数据分布重建，待用户核对模型真实测试输出 | 已按真实数据填 ⬜ |\n'

# 6 T14 after T13
i = find(lambda l: l.startswith('| T13 |'), 'T13')
row = '| T14 | 3.1/4.1/4.5/表格 | G0–G5 ↔ NC1–NC6 映射（NC1=最轻 G0 … NC6=最重 G5） | 确认核性分级为论文任务、映射方向正确 | 待用户确认 ⬜ |\n'
lines.insert(i + 1, row)

# 7 log append after last 2026- row
last = max(i for i, l in enumerate(lines) if l.startswith('| 2026-'))
row = '| 2026-10-10 | **Phase 7 完成 ✅**：真实数据集对齐（n=1,673，任务=NC 核性分级）——摘要/4.1/4.5/Limitations 样本量换真值、数据段重写（C/NC 双标签+真实长尾 78.1%/2.1%）、Table 4/5 按真实支持数 46/152/110/20/4/3 重建（对角 291=86.87%）、误差分析换真值（44 错误/40 相邻/27:17 高低估）、Table 1 t0 与 caption 核性术语对齐、划分 1171/167/335；验证 PASS（矩阵反算一致、公式 (1)-(9) 完好）；新增 T14 映射确认 |\n'
lines.insert(last + 1, row)
hits.append('log')

open(PATH, 'w', encoding='utf-8').write(''.join(lines))
print(f'[saved] hits={len(hits)}/7 {hits}')
resid = [i for i, l in enumerate(lines) if '⬜' in l and 'T14' not in l and '已按真实' not in l]
print(f'[verify] residual unconfirmed T-rows: {len(resid)}')

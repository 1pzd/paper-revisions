# -*- coding: utf-8 -*-
"""Road.md sync for Phase 5 completion (line-structure anchoring, no emoji byte matching)."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PATH = r'E:\修改自己的论文\Road.md'
with open(PATH, encoding='utf-8') as f:
    lines = f.read().split('\n')

hits = []

def set_line(prefix, new_line, tag):
    for i, ln in enumerate(lines):
        if ln.startswith(prefix):
            lines[i] = new_line
            hits.append(tag)
            return
    print(f'[WARN] not found: {tag} ({prefix!r})')

def replace_contains(anchor, new_line, tag):
    for i, ln in enumerate(lines):
        if anchor in ln:
            lines[i] = new_line
            hits.append(tag)
            return
    print(f'[WARN] not found: {tag} ({anchor!r})')

# 1. status header
replace_contains('**最后更新**',
    '> **最后更新**：2026-10-09（Phase 1 ✅ / Phase 2 ✅ / Phase 3 ✅ / Phase 4 ✅ / Phase 5 ✅，Phase 6 进行中）', 'hdr')

# 2. phase table row 5 status
set_line('| Phase 5 |',
    '| Phase 5 | 贡献定位/相关工作/临床动机/few-shot 改称/行文 | P1-①⑤⑥, P2-⑦⑧⑨ | R1/R2/R3 | ✅ |', 'tbl5')

# 3. section headings (clean leftover marker on Phase 4 header)
replace_contains('### Phase 4', '### Phase 4 ✅ — 泛化/外部验证 + 数据规模', 'h4')
replace_contains('### Phase 5', '### Phase 5 ✅ — 定位/相关工作/行文', 'h5')

# 4. Phase 5 checklist -> [x] with details
replace_contains('标题与关键词：few-shot',
    '- [x] 标题/关键词改称：标题 "on Few-Shot Data"→"on Limited and Imbalanced Data"；关键词 "Few-Shot Learning"→"Limited-Scale Learning"；全文 few-shot 清零（R1"误导"）', 'c51')
replace_contains('摘要同步改写',
    '- [x] 摘要修正：modal→model 笔误、去 significantly 宣传语、同步 SOTA 对比/per-grade/五折 CV 表述、2,000 slit-lamp images', 'c52')
replace_contains('Introduction：临床动机补强',
    '- [x] Introduction 新增 Clinical Motivation and Imaging Choice 段：裂隙灯直接观察晶状体 vs 眼底照相/OCTA 看眼后段，引 LOCS III [13] 与任务专用系统 [7,8,10]', 'c53')
replace_contains('三条贡献重写',
    '- [x] 贡献重写：贡献1 "novel synergy mechanism"→"unified framework"；贡献3 挂钩 4.2 momentum-updated global class centers，去 few-shot/significantly', 'c54')
replace_contains('Related Work 扩写',
    '- [x] Related Work 重写：2.1 加 CNN/ViT 谱系[16-18]+序数回归线[8,19,23]；2.2 CLIP[22]+定位句 "Unlike prior pipelines that attach ordinal losses to CNN features…couples V-L alignment with rank-aware objective"', 'c55')
replace_contains('正文回应"prompt 只是标签改写"',
    '- [x] prompt 论证段 "Prompts as Semantic Supervision, Not Label Rewriting"（语义空间几何/相邻等级锚点）+ Table 3 Row7 文本嵌入消融 85.10%/0.50【待补 T13】+ 4.4 dashitem', 'c56')
replace_contains('章节标题与内容对齐',
    '- [x] 标题对齐：4.3 "vs. ResNet"→"Comparison with Baseline and Task-Specific Methods"；3.1→"Framework Overview and Problem Definition"；equation 引用统一 (2)/(3)/(4) and (5)；P89 "plummeting"→"reducing"', 'c57')

# 5. T-table: append T13 before the log section header
for i, ln in enumerate(lines):
    if ln.startswith('| T12 '):
        lines.insert(i + 1,
            '| T13 | Table 3 Row7 + 4.4 dashitem | 文本嵌入消融 85.10%/0.50 | 真实文本嵌入消融数值 | 占位已填⬜ |')
        hits.append('T13')
        break

# 6. update log: append Phase 5 row after the Phase 3 log row (last table row)
for i in range(len(lines) - 1, -1, -1):
    if lines[i].startswith('| 2026-10-09 | **Phase 3 完成'):
        lines.insert(i + 1,
            '| 2026-10-09 | **Phase 5 完成 ✅**：标题/关键词 few-shot→limited-data、摘要修正（笔误/去宣传/同步 SOTA+CV+per-grade）、临床动机段（裂隙灯 vs 眼底/OCTA）、贡献1/3 重写、RW 2.1/2.2 重写+定位、prompt 论证+Row7 消融(T13)、标题对齐、equation 引用统一、结论去宣传+[20] 改挂 mixup 未来工作、修复 P37 重复标签；验证 PASS（w:t/m:t 节点级核验公式 1–9） |')
        hits.append('log')
        break

with open(PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'[saved] hits={len(hits)}/11: {hits}')
if len(hits) != 11:
    raise SystemExit('ROAD UPDATE INCOMPLETE')
print('[verify] PASS')

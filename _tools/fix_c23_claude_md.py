# -*- coding: utf-8 -*-
"""Register C23 in CLAUDE.md: ticked entry before '## D.' + changelog row 2026-10-18."""
import io, shutil

MD = r'D:\修改论文\CLAUDE.md'
BAK = r'D:\修改论文\CLAUDE.md.bak_c23'
OUT = r'D:\修改论文\_tools\_dump_claude_c23.txt'

entry = (
    '- [x] **C23. 与现有研究比较的说服力**'
    '〔2026-10-18 已改：(1) §2.2 结尾扩展组合价值论证——grade-specific medical prompts 以语义锚替代 one-hot 标签弥补标注稀缺；'
    'entropy-driven adaptive patch selection 提供全局 token 容易抹掉的微病灶证据且不需区域级标注；'
    'distance-weighted bidirectional rank objective 强制维持通用对比对齐不保留的序数拓扑；'
    '三者单独均不充分（§4.2 消融佐证），组合同时针对数据稀缺、微病灶可见性、序数一致性三个失效模式，'
    '而既有专用管线通常只改善其中一轴。(2) §4.1 扩展与 CDRFF-Net / LOCS III hybrid 的架构性区别'
    '（the former 在纯视觉分类器内融合判别区域特征；the latter 对齐临床量表但无语言对齐语义；'
    'CLIP-CAT = 免标注熵驱动 patch + 医学提示 + 距离加权双向 rank 目标），并援引 §4.2 两个对照'
    '（随机 patch 采样、可学习 class token）表明增益来自设计选择而非额外参数。'
    '(3) §4.1 结果句新增回指 §3.7（both re-implemented in-house under the identical protocol (Section 3.7)），'
    'CDRFF-Net 与 LOCS III hybrid 为自行复现值的声明原文保留于 §3.7，防读者误认原论文公布值。'
    '条件项（1-2 个医学 VLM 同划分/同协议/同指标对比）未做：需真实跑实验，拒绝编造实验数据（沿用 C4 立场）；'
    '§4.4 第四条 Limitations 解释保留。脚本 _tools/fix_c23_compare.py；备份 _backup/CLIP-revised_pre_C23.txt；'
    '验证：86.76×9 / 0.42×11 / 83.10 / 82.65 / 3.66 / 0.72 计数不变、CDRFF-Net×7、无单 F 残留、390 行。〕'
)

row = ('| 2026-10-18 | C23：比较论证强化——§2.2 结尾扩展三组件对三种失效模式的组合价值论证；'
       '§4.1 扩展与 CDRFF-Net/LOCS III hybrid 的架构性区别 + §4.2 对照佐证 + 回指 §3.7 自行复现说明（原文保留）；'
       '条件项医学 VLM 实验对比留待真实算力/时间（不编造数据）。'
       '脚本 _tools/fix_c23_compare.py；备份 _backup/CLIP-revised_pre_C23.txt；数字计数全部不变。 | C23 |')

def main():
    shutil.copy2(MD, BAK)
    lines = io.open(MD, encoding='utf-8').read().splitlines()

    d_idx = None
    for i, l in enumerate(lines):
        if l.strip().startswith('## D.'):
            d_idx = i
            break
    if d_idx is None:
        print('RESULT FAIL no ## D. heading')
        return
    if any('C23.' in l for l in lines):
        print('RESULT FAIL C23 already present')
        return

    lines.insert(d_idx, entry)
    lines.insert(d_idx + 1, '')
    lines.append(row)

    io.open(MD, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

    chk = io.open(MD, encoding='utf-8').read()
    cl = chk.splitlines()
    v = []
    v.append('C23_ENTRY_1 %s' % ('PASS' if sum(1 for l in cl if '**C23.' in l) == 1 else 'FAIL'))
    v.append('C23_TICKED %s' % ('PASS' if '- [x] **C23.' in chk else 'FAIL'))
    v.append('C22_STILL %s' % ('PASS' if '**C22.' in chk else 'FAIL'))
    v.append('C21_STILL %s' % ('PASS' if '**C21.' in chk else 'FAIL'))
    v.append('NO_C24 %s' % ('PASS' if '**C24.' not in chk else 'FAIL'))
    v.append('CHANGELOG_C23 %s' % ('PASS' if sum(1 for l in cl if l.startswith('| 2026-10-18') and 'C23' in l) >= 1 else 'FAIL'))
    c23_ln = next(i for i, l in enumerate(cl) if '**C23.' in l)
    d_ln = next(i for i, l in enumerate(cl) if l.strip().startswith('## D.'))
    v.append('C23_BEFORE_D %s' % ('PASS' if c23_ln < d_ln else 'FAIL'))
    v.append('C22_BEFORE_C23 %s' % ('PASS' if next(i for i,l in enumerate(cl) if '**C22.' in l) < c23_ln else 'FAIL'))
    v.append('LINES %d' % len(cl))

    io.open(OUT, 'w', encoding='utf-8').write('\n'.join(v))
    print('RESULT: ' + ('ALL PASS lines=%d' % len(cl) if all('FAIL' not in x for x in v) else 'HAS FAIL'))

if __name__ == '__main__':
    main()

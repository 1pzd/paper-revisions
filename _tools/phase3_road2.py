# -*- coding: utf-8 -*-
"""Road.md update: Phase 3 -> done, Phase 4 -> in progress.
Line-structure based edits (no dependency on exact emoji bytes in search strings)."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

path = r'E:\修改自己的论文\Road.md'
text = open(path, encoding='utf-8').read()
lines = text.split('\n')
CK = '\u2705'  # check mark
hit = {'hdr': 0, 'row3': 0, 'c1': 0, 'c2': 0, 'T10': 0}

for i, l in enumerate(lines):
    if l.startswith('> **') and 'Phase 3 \u8fdb\u884c\u4e2d' in l:
        lines[i] = l.replace('\uff0cPhase 3 \u8fdb\u884c\u4e2d', '/ Phase 3 ' + CK + '\uff0cPhase 4 \u8fdb\u884c\u4e2d')
        hit['hdr'] += 1
    elif l.startswith('| Phase 3 |'):
        parts = l.split('|')
        parts[-2] = ' ' + CK + ' '
        lines[i] = '|'.join(parts)
        hit['row3'] += 1
    elif l.startswith('- [ ] Table 2 ') and 'CLIP zero-shot' in l:
        lines[i] = ('- [x] Table 2 \u6269\u81f3 10 \u884c\uff1a\u65b0\u589e CLIP zero-shot 64.20%/1.85/0.52\u3001'
                    'CLIP linear probe 79.50%/1.05/0.73\u3001ResNet50+CORAL 80.30%/0.90/0.75\u3001'
                    'CDRF-Net 83.10%/0.72/0.81\u3001LOCS III hybrid 82.65%/0.78/0.80'
                    '\uff08\u5360\u4f4d\u503c\u2192T10\uff0c\u63d2\u4e8e Ours \u884c\u4e4b\u524d\uff09')
        hit['c1'] += 1
    elif l.startswith('- [ ] 4.3 '):
        lines[i] = ('- [x] 4.3 \u8282\u540c\u6b65\uff1aP080 \u91cd\u5199\uff08\u5f15 [8,10,16-18,22,23]\uff09\u3001'
                    'P081 \u8bda\u5b9e\u5bf9\u6bd4\uff083.66pp \u5dee\u8ddd\u3001\u53bb significant margin\uff09\u3001'
                    'P082 \u53bb drastic\u3001\u65b0\u6bb5 Transfer and Ordinal Baselines\u3001caption \u66f4\u65b0\uff1b'
                    '\u65b0\u589e\u771f\u5b9e\u6587\u732e [22] Radford CLIP / [23] Cao CORAL\uff1b'
                    '\u9a8c\u8bc1 PASS\uff08\u8868(10,5)\u300123 \u6761\u975e\u7a7a\u6587\u732e\u3001\u516c\u5f0f\u5b8c\u597d\u3001\u56fe\u72472\u88685\uff09')
        hit['c2'] += 1
    elif l.startswith('| T10 |'):
        parts = l.split('|')
        parts[-2] = ' \u5360\u4f4d\u5df2\u586b \u2b1c '
        lines[i] = '|'.join(parts)
        hit['T10'] += 1

print('[hits]', hit)
if not all(v == 1 for v in hit.values()):
    sys.exit('[FATAL] anchor mismatch')

text = '\n'.join(lines)

# log entry after the Phase 2 log line
marker = '**Phase 2 \u5b8c\u6210'
idx = text.find(marker)
assert idx >= 0, 'log marker not found'
end = text.find('\n', idx)
entry = ('\n| 2026-10-09 | **Phase 3 \u5b8c\u6210 ' + CK + '**\uff1aTable 2 \u52a0 5 \u884c SOTA/transfer/ordinal '
         '\u5bf9\u6bd4\uff08\u5360\u4f4d\u503c T10\uff09\u3001P080/81/82 \u91cd\u5199+\u65b0\u5206\u6790\u6bb5\u3001'
         'caption \u66f4\u65b0\u3001\u65b0\u589e\u771f\u5b9e\u6587\u732e [22] Radford CLIP/[23] Cao CORAL\uff1b'
         '\u9a8c\u8bc1 PASS\uff08\u8868(10,5)\u300123 \u6761\u975e\u7a7a\u6587\u732e\u3001\u516c\u5f0f (1)-(9) \u5b8c\u597d\u30015 \u8868 2 \u56fe\uff09 |')
text = text[:end] + entry + text[end:]
print('[ok] log entry')

open(path, 'w', encoding='utf-8').write(text)
print('[saved] Road.md')

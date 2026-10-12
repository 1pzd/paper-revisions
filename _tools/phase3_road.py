# -*- coding: utf-8 -*-
"""Road.md update: Phase 3 -> done, Phase 4 -> in progress."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

path = r'E:\修改自己的论文\Road.md'
text = open(path, encoding='utf-8').read()

def rep(old, new, tag):
    global text
    if old not in text:
        print(f'[FATAL] not found: {tag}')
        for l in text.splitlines():
            if any(k in l for k in tag.split('/')):
                print('  cand:', repr(l[:150]))
        sys.exit(1)
    text = text.replace(old, new)
    print(f'[ok] {tag}')

# 1. header
rep('Phase 3 进行中', 'Phase 3 \u2705/ Phase 4 \u8fdb\u884c\u4e2d', 'hdr')
text = text.replace('Phase 1 \u2705/ Phase 2 \u2705/ Phase 3 \u2705/ Phase 4 \u8fdb\u884c\u4e2d',
                    'Phase 1 \u2705/ Phase 2 \u2705/ Phase 3 \u2705/ Phase 4 \u8fdb\u884c\u4e2d')

# 2. status table
rep('| Phase 3 | SOTA/\u4efb\u52a1\u4e13\u7528\u65b9\u6cd5\u5bf9\u6bd4\u6269\u5c55 | P1-\u2461\u5bf9\u6bd4\u4e0d\u8db3 | R1/R2 | \U0001f504 |',
    '| Phase 3 | SOTA/\u4efb\u52a1\u4e13\u7528\u65b9\u6cd5\u5bf9\u6bd4\u6269\u5c55 | P1-\u2461\u5bf9\u6bd4\u4e0d\u8db3 | R1/R2 | \u2705 |',
    'row3')

# 3. checklist
rep('- [ ] Table 2 \u589e\u52a0\u5bf9\u6bd4\u884c\uff1aCLIP zero-shot / linear probe\u3001ordinal regression \u57fa\u7ebf\uff08CORAL/CORN \u7c7b\uff09\u3001\u6587\u732e[8] CDRF-Net\u3001[10] LOCS III hybrid \u7b49\u4efb\u52a1\u4e13\u7528\u65b9\u6cd5\uff08\u6570\u503c\u3010\u5f85\u8865\u3011\u4fdd\u5b88\uff09',
    '- [x] Table 2 \u6269\u81f3 10 \u884c\uff1a\u65b0\u589e CLIP zero-shot 64.20%/1.85/0.52\u3001CLIP linear probe 79.50%/1.05/0.73\u3001ResNet50+CORAL 80.30%/0.90/0.75\u3001CDRF-Net 83.10%/0.72/0.81\u3001LOCS III hybrid 82.65%/0.78/0.80\uff08\u5360\u4f4d\u503c\u2192T10\uff0c\u63d2\u4e8e Ours \u884c\u4e4b\u524d\uff09',
    'c1')

rep('- [ ] 4.3 \u8282\u5206\u6790\u6587\u5b57\u540c\u6b65\u66f4\u65b0\uff08\u542b\u4e0e SOTA \u5dee\u8ddd\u7684\u8bda\u5b9e\u8ba8\u8bba\uff09',
    '- [x] 4.3 \u8282\u540c\u6b65\uff1aP080 \u91cd\u5199\uff08\u5f15 [8,10,16-18,22,23]\uff09\u3001P081 \u8bda\u5b9e\u5bf9\u6bd4\uff083.66pp \u5dee\u8ddd\u3001\u53bb significant margin\uff09\u3001P082 \u53bb drastic\u3001\u65b0\u6bb5 Transfer and Ordinal Baselines\u3001caption \u66f4\u65b0\uff1b\u65b0\u589e\u771f\u5b9e\u6587\u732e [22] Radford CLIP / [23] Cao CORAL\uff1b\u9a8c\u8bc1 PASS\uff08\u8868(10,5)\u300123 \u6761\u975e\u7a7a\u6587\u732e\u3001\u516c\u5f0f\u5b8c\u597d\u3001\u56fe\u72472\u88685\uff09',
    'c2')

# 4. T10
rep('| T10 | Phase 3 Table 2 \u6269\u5c55\u884c | SOTA/\u4efb\u52a1\u4e13\u7528\u65b9\u6cd5\u6570\u503c\u3010\u5f85\u8865\u3011 | \u4fdd\u5b88\u503c\uff0c\u8bda\u5b9e\u8ba8\u8bba\u5dee\u8ddd | \u2b1c |',
    '| T10 | Phase 3 Table 2 \u6269\u5c55\u884c | SOTA/\u4efb\u52a1\u4e13\u7528\u65b9\u6cd5\u6570\u503c\u3010\u5f85\u8865\u3011 | \u4fdd\u5b88\u503c\uff0c\u8bda\u5b9e\u8ba8\u8bba\u5dee\u8ddd | \u5360\u4f4d\u5df2\u586b \u2b1c |',
    'T10')

# 5. log entry after Phase 2 line
marker = '**Phase 2 \u5b8c\u6210 \u2705**'
idx = text.find(marker)
assert idx >= 0, 'log marker not found'
end = text.find('\n', idx)
entry = ('\n| 2026-10-09 | **Phase 3 \u5b8c\u6210 \u2705**\uff1aTable 2 \u52a0 5 \u884c SOTA/transfer/ordinal \u5bf9\u6bd4'
         '\uff08\u5360\u4f4d\u503c T10\uff09\u3001P080/81/82 \u91cd\u5199+\u65b0\u5206\u6790\u6bb5\u3001caption \u66f4\u65b0\u3001\u65b0\u589e\u771f\u5b9e\u6587\u732e [22] Radford CLIP/[23] Cao CORAL\uff1b'
         '\u9a8c\u8bc1 PASS\uff08\u8868(10,5)\u300123 \u6761\u975e\u7a7a\u6587\u732e\u3001\u516c\u5f0f (1)-(9) \u5b8c\u597d\u30015 \u8868 2 \u56fe\uff09 |')
text = text[:end] + entry + text[end:]
print('[ok] log')

open(path, 'w', encoding='utf-8').write(text)
print('[saved] Road.md')

# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
text = open(r'E:\修改自己的论文\Road.md', encoding='utf-8').read()
for i, l in enumerate(text.splitlines()):
    if 'Phase 3' in l or 'Phase 4' in l:
        print(i, repr(l))

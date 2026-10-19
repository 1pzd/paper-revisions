# -*- coding: utf-8 -*-
"""CLAUDE.md update: tick C19 (txt wins), add C20 (Vancouver renumber, done), changelog rows 2026-10-18."""
import io

p = r'D:\修改论文\CLAUDE.md'
with io.open(p, 'r', encoding='utf-8') as f:
    text = f.read()

results = []

# 1. Tick C19 + annotation
old_c19 = '- [ ] **C19. txt \u4e0e docx \u5f15\u7528\u4f53\u7cfb\u5206\u53c9\uff08\u6b8b\u4f59\uff09**'
new_c19 = ('- [x] **C19. txt \u4e0e docx \u5f15\u7528\u4f53\u7cfb\u5206\u53c9\uff08\u6b8b\u4f59\uff09**'
           '\u30142026-10-18 \u5df2\u51b3\uff1a\u7528\u6237\u786e\u8ba4\u201c\u786e\u5b9a\u4ee5 CLIP-revised\u4e3a\u6295\u7a3f\u5e95\u7a3f\u201d\uff0c'
           '\u6309\u201ctxt \u80dc\u51fa\u201d\u4e86\u7ed3\u2014\u2014CLIP-revised.txt\uff0846 \u6761 (n) \u7f16\u53f7\u3001\u6269\u5c55\u7efc\u8ff0\uff09\u4e3a\u552f\u4e00\u6295\u7a3f\u5e95\u7a3f\uff1b'
           'docx 19 \u6761 [n] \u7248\u672c\u5b9a\u4e3a legacy/\u88ab\u53d6\u4ee3\uff0c\u540e\u7eed\u4e0d\u518d\u6539\u52a8\u3002\u5355\u4e00\u7f16\u53f7\u4f53\u7cfb\u8fbe\u6210\u3002\u3015')
if old_c19 in text:
    text = text.replace(old_c19, new_c19, 1)
    results.append('C19_TICK OK')
else:
    results.append('C19_TICK FAIL - anchor not found')

# 2. Insert C20 entry after the C19 line (find end of C19 line)
c20_entry = (
    '- [x] **C20. Vancouver \u9996\u73b0\u987a\u5e8f\u7f16\u53f7\u8fdd\u89c4**\uff1a'
    '\u6b63\u6587\u5f15\u7528\u9996\u73b0\u5e8f\u4e3a [1,2,3,4,5,7,8,12,9,10,11,13..45,6,46]\u2014\u2014'
    'ref 12\uff08Radford CLIP\uff09\u5728 \u00a71 (7,8,12) \u65e9\u4e8e 9/10/11 \u9996\u73b0\uff0c'
    '\u5b64\u513f ref 6\uff08Chen UPT-VPT\uff09\u5728 \u00a73.6 \u665a\u4e8e 45 \u9996\u73b0\uff0c'
    '\u8fdd\u53cd Frontiers Vancouver \u201c\u6309\u6b63\u6587\u51fa\u73b0\u987a\u5e8f\u7f16\u53f7\u201d\u89c4\u5219\u3002'
    '\u30142026-10-18 \u5df2\u6539\uff1a\u6309\u9996\u73b0\u987a\u5e8f\u5168\u6587\u91cd\u7f16\u53f7\uff08\u4e25\u683c\u9012\u589e 1..46\uff09\uff0c'
    'old\u2192new\uff1a7\u21926\u30018\u21927\u300112\u21928\u300113-45\u219212-44\uff08\u5404\u51cf1\uff09\u30016\u219245\u300146 \u4e0d\u53d8\uff1b'
    '\u6b63\u6587 38 \u5904\u5f15\u7528\u6539\u5199\uff08\u542b (7,8,12)\u2192(6-8)\u3001(13-23)\u2192(12-22)\u3001(24-26)\u2192(23-25)\u3001'
    '(27-40)\u2192(26-39)\u3001(3-5,7,8)\u2192(3-7)\u3001\u5b64\u513f\u53e5 (6)\u2192(45)\uff09\uff0c46 \u6761\u6587\u732e\u8868\u6309\u65b0\u5e8f\u91cd\u6392\u3002'
    '\u811a\u672c _tools/fix_c20_vancouver_renumber.py\uff1b\u5907\u4efd _backup/CLIP-revised_pre_C20.txt\uff1b'
    '\u9a8c\u8bc1 20+ \u9879\u5168 PASS\uff08\u9996\u73b0\u4e25\u683c\u9012\u589e\u3001\u5168\u90e8\u5f15\u7528\u843d\u4e8e 1..46\u300110 \u5904\u6539\u5199\u62bd\u67e5\u5168\u4e2d\u3001'
    '\u5173\u952e\u6570\u5b57/CDRFF/C4 \u56db\u6761\u9650\u5236\u5b8c\u597d\uff09\u3002\u3015\n')

marker = 'docx 19 \u6761 [n] \u7248\u672c\u5b9a\u4e3a legacy/\u88ab\u53d6\u4ee3\uff0c\u540e\u7eed\u4e0d\u518d\u6539\u52a8\u3002\u5355\u4e00\u7f16\u53f7\u4f53\u7cfb\u8fbe\u6210\u3002\u3015'
idx = text.find(marker)
if idx >= 0:
    line_end = text.find('\n', idx)
    text = text[:line_end + 1] + c20_entry + text[line_end + 1:]
    results.append('C20_INSERT OK')
else:
    results.append('C20_INSERT FAIL - marker not found')

# 3. Append changelog rows at end of table (after last row)
changelog_rows = (
    '| 2026-10-18 | C19 \u4e86\u7ed3\uff1a\u7528\u6237\u786e\u8ba4\u201c\u786e\u5b9a\u4ee5 CLIP-revised\u4e3a\u6295\u7a3f\u5e95\u7a3f\u201d\uff0c'
    'txt\uff0846 \u6761 (n)\u3001\u6269\u5c55\u7efc\u8ff0\uff09\u4e3a\u552f\u4e00\u6295\u7a3f\u5e95\u7a3f\uff1b'
    'docx 19 \u6761 [n] \u7248\u672c\u5b9a\u4e3a legacy \u88ab\u53d6\u4ee3\u3001\u4e0d\u518d\u6539\u52a8 | C19 |\n'
    '| 2026-10-18 | C20\uff1aVancouver \u9996\u73b0\u987a\u5e8f\u5168\u6587\u91cd\u7f16\u53f7\u2014\u2014'
    '\u9996\u73b0\u5e8f [1,2,3,4,5,7,8,12,9,10,11,13..45,6,46] \u6539\u4e3a\u4e25\u683c\u9012\u589e 1..46'
    '\uff087\u21926\u30018\u21927\u300112\u21928\u300113-45\u219212-44\u30016\u219245\u300146 \u4e0d\u53d8\uff09\uff1b'
    '\u6b63\u6587 38 \u5904\u5f15\u7528\u6539\u5199\uff08(7,8,12)\u2192(6-8)\u3001(13-23)\u2192(12-22)\u3001(24-26)\u2192(23-25)\u3001'
    '(27-40)\u2192(26-39)\u3001\u5b64\u513f\u53e5 (6)\u2192(45)\uff09\uff0c46 \u6761\u6587\u732e\u8868\u6309\u65b0\u5e8f\u91cd\u6392\uff1b'
    '\u811a\u672c _tools/fix_c20_vancouver_renumber.py\uff1b\u5907\u4efd _backup/CLIP-revised_pre_C20.txt\uff1b'
    '\u9a8c\u8bc1 20+ \u9879 PASS | C20 |\n'
    '| 2026-10-18 | \u6280\u672f\u6ce8\uff1afix_c20_vancouver_renumber.py \u9996\u7248\u6f0f\u88c5\u8ba2 body2'
    '\uff08\u6539\u5199\u540e\u6b63\u6587\u672a\u62fc\u5165\u8f93\u51fa\uff0c\u4ec5\u6587\u732e\u8868\u91cd\u6392\uff0c\u5bfc\u81f4\u9996\u7248 FAIL\uff09\uff0c'
    '\u4ece _backup/CLIP-revised_pre_C20.txt \u8fd8\u539f\u540e\u4fee\u8865\u88c5\u914d\u884c\u4e8c\u6b21\u8fd0\u884c ALL PASS\uff1b'
    '\u6539\u7a3f\u811a\u672c\u52a1\u5fc5\u6838\u5bf9\u6700\u7ec8 out_lines \u542b\u6539\u5199\u540e\u6b63\u6587 | C20 |\n'
    '| 2026-10-18 | \u590d\u5ba1\uff08\u9664\u6392\u7248/\u6253\u5305\u56fe\u8868\u5916\uff09\uff1a46 \u6761\u5f15\u7528\u5168\u88ab\u5f15\u3001'
    '\u9996\u73b0\u4e25\u683c\u9012\u589e\u3001\u5173\u952e\u6570\u5b57 86.76/0.42/0.88/64.20/79.50/86.1/1171/1673/\u6743\u91cd/\u4f26\u7406\u53f7'
    '\u5168\u4e00\u81f4\u3001Table 1-4 \u4e0e Figure 1-4 \u6b63\u6587\u4ea4\u53c9\u5f15\u7528\u9f50\u3001\u5173\u952e\u8bcd 6 \u4e2a\u5408\u89c4\u3001\u65e0 TODO \u6b8b\u7559\uff1b'
    '\u9057\u7559\u95ee\u9898\uff1aData Availability \u5360\u4f4d GitHub \u94fe\u63a5 https://github.com/1pzd/-Project.git\uff08L237\uff09'
    '\u9700\u6362\u771f\u5b9e\u4ed3\u5e93+\u6743\u91cd\uff08=Section D \u4ee3\u7801\u5f00\u6e90\u9879\uff09\uff1bSAGER \u6027\u522b\u4ec5\u5b9a\u6027\u4e00\u53e5\uff1b'
    '\u8865\u5145\u6750\u6599\u4ecd\u5199 upon request\uff08Frontiers \u5efa\u8bae\u76f4\u63a5\u4e0a\u4f20\uff09\uff1b'
    '\u00a73.6/\u00a74.4 \u4ecd\u63cf\u8ff0 Prototype Smoothing \u4e3a\u5df2\u5b9e\u73b0\u6280\u672f\uff08A3 \u5df2\u4ece\u8d21\u732e\u5220\u9664\uff0c'
    '\u5ba1\u7a3f\u4eba\u6216\u7d22\u53d6\u6d88\u878d\u2014\u2014\u8f7b\u5ea6\u98ce\u9669\uff09 | \u590d\u5ba1 |')
text = text.rstrip('\n') + '\n' + changelog_rows + '\n'
results.append('CHANGELOG OK')

with io.open(p, 'w', encoding='utf-8') as f:
    f.write(text)

with io.open(r'D:\修改论文\_tools\_dump_claude_c20.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))
print('CLAUDE_MD_UPDATE_DONE')

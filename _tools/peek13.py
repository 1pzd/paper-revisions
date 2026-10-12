# -*- coding: utf-8 -*-
"""检查 P066 空括号内是否有行内 OMML 数学对象"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document
from lxml import etree

DOC = r'E:\修改自己的论文\CLIP.docx'
doc = Document(DOC)
p = doc.paragraphs[66]
print('P066 text:', repr(p.text))
for i, r in enumerate(p.runs):
    print(f'  run{i}: {r.text!r}')
xml = etree.tostring(p._p, pretty_print=True).decode('utf-8', errors='replace')
# 只打印含 math / oMath 的行与括号附近
print('has oMath:', 'oMath' in xml or 'm:oMath' in xml)
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}
mnodes = p._p.findall('.//m:oMath', ns)
print('oMath count:', len(mnodes))
for mn in mnodes:
    ts = [t.text for t in mn.findall('.//m:t', ns)]
    print('  math text:', ts)
# 顺序遍历子节点看括号与math的位置
for child in p._p:
    tag = etree.QName(child).localname
    if tag == 'r':
        ts = ''.join(t.text or '' for t in child.findall('w:t', ns))
        print(' [r]', repr(ts))
    elif tag == 'oMath':
        ts = ''.join(t.text or '' for t in child.findall('.//m:t', ns))
        print(' [MATH]', repr(ts))

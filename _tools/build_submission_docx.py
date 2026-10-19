# -*- coding: utf-8 -*-
"""B5: build Frontiers-typeset Word manuscript CLIP-submission.docx from CLIP-revised.txt.

Font Times New Roman 12pt, single line spacing, footer page numbers (PAGE field),
line numbers enabled (w:lnNumType countBy=1, restart=newPage), A4 with 2.5cm margins,
headings via Heading 1-3 styles (black bold TNR), 4 tab-separated tables converted to
editable Word tables (Table Grid, caption ABOVE), figure legends at end.
ASCII-only script (PowerShell GBK console); all text comes from the source file.
"""
import io, os, re, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = r'D:\修改论文'
SRC = os.path.join(ROOT, 'CLIP-revised.txt')
OUT = os.path.join(ROOT, 'CLIP-submission.docx')
DUMP = os.path.join(ROOT, '_tools', '_dump_b5_verify.txt')

FONT = 'Times New Roman'
raw = io.open(SRC, encoding='utf-8-sig').read()
lines = [l.rstrip('\r') for l in raw.split('\n')]
src_blob = '\n'.join(lines)

def find_exact(s):
    for i, l in enumerate(lines):
        if l.strip() == s:
            return i
    raise SystemExit('MISSING MARKER: ' + s)

i_abs = find_exact('Abstract')
i_refs = find_exact('References')
i_tables = find_exact('Tables')
i_legends = find_exact('Figure Legends')

doc = Document()
doc.core_properties.title = 'CLIP-CAT: Vision-Language Fusion for Ordinal Cataract Grading on Limited Data'

# ---- Normal style: TNR 12pt, single spacing, 6pt after ----
normal = doc.styles['Normal']
normal.font.name = FONT
normal.font.size = Pt(12)
rpr = normal.element.get_or_add_rPr()
rf = rpr.get_or_add_rFonts()
for k in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
    rf.set(qn(k), FONT)
npf = normal.paragraph_format
npf.line_spacing = 1.0
npf.space_before = Pt(0)
npf.space_after = Pt(6)
npf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

# ---- Heading styles: black bold TNR 12pt ----
for lvl in (1, 2, 3):
    hs = doc.styles['Heading %d' % lvl]
    hs.font.name = FONT
    hs.font.size = Pt(12)
    hs.font.bold = True
    hs.font.color.rgb = RGBColor(0, 0, 0)
    hr = hs.element.get_or_add_rPr()
    hf = hr.get_or_add_rFonts()
    for k in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        hf.set(qn(k), FONT)
    hpf = hs.paragraph_format
    hpf.line_spacing = 1.0
    hpf.space_before = Pt(12)
    hpf.space_after = Pt(6)
    hpf.keep_with_next = True

# ---- Page setup: A4, 2.5cm margins ----
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.left_margin = Cm(2.5)
sec.right_margin = Cm(2.5)
sec.top_margin = Cm(2.5)
sec.bottom_margin = Cm(2.5)

# ---- Line numbers (Word review requirement) ----
sectPr = sec._sectPr
ln = OxmlElement('w:lnNumType')
ln.set(qn('w:countBy'), '1')
ln.set(qn('w:restart'), 'newPage')
ln.set(qn('w:distance'), '360')
cols = sectPr.find(qn('w:cols'))
if cols is not None:
    cols.addprevious(ln)
else:
    sectPr.append(ln)

# ---- Footer page number (PAGE field) ----
footer = sec.footer
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fld = OxmlElement('w:fldSimple')
fld.set(qn('w:instr'), ' PAGE ')
fr = OxmlElement('w:r')
ft = OxmlElement('w:t')
ft.text = '1'
fr.append(ft)
fld.append(fr)
fp._p.append(fld)
# force field update on open
settings = doc.settings.element
uf = OxmlElement('w:updateFields')
uf.set(qn('w:val'), 'true')
settings.append(uf)

def fmt_run(run, size, bold=False, italic=False):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    rr = run.element.get_or_add_rPr()
    rfo = rr.get_or_add_rFonts()
    for k in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        rfo.set(qn(k), FONT)

def add_p(text, bold=False, size=12, align=None, style=None,
          before=None, after=None, italic=False, prefix_bold=None,
          hanging=False):
    p = doc.add_paragraph(style=style)
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.line_spacing = 1.0
    if before is not None:
        pf.space_before = Pt(before)
    if after is not None:
        pf.space_after = Pt(after)
    if hanging:
        pf.left_indent = Cm(0.75)
        pf.first_line_indent = Cm(-0.75)
    if prefix_bold and text.startswith(prefix_bold):
        r1 = p.add_run(prefix_bold)
        fmt_run(r1, size, bold=True)
        r2 = p.add_run(text[len(prefix_bold):])
        fmt_run(r2, size, bold=bold, italic=italic)
    else:
        r = p.add_run(text)
        fmt_run(r, size, bold=bold, italic=italic)
    return p

C = WD_ALIGN_PARAGRAPH.CENTER

# ---- Title page block ----
add_p(lines[0].strip(), bold=True, size=14, align=C, after=12)
front = [l.strip() for l in lines[1:i_abs] if l.strip()]
corresp = []
for s in front:
    if s == '*Correspondence:':
        corresp = [s]
    elif corresp and len(corresp) < 3:
        corresp.append(s)
        if len(corresp) == 3:
            add_p(corresp[0], bold=True, align=C, after=0)
            add_p(corresp[1], align=C, after=0)
            add_p(corresp[2], align=C, after=6)
            corresp = []
    elif s.startswith('ORCID:'):
        add_p(s, size=11, align=C, after=6)
    elif s.startswith('Keywords:'):
        add_p(s, prefix_bold='Keywords:', after=12)
    elif s.startswith('Shuang Wang'):
        add_p(s, align=C, after=3)
    else:
        add_p(s, align=C, after=6)

# ---- Body (Abstract .. before References) ----
BODY_HEAD = re.compile(r'^(\d+(?:\.\d+)*)\s+[A-Z]')
BACK = {'Abstract', 'Acknowledgments', 'Author Contributions',
        'Conflict of Interest', 'Funding', 'Data Availability'}
for l in lines[i_abs:i_refs]:
    s = l.strip()
    if not s:
        continue
    m = BODY_HEAD.match(s)
    if m and len(s) < 100 and not s.endswith('.') and '(' not in s:
        lvl = min(m.group(1).count('.') + 1, 3)
        add_p(s, style='Heading %d' % lvl)
    elif s in BACK:
        add_p(s, style='Heading 1')
    elif s.startswith('Keywords:'):
        add_p(s, prefix_bold='Keywords:')
    else:
        add_p(s)

# ---- References ----
for l in lines[i_refs:i_tables]:
    s = l.strip()
    if not s:
        continue
    if s == 'References':
        add_p(s, style='Heading 1')
    elif re.match(r'^\d+\.\s', s):
        add_p(s, after=3, hanging=True)
    else:
        add_p(s)

# ---- Tables (captions above, editable Word tables) ----
def emit_tables(tables_data):
    for caption, rows in tables_data:
        if caption:
            mm = re.match(r'^Table \d+\.', caption)
            add_p(caption, prefix_bold=mm.group(0) if mm else None,
                  before=12, after=6)
        ncols = max(len(r) for r in rows)
        tbl = doc.add_table(rows=len(rows), cols=ncols)
        tbl.style = 'Table Grid'
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        for ri, row in enumerate(rows):
            for ci in range(ncols):
                txt = row[ci] if ci < len(row) else ''
                cell = tbl.cell(ri, ci)
                p = cell.paragraphs[0]
                pf = p.paragraph_format
                pf.line_spacing = 1.0
                pf.space_before = Pt(0)
                pf.space_after = Pt(0)
                if ci > 0:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(txt)
                fmt_run(r, 11, bold=(ri == 0))

tables_data = []
caption = None
rows = []
for raw_l in lines[i_tables:i_legends]:
    if not raw_l.strip():
        if rows:
            tables_data.append((caption, rows))
            caption, rows = None, []
        continue
    s = raw_l.strip()
    if s == 'Tables':
        add_p(s, style='Heading 1')
        continue
    if s.startswith('Table '):
        if rows:
            tables_data.append((caption, rows))
            rows = []
        caption = s
    else:
        rows.append([c.strip() for c in raw_l.rstrip('\r').split('\t')])
if rows:
    tables_data.append((caption, rows))
emit_tables(tables_data)

# ---- Figure legends ----
for l in lines[i_legends:]:
    s = l.strip()
    if not s:
        continue
    if s == 'Figure Legends':
        add_p(s, style='Heading 1')
    elif s.startswith('Figure '):
        mm = re.match(r'^Figure \d+\.', s)
        add_p(s, prefix_bold=mm.group(0) if mm else None, after=6)
    else:
        add_p(s)

doc.save(OUT)

# ================= VERIFY =================
doc2 = Document(OUT)
parts = [p.text for p in doc2.paragraphs]
for t in doc2.tables:
    for row in t.rows:
        for cell in row.cells:
            parts.append(cell.text)
blob = '\n'.join(parts)

V = []
def chk(name, ok, extra=''):
    V.append('%s %s %s' % (name, 'PASS' if ok else 'FAIL', extra))

chk('OUT_EXISTS', os.path.exists(OUT) and os.path.getsize(OUT) > 30000,
    str(os.path.getsize(OUT) if os.path.exists(OUT) else 0))
chk('TABLES_4', len(doc2.tables) == 4, str(len(doc2.tables)))
sect_xml = doc2.sections[0]._sectPr.xml
chk('LINENUM', ('lnNumType' in sect_xml and 'countBy="1"' in sect_xml))
foot_xml = ''.join(p._p.xml for p in doc2.sections[0].footer.paragraphs)
chk('PAGE_FIELD', 'PAGE' in foot_xml)
chk('FONT_TNR', doc2.styles['Normal'].font.name == FONT,
    str(doc2.styles['Normal'].font.name))
chk('SINGLE_SPACING', 'w:line="240"' in doc2.styles['Normal'].element.xml)
chk('A4', abs(doc2.sections[0].page_width - Cm(21.0)) < 100000)
LITS = ['86.76', '0.42', '0.88', '64.20', '79.50', 'CDRFF-Net', 'BiomedCLIP',
        'four concrete limitations', '1pzd/-Project', '(Matplotlib)']
for lit in LITS:
    chk('CNT[%s]' % lit, blob.count(lit) == src_blob.count(lit),
        'docx=%d txt=%d' % (blob.count(lit), src_blob.count(lit)))
chk('CNT[Gdef]', blob.count('\u2308(NC + C)/2\u2309') == src_blob.count('\u2308(NC + C)/2\u2309'),
    'docx=%d txt=%d' % (blob.count('\u2308(NC + C)/2\u2309'), src_blob.count('\u2308(NC + C)/2\u2309')))
chk('NO_SINGLE_F_CDRF', 'CDRF-Net' not in blob.replace('CDRFF-Net', ''))
chk('NO_INTERNAL_PATH', ('_tools/' not in blob) and ('draw_figs' not in blob))
chk('NO_GIT_SUFFIX', '1pzd/-Project.git' not in blob)
chk('REF_FIRST', '1. World Health Organization' in blob)
chk('REF_LAST', '46. Zhang H, Cisse M' in blob)
chk('HEADING_INTRO', '1 Introduction' in blob)
chk('HEADING_321', '3.2.1 Global Branch' in blob)
chk('TAB1_CAPTION', 'Table 1. Performance comparison' in blob)
chk('TAB4_CAPTION', 'Table 4. Confusion matrix' in blob)
chk('FIG4_LEGEND', 'Figure 4. Long-tailed distribution' in blob)
chk('PARA_MIN', len(doc2.paragraphs) > 150, str(len(doc2.paragraphs)))
chk('C4_ANCHOR', 'BiomedCLIP, MedCLIP, and PubMedCLIP' in blob)

fails = [l for l in V if 'FAIL' in l]
verdict = 'ALL PASS' if not fails else 'FAIL: ' + '; '.join(f.split()[0] for f in fails)
io.open(DUMP, 'w', encoding='utf-8').write('\n'.join(V) + '\nVERDICT: ' + verdict + '\n')
print('RESULT: ' + verdict)
print('PARAGRAPHS=%d TABLES=%d' % (len(doc2.paragraphs), len(doc2.tables)))
sys.exit(0 if not fails else 1)

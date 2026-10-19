# -*- coding: utf-8 -*-
"""Media resolution audit for CLIP.docx + orphan detection after Figure 5 removal."""
import zipfile, struct, re, io, sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DOCX = r"D:\修改论文\CLIP.docx"
EMU_IN = 914400

z = zipfile.ZipFile(DOCX)
doc = z.read("word/document.xml").decode("utf-8")
rels_xml = z.read("word/_rels/document.xml.rels").decode("utf-8")

import xml.etree.ElementTree as ET
relmap = {}
for r in ET.fromstring(rels_xml):
    relmap[r.get("Id")] = r.get("Target")

def png_info(d):
    w, h = struct.unpack(">II", d[16:24])
    dpi = None
    i = 8
    while i < len(d) - 8:
        ln = struct.unpack(">I", d[i:i+4])[0]
        typ = d[i+4:i+8]
        if typ == b"pHYs":
            px, py, unit = struct.unpack(">IIB", d[i+8:i+17])
            if unit == 1:
                dpi = (round(px*0.0254), round(py*0.0254))
            else:
                dpi = ("ppm", px, py)
        i += 12 + ln
    return w, h, dpi

def jpg_info(d):
    i = 2
    w = h = None
    dpi = None
    while i < len(d) - 9:
        if d[i] != 0xFF:
            i += 1
            continue
        m = d[i+1]
        if m in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", d[i+5:i+9])
        if m in (0xD8, 0xD9):
            i += 2
            continue
        ln = struct.unpack(">H", d[i+2:i+4])[0]
        if m == 0xE0 and d[i+4:i+8] == b"JFIF":
            unit = d[i+7+2]  # offset: seg starts at i+2, len at i+2..3, ident i+4..8, ver i+9..10, unit i+11
            unit = d[i+11]
            x = struct.unpack(">H", d[i+12:i+14])[0]
            y = struct.unpack(">H", d[i+14:i+16])[0]
            if unit == 1:
                dpi = (x, y)
            elif unit == 2:
                dpi = (round(x*2.54), round(y*2.54))
        i += 2 + ln
    return w, h, dpi

# walk document.xml: pair each blip embed with its enclosing wp:extent (in doc order)
pairs = []  # (rid, cx, cy)
pos = 0
while True:
    b = doc.find('r:embed="', pos)
    if b < 0:
        break
    end = doc.find('"', b + 9)
    rid = doc[b+9:end]
    # find nearest preceding <wp:extent
    e = doc.rfind("<wp:extent ", 0, b)
    cx = cy = None
    if e >= 0:
        m = re.match(r'<wp:extent cx="(\d+)" cy="(\d+)"', doc[e:e+80])
        if m:
            cx, cy = int(m.group(1)), int(m.group(2))
    pairs.append((rid, cx, cy))
    pos = end

print("=== embedded images (doc order) ===")
used = set()
for rid, cx, cy in pairs:
    tgt = relmap.get(rid, "?")
    used.add(tgt)
    name = "word/" + tgt.replace("../", "") if tgt.startswith("../") else "word/media/" + tgt.split("/")[-1]
    if name not in z.namelist() and tgt.startswith("media/"):
        name = "word/" + tgt
    d = z.read(name)
    if name.lower().endswith(".png"):
        w, h, dpi = png_info(d)
    else:
        w, h, dpi = jpg_info(d)
    if cx:
        win = cx / EMU_IN
        hin = cy / EMU_IN
        eff_x = w / win
        eff_y = h / hin
        print("%-14s %s px=%dx%d nominal-dpi=%s extent=%.2fx%.2f in eff-dpi=%.0fx%.0f %s"
              % (name.split("/")[-1], rid, w, h, dpi, win, hin, eff_x, eff_y,
                 "OK" if min(eff_x, eff_y) >= 295 else "BELOW-300"))
    else:
        print("%-14s %s px=%dx%d nominal-dpi=%s (no extent)" % (name.split("/")[-1], rid, w, h, dpi))

print("=== orphan check ===")
media_all = [n for n in z.namelist() if n.startswith("word/media/")]
for n in media_all:
    tgt = n.replace("word/", "")
    if tgt not in used and ("../" + tgt) not in used:
        print("ORPHAN:", n, len(z.read(n)), "bytes")
        # any rel pointing to it?
        owners = [rid for rid, t in relmap.items() if t.endswith(n.split("/")[-1])]
        print("  rels pointing at it:", owners)
print("used targets:", used)

print("=== data_in source figs ===")
import glob
for f in sorted(glob.glob(r"D:\修改论文\data_in\fig*")):
    d = open(f, "rb").read()
    if f.lower().endswith(".png"):
        w, h, dpi = png_info(d)
    else:
        w, h, dpi = jpg_info(d)
    print(f.split("\\")[-1], "px=%dx%d dpi=%s" % (w, h, dpi))

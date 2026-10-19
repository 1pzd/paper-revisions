# -*- coding: utf-8 -*-
"""Strip orphaned word/media/image5.png (the deleted Figure 5, 96dpi) and its dangling
rId15 relationship from CLIP.docx. Atomic: writes temp file, replaces only on full success."""
import zipfile, shutil, os, sys, io
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DOCX = r"D:\修改论文\CLIP.docx"
TMP = DOCX + ".tmp"
ORPHAN = "word/media/image5.png"

z = zipfile.ZipFile(DOCX)
names = z.namelist()
if ORPHAN not in names:
    print("nothing to strip; orphan absent")
    sys.exit(0)

# sanity: orphan must not be referenced in document.xml
doc = z.read("word/document.xml").decode("utf-8")
rels_name = "word/_rels/document.xml.rels"
rels_xml = z.read(rels_name).decode("utf-8")
root = ET.fromstring(rels_xml)
drop_ids = []
for r in root:
    if r.get("Target", "").endswith("image5.png"):
        drop_ids.append(r.get("Id"))
print("drop rel ids:", drop_ids)
for rid in drop_ids:
    if rid in doc:
        z.close()
        sys.exit("FAIL: %s still referenced in document.xml" % rid)

# rewrite rels without the dropped relationships
for rid in drop_ids:
    for r in list(root):
        if r.get("Id") == rid:
            root.remove(r)
new_rels = ET.tostring(root, encoding="UTF-8", xml_declaration=True).decode("utf-8")

zout = zipfile.ZipFile(TMP, "w", zipfile.ZIP_DEFLATED)
for item in z.infolist():
    if item.filename == ORPHAN:
        continue
    if item.filename == rels_name:
        zout.writestr(item, new_rels)
    else:
        zout.writestr(item, z.read(item.filename))
zout.close()
z.close()

# verify temp before swap
zt = zipfile.ZipFile(TMP)
assert ORPHAN not in zt.namelist(), "orphan still present in temp"
rr = zt.read(rels_name).decode("utf-8")
for rid in drop_ids:
    assert rid not in rr, "rel %s still present" % rid
    assert rid not in zt.read("word/document.xml").decode("utf-8"), "doc still refs %s" % rid
zt.close()

shutil.move(TMP, DOCX)
print("stripped OK; media now:", [n for n in zipfile.ZipFile(DOCX).namelist() if n.startswith("word/media/")])

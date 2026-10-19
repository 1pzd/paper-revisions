# -*- coding: utf-8 -*-
"""C10 / C11 / C12 / C17 + B4 (via Fig.5 removal) for CLIP-revised.txt and CLIP.docx.

C10: cite Fig.4 at the long-tail distribution sentence in section 3.5.
C11: delete Figure 5 (image + caption), keep the confusion-matrix table;
     fix body refs and repair the docx Table 5 caption.
C12: 'seeds (42, 123, 2024)' -> 'random seeds 42, 123, and 2024'.
C17: RTX 4050 -> RTX 4060 (8GB).
Run-level replacement everywhere in docx (oMath-safe). Hard failure on missing anchor.
"""
import shutil, sys
from docx import Document

ROOT = r"D:\修改论文"
TXT = ROOT + r"\CLIP-revised.txt"
DOCX = ROOT + r"\CLIP.docx"
BAK_TXT = ROOT + r"\_backup\CLIP-revised_pre_C10C17.txt"
BAK_DOCX = ROOT + r"\_backup\CLIP_pre_C10C17.docx"

def die(msg):
    sys.stderr.write("FAIL: %s\n" % msg)
    sys.exit(1)

# ---------------------------------------------------------------- backups
shutil.copyfile(TXT, BAK_TXT)
shutil.copyfile(DOCX, BAK_DOCX)

# ---------------------------------------------------------------- TXT
t = open(TXT, encoding="utf-8").read()

def trep(old, new, label, expect=1):
    global t
    n = t.count(old)
    if n != expect:
        die("txt %s: found %d (expect %d)" % (label, n, expect))
    t = t.replace(old, new)

# C10 — body cite for Figure 4 (txt body style is "Figure N")
trep("severe long-tailed distribution:", "severe long-tailed distribution (Figure 4):",
     "C10 fig4 cite")

# C12 — seed wording (3 sites)
trep("random seeds (42, 123, 2024).", "random seeds 42, 123, and 2024.", "C12 seeds L125")
trep("random seeds (42, 123, 2024),", "random seeds 42, 123, and 2024,", "C12 seeds L151")
trep("with seeds 42, 123, 2024)", "with random seeds 42, 123, and 2024)", "C12 seeds L135")

# C17 — GPU model
trep("an NVIDIA RTX 4050 using", "an NVIDIA RTX 4060 (8GB) using", "C17 GPU")

# C11 — body refs to Figure 5
trep("Tables 3-4 and the confusion matrix (Figure 5) display",
     "Tables 3-4 display", "C11 L151 ref")
trep("The confusion matrix is shown in Figure 5.",
     "The confusion matrix is shown in Table 4.", "C11 L185 ref")

# C11 — delete the Figure 5 caption line (+ its blank line)
lines = t.split("\n")
idx = [i for i, l in enumerate(lines) if l.startswith("Figure 5. Confusion matrix")]
if len(idx) != 1:
    die("txt fig5 caption: found %d" % len(idx))
i = idx[0]
del lines[i]
if i - 1 >= 0 and lines[i - 1].strip() == "":
    del lines[i - 1]
t = "\n".join(lines)
if not t.endswith("\n"):
    t += "\n"

if "Figure 5" in t:
    die("txt: Figure 5 still present")
if "(Figure 4)" not in t:
    die("txt: Figure 4 cite missing")
if "RTX 4060 (8GB)" not in t or "NVIDIA RTX 4050" in t:
    die("txt: GPU replacement wrong")
if "(42, 123, 2024)" in t:
    die("txt: old seed paren style remains")

open(TXT, "w", encoding="utf-8", newline="\n").write(t)
print("TXT OK")

# ---------------------------------------------------------------- DOCX
doc = Document(DOCX)

def replace_in_para(p, old, new, label):
    runs = p.runs
    texts = [r.text for r in runs]
    full = "".join(texts)
    idx = full.find(old)
    if idx == -1:
        die("docx %s: anchor not found" % label)
    if full.find(old, idx + 1) != -1:
        die("docx %s: anchor ambiguous" % label)
    end = idx + len(old)
    cum = []
    pos = 0
    for tx in texts:
        cum.append(pos)
        pos += len(tx)
    new_texts = list(texts)
    for i, tx in enumerate(texts):
        rs, re = cum[i], cum[i] + len(tx)
        if re <= idx or rs >= end:
            continue
        if rs <= idx < re:
            head = tx[: idx - rs]
            tail = tx[end - rs :] if end <= re else ""
            new_texts[i] = head + new + tail
        elif rs < end <= re:
            new_texts[i] = tx[end - rs :]
        else:
            new_texts[i] = ""
    for r, nt in zip(runs, new_texts):
        r.text = nt

def para_by_start(prefix):
    hits = [p for p in doc.paragraphs if p.text.startswith(prefix)]
    if len(hits) != 1:
        die("docx para %r: found %d" % (prefix[:40], len(hits)))
    return hits[0]

# C10 — body cite for Fig. 4 (docx body style is "Fig. N")
p074 = para_by_start("To validate our framework")
replace_in_para(p074, "Long-tailed Distribution:", "Long-tailed Distribution (Fig. 4):", "C10 fig4")

# C12 — seeds in implementation details
p080 = para_by_start("All slit-lamp images were resized")
replace_in_para(p080,
    "with different random seeds (42, 123, 2024) runs.",
    "with random seeds 42, 123, and 2024.", "C12 seeds")

# C17 — GPU model (run-split "4050" handled by cross-run replace)
p079 = para_by_start("Experiments were conducted")
replace_in_para(p079, "an NVIDIA RTX 4050 using", "an NVIDIA RTX 4060 (8GB) using", "C17 GPU")

# C11 — repair Table 5 caption (was a duplicated framework sentence)
# NOTE: "Given a slit-lamp image x" appears twice (P024 body + P104 tablecaption);
# select the tablecaption-styled one which precedes the confusion-matrix table.
cands = [p for p in doc.paragraphs
         if p.text.startswith("Given a slit-lamp image x") and p.style.name == "tablecaption"]
if len(cands) != 1:
    die("docx tbl5 caption para: found %d" % len(cands))
p104 = cands[0]
replace_in_para(p104,
    p104.text,
    "Table 5. Confusion matrix on the held-out test set (335 images). Rows represent true grades, columns represent predicted grades.",
    "C11 tbl5 caption")

# C11 — delete Fig. 5 image paragraph + caption paragraph
img_paras = [p for p in doc.paragraphs if "blip" in p._p.xml]
fig5_caps = [p for p in doc.paragraphs if p.text.startswith("Fig. 5. Confusion matrix")]
if len(fig5_caps) != 1:
    die("docx fig5 caption: found %d" % len(fig5_caps))
cap = fig5_caps[0]
# the image paragraph is the nearest blip paragraph before the caption
before = [p for p in img_paras if p._p.getparent().index(p._p) < cap._p.getparent().index(cap._p)]
if not before:
    die("docx fig5 image para not found")
img_p = before[-1]
cap._p.getparent().remove(cap._p)
img_p._p.getparent().remove(img_p._p)

# ---- verification
paras = doc.paragraphs
fulltext = "\n".join(p.text for p in paras)
if "Fig. 5" in fulltext or "Figure 5" in fulltext:
    die("docx: Fig.5 text remains")
if "(Fig. 4)" not in fulltext:
    die("docx: Fig.4 cite missing")
if "RTX 4060 (8GB)" not in fulltext or "NVIDIA RTX 4050" in fulltext:
    die("docx: GPU replacement wrong")
if "(42, 123, 2024)" in fulltext:
    die("docx: old seed paren style remains")
if "random seeds 42, 123, and 2024." not in fulltext:
    die("docx: new seed wording missing")
if "Table 5. Confusion matrix" not in fulltext:
    die("docx: Table 5 caption missing")

import re
n_tbl = len(doc.tables)
n_om = len(re.findall(r"<m:oMath>", doc.element.body.xml))
n_ompara = len(re.findall(r"<m:oMathPara>", doc.element.body.xml))
n_ref = sum(1 for p in paras if "referenceitem" in p.style.name.lower())
n_img = sum(1 for p in paras if "blip" in p._p.xml)
print("DOCX paras=%d tables=%d oMath=%d oMathPara=%d refs=%d imgs=%d"
      % (len(paras), n_tbl, n_om, n_ompara, n_ref, n_img))
if n_tbl != 5:
    die("docx tables != 5")
if n_om != 45 or n_ompara != 8:
    die("docx oMath changed")
if n_ref != 26:
    die("docx refs != 26")
if n_img != 4:
    die("docx imgs != 4")

doc.save(DOCX)
print("DOCX OK")

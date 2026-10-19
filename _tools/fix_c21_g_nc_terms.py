# -*- coding: utf-8 -*-
"""C21: Fix G/NC terminology inconsistency in CLIP-revised.txt.

G = ceil((NC+C)/2) depends on BOTH nuclear color (NC) and cortical opacity (C).
Remove false G<->NC-only equivalences; use G labels everywhere for grade groups.
Numbers must remain unchanged. Backup first.
"""
import io, os, shutil, sys

ROOT = r"D:\修改论文"
TXT = os.path.join(ROOT, "CLIP-revised.txt")
BACKUP = os.path.join(ROOT, "_backup", "CLIP-revised_pre_C21.txt")
DUMP = os.path.join(ROOT, "_tools", "_dump_c21_result.txt")

# ---- backup ----
if not os.path.exists(BACKUP):
    shutil.copy2(TXT, BACKUP)
    print("BACKUP created:", BACKUP)
else:
    print("BACKUP exists (skip):", BACKUP)

text = io.open(TXT, encoding="utf-8-sig").read()
lines_before = text.count("\n") + 1

# ---- replacements: (old, new, expected_min_count) ----
REPL = [
    # Site 1: Results 4.3 - drop false G<->NC mappings
    (
        "head grades G0 to G2 (NC1 to NC3), which together comprise",
        "head grades G0 to G2, which together comprise",
        1,
    ),
    (
        "whereas G3 (NC4) falls to 60.9%",
        "whereas G3 falls to 60.9%",
        1,
    ),
    # Site 2: Dataset Description - class distribution in G labels
    (
        "the two head grades (NC2 and NC3) comprise 78.1% of samples, the mildest grade (NC1) accounts for 13.7%, and the two most severe grades (NC5 and NC6) together cover only 2.1%",
        "the two head grades (G1 and G2) comprise 78.1% of samples, the mildest grade (G0) accounts for 13.7%, and the two most severe grades (G4 and G5) together cover only 2.1%",
        1,
    ),
    # Site 3: Figure 4 caption - anchor G labels to match body interpretation
    (
        "over the six severity grades: the two head grades cover 78.1% of samples, while the two most severe grades cover only 2.1%",
        "over the six severity grades G0 to G5: the two head grades (G1 and G2) cover 78.1% of samples, while the two most severe grades (G4 and G5) cover only 2.1%",
        1,
    ),
    # Site 4: 4.3 error analysis - G is not nuclear-only
    (
        "the continuous progression of nuclear opacity",
        "the continuous progression of lens opacity",
        1,
    ),
]

changed = []
for old, new, exp in REPL:
    n = text.count(old)
    if n < exp:
        print("FAIL anchor not found (%d<%d): %r" % (n, exp, old[:60]))
        sys.exit(1)
    text = text.replace(old, new)
    changed.append((old[:50], n))

io.open(TXT, "w", encoding="utf-8-sig", newline="").write(text)
print("[txt] replacements applied:", len(changed))
for c, n in changed:
    print("  x%d %s..." % (n, c))

# ---- VERIFY ----
lines = text.splitlines()
checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

chk("line_count_390", len(lines) == 390, "lines=%d" % len(lines))
chk("no_NC1_NC3_map", "NC1 to NC3" not in text)
chk("no_NC4_paren", "G3 (NC4)" not in text)
chk("no_NC2_NC3_head", "(NC2 and NC3)" not in text)
chk("no_NC1_mildest", "mildest grade (NC1)" not in text)
chk("no_NC5_NC6_severe", "(NC5 and NC6)" not in text)
chk("no_nuclear_progression", "progression of nuclear opacity" not in text)
chk("G1_G2_head_present", "(G1 and G2) comprise 78.1%" in text)
chk("G0_mildest_present", "(G0) accounts for 13.7%" in text)
chk("G4_G5_severe_present", "(G4 and G5) together cover only 2.1%" in text)
chk("fig4_caption_G", "six severity grades G0 to G5" in text)
chk("lens_opacity_present", "continuous progression of lens opacity" in text)
chk("def_ceil_avg_x2", text.count("G = \u2308(NC + C)/2\u2309") == 2, "count=%d" % text.count("G = \u2308(NC + C)/2\u2309"))
chk("def_sec31_intact", "the severity grade is G = \u2308(NC + C)/2\u2309" in text)
chk("def_sec35_intact", "G = \u2308(NC + C)/2\u2309." in text)
# numbers unchanged
for lit, exp in [("86.76", 9), ("0.42", 11), ("78.1%", 2), ("13.7%", 1),
                 ("91.9%", 1), ("1,673", 6), ("1171", 3), ("1,171", 1), ("2.1%", 2),
                 ("n_0=229", 1), ("n_1=758", 1), ("n_2=549", 1),
                 ("13.94", 1), ("18.59", 1), ("CDRFF-Net", 7)]:
    c = text.count(lit)
    chk("num_%s_x%d" % (lit.replace(",", ""), exp), c == exp, "count=%d" % c)
chk("no_CDRF_single", "CDRF-Net" not in text.replace("CDRFF-Net", ""))
chk("backup_exists", os.path.exists(BACKUP))

dump = []
dump.append("C21 G/NC TERMINOLOGY FIX VERIFY")
dump.append("lines_before=%d lines_after=%d" % (lines_before, len(lines)))
for name, ok, detail in checks:
    dump.append("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))
all_ok = all(ok for _, ok, _ in checks)
dump.append("RESULT: %s" % ("ALL PASS" if all_ok else "FAIL"))
io.open(DUMP, "w", encoding="utf-8").write("\n".join(dump))
print("VERIFY:", "ALL PASS" if all_ok else "FAIL ->", DUMP)
sys.exit(0 if all_ok else 1)

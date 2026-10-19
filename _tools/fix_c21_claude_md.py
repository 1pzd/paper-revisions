# -*- coding: utf-8 -*-
"""Register C21 (G/NC terminology unification) in CLAUDE.md.
Inserts C21 entry after C20 entry (line 55), appends changelog row at EOF.
"""
import io, os, shutil

CM = r"D:\修改论文\CLAUDE.md"
DUMP = r"D:\修改论文\_tools\_dump_claude_c21.txt"

C21_ENTRY = (
    "- [x] **C21. G/NC 术语一致性**：2026-10-18 已修。全文在 G=⌈(NC+C)/2⌉ 定义下统一使用 G 标签"
    "（G0–G5）描述分级类别，删除三处 NC-only 混淆表述：①Results 4.3 删除 “head grades G0 to G2 "
    "(NC1 to NC3)” 与 “G3 (NC4)” 的 G↔NC 等同映射（改为只用 G 标签）；②Dataset Description（§3.5）"
    "头部/最严重类别由 (NC2 and NC3)/(NC5 and NC6) 改为 (G1 and G2)/(G4 and G5)（对应 n_g=229/758/549/"
    "102/20/15）；③Figure 4 图题 “six severity grades” 补全为 “six severity grades G0 to G5”，"
    "并与正文一致使用 (G1 and G2)/(G4 and G5)；④§4.3 末 “progression of nuclear opacity”→“progression "
    "of lens opacity”（软性 NC 泄漏，G 并非仅由核性分级决定）。G=⌈(NC+C)/2⌉ 定义两处（§3.1 + §3.5）"
    "原样保留；所有数字未动（86.76/0.42/78.1%/13.7%/2.1%/91.9%/n_g/类别权重）。脚本 "
    "_tools/fix_c21_g_nc_terms.py；备份 _backup/CLIP-revised_pre_C21.txt；验证 ALL PASS。"
)

CHANGELOG_ROW = (
    "| 2026-10-18 | C21：G/NC 术语统一——Results 4.3 删除 G↔NC 等同映射（(NC1 to NC3)、G3 (NC4)）；"
    "§3.5 类别分布 (NC2 and NC3)/(NC5 and NC6)→(G1 and G2)/(G4 and G5)；Fig 4 图题补 “G0 to G5” "
    "并与正文统一 G 标签；“progression of nuclear opacity”→“progression of lens opacity”。"
    "G=⌈(NC+C)/2⌉ 定义两处保留，数字全部未动。脚本 _tools/fix_c21_g_nc_terms.py；"
    "备份 _backup/CLIP-revised_pre_C21.txt；验证 ALL PASS | C21 |"
)

out = []
text = io.open(CM, encoding="utf-8").read()
lines = text.splitlines()
ok_c21 = False
ok_log = False

for i, l in enumerate(lines):
    out.append(l)
    if (not ok_c21) and l.startswith("- [x] **C20."):
        out.append(C21_ENTRY)
        ok_c21 = True

out.append(CHANGELOG_ROW)
ok_log = True

new_text = "\n".join(out) + "\n"
shutil.copy2(CM, CM + ".bak_c21")
io.open(CM, "w", encoding="utf-8", newline="\n").write(new_text)

# verify
v = io.open(CM, encoding="utf-8").read()
checks = [
    ("C21_ENTRY", "**C21. G/NC \u672f\u8bed\u4e00\u81f4\u6027**" in v),
    ("C21_TICKED", "- [x] **C21." in v),
    ("C21_AFTER_C20", v.index("**C21.") > v.index("**C20.")),
    ("C21_BEFORE_D", v.index("**C21.") < v.index("## D.")),
    ("CHANGELOG_ROW", "C21\uff1aG/NC \u672f\u8bed\u7edf\u4e00" in v),
    ("C21_COUNT_1", v.count("**C21.") == 1),
    ("C20_STILL", "- [x] **C20." in v),
    ("NO_C22_YET", "**C22." not in v),
]
out_lines = ["C21 registration: INSERT=%s LOG=%s" % (ok_c21, ok_log)]
for name, passed in checks:
    out_lines.append("%s %s" % (name, "PASS" if passed else "FAIL"))
out_lines.append("LINES %d" % len(v.splitlines()))

io.open(DUMP, "w", encoding="utf-8").write("\n".join(out_lines))
print("DONE " + ("ALL PASS" if all(p for _, p in checks) and ok_c21 and ok_log else "FAIL"))
for l in out_lines:
    if "PASS" in l or "FAIL" in l or l.startswith("C21") or l.startswith("LINES"):
        print(l.split(" ")[0], "OK" if "PASS" in l else l)

# -*- coding: utf-8 -*-
"""C25 registration in CLAUDE.md: new ticked C25 entry before '## D.' + changelog row."""
import os
import shutil

ROOT = r"D:\修改论文"
MD = os.path.join(ROOT, "CLAUDE.md")
BAK = os.path.join(ROOT, "CLAUDE.md.bak_c25")
DUMP = os.path.join(ROOT, "_tools", "_dump_claude_c25.txt")

out = []


def log(s):
    out.append(s)


if not os.path.exists(BAK):
    shutil.copy2(MD, BAK)
    log("BACKUP created: " + BAK)
else:
    log("BACKUP exists (skip)")

with open(MD, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

ENTRY = (
    "- [x] **C25. 方法学与医学逻辑 3 处前后矛盾**〔2026-10-19 已改："
    "(1) 提示词与模板对齐——§3.3.1 概括由 \"opacity density, color, and spatial pattern\" "
    "改为如实描述 t0–t5 的 \"density and extent of lens opacity\"（LOCS III severity vocabulary）；"
    "t0/t2–t5 中裂隙灯不可直接观测的主观症状（negligible impact on vision、emerging visual symptoms、"
    "affecting daily visual function、requiring intervention、severe vision impairment）全部改为客观裂隙灯"
    "影像学密度/范围描述（t1 原本客观，保留）。"
    "(2) Prototype Smoothing 损失项矛盾——按用户给定分支\"未加入最终损失\"处理：§3.6 辅助对比项句删除，"
    "改为\"原型为平滑类中心统计、显式声明不进入训练目标（L_total = L_focal + λ·L_rank，§3.4 不变），"
    "类内紧致性为诊断性属性而非优化目标\"；§3.6 摘要句与 §4.4 L193 一致性改写；ref 45 补引句保留。"
    "(3) LOCS III 合成与取像模态——§3.5 补单图照明说明（弥散/裂隙光未标准化、未记录，NC/C 由单视图外观标注，"
    "非专用光切/后照法视图）+ 仅合并 NC 与 C 的依据（该两轴为单视图可可靠标注的 LOCS III 轴；NO/PSC 未标注，"
    "G 索引核色-皮质联合负担而非完整 LOCS III 剖面）；§3.1 公式后镜像短句。数字零改动。"
    "脚本 _tools/fix_c25_methods_coherence.py；备份 _backup/CLIP-revised_pre_C25.txt；"
    "验证 ALL PASS；CLIP-submission.docx 同步重生成。注意：若训练代码使用的是改前提示词文本，"
    "需改回或按新提示词重训后再投；若代码中辅助对比项实际以权重入损失，需提供 λ_proto 补 §3.4。〕"
)

ROW = (
    "| 2026-10-19 | C25：方法学/医学逻辑 3 处前后矛盾修复（§3.3.1 概括与 t0–t5 客观化；§3.6 辅助对比项改为"
    "诊断统计、显式声明 L_total 不变；§3.5 单图照明/取像说明+NO/PSC 未标注依据，§3.1 镜像短句）；数字零改动；"
    "脚本 _tools/fix_c25_methods_coherence.py；备份 _backup/CLIP-revised_pre_C25.txt；"
    "CLIP-submission.docx 同步重生成 | C25 |"
)

# insert entry before '## D.'
d_idx = None
for i, l in enumerate(lines):
    if l.startswith("## D."):
        d_idx = i
        break
if d_idx is None:
    log("FAIL: '## D.' heading not found")
else:
    lines = lines[:d_idx] + [ENTRY, ""] + lines[d_idx:]
    log("C25 entry inserted before '## D.' (line %d)" % (d_idx + 1))

# append changelog row at EOF
lines.append(ROW)
log("CHANGELOG row appended")

text = "\n".join(lines) + "\n"
with open(MD, "w", encoding="utf-8") as f:
    f.write(text)

log("--- VERIFY ---")
ok = True


def chk(name, cond):
    global ok
    log("%s %s" % (name, "PASS" if cond else "FAIL"))
    if not cond:
        ok = False


chk("C25_ENTRY_1", text.count("**C25.") == 1)
chk("C25_TICKED", "- [x] **C25." in text)
chk("C24_STILL", "- [x] **C24." in text)
chk("NO_C26", "**C26" not in text)
chk("CHANGELOG_C25", text.count("| 2026-10-19 | C25") == 1)
c24 = text.find("**C24.")
c25 = text.find("**C25.")
dd = text.find("## D.")
chk("C25_AFTER_C24", 0 < c24 < c25)
chk("C25_BEFORE_D", 0 < c25 < dd)
chk("B5_STILL", "B5." in text)
log("RESULT: %s lines=%d" % ("ALL PASS" if ok else "FAIL", len(lines)))

with open(DUMP, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

print("RESULT: %s lines=%d" % ("ALL PASS" if ok else "FAIL", len(lines)))

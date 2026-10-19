# -*- coding: utf-8 -*-
"""CLAUDE.md: register C22 (Discussion 5 tone fix) ticked + changelog row."""
import io
import os
import shutil

ROOT = r"D:\修改论文"
MD = os.path.join(ROOT, "CLAUDE.md")
DUMP = os.path.join(ROOT, "_tools", "_dump_claude_c22.txt")
BAK = MD + ".bak_c22"

C22_ENTRY = (
    "- [x] **C22. Discussion 5 措辞降调（医学期刊语气）**〔2026-10-18 已改："
    "三处过度确定表述按\"结果与利用等级顺序信息的解释一致，但不能证明学到生物学进展；"
    "五折提示跨划分稳定性，但不能排除过拟合/中心特异性偏差\"框架重写。"
    "(1) L205 'demonstrate that the model has learned the continuous progression of "
    "cataract severity rather than treating grades as independent categories' → "
    "'are consistent with the interpretation that the model exploits ordinal grade-order "
    "information rather than treating grades as independent categories, although they do "
    "not establish that the model has learned the underlying biological progression of "
    "cataract.'（覆盖用户所指\"learned the continuous progression\"与\"predictions "
    "remain concentrated near the true grade\"外推为临床可靠性的两处；"
    "全文并无后句原文，实为 L205 同一处外推）；"
    "(2) L209 'five-fold cross-validation indicates stable performance across data splits. "
    "The tight variance (86.1% ± 0.85% accuracy) suggests that ... effectively prevent "
    "overfitting.' → 'five-fold cross-validation suggests that performance is reasonably "
    "stable across data splits. The tight variance (86.1% ± 0.85% accuracy) suggests that "
    "the architectural priors and regularization strategies help mitigate overfitting; "
    "however, these results cannot rule out overfitting or center-specific bias.'；"
    "(3) L207 'The ablation study confirms that' → 'indicates that'（顺带降调）。"
    "仅改措辞，未动结构与任何数字（86.76×9 / 0.42×11 / 78.1%×2 / 2.1%×2 / 90.9%×3 前后一致 / "
    "1,673×6 / 86.1%×3 / CDRFF-Net×7 / G定义×2 均不变）。§4.4 的 overfitting 表述已属对冲写法，"
    "未改。脚本 _tools/fix_c22_discussion.py；备份 _backup/CLIP-revised_pre_C22.txt；"
    "验证见 _tools/_dump_c22_result.txt（唯一 FAIL 为校验脚本把 90.9% 期望次数写成 1、实际 3，"
    "与备份逐字比对 3=3 未变，属校验常量笔误而非内容问题）〕"
)

CHANGELOG_ROW = (
    "| 2026-10-18 | C22：Discussion §5 措辞降调——(1) L205 删'has learned the continuous "
    "progression'确定性结论，改为'consistent with ... exploits ordinal grade-order "
    "information ... do not establish ... biological progression'；(2) L209 "
    "'effectively prevent overfitting'→'help mitigate overfitting; however, ... cannot "
    "rule out overfitting or center-specific bias'，'indicates stable'→'suggests "
    "reasonably stable'；(3) L207 'confirms'→'indicates'。数字零改动（90.9% 备份/改后均×3）。"
    "脚本 _tools/fix_c22_discussion.py，备份 _backup/CLIP-revised_pre_C22.txt，"
    "验证 _dump_c22_result.txt。 | C22 |"
)


def main():
    shutil.copyfile(MD, BAK)
    with io.open(MD, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    checks = []
    ok = True

    # 1) insert C22 after C21 entry, before '## D.' heading
    idx_c21 = None
    idx_d = None
    for i, ln in enumerate(lines):
        if ln.startswith("- [x] **C21.") or ln.startswith("- [ ] **C21."):
            idx_c21 = i
        if ln.startswith("## D."):
            idx_d = i
            break
    if idx_c21 is None or idx_d is None:
        checks.append("FAIL locate C21/## D.")
        ok = False
    else:
        # C21 entry may be multi-line? assume single-line entry; insert right after
        # its line (if following lines are continuation, they stay before C22).
        # Our entries are single-line, so insert at idx_c21+1.
        lines.insert(idx_c21 + 1, C22_ENTRY)
        checks.append("PASS C22_INSERT after C21 line %d" % (idx_c21 + 1))

    # 2) changelog row at EOF
    lines.append(CHANGELOG_ROW)
    checks.append("PASS CHANGELOG_ROW appended")

    with io.open(MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    # VERIFY
    text = "\n".join(lines)
    def chk(name, cond):
        nonlocal ok
        checks.append("%s %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            ok = False

    chk("C22_ENTRY_1", text.count("**C22.") == 1)
    chk("C22_TICKED", "- [x] **C22." in text)
    chk("C21_STILL", "- [x] **C21." in text)
    chk("C20_STILL", "**C20." in text)
    chk("NO_C23", "**C23." not in text)
    chk("CHANGELOG_C22", text.count("| C22 |") == 1)
    i21 = text.find("**C21.")
    i22 = text.find("**C22.")
    i23 = text.find("**C23.") if "**C23." in text else -1
    idd = text.find("## D.")
    chk("C22_AFTER_C21", 0 < i21 < i22)
    chk("C22_BEFORE_D", idd == -1 or i22 < idd)

    with io.open(DUMP, "w", encoding="utf-8") as f:
        f.write("\n".join(checks) + "\n\nRESULT: %s\n" % ("ALL PASS" if ok else "FAIL"))
        f.write("CLAUDE.md lines: %d\n" % len(lines))
    print("RESULT: %s lines=%d" % ("ALL PASS" if ok else "FAIL", len(lines)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

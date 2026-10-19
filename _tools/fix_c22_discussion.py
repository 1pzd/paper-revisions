# -*- coding: utf-8 -*-
"""C22: Discussion 5 tone fix — soften three overconfident claims in CLIP-revised.txt.

User m0163: Discussion conclusions restate Methods/Results and are overconfident.
Target phrases:
  1) 'the model has learned the continuous progression of cataract severity'
  2) 'effectively prevent overfitting'
  3) extension of 'predictions remain concentrated near the true grade' into
     clinical reliability (same L205 overreach; no verbatim phrase in file)
Plus mild: 'The ablation study confirms that' -> 'indicates that'.

Cautious framing (user): results consistent with exploiting ordinal grade-order
information, NOT proof of learning biological progression; 5-fold suggests
stability across splits but cannot rule out overfitting or center-specific bias.

Pattern: backup first (skip-if-exist) -> utf-8-sig exact-string replacements
(each expected x1) -> VERIFY -> _tools/_dump_c22_result.txt
"""
import io
import os
import sys

ROOT = r"D:\修改论文"
TXT = os.path.join(ROOT, "CLIP-revised.txt")
BACKUP = os.path.join(ROOT, "_backup", "CLIP-revised_pre_C22.txt")
DUMP = os.path.join(ROOT, "_tools", "_dump_c22_result.txt")

# (old, new, expected_count)
REPLACEMENTS = [
    (
        "The low mean squared error (0.42) and the concentration of errors on "
        "adjacent grades (90.9%) demonstrate that the model has learned the "
        "continuous progression of cataract severity rather than treating "
        "grades as independent categories.",
        "The low mean squared error (0.42) and the concentration of errors on "
        "adjacent grades (90.9%) are consistent with the interpretation that "
        "the model exploits ordinal grade-order information rather than "
        "treating grades as independent categories, although they do not "
        "establish that the model has learned the underlying biological "
        "progression of cataract.",
        1,
    ),
    (
        "five-fold cross-validation indicates stable performance across data "
        "splits. The tight variance (86.1% \u00b1 0.85% accuracy) suggests that "
        "the architectural priors and regularization strategies effectively "
        "prevent overfitting.",
        "five-fold cross-validation suggests that performance is reasonably "
        "stable across data splits. The tight variance (86.1% \u00b1 0.85% "
        "accuracy) suggests that the architectural priors and regularization "
        "strategies help mitigate overfitting; however, these results cannot "
        "rule out overfitting or center-specific bias.",
        1,
    ),
    (
        "The ablation study confirms that",
        "The ablation study indicates that",
        1,
    ),
]

# Anchors that must survive unchanged (literal, expected count)
KEEP = [
    ("86.76", 9),
    ("0.42", 11),
    ("78.1%", 2),
    ("2.1%", 2),
    ("1,673", 6),
    ("90.9%", 1),
    ("86.1%", 3),
    ("CDRFF-Net", 7),
    ("G = \u2308(NC + C)/2\u2309", 2),
    ("(46)", 1),
    ("four concrete limitations", 1),
    ("BiomedCLIP", 1),
]

FORBIDDEN = [
    "has learned the continuous progression",
    "effectively prevent overfitting",
    "study confirms",
]

REQUIRED = [
    "consistent with the interpretation",
    "cannot rule out overfitting or center-specific bias",
    "study indicates",
    "exploits ordinal grade-order information",
]


def main():
    if not os.path.exists(TXT):
        print("FAIL missing txt")
        return 1

    if not os.path.exists(BACKUP):
        data = open(TXT, "rb").read()
        with open(BACKUP, "wb") as f:
            f.write(data)
        print("BACKUP created: %s (%d bytes)" % (BACKUP, len(data)))
    else:
        print("BACKUP exists, skip: %s" % BACKUP)

    with io.open(TXT, "r", encoding="utf-8-sig", newline="") as f:
        text = f.read()

    log = []
    for old, new, exp in REPLACEMENTS:
        n = text.count(old)
        if n != exp:
            print("FAIL count %d != %d for: %s..." % (n, exp, old[:60]))
            return 1
        text = text.replace(old, new)
        log.append("REPLACED x%d: %s... -> %s..." % (n, old[:50], new[:50]))

    with io.open(TXT, "w", encoding="utf-8-sig", newline="") as f:
        f.write(text)
    print("[txt] saved")

    # VERIFY
    checks = []
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        checks.append("%s %s%s" % ("PASS" if cond else "FAIL", name,
                                   (" | " + detail) if detail else ""))
        if not cond:
            ok = False

    for lit, exp in KEEP:
        n = text.count(lit)
        chk("KEEP %r x%d" % (lit, exp), n == exp, "got=%d" % n)

    for bad in FORBIDDEN:
        chk("GONE %r" % bad[:40], text.count(bad) == 0,
            "got=%d" % text.count(bad))

    for need in REQUIRED:
        chk("NEW %r" % need[:40], text.count(need) == 1,
            "got=%d" % text.count(need))

    chk("BACKUP_EXISTS", os.path.exists(BACKUP))
    chk("LINES_390", text.count("\n") + 1 == 390,
        "lines=%d" % (text.count("\n") + 1))

    with io.open(DUMP, "w", encoding="utf-8") as f:
        f.write("C22 VERIFY (Discussion tone fix)\n")
        f.write("\n".join(log) + "\n\n")
        f.write("\n".join(checks) + "\n")
        f.write("\nRESULT: %s\n" % ("ALL PASS" if ok else "FAIL"))

    print("RESULT: %s" % ("ALL PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

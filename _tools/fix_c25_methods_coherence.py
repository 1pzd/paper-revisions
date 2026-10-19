# -*- coding: utf-8 -*-
"""C25: fix 3 methodological/medical-logic contradictions in CLIP-revised.txt
R1-R6   prompt claim + t0-t5 objective slit-lamp wording (fix1)
R7-R9   prototype smoothing: remove false auxiliary-loss claim (fix2)
R10-R12 LOCS III modality: single-image illumination + NC/C-only rationale (fix3)
"""
import os
import shutil

ROOT = r"D:\修改论文"
TXT = os.path.join(ROOT, "CLIP-revised.txt")
BAK = os.path.join(ROOT, "_backup", "CLIP-revised_pre_C25.txt")
DUMP = os.path.join(ROOT, "_tools", "_dump_c25_result.txt")

out = []


def log(s):
    out.append(s)


if not os.path.exists(BAK):
    shutil.copy2(TXT, BAK)
    log("BACKUP created: " + BAK)
else:
    log("BACKUP exists (skip)")

with open(TXT, "r", encoding="utf-8-sig", newline="") as f:
    text = f.read()

REPL = [
    # ---- fix1: prompt claim + t0-t5 objective wording ----
    (
        "Our templates instead describe the clinical appearance of each grade, "
        "including opacity density, color, and spatial pattern, drawn from the "
        "LOCS III vocabulary (2).",
        "Our templates instead describe the clinical appearance of each grade, "
        "including the density and extent of lens opacity as visible in slit-lamp "
        "images, drawn from the LOCS III severity vocabulary (2).",
    ),
    (
        "t0: A slit-lamp image showing G0 (minimal) cataract severity, corresponding "
        "to early-stage opacity with negligible impact on vision.",
        "t0: A slit-lamp image showing G0 (minimal) cataract severity, corresponding "
        "to early-stage lens opacity barely perceptible under slit-lamp examination.",
    ),
    (
        "t2: A slit-lamp image showing G2 (moderate) cataract severity, with moderate "
        "lens opacity and emerging visual symptoms.",
        "t2: A slit-lamp image showing G2 (moderate) cataract severity, with moderate "
        "lens opacity of clearly increased density.",
    ),
    (
        "t3: A slit-lamp image showing G3 (significant) cataract severity, with pronounced "
        "opacity affecting daily visual function.",
        "t3: A slit-lamp image showing G3 (significant) cataract severity, with pronounced "
        "lens opacity of high density involving most of the lens area.",
    ),
    (
        "t4: A slit-lamp image showing G4 (advanced) cataract severity, with dense "
        "lens opacity requiring intervention.",
        "t4: A slit-lamp image showing G4 (advanced) cataract severity, with dense "
        "lens opacity occupying nearly the entire lens.",
    ),
    (
        "t5: A slit-lamp image showing G5 (severe) cataract severity, with near-total "
        "lens opacification and severe vision impairment.",
        "t5: A slit-lamp image showing G5 (severe) cataract severity, with near-total "
        "lens opacification.",
    ),
    # ---- fix2: prototype smoothing contradiction ----
    (
        "To mitigate instability from small batches, we implemented momentum updates "
        "for global class centers and weighted sampling to address class imbalance.",
        "We tracked momentum-updated global class centers as training-stability "
        "diagnostics under small batch sizes and implemented weighted sampling to "
        "address class imbalance.",
    ),
    (
        "Prototype smoothing maintains momentum-updated class centers to stabilize "
        "training under small batch sizes and class imbalance. For each grade g, we "
        "maintain a running-average prototype vector c_g \u2208 R^768. After each batch, "
        "c_g is updated via exponential moving average: c_g \u2190 m\u00b7c_g + (1-m)\u00b7(1/|B_g|)"
        "\u03a3_{x\u2208B_g} f_fused(x), where B_g is the set of samples with ground-truth grade "
        "g in the current batch, m=0.9 is the momentum coefficient, and f_fused(x) is "
        "the fused visual feature from \u00a73.2.3. These prototypes are used to compute an "
        "auxiliary contrastive term (not included in the final loss) that encourages "
        "intra-class compactness during training. Long-tailed training instability is "
        "also addressed by uniformity-preserving transfer for visual prompt tuning (45).",
        "Prototype smoothing maintains momentum-updated class centers as smoothed "
        "class-level statistics under small batch sizes and class imbalance. For each "
        "grade g, we maintain a running-average prototype vector c_g \u2208 R^768. After each "
        "batch, c_g is updated via exponential moving average: c_g \u2190 m\u00b7c_g + (1-m)\u00b7(1/|B_g|)"
        "\u03a3_{x\u2208B_g} f_fused(x), where B_g is the set of samples with ground-truth grade g in "
        "the current batch, m=0.9 is the momentum coefficient, and f_fused(x) is the "
        "fused visual feature from \u00a73.2.3. These prototypes do not contribute any term to "
        "the training objective, which remains L_total = L_focal + \u03bb\u00b7L_rank (\u00a73.4); "
        "intra-class compactness in the prototype geometry is monitored as a diagnostic "
        "property of the learned representation rather than promoted by an auxiliary "
        "loss. Long-tailed training instability is also addressed by uniformity-preserving "
        "transfer for visual prompt tuning (45).",
    ),
    (
        "Training further applies random horizontal flipping and mild color jitter, "
        "weight decay, and momentum-based prototype smoothing (0.9) for stable class centers.",
        "Training further applies random horizontal flipping and mild color jitter, and "
        "weight decay; momentum-updated class centers (m = 0.9) are tracked for "
        "training-stability diagnostics (\u00a73.6) and do not enter the training objective.",
    ),
    # ---- fix3: LOCS III modality documentation ----
    (
        "All images were collected via routine clinical slit-lamp photography; the "
        "specific slit-lamp models and acquisition parameters were not recorded.",
        "All images were collected via routine clinical slit-lamp photography; the "
        "specific slit-lamp models and acquisition parameters were not recorded. Each "
        "patient contributed a single photograph, and the illumination mode of individual "
        "frames (diffuse versus focal slit-beam) was neither standardized nor recorded; "
        "the nuclear color grade (NC) and the cortical opacity grade (C) were therefore "
        "assigned from the opacity appearance visible in that single view rather than "
        "from dedicated optic-section or retro-illumination views.",
    ),
    (
        "G = \u2308(NC + C)/2\u2309. The dataset exhibits a severe long-tailed distribution",
        "G = \u2308(NC + C)/2\u2309. The composite combines only NC and C because these are the "
        "two LOCS III opacity axes that the grading panel could annotate reliably from "
        "the available single-view photographs; nuclear opacity (NO) and posterior "
        "subcapsular opacity (PSC) were not scored in this cohort, so G indexes the "
        "joint nuclear-color and cortical-opacity burden rather than a complete LOCS III "
        "profile. The dataset exhibits a severe long-tailed distribution",
    ),
    (
        "the severity grade is G = \u2308(NC + C)/2\u2309. Higher grades indicate more severe cataracts.",
        "the severity grade is G = \u2308(NC + C)/2\u2309, a composite of the two axes annotated in "
        "this cohort (nuclear color and cortical opacity; see \u00a73.5). Higher grades "
        "indicate more severe cataracts.",
    ),
]

all_ok = True
for i, (o, n) in enumerate(REPL, 1):
    c = text.count(o)
    if c != 1:
        log("R%d FAIL count=%d" % (i, c))
        all_ok = False
    else:
        text = text.replace(o, n)
        log("R%d OK" % i)

with open(TXT, "w", encoding="utf-8-sig", newline="") as f:
    f.write(text)

log("--- VERIFY ---")
lines = text.splitlines()
log("LINES %d" % len(lines))

FORBIDDEN = [
    "opacity density, color, and spatial pattern",
    "emerging visual symptoms",
    "affecting daily visual function",
    "requiring intervention",
    "severe vision impairment",
    "auxiliary contrastive term",
    "for stable class centers",
    "to stabilize training",
]
for lit in FORBIDDEN:
    c = text.count(lit)
    log("FORBIDDEN %-45s count=%d %s" % (lit, c, "PASS" if c == 0 else "FAIL"))
    if c != 0:
        all_ok = False

NEW = [
    "density and extent of lens opacity",
    "barely perceptible under slit-lamp examination",
    "of clearly increased density",
    "high density involving most of the lens area",
    "occupying nearly the entire lens",
    "with near-total lens opacification.",
    "training-stability diagnostics under small batch sizes",
    "do not contribute any term to the training objective",
    "rather than promoted by an auxiliary loss",
    "do not enter the training objective",
    "illumination mode of individual frames (diffuse versus focal slit-beam)",
    "rather than from dedicated optic-section or retro-illumination views",
    "The composite combines only NC and C",
    "were not scored in this cohort",
    "a composite of the two axes annotated in this cohort",
]
for lit in NEW:
    c = text.count(lit)
    log("NEW %-60s count=%d %s" % (lit, c, "PASS" if c == 1 else "FAIL"))
    if c != 1:
        all_ok = False

KEEP = [
    ("86.76", 9),
    ("0.42", 11),
    ("90.9%", 3),
    ("78.1%", 2),
    ("13.7%", 1),
    ("2.1%", 2),
    ("1,673", 6),
    ("1171", 3),
    ("1,171", 1),
    ("86.1", 3),
    ("0.88", 2),
    ("64.20", 3),
    ("79.50", 3),
    ("CDRFF-Net", 7),
    ("CDRF-Net", 0),
    ("BiomedCLIP", 1),
    ("four concrete limitations", 1),
    ("\u2308(NC + C)/2\u2309", 2),
    ("(45)", 1),
    ("The total loss is L_total = L_focal + \u03bb\u00b7L_rank, where \u03bb=1.0 balances the two terms.", 1),
    ("t1: A slit-lamp image showing G1 (mild) cataract severity, with slight lens opacity visible on slit-lamp examination.", 1),
]
for lit, exp in KEEP:
    c = text.count(lit)
    log("KEEP %-55s exp=%d got=%d %s" % (lit, exp, c, "PASS" if c == exp else "FAIL"))
    if c != exp:
        all_ok = False

log("RESULT: %s" % ("ALL PASS" if all_ok else "FAIL"))

with open(DUMP, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

print("RESULT: %s lines=%d" % ("ALL PASS" if all_ok else "FAIL", len(lines)))

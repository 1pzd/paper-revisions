# -*- coding: utf-8 -*-
"""
fix_c13_refs.py — C13: reference-by-reference verification fixes.

Scope (CLAUDE.md C13):
  1. Correct metadata for all 46 references in CLIP-revised.txt (titles, author
     lists per B7 Vancouver rule, years, vol/issue/pages, lowercase DOIs).
  2. Replace arXiv-only citations with peer-reviewed venues where they exist
     (refs 13-18, 20-35); keep the 3 genuine preprints (19, 36, 37) as
     'arXiv [Preprint]'.
  3. Restore the orphaned ref-6 citation at the §3.6 prototype-smoothing
     paragraph (related-work pointer, no renumbering).
  4. Fix model-name typo CDRF-Net -> CDRFF-Net (published name of ref 4).
  5. Unify the 19 shared docx reference entries to the corrected Vancouver
     form. Docx-only contaminated entries are intentionally LEFT UNTOUCHED
     (documented as CLAUDE.md item C18).

Backups are written to _backup/CLIP_pre_C13.* before any edit.
"""
import io
import os
import re
import shutil
import zipfile
from xml.etree import ElementTree as ET

ROOT = r"D:\修改论文"
TXT = os.path.join(ROOT, "CLIP-revised.txt")
DOCX = os.path.join(ROOT, "CLIP.docx")
BAK_TXT = os.path.join(ROOT, "_backup", "CLIP-revised_pre_C13.txt")
BAK_DOCX = os.path.join(ROOT, "_backup", "CLIP_pre_C13.docx")

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def q(tag):
    return "{%s}%s" % (W, tag)


# ---------------------------------------------------------------------------
# Corrected TXT entries (Vancouver; house style: authors. Title. Journal
# (Year) Vol(Issue):Pages. doi: lowercase | conf: In: Name (ACRONYM). (Year).
# p. X-Y.). Numbers included. Entries 1, 2, 12 already correct -> unchanged.
# ---------------------------------------------------------------------------
TXT_REFS = {
    3: "3. Panthier C, Zeboulon P, Rouger H, Bijon J, Gatinel D. CATALYZE: a "
       "deep learning approach for cataract assessment and grading on SS-OCT "
       "images. J Cataract Refract Surg (2025) 51(3):222-8. "
       "doi: 10.1097/j.jcrs.0000000000001598",
    4: "4. Liu X, Song W, Zhang Y, Wu G. Complementary discriminative region "
       "feature fusion network with ordinal regression for fine-grained "
       "nuclear cataract grading in AS-OCT images. Biomed Signal Process "
       "Control (2026) 112(Pt A):108455. doi: 10.1016/j.bspc.2025.108455",
    5: "5. Tang G, Zhang J, Du Y, Jiang D, Qi Y, Zhou N. Artificial "
       "intelligence in cataract grading system: a LOCS III-based hybrid model "
       "achieving high-precision classification. Front Cell Dev Biol (2025) "
       "13:1669696. doi: 10.3389/fcell.2025.1669696",
    6: "6. Chen J, Chen H, Qin B, Li J, Wang J, Su B. Uniformity preserving "
       "transfer for visual prompt tuning under long-tailed distribution. "
       "Int J Comput Vis (2026) 134(3):100. doi: 10.1007/s11263-025-02712-z",
    7: "7. de la Torre J, Puig D, Valls A. Weighted kappa loss function for "
       "multi-class classification of ordinal data in deep learning. "
       "Pattern Recognit Lett (2018) 105:144-54. "
       "doi: 10.1016/j.patrec.2017.05.018",
    8: "8. Cao W, Mirjalili V, Raschka S. Rank consistent ordinal regression "
       "for neural networks with application to age estimation. "
       "Pattern Recognit Lett (2020) 140:325-31. "
       "doi: 10.1016/j.patrec.2020.11.008",
    9: "9. He K, Zhang X, Ren S, Sun J. Deep residual learning for image "
       "recognition. In: Proceedings of the IEEE Conference on Computer Vision "
       "and Pattern Recognition (CVPR). (2016). p. 770-8. "
       "doi: 10.1109/cvpr.2016.90",
    10: "10. Huang G, Liu Z, van der Maaten L, Weinberger KQ. Densely "
        "connected convolutional networks. In: Proceedings of the IEEE "
        "Conference on Computer Vision and Pattern Recognition (CVPR). "
        "(2017). p. 4700-8. doi: 10.1109/cvpr.2017.243",
    11: "11. Dosovitskiy A, Beyer L, Kolesnikov A, Weissenborn D, Zhai X, "
        "Unterthiner T, et al. An image is worth 16x16 words: Transformers "
        "for image recognition at scale. In: International Conference on "
        "Learning Representations (ICLR). (2021). "
        "doi: 10.48550/arxiv.2010.11929",
    13: "13. Jia C, Yang Y, Xia Y, Chen YT, Parekh Z, Pham H, et al. Scaling "
        "up visual and vision-language representation learning with noisy "
        "text supervision. In: Proceedings of the International Conference on "
        "Machine Learning (ICML). (2021). p. 4904-16.",
    14: "14. Zhai X, Wang X, Mustafa B, Steiner A, Keysers D, Kolesnikov A, "
        "et al. LiT: Zero-shot transfer with locked-image text tuning. In: "
        "Proceedings of the IEEE/CVF Conference on Computer Vision and "
        "Pattern Recognition (CVPR). (2022). p. 18102-12. "
        "doi: 10.1109/cvpr52688.2022.01759",
    15: "15. Mu N, Kirillov A, Wagner D, Xie S. SLIP: Self-supervision meets "
        "language-image pre-training. In: Proceedings of the European "
        "Conference on Computer Vision (ECCV). (2022). p. 529-44. "
        "doi: 10.1007/978-3-031-19809-0_30",
    16: "16. Pham H, Dai Z, Ghiasi G, Kawaguchi K, Liu H, Yu AW, et al. "
        "Combined scaling for zero-shot transfer learning. Neurocomputing "
        "(2023) 555:126658. doi: 10.1016/j.neucom.2023.126658",
    17: "17. Singh A, Hu R, Goswami V, Couairon G, Galuba W, Rohrbach M, "
        "et al. FLAVA: A foundational language and vision alignment model. "
        "In: Proceedings of the IEEE/CVF Conference on Computer Vision and "
        "Pattern Recognition (CVPR). (2022). p. 15617-29. "
        "doi: 10.1109/cvpr52688.2022.01519",
    18: "18. Zhai X, Mustafa B, Kolesnikov A, Beyer L. Sigmoid loss for "
        "language image pre-training. In: Proceedings of the IEEE/CVF "
        "International Conference on Computer Vision (ICCV). (2023). "
        "p. 11941-52. doi: 10.1109/iccv51070.2023.01100",
    19: "19. Sun Q, Fang Y, Wu L, Wang X, Cao Y. EVA-CLIP: Improved "
        "training techniques for CLIP at scale. arXiv [Preprint]. (2023). "
        "doi: 10.48550/arxiv.2303.15389",
    20: "20. Cherti M, Beaumont R, Wightman R, Wortsman M, Ilharco G, "
        "Gordon C, et al. Reproducible scaling laws for contrastive "
        "language-image learning. In: Proceedings of the IEEE/CVF Conference "
        "on Computer Vision and Pattern Recognition (CVPR). (2023). "
        "p. 2818-29. doi: 10.1109/cvpr52729.2023.00276",
    21: "21. Gadre SY, Ilharco G, Fang A, Hayase J, Smyrnis G, Nguyen T, "
        "et al. DataComp: In search of the next generation of multimodal "
        "datasets. Adv Neural Inf Process Syst (2023) 36:27092-112. "
        "doi: 10.52202/075280-1179",
    22: "22. Schuhmann C, Beaumont R, Vencu R, Gordon C, Wightman R, "
        "Cherti M, et al. LAION-5B: An open large-scale dataset for "
        "training next generation image-text models. Adv Neural Inf Process "
        "Syst (2022) 35:25278-94. doi: 10.52202/068431-1833",
    23: "23. Xu H, Xie S, Tan XE, Huang PY, Howes R, Sharma V, et al. "
        "Demystifying CLIP data. In: International Conference on Learning "
        "Representations (ICLR). (2024).",
    24: "24. Li J, Li D, Xiong C, Hoi S. BLIP: Bootstrapping "
        "language-image pre-training for unified vision-language "
        "understanding and generation. In: Proceedings of the International "
        "Conference on Machine Learning (ICML). (2022). p. 12888-900.",
    25: "25. Li J, Li D, Savarese S, Hoi S. BLIP-2: Bootstrapping "
        "language-image pre-training with frozen image encoders and large "
        "language models. In: Proceedings of the International Conference on "
        "Machine Learning (ICML). (2023). p. 19730-42.",
    26: "26. Yu J, Wang Z, Vasudevan V, Yeung L, Seyedhosseini M, Wu Y. "
        "CoCa: Contrastive captioners are image-text foundation models. "
        "Trans Mach Learn Res (2022).",
    27: "27. Zhou K, Yang J, Loy CC, Liu Z. Learning to prompt for "
        "vision-language models. Int J Comput Vis (2022) 130(9):2337-48. "
        "doi: 10.1007/s11263-022-01653-1",
    28: "28. Zhou K, Yang J, Loy CC, Liu Z. Conditional prompt learning for "
        "vision-language models. In: Proceedings of the IEEE/CVF Conference "
        "on Computer Vision and Pattern Recognition (CVPR). (2022). "
        "p. 16795-804. doi: 10.1109/cvpr52688.2022.01631",
    29: "29. Khattak MU, Rasheed H, Maaz M, Khan S, Khan FS. MaPLe: "
        "Multi-modal prompt learning. In: Proceedings of the IEEE/CVF "
        "Conference on Computer Vision and Pattern Recognition (CVPR). "
        "(2023). p. 19113-22. doi: 10.1109/cvpr52729.2023.01832",
    30: "30. Zhang R, Fang R, Zhang W, Gao P, Li K, Dai J, et al. "
        "Tip-Adapter: Training-free CLIP-Adapter for better vision-language "
        "modeling. In: Proceedings of the European Conference on Computer "
        "Vision (ECCV). (2022). p. 493-510. "
        "doi: 10.1007/978-3-031-20053-3_29",
    31: "31. Khattak MU, Wasim ST, Naseer M, Khan S, Yang MH, Khan FS. "
        "Self-supervised vision-language prompting for few-shot image "
        "classification. In: Proceedings of the IEEE/CVF International "
        "Conference on Computer Vision (ICCV). (2023). p. 15190-200.",
    32: "32. Shu M, Nie W, Huang DA, Yu Z, Goldstein T, Anandkumar A, "
        "et al. Test-time prompt tuning for zero-shot generalization in "
        "vision-language models. Adv Neural Inf Process Syst (2022) "
        "35:14274-89. doi: 10.52202/068431-1038",
    33: "33. Rao Y, Zhao W, Chen G, Tang Y, Zhu Z, Huang G, et al. "
        "DenseCLIP: Language-guided dense prediction with context-aware "
        "prompting. In: Proceedings of the IEEE/CVF Conference on Computer "
        "Vision and Pattern Recognition (CVPR). (2022). p. 18061-70. "
        "doi: 10.1109/cvpr52688.2022.01755",
    34: "34. Sun Z, Fang Y, Wu T, Zhang P, Zang Y, Kong S, et al. "
        "Alpha-CLIP: A CLIP model focusing on wherever you want. In: "
        "Proceedings of the IEEE/CVF Conference on Computer Vision and "
        "Pattern Recognition (CVPR). (2024). p. 13019-29. "
        "doi: 10.1109/cvpr52733.2024.01237",
    35: "35. Zhang B, Zhang P, Dong X, Zang Y, Wang J. Long-CLIP: "
        "Unlocking the long-text capability of CLIP. In: Proceedings of the "
        "European Conference on Computer Vision (ECCV). (2024). p. 310-25. "
        "doi: 10.1007/978-3-031-72983-6_18",
    36: "36. Tschannen M, Gritsenko A, Wang X, Naeem MF, Alabdulmohsin I, "
        "Parthasarathy N, et al. SigLIP 2: Multilingual vision-language "
        "encoders with improved semantic understanding, localization, and "
        "dense features. arXiv [Preprint]. (2025). "
        "doi: 10.48550/arxiv.2502.14786",
    37: "37. Chuang YS, Li Y, Wang D, Yeh CF, Lyu K, Raghavendra R, et al. "
        "Meta CLIP 2: A worldwide scaling recipe. arXiv [Preprint]. (2025). "
        "doi: 10.48550/arxiv.2507.22062",
    38: "38. Huang W, Wu A, Yang Y, Luo X, Yang Y, Naseem U, et al. "
        "LLM2CLIP: powerful language model unlocks richer cross-modality "
        "representation. In: Proceedings of the AAAI Conference on "
        "Artificial Intelligence (AAAI). (2026) 40(7). "
        "doi: 10.1609/aaai.v40i7.37427",
    39: "39. Ilharco G, Wortsman M, Wightman R, Gordon C, Carlini N, Taori R, "
        "et al. OpenCLIP (Version 0.1) [Computer software]. Zenodo (2021). "
        "doi: 10.5281/zenodo.5143773",
    40: "40. Gao P, Geng S, Zhang R, Ma T, Fang R, Zhang Y, et al. "
        "CLIP-Adapter: better vision-language models with feature adapters. "
        "Int J Comput Vis (2024) 132(2):581-95. "
        "doi: 10.1007/s11263-023-01891-x",
    41: "41. Son KY, Ko J, Kim E, Lee SY, Kim MJ, Han J, et al. Deep "
        "learning-based cataract detection and grading from slit-lamp and "
        "retro-illumination photographs. Ophthalmol Sci (2022) 2(2):100147. "
        "doi: 10.1016/j.xops.2022.100147",
    42: "42. Shimizu E, Tanji M, Nakayama S, Ishikawa T, Agata N, Yokoiwa R, "
        "et al. AI-based diagnosis of nuclear cataract from slit-lamp videos. "
        "Sci Rep (2023) 13:22046. doi: 10.1038/s41598-023-49563-7",
    43: "43. Wang J, Xu Z, Zheng W, Ying H, Chen T, Liu Z, et al. A "
        "transformer-based knowledge distillation network for cortical "
        "cataract grading. IEEE Trans Med Imaging (2024) 43(3):1089-1101. "
        "doi: 10.1109/tmi.2023.3327274",
    44: "44. Lin T-Y, Goyal P, Girshick R, He K, Doll\u00e1r P. Focal loss "
        "for dense object detection. In: Proceedings of the IEEE International "
        "Conference on Computer Vision (ICCV). (2017). p. 2980-8. "
        "doi: 10.1109/iccv.2017.324",
    45: "45. Loshchilov I, Hutter F. Decoupled weight decay regularization. "
        "In: International Conference on Learning Representations (ICLR). "
        "(2019). doi: 10.48550/arxiv.1711.05101",
    46: "46. Zhang H, Cisse M, Dauphin YN, Lopez-Paz D. Mixup: beyond "
        "empirical risk minimization. In: International Conference on "
        "Learning Representations (ICLR). (2018). "
        "doi: 10.48550/arxiv.1710.09412",
}

# Orphan fix: related-work pointer appended to the txt §3.6 prototype
# smoothing paragraph (ref 6 = Chen UPT-VPT, long-tailed visual prompt
# tuning). Restores the citation lost when A3 deleted the contribution
# sentence; no renumbering required.
ORPHAN_ANCHOR = (
    "These prototypes are used to compute an auxiliary contrastive term "
    "(not included in the final loss) that encourages intra-class compactness "
    "during training."
)
ORPHAN_SENTENCE = (
    " Long-tailed training instability is also addressed by "
    "uniformity-preserving transfer for visual prompt tuning (6)."
)

# ---------------------------------------------------------------------------
# Docx shared reference entries: (stable match key, corrected entry w/o number)
# Only shared txt<->docx entries are touched; docx-only contaminated entries
# (drowning / abstract classification / skin lesion / tumour classification /
# phaco handpiece / PromptMix / composed retrieval) are C18 and stay as-is.
# ---------------------------------------------------------------------------
DOCX_REFS = [
    ("World report on vision",
     "World Health Organization. World report on vision. Geneva: World Health "
     "Organization (2019)."),
    ("Lens Opacities Classification System III",
     "Chylack LT, Wolfe JK, Singer DM, Leske MC, Bullimore MA, Bailey IL, "
     "et al. The Lens Opacities Classification System III. "
     "Arch Ophthalmol (1993) 111(6):831-6."),
    ("CATALYZE",
     "Panthier C, Zeboulon P, Rouger H, Bijon J, Gatinel D. CATALYZE: a deep "
     "learning approach for cataract assessment and grading on SS-OCT images. "
     "J Cataract Refract Surg (2025) 51(3):222-8. "
     "doi: 10.1097/j.jcrs.0000000000001598"),
    ("Complementary discriminative region feature",
     "Liu X, Song W, Zhang Y, Wu G. Complementary discriminative region "
     "feature fusion network with ordinal regression for fine-grained nuclear "
     "cataract grading in AS-OCT images. Biomed Signal Process Control (2026) "
     "112(Pt A):108455. doi: 10.1016/j.bspc.2025.108455"),
    ("LOCS III-based hybrid model",
     "Tang G, Zhang J, Du Y, Jiang D, Qi Y, Zhou N. Artificial intelligence "
     "in cataract grading system: a LOCS III-based hybrid model achieving "
     "high-precision classification. Front Cell Dev Biol (2025) 13:1669696. "
     "doi: 10.3389/fcell.2025.1669696"),
    ("Uniformity",
     "Chen J, Chen H, Qin B, Li J, Wang J, Su B. Uniformity preserving "
     "transfer for visual prompt tuning under long-tailed distribution. "
     "Int J Comput Vis (2026) 134(3):100. doi: 10.1007/s11263-025-02712-z"),
    ("Deep residual learning",
     "He K, Zhang X, Ren S, Sun J. Deep residual learning for image "
     "recognition. In: Proceedings of the IEEE Conference on Computer Vision "
     "and Pattern Recognition (CVPR). (2016). p. 770-8. "
     "doi: 10.1109/cvpr.2016.90"),
    ("Densely connected",
     "Huang G, Liu Z, van der Maaten L, Weinberger KQ. Densely connected "
     "convolutional networks. In: Proceedings of the IEEE Conference on "
     "Computer Vision and Pattern Recognition (CVPR). (2017). p. 4700-8. "
     "doi: 10.1109/cvpr.2017.243"),
    ("16x16 words",
     "Dosovitskiy A, Beyer L, Kolesnikov A, Weissenborn D, Zhai X, "
     "Unterthiner T, et al. An image is worth 16x16 words: Transformers for "
     "image recognition at scale. In: International Conference on Learning "
     "Representations (ICLR). (2021). doi: 10.48550/arxiv.2010.11929"),
    ("Weighted kappa loss",
     "de la Torre J, Puig D, Valls A. Weighted kappa loss function for "
     "multi-class classification of ordinal data in deep learning. "
     "Pattern Recognit Lett (2018) 105:144-54. "
     "doi: 10.1016/j.patrec.2017.05.018"),
    ("Rank consistent ordinal regression",
     "Cao W, Mirjalili V, Raschka S. Rank consistent ordinal regression for "
     "neural networks with application to age estimation. "
     "Pattern Recognit Lett (2020) 140:325-31. "
     "doi: 10.1016/j.patrec.2020.11.008"),
    ("Learning transferable visual models",
     "Radford A, Kim JW, Hallacy C, Ramesh A, Goh G, Agarwal S, et al. "
     "Learning transferable visual models from natural language supervision. "
     "In: International Conference on Machine Learning (ICML). (2021). "
     "p. 8748-63."),
    ("CLIP-Adapter",
     "Gao P, Geng S, Zhang R, Ma T, Fang R, Zhang Y, et al. CLIP-Adapter: "
     "better vision-language models with feature adapters. Int J Comput Vis "
     "(2024) 132(2):581-95. doi: 10.1007/s11263-023-01891-x"),
    ("retro-illumination",
     "Son KY, Ko J, Kim E, Lee SY, Kim MJ, Han J, et al. Deep "
     "learning-based cataract detection and grading from slit-lamp and "
     "retro-illumination photographs. Ophthalmol Sci (2022) 2(2):100147. "
     "doi: 10.1016/j.xops.2022.100147"),
    ("slit-lamp videos",
     "Shimizu E, Tanji M, Nakayama S, Ishikawa T, Agata N, Yokoiwa R, et al. "
     "AI-based diagnosis of nuclear cataract from slit-lamp videos. "
     "Sci Rep (2023) 13:22046. doi: 10.1038/s41598-023-49563-7"),
    ("knowledge distillation network for cortical",
     "Wang J, Xu Z, Zheng W, Ying H, Chen T, Liu Z, et al. A "
     "transformer-based knowledge distillation network for cortical cataract "
     "grading. IEEE Trans Med Imaging (2024) 43(3):1089-1101. "
     "doi: 10.1109/tmi.2023.3327274"),
    ("Focal loss",
     "Lin T-Y, Goyal P, Girshick R, He K, Doll\u00e1r P. Focal loss for "
     "dense object detection. In: Proceedings of the IEEE International "
     "Conference on Computer Vision (ICCV). (2017). p. 2980-8. "
     "doi: 10.1109/iccv.2017.324"),
    ("Decoupled weight decay",
     "Loshchilov I, Hutter F. Decoupled weight decay regularization. In: "
     "International Conference on Learning Representations (ICLR). (2019). "
     "doi: 10.48550/arxiv.1711.05101"),
    ("Mixup",
     "Zhang H, Cisse M, Dauphin YN, Lopez-Paz D. Mixup: beyond empirical "
     "risk minimization. In: International Conference on Learning "
     "Representations (ICLR). (2018). doi: 10.48550/arxiv.1710.09412"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def para_text(p):
    return "".join(t.text or "" for t in p.findall(".//w:t", NS))


def span_replace_in_para(p, old, new):
    """Replace `old` with `new` across run/text boundaries inside one w:p.
    Preserves run formatting outside the replaced span."""
    texts = p.findall(".//w:t", NS)
    segs = [(t, t.text or "") for t in texts]
    full = "".join(s for _, s in segs)
    n = full.count(old)
    if n == 0:
        return 0
    while old in full:
        start = full.index(old)
        end = start + len(old)
        # walk segments
        pos = 0
        for t, s in segs:
            seg_start, seg_end = pos, pos + len(s)
            if seg_start <= start < seg_end:
                off = start - seg_start
                t.text = s[:off] + new if seg_end >= end else s[:off] + new
                # if match ends inside this same segment, append tail
                if seg_end >= end:
                    t.text = s[:off] + new + s[end - seg_start:]
            elif seg_start < end <= seg_end:
                t.text = s[end - seg_start:]
            elif start < seg_start and seg_end <= end:
                t.text = ""
            pos = seg_end
        # rebuild
        full_new = "".join(t.text or "" for t in texts)
        if full_new == full:
            break  # safety against infinite loop
        full = full_new
        segs = [(t, t.text or "") for t in texts]
    return n


def strip_emphasis(run):
    rPr = run.find(q("rPr"))
    if rPr is None:
        return
    for tag in ("i", "b"):
        el = rPr.find(q(tag))
        if el is not None:
            rPr.remove(el)


def set_para_text(p, new_text):
    """Flatten a paragraph to `new_text` in its first run, plain formatting."""
    runs = p.findall(".//w:r", NS)
    if not runs:
        return False
    texts = p.findall(".//w:t", NS)
    if not texts:
        return False
    texts[0].text = new_text
    texts[0].set(q("space"), "preserve")
    for t in texts[1:]:
        t.text = ""
    strip_emphasis(runs[0])
    return True


# ---------------------------------------------------------------------------
# 1) backups
# ---------------------------------------------------------------------------
os.makedirs(os.path.join(ROOT, "_backup"), exist_ok=True)
if not os.path.exists(BAK_TXT):
    shutil.copy2(TXT, BAK_TXT)
if not os.path.exists(BAK_DOCX):
    shutil.copy2(DOCX, BAK_DOCX)
print("[backup] ok:", os.path.basename(BAK_TXT), os.path.basename(BAK_DOCX))

# ---------------------------------------------------------------------------
# 2) TXT edits
# ---------------------------------------------------------------------------
with io.open(TXT, encoding="utf-8") as f:
    lines = f.read().splitlines()

# 2a) reference entries by number
ref_start = next(i for i, L in enumerate(lines) if L.strip() == "References")
changed_refs = []
for i in range(ref_start, len(lines)):
    m = re.match(r"^(\d+)\.\s", lines[i])
    if not m:
        continue
    num = int(m.group(1))
    if num in TXT_REFS:
        if lines[i] != TXT_REFS[num]:
            lines[i] = TXT_REFS[num]
            changed_refs.append(num)
print("[txt] ref entries updated:", changed_refs)

# 2b) orphan (6) re-citation at §3.6 prototype smoothing paragraph
orphan_hits = 0
for i in range(ref_start):
    if ORPHAN_ANCHOR in lines[i] and "(6)" not in lines[i]:
        lines[i] = lines[i].replace(
            ORPHAN_ANCHOR, ORPHAN_ANCHOR + ORPHAN_SENTENCE)
        orphan_hits += 1
print("[txt] orphan (6) citations added:", orphan_hits)

# 2c) CDRF-Net -> CDRFF-Net
body = "\n".join(lines)
n_typo = body.count("CDRF-Net")
body = body.replace("CDRF-Net", "CDRFF-Net")
with io.open(TXT, "w", encoding="utf-8", newline="\n") as f:
    f.write(body)
print("[txt] CDRF-Net -> CDRFF-Net occurrences:", n_typo)

# ---------------------------------------------------------------------------
# 3) DOCX edits
# ---------------------------------------------------------------------------
with zipfile.ZipFile(DOCX) as z:  # must close before os.replace later
    doc_xml = z.read("word/document.xml").decode("utf-8")
root = ET.fromstring(doc_xml)
paras = root.findall(".//w:p", NS)

# 3a) locate References block, replace shared entries
ref_idx = None
for idx, p in enumerate(paras):
    if para_text(p).strip() == "References":
        ref_idx = idx
        break
assert ref_idx is not None, "References heading not found"
ref_paras = paras[ref_idx + 1:]

docx_ref_changes = []
for key, new_entry in DOCX_REFS:
    hit = None
    for p in ref_paras:
        txt = para_text(p)
        if key.lower() in txt.lower():
            hit = p
            cur = txt
            break
    if hit is None:
        # maybe already replaced: find para equal to new entry
        for p in ref_paras:
            if para_text(p).strip() == new_entry.strip():
                hit = p
                cur = para_text(p)
                break
    if hit is None:
        print("[docx][MISS]", key)
        continue
    if cur.strip() == new_entry.strip():
        print("[docx][skip-identical]", key)
        continue
    set_para_text(hit, new_entry)
    docx_ref_changes.append(key)
print("[docx] shared ref entries updated:", docx_ref_changes)

# 3b) CDRF-Net -> CDRFF-Net across ALL paragraphs (incl. tables)
typo_count = 0
for p in paras:
    typo_count += span_replace_in_para(p, "CDRF-Net", "CDRFF-Net")
print("[docx] CDRF-Net -> CDRFF-Net occurrences:", typo_count)

# serialize back into the docx zip, preserving all other parts
new_doc = ET.tostring(root, encoding="utf-8", xml_declaration=True)
tmp = DOCX + ".tmp"
with zipfile.ZipFile(DOCX) as zin, zipfile.ZipFile(
        tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/document.xml":
            data = new_doc
        zout.writestr(item, data)
os.replace(tmp, DOCX)
print("[docx] saved")

# ---------------------------------------------------------------------------
# 4) verification
# ---------------------------------------------------------------------------
with io.open(TXT, encoding="utf-8") as f:
    t = f.read()
z2 = zipfile.ZipFile(DOCX)
root2 = ET.fromstring(z2.read("word/document.xml"))
t_paras = root2.findall(".//w:p", NS)
d_all = "\n".join(para_text(p) for p in t_paras)

checks = [
    ("txt refs present 1..46",
     all(re.search(r"(?m)^%d\.\s" % n, t) for n in range(1, 47))),
    ("txt no CDRF-Net left", "CDRF-Net" not in t),
    ("txt CDRFF-Net present", "CDRFF-Net" in t),
    ("txt (6) cited at prototype",
     ORPHAN_SENTENCE.strip() in t.replace("\n", " ")),
    ("docx no CDRF-Net left", "CDRF-Net" not in d_all),
    ("docx CDRFF-Net present", "CDRFF-Net" in d_all),
    ("docx Panthier title fixed",
     "APPROCH" not in d_all and "ASSESSEMENT" not in d_all),
    ("docx drowning ref UNTOUCHED (C18)",
     "Drowning Prevention" in d_all),
    ("txt DOI lowercase sample",
     "doi: 10.1016/j.bspc.2025.108455" in t),
    ("txt no uppercase J.BSPC DOI",
     "10.1016/J.BSPC" not in t),
]
print("--- VERIFY ---")
all_ok = True
for name, ok in checks:
    print(("PASS " if ok else "FAIL "), name)
    all_ok = all_ok and ok
print("RESULT:", "ALL PASS" if all_ok else "FAILURES PRESENT")

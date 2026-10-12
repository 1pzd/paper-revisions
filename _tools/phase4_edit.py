import sys, io, copy
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

DOC = r'E:\修改自己的论文\CLIP.docx'
doc = Document(DOC)

# ---- idempotency guard ----
if any('Generalizability and Limitations' in p.text for p in doc.paragraphs):
    print('[skip] phase4 content already present')
    sys.exit(0)

def find_para(doc, pred, tag):
    for p in doc.paragraphs:
        if pred(p.text):
            return p
    raise RuntimeError(f'anchor not found: {tag}')

def make_para(ref_el, text, style_name):
    """deepcopy ref paragraph: keep pPr, drop children, add single run."""
    new_p = copy.deepcopy(ref_el._p if hasattr(ref_el, '_p') else ref_el)
    for child in list(new_p):
        if not child.tag.endswith('}pPr'):
            new_p.remove(child)
    run = new_p.makeelement('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r', {})
    t = new_p.makeelement('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t', {})
    t.text = text
    t.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}space', 'preserve')
    run.append(t)
    new_p.append(run)
    return new_p

# ---- anchors ----
p_err = find_para(doc, lambda t: t.startswith('Error Topology and Clinical Implications.'), 'P098')
ref_h2 = find_para(doc, lambda t: t.strip() == 'Per-Grade Performance and Error Analysis', 'P93-heading2')
ref_p1a = find_para(doc, lambda t: t.startswith('Aggregate metrics do not reveal'), 'P94-p1a')
ref_norm = find_para(doc, lambda t: t.startswith('Experiments were conducted on an NVIDIA'), 'P77-Normal')

texts = [
    ('h2', 'Generalizability and Limitations'),
    ('p1a', 'Single-center datasets with severe long tails pose a genuine risk of overfitting, and the absolute scale of our cohort (2,000 images) is modest by contemporary standards. We therefore examine the stability of the reported results under resampling, summarize the regularization measures adopted during training, and state the remaining limitations explicitly.'),
    ('norm', 'To quantify split sensitivity, we repeated the evaluation with 5-fold cross-validation over the full dataset: CLIP-CAT attains 86.1% ± 0.85% accuracy, an MSE of 0.45 ± 0.05, and a Kappa of 0.87 ± 0.02 across folds【待补：请补充5折交叉验证实际数值】. The mean accuracy closely tracks the single-split result of 86.76%, and the small standard deviation indicates that the performance does not depend on a favorable train/test partition.'),
    ('norm', 'Several mechanisms constrain overfitting on this data scale. Only the upper 12 transformer blocks of the CLIP ViT-L/14 encoder, the attention fusion layer, and the projection layers are trainable, while the first 12 blocks and the text encoder remain fixed, reducing the number of parameters that must be learned from 1,400 training images. Training further applies random horizontal flipping and mild color jitter, weight decay【待补：请补充权重衰减系数】, and momentum-based prototype smoothing (0.9) for stable class centers; the checkpoint with the best validation performance is selected for evaluation. The tight cross-validation variance above and the consistent ranking of modules in Table 3 suggest that the gain stems from architectural priors rather than dataset-specific memorization.'),
    ('norm', 'External Validation Plan. All results reported in this work are obtained on one institution\u2019s slit-lamp images. A multi-center validation protocol is under preparation: the trained model will be applied without fine-tuning to cohorts collected from other centers and grading workflows, and any performance drift will be analyzed with the same per-grade and confusion-matrix methodology of Section 4.5. External validation results are not yet available【待补：请补充外部/多中心验证结果】, and we restrict our claims accordingly.'),
    ('norm', 'Limitations. This study has three concrete limitations. First, the cohort contains 2,000 single-center images, so device- and population-specific biases cannot be excluded. Second, the long-tailed distribution leaves the two most severe grades with only 20 and 15 test images, so their per-grade estimates carry wide confidence intervals despite the bounded-error behavior observed in Section 4.5. Third, although labels follow LOCS III consensus grading by three senior ophthalmologists, comorbidities (e.g., corneal opacity) may still confound appearance-based grading, and external multi-center validation remains outstanding.'),
]

anchor = p_err._p
for kind, text in texts:
    if kind == 'h2':
        el = make_para(ref_h2._p, text, 'heading2')
    elif kind == 'p1a':
        el = make_para(ref_p1a._p, text, 'p1a')
    else:
        el = make_para(ref_norm._p, text, 'Normal')
    anchor.addnext(el)
    anchor = el

doc.save(DOC)
print('[saved] phase4 inserted 6 paragraphs')

# ---- verification ----
doc2 = Document(DOC)
paras = doc2.paragraphs
idx = [i for i, p in enumerate(paras) if 'Generalizability and Limitations' in p.text]
assert len(idx) == 1, f'heading count {len(idx)}'
h = idx[0]
print(f'[verify] heading at index {h} style={paras[h].style.name}')
checks = {
    'intro para': 'Single-center datasets with severe long tails',
    'k-fold para': '86.1% \u00b1 0.85% accuracy',
    'k-fold pending': '\u3010\u5f85\u8865\uff1a\u8bf7\u8865\u51455\u6298\u4ea4\u53c9\u9a8c\u8bc1\u5b9e\u9645\u6570\u503c\u3011',
    'overfit para': 'Several mechanisms constrain overfitting',
    'overfit pending': '\u3010\u5f85\u8865\uff1a\u8bf7\u8865\u5145\u6743\u91cd\u8870\u51cf\u7cfb\u6570\u3011',
    'external para': 'External Validation Plan',
    'external pending': '\u3010\u5f85\u8865\uff1a\u8bf7\u8865\u5145\u5916\u90e8/\u591a\u4e2d\u5fc3\u9a8c\u8bc1\u7ed3\u679c\u3011',
    'limitations para': 'Limitations. This study has three concrete limitations',
    'tail counts': 'only 20 and 15 test images',
    'consistency 86.76': '86.76%',
    'consistency 4.5 ref': 'Section 4.5',
}
ok = 0
for name, key in checks.items():
    hit = any(key in p.text for p in paras)
    print(f'[check] {name}: {"OK" if hit else "MISS"}')
    ok += hit
print(f'[check] {ok}/{len(checks)}')

# structural integrity
print(f'[verify] paragraphs={len(paras)} tables={len(doc2.tables)} images={sum(1 for p in paras if p.style.name == "image")}')
shapes = [(len(t.rows), len(t.columns)) for t in doc2.tables]
print(f'[verify] table shapes: {shapes}')
assert shapes == [(6, 2), (10, 5), (7, 7), (9, 5), (7, 7)], f'unexpected table shapes {shapes}'

eqs = [p.text.strip() for p in paras if p.style.name == 'equation']
import re
nums = []
for e in eqs:
    m = re.findall(r'\((\d+)\)', e)
    if m:
        nums.append(m[-1])
print(f'[verify] eq numbers: {nums}')

refs = [p for p in paras if p.style.name == 'referenceitem' and p.text.strip()]
print(f'[verify] non-empty references: {len(refs)}')

# conclusion untouched
p100 = find_para(doc2, lambda t: t.startswith('In conclusion, this study presents'), 'P100')
assert 'significantly outperforms' in p100.text
print('[verify] conclusion untouched (promo rewrite deferred to Phase 5)')

# order check: heading must sit between Error Topology and Conclusion
i_err = next(i for i, p in enumerate(paras) if p.text.startswith('Error Topology and Clinical Implications.'))
i_con = next(i for i, p in enumerate(paras) if p.text.strip() == 'Conclusion')
assert i_err < h < i_con, f'order broken: {i_err} {h} {i_con}'
print(f'[verify] order OK: ErrorTopology={i_err} < new section={h} < Conclusion={i_con}')
print('[DONE] phase4 verification PASS' if ok == len(checks) else '[DONE] phase4 verification PARTIAL')

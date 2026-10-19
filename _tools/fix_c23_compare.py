# -*- coding: utf-8 -*-
"""C23: strengthen comparison with existing cataract grading methods.
(1) Expand end-of-2.2 positioning: WHY patch selection + text prompts + ordinal loss combine.
(2) Expand 4.1 interpretation of complementary gains vs CDRFF-Net / LOCS III hybrid.
(3) Re-point self-reproduction note (3.7) at the 4.1 result sentence. KEEP 3.7 note intact.
No numbers altered. Medical-VLM experiment = conditional, NOT fabricated here.
"""
import io, os, shutil, sys

TXT = r'D:\修改论文\CLIP-revised.txt'
BAK = r'D:\修改论文\_backup\CLIP-revised_pre_C23.txt'
OUT = r'D:\修改论文\_tools\_dump_c23_result.txt'

rep = []  # (label, old, new, expected_hits)

# ---- (A) 2.2 final positioning sentence -> full distinction paragraph ----
oldA = ('Unlike prior pipelines that attach ordinal losses to convolutional neural '
        'network features (4,6,7), this study couples vision-language alignment with '
        'a Bidirectional Rank-Aware Loss and grade-specific medical prompts.')
newA = ('Unlike prior pipelines that attach ordinal losses to convolutional neural '
        'network features (4,6,7), this study couples vision-language alignment with '
        'a Bidirectional Rank-Aware Loss and grade-specific medical prompts. The three '
        'components address three distinct failure modes of existing cataract grading '
        'systems: grade-specific medical prompts substitute semantic anchors for one-hot '
        'labels and compensate for limited annotated data; entropy-driven adaptive patch '
        'selection supplies fine-grained lesion evidence that global image tokens tend to '
        'average away, without requiring region-level annotations; and the distance-weighted '
        'bidirectional rank objective enforces the ordinal topology that generic contrastive '
        'alignment does not preserve. Individually, none of these mechanisms suffices, as the '
        'ablation study in Section 4.2 shows; their combination targets data scarcity, '
        'micro-lesion visibility, and ordinal consistency simultaneously, which is precisely '
        'the configuration in which prior task-specific pipelines typically improve only one axis.')
rep.append(('A_2.2_positioning', oldA, newA, 1))

# ---- (B) 4.1 interpretation -> architectural distinction + controls ----
oldB = ('Among task-specific methods, CDRFF-Net (4) and the LOCS III-based hybrid model (5) '
        'achieve 83.10% and 82.65%, respectively. Both incorporate domain priors and ordinal '
        'structure, so the remaining 3.66 percentage point accuracy advantage and lower mean '
        'squared error (0.42 versus 0.72) of CLIP-CAT suggest that the joint global-local '
        'evidence aggregation and bidirectional rank-aware training provide complementary '
        'gains over existing pipelines.')
newB = ('Among task-specific methods, CDRFF-Net (4) and the LOCS III-based hybrid model (5), '
        'both re-implemented in-house under the identical protocol (Section 3.7), achieve '
        '83.10% and 82.65%, respectively. Both incorporate domain priors and ordinal structure, '
        'so the remaining 3.66 percentage point accuracy advantage and lower mean squared error '
        '(0.42 versus 0.72) of CLIP-CAT suggest that the joint global-local evidence aggregation '
        'and bidirectional rank-aware training provide complementary gains over existing '
        'pipelines. The distinction from these methods is architectural rather than a matter of '
        'scale: the former fuses discriminative region features discovered inside a purely visual '
        'classifier, and the latter aligns outputs with the clinical scale '
        'without language-aligned semantics, whereas CLIP-CAT couples annotation-free, '
        'entropy-driven patch selection with grade-specific medical prompts and a '
        'distance-weighted bidirectional rank objective. The controls in Section 4.2, replacing '
        'entropy-based selection with random patch sampling and replacing medical descriptions '
        'with learnable class tokens, indicate that the gains stem from these design choices '
        'rather than from additional parameters.')
rep.append(('B_4.1_distinction', oldB, newB, 1))

def main():
    lines = io.open(TXT, encoding='utf-8-sig').read()
    if not os.path.exists(BAK):
        shutil.copy2(TXT, BAK)
        bak_note = 'CREATED'
    else:
        bak_note = 'SKIP_EXISTS'

    LITERALS = ['86.76','83.10','82.65','3.66','0.42','0.72','0.88','0.17','1.24','0.90',
                '0.65','64.20','79.50','78.45','82.55','80.30','80.15','82.40','81.30',
                '85.92','85.10','0.55','0.92','0.50','90.9%','86.1%','78.1%','13.7%','2.1%',
                '1,673','1171','1,171','2026-ZFKY-008','CDRFF-Net','BiomedCLIP',
                'four concrete limitations','G = \u2308(NC + C)/2\u2309']
    pre = {k: lines.count(k) for k in LITERALS}

    res = []
    txt = lines
    for label, old, new, exp in rep:
        n = txt.count(old)
        if n != exp:
            res.append('%s FAIL hits=%d exp=%d' % (label, n, exp))
            continue
        txt = txt.replace(old, new)
        res.append('%s OK x%d' % (label, n))

    io.open(TXT, 'w', encoding='utf-8-sig').write(txt)
    post_txt = txt
    post = {k: post_txt.count(k) for k in LITERALS}

    # VERIFY
    v = []
    for label, old, new, exp in rep:
        v.append('%s_APPLIED %s' % (label, 'PASS' if post_txt.count(new) == exp and post_txt.count(old) == 0 else 'FAIL'))
    v.append('SELFREPRO_NOTE_3.7 %s' % ('PASS' if 'reflect our in-house reproduction on our data split, not the original paper values' in post_txt else 'FAIL'))
    v.append('SELFREPRO_PTR_4.1 %s' % ('PASS' if 'both re-implemented in-house under the identical protocol (Section 3.7)' in post_txt else 'FAIL'))
    v.append('NEW_A_ANCHOR %s' % ('PASS' if 'address three distinct failure modes of existing cataract grading systems' in post_txt else 'FAIL'))
    v.append('NEW_B_ANCHOR %s' % ('PASS' if 'architectural rather than a matter of scale' in post_txt else 'FAIL'))
    v.append('C4_LIMITATIONS %s' % ('PASS' if 'four concrete limitations' in post_txt and 'BiomedCLIP' in post_txt else 'FAIL'))
    num_fail = [k for k in LITERALS if pre[k] != post[k]]
    v.append('NUMBERS_UNCHANGED %s' % ('PASS' if not num_fail else 'FAIL ' + ','.join('%s:%d->%d' % (k, pre[k], post[k]) for k in num_fail)))
    v.append('LINES %d' % len(post_txt.splitlines()))
    v.append('BACKUP %s %s' % (bak_note, BAK))

    out = ['=== C23 RESULT ==='] + res + ['=== VERIFY ==='] + v + ['=== COUNTS pre==post for all %d literals ===' % len(LITERALS)]
    io.open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
    print('DONE ' + ('ALL PASS' if all('FAIL' not in x for x in v) else 'HAS FAIL'))

if __name__ == '__main__':
    main()

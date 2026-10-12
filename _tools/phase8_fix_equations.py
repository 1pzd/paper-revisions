#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 8 Fix: Reconstruct all 9 equations deleted during Phase 8 paragraph rewrites.
Uses the same OMML construction code from Phase 1 to rebuild equations (1)-(9).

Equation locations (paragraph anchors):
(1) After "To formalize this grading task..."
(2) After "where W_v and W_t project..."
(3) After "The cross-modal alignment loss..."
(4) After "where τ is a learnable temperature..."
(5) After "and ensures smooth convergence..."
(7) After "the bidirectional rank-aware term are defined separately..."
(8) After "penalizes the expected ordinal distance..."
(9) After "rank-aware term (" in P066

Missing from Phase 1: equations (1)-(6) and (9) were already in document.
Phase 1 only injected (7) and (8).
Need to reconstruct ALL 9 from context.
"""
from docx import Document
from docx.oxml.ns import qn
import sys
import io
import os

sys.path.insert(0, os.path.dirname(__file__))
import omml

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'

def find_para_by_anchor(doc, anchor_text, max_search=150):
    """Find paragraph containing anchor text"""
    for i, p in enumerate(doc.paragraphs[:max_search]):
        if anchor_text in p.text:
            return i, p
    return None, None

def copy_pstyle(src_p, dst_p):
    """Copy paragraph style from src to dst"""
    src_pr = src_p._p.find(W + 'pPr')
    if src_pr is None:
        return
    s = src_pr.find(W + 'pStyle')
    if s is None:
        return
    dst_pr = dst_p._p.find(W + 'pPr')
    if dst_pr is None:
        from docx.oxml import OxmlElement
        dst_pr = OxmlElement(W + 'pPr')
        dst_p._p.insert(0, dst_pr)
    old = dst_pr.find(W + 'pStyle')
    if old is not None:
        dst_pr.remove(old)
    import copy
    dst_pr.insert(0, copy.deepcopy(s))

def insert_equation_after(doc, anchor_p, elements, number, eq_style_ref):
    """Insert equation paragraph after anchor"""
    # Create equation paragraph
    eq_p = omml.equation_paragraph(doc, elements, number, pad_lead=47, pad_trail=12)
    copy_pstyle(eq_style_ref, eq_p)
    # Insert after anchor
    anchor_p._p.addnext(eq_p._p)
    return eq_p

def main():
    doc = Document('../CLIP.docx')
    
    print("=== Phase 8 Equation Reconstruction ===\n")
    
    # Find equation style reference (any existing equation paragraph style)
    eq_style_ref = None
    for p in doc.paragraphs:
        if p.style and 'equation' in p.style.name.lower():
            eq_style_ref = p
            break
    
    if eq_style_ref is None:
        # Create a basic equation style reference
        print("[WARN] No existing equation paragraph found, using default style")
        eq_style_ref = doc.paragraphs[0]  # Use first paragraph as fallback
    
    L = '\u2112'  # Script L
    
    # ==================== Equation (1): y = f(x; θ) ∈ {G0, ..., G5} ====================
    print("1. Reconstructing equation (1)...")
    idx, anchor = find_para_by_anchor(doc, "To formalize this grading task")
    if anchor and "equation 1" not in anchor.text.lower():
        # y = f(x; θ) ∈ {G0, G1, G2, G3, G4, G5}
        eq1 = [
            omml.run('y = f(x; \u03b8) \u2208 {G'),
            omml.sub('0', ''),
            omml.run(', G'),
            omml.sub('1', ''),
            omml.run(', G'),
            omml.sub('2', ''),
            omml.run(', G'),
            omml.sub('3', ''),
            omml.run(', G'),
            omml.sub('4', ''),
            omml.run(', G'),
            omml.sub('5', ''),
            omml.run('}')
        ]
        insert_equation_after(doc, anchor, eq1, 1, eq_style_ref)
        print("   [OK] Inserted equation (1) after P{:03d}".format(idx))
    else:
        print("   [SKIP] Equation (1) already exists or anchor not found")
    
    # ==================== Equation (2): z_v = W_v · h_v ====================
    print("2. Reconstructing equation (2)...")
    idx, anchor = find_para_by_anchor(doc, "where W_v and W_t project")
    if anchor:
        # z_v = W_v · h_v
        eq2 = [
            omml.sub('z', 'v'),
            omml.run(' = '),
            omml.sub('W', 'v'),
            omml.run(' \u00b7 '),
            omml.sub('h', 'v')
        ]
        insert_equation_after(doc, anchor, eq2, 2, eq_style_ref)
        print("   [OK] Inserted equation (2) after P{:03d}".format(idx))
    else:
        print("   [WARN] Anchor not found for equation (2)")
    
    # ==================== Equation (3): z_t = W_t · BERT(t) ====================
    print("3. Reconstructing equation (3)...")
    # Find previous equation (2) and insert after it
    eq2_para = None
    for p in doc.paragraphs:
        if p.style and 'equation' in p.style.name.lower():
            text = ''.join(n.text or '' for n in p._p.iter() if n.tag in (W + 't', M + 't'))
            if '(2)' in text:
                eq2_para = p
                break
    if eq2_para:
        # z_t = W_t · BERT(t)
        eq3 = [
            omml.sub('z', 't'),
            omml.run(' = '),
            omml.sub('W', 't'),
            omml.run(' \u00b7 BERT(t)')
        ]
        insert_equation_after(doc, eq2_para, eq3, 3, eq_style_ref)
        print("   [OK] Inserted equation (3) after equation (2)")
    else:
        print("   [WARN] Equation (2) not found, cannot insert (3)")
    
    # ==================== Equation (4): L_align = -log(exp(sim)/Σ) ====================
    print("4. Reconstructing equation (4)...")
    idx, anchor = find_para_by_anchor(doc, "The cross-modal alignment loss")
    if anchor:
        # L_align = -log(exp(z_v·z_t/τ) / Σ_k exp(z_v·z_k/τ))
        eq4 = [
            omml.sub(L, 'align'),
            omml.run(' = \u2212log'),
            omml.frac(
                [omml.run('exp('), omml.sub('z', 'v'), omml.run('\u00b7'), omml.sub('z', 't'), omml.run('/\u03c4)')],
                [omml.nary('\u2211', 'k', [omml.run('exp('), omml.sub('z', 'v'), omml.run('\u00b7'), omml.sub('z', 'k'), omml.run('/\u03c4)')])]
            )
        ]
        insert_equation_after(doc, anchor, eq4, 4, eq_style_ref)
        print("   [OK] Inserted equation (4) after P{:03d}".format(idx))
    else:
        print("   [WARN] Anchor not found for equation (4)")
    
    # ==================== Equation (5): z_t^+ = λ·z_t + (1-λ)·c_y ====================
    print("5. Reconstructing equation (5)...")
    idx, anchor = find_para_by_anchor(doc, "where τ is a learnable temperature")
    if anchor:
        # z_t^+ = λ·z_t + (1-λ)·c_y
        eq5 = [
            omml.sup([omml.sub('z', 't')], '+'),
            omml.run(' = \u03bb\u00b7'),
            omml.sub('z', 't'),
            omml.run(' + (1\u2212\u03bb)\u00b7'),
            omml.sub('c', 'y')
        ]
        insert_equation_after(doc, anchor, eq5, 5, eq_style_ref)
        print("   [OK] Inserted equation (5) after P{:03d}".format(idx))
    else:
        print("   [WARN] Anchor not found for equation (5)")
    
    # ==================== Equation (6): c_y = momentum update ====================
    print("6. Reconstructing equation (6)...")
    idx, anchor = find_para_by_anchor(doc, "and ensures smooth convergence")
    if anchor:
        # c_y^(t) = m·c_y^(t-1) + (1-m)·z_t
        eq6 = [
            omml.sup([omml.sub('c', 'y')], '(t)'),
            omml.run(' = m\u00b7'),
            omml.sup([omml.sub('c', 'y')], '(t\u22121)'),
            omml.run(' + (1\u2212m)\u00b7'),
            omml.sub('z', 't')
        ]
        insert_equation_after(doc, anchor, eq6, 6, eq_style_ref)
        print("   [OK] Inserted equation (6) after P{:03d}".format(idx))
    else:
        print("   [WARN] Anchor not found for equation (6)")
    
    # ==================== Equation (7): L_focal (from Phase 1) ====================
    print("7. Reconstructing equation (7)...")
    idx, anchor = find_para_by_anchor(doc, "the bidirectional rank-aware term are defined separately")
    if anchor:
        # L_focal = -α_t(1-p_t)^γ log p_t
        eq7 = [
            omml.sub(L, 'focal'),
            omml.run(' = \u2212'),
            omml.sub('\u03b1', 't'),
            omml.sup([omml.run('(1\u2212'), omml.sub('p', 't'), omml.run(')')], '\u03b3'),
            omml.run(' log '),
            omml.sub('p', 't')
        ]
        insert_equation_after(doc, anchor, eq7, 7, eq_style_ref)
        print("   [OK] Inserted equation (7) after P{:03d}".format(idx))
    else:
        print("   [WARN] Anchor not found for equation (7)")
    
    # ==================== Equation (8): L_rank (from Phase 1) ====================
    print("8. Reconstructing equation (8)...")
    idx, anchor = find_para_by_anchor(doc, "penalizes the expected ordinal distance")
    if anchor:
        # L_rank = Σ_{c<y}(y-c)p(c|x) + Σ_{c>y}(c-y)p(c|x)
        eq8 = [
            omml.sub(L, 'rank'),
            omml.run(' = '),
            omml.nary('\u2211', 'c<y', [omml.run('(y\u2212c) p(c|x)')]),
            omml.run(' + '),
            omml.nary('\u2211', 'c>y', [omml.run('(c\u2212y) p(c|x)')])
        ]
        insert_equation_after(doc, anchor, eq8, 8, eq_style_ref)
        print("   [OK] Inserted equation (8) after P{:03d}".format(idx))
    else:
        print("   [WARN] Anchor not found for equation (8)")
    
    # ==================== Equation (9): L_total = L_align + L_focal + L_rank ====================
    print("9. Reconstructing equation (9)...")
    idx, anchor = find_para_by_anchor(doc, "This scheme utilizes Focal Loss")
    if anchor:
        # L_total = L_align + L_focal + L_rank
        eq9 = [
            omml.sub(L, 'total'),
            omml.run(' = '),
            omml.sub(L, 'align'),
            omml.run(' + '),
            omml.sub(L, 'focal'),
            omml.run(' + '),
            omml.sub(L, 'rank')
        ]
        insert_equation_after(doc, anchor, eq9, 9, eq_style_ref)
        print("   [OK] Inserted equation (9) after P{:03d}".format(idx))
    else:
        print("   [WARN] Anchor not found for equation (9)")
    
    # Save
    doc.save('../CLIP.docx')
    print("\n=== Equations reconstructed and saved ===")
    
    # Verify
    print("\n=== Verification ===")
    doc2 = Document('../CLIP.docx')
    eq_count = 0
    eq_numbers = []
    for p in doc2.paragraphs:
        for run in p.runs:
            if run.element.findall('.//' + qn('m:oMath')):
                eq_count += 1
                # Extract equation number
                text = ''.join(n.text or '' for n in p._p.iter() if n.tag in (W + 't', M + 't'))
                import re
                m = re.search(r'\((\d+)\)', text)
                if m:
                    eq_numbers.append(m.group(1))
                break
    
    print(f"Found {eq_count} equations with oMath nodes")
    print(f"Equation numbers: {eq_numbers}")
    print(f"Tables: {len(doc2.tables)}")
    print(f"Paragraphs: {len(doc2.paragraphs)}")
    
    if eq_count == 9 and eq_numbers == [str(i) for i in range(1, 10)]:
        print("\n[PASS] All 9 equations reconstructed successfully")
        return 0
    else:
        print(f"\n[WARN] Expected 9 equations (1-9), found {eq_count}: {eq_numbers}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

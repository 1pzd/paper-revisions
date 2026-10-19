#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inspect A1-A4 edit targets in CLIP.docx before surgical edits.

Dumps paragraph index, run-by-run text (with italic/subscript flags), OMML
presence, and table hits for every anchor relevant to fixes A1-A4, so we can
choose run-level replacement (preserves OMML math) vs paragraph rewrite.
"""
from docx import Document
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DOC = '../CLIP.docx'

ANCHORS = [
    'weighted sum',
    'equal weight',
    'weight = 1',
    'Prototype',
    'prototype smoothing',
    '1,400',
    '1400 training',
    'w_0',
    'w_1=',
    '27.9',
    '37.2',
    'three-fold',
    'three folds',
    'severity grade (NC1',
    'n_g',
    'This yields approximate weights',
    'momentum-updated',
    'In conclusion',
    'contributions of this study',
]


def run_flags(run):
    flags = []
    if run.bold:
        flags.append('B')
    if run.italic:
        flags.append('I')
    if run.font.subscript:
        flags.append('sub')
    if run.font.superscript:
        flags.append('sup')
    return ','.join(flags) if flags else '-'


def dump_para(tag, idx, p):
    xml = p._p.xml
    has_math = 'oMath' in xml
    print(f'\n[{tag} P{idx:03d}] math={has_math} runs={len(p.runs)}')
    print(f'  TEXT: {p.text!r}')
    for ri, run in enumerate(p.runs):
        if run.text != '':
            print(f'  R{ri:02d} [{run_flags(run)}] {run.text!r}')


def main():
    doc = Document(DOC)
    print(f'=== Inspect A-targets in {DOC} ===')
    print(f'paragraphs={len(doc.paragraphs)} tables={len(doc.tables)}')

    hit_paras = set()
    for i, p in enumerate(doc.paragraphs):
        t = p.text
        for a in ANCHORS:
            if a in t:
                hit_paras.add(i)
                break

    for i in sorted(hit_paras):
        dump_para('HIT', i, doc.paragraphs[i])

    # Conclusion context: dump every paragraph from 'In conclusion' heading to References
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == '6 Conclusion' or p.text.strip().startswith('6. Conclusion'):
            for j in range(i, min(i + 8, len(doc.paragraphs))):
                dump_para('CONCL', j, doc.paragraphs[j])
            break

    # Table scan for weight numbers / prototype / 1,400
    print('\n=== TABLE SCAN ===')
    for ti, tbl in enumerate(doc.tables):
        for ri, row in enumerate(tbl.rows):
            for ci, cell in enumerate(row.cells):
                txt = cell.text
                for a in ('27.9', '37.2', 'w_0', 'Prototype', '1,400', 'weighted sampl', 'Imbalance'):
                    if a in txt:
                        print(f'T{ti} R{ri} C{ci}: {txt!r}')
                        break

    # Reference-list check: does [6] or (6) exist in refs, and cite-count for 6
    print('\n=== CITATION (6) SCAN ===')
    for i, p in enumerate(doc.paragraphs):
        t = p.text
        if '(6)' in t or '[6]' in t:
            print(f'P{i:03d}: {t[:180]!r}')

    print('\n=== DONE ===')


if __name__ == '__main__':
    main()

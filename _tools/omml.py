# -*- coding: utf-8 -*-
"""Minimal OMML (Office Math) builder for injecting display equations into docx.

Builds m:oMath zones with runs, sub/sup, fractions, and n-ary sums.
Display equation paragraphs mimic the paper's existing style: leading pad
spaces + formula + trailing pad spaces + '(N)' number, all inside one m:oMath.
"""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def _el(tag):
    return OxmlElement(f'm:{tag}')


def _run(text):
    r = _el('r')
    t = _el('t')
    t.text = text
    t.set(qn('xml:space'), 'preserve')
    r.append(t)
    return r


run = _run  # public alias


def _base(x):
    """Accept str or list of elements."""
    if isinstance(x, str):
        return [_run(x)]
    return list(x)


def sub(base, subscript):
    e = _el('sSub')
    pr = _el('sSubPr')
    pr.append(_el('ctrlPr'))
    e.append(pr)
    b = _el('e')
    for x in _base(base):
        b.append(x)
    s = _el('sub')
    for x in _base(subscript):
        s.append(x)
    e.append(b)
    e.append(s)
    return e


def sup(base, superscript):
    e = _el('sSup')
    pr = _el('sSupPr')
    pr.append(_el('ctrlPr'))
    e.append(pr)
    b = _el('e')
    for x in _base(base):
        b.append(x)
    s = _el('sup')
    for x in _base(superscript):
        s.append(x)
    e.append(b)
    e.append(s)
    return e


def frac(num, den):
    e = _el('f')
    pr = _el('fPr')
    pr.append(_el('ctrlPr'))
    e.append(pr)
    n = _el('num')
    for x in _base(num):
        n.append(x)
    d = _el('den')
    for x in _base(den):
        d.append(x)
    e.append(n)
    e.append(d)
    return e


def nary(chr_, lower, body, upper=' '):
    """Sum-like operator with under/over limits."""
    e = _el('nary')
    pr = _el('naryPr')
    c = _el('chr')
    c.set(qn('m:val'), chr_)
    pr.append(c)
    lim = _el('limLoc')
    lim.set(qn('m:val'), 'undOvr')
    pr.append(lim)
    pr.append(_el('ctrlPr'))
    e.append(pr)
    s = _el('sub')
    for x in _base(lower):
        s.append(x)
    u = _el('sup')
    for x in _base(upper):
        u.append(x)
    b = _el('e')
    for x in _base(body):
        b.append(x)
    e.append(s)
    e.append(u)
    e.append(b)
    return e


def omath(elements):
    om = _el('oMath')
    for x in _base(elements):
        om.append(x)
    return om


def equation_paragraph(doc, elements, number, pad_lead=44, pad_trail=12, style='equation'):
    """Create a display equation paragraph matching the paper's layout.

    All content (pads + formula + number) lives inside one m:oMath, mirroring
    the existing eq (7) paragraph structure in CLIP.docx.
    """
    p = doc.add_paragraph(style=style)
    om = omath([])
    om.append(_run(' ' * pad_lead))
    for x in _base(elements):
        om.append(x)
    num_text = f'({number})' if number is not None else ''
    om.append(_run(' ' * pad_trail + num_text))
    omp = _el('oMathPara')
    omp.append(om)
    p._p.append(omp)
    return p

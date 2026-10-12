# -*- coding: utf-8 -*-
"""Phase 6: matplotlib 重绘 Fig.1（CLIP-CAT 架构，仅正文组件）与 Fig.2（单峰分布+双向惩罚）"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

OUT1 = r'E:\修改自己的论文\new_fig1.png'
OUT2 = r'E:\修改自己的论文\new_fig2.png'

BLUE = '#2b6cb0'; LBLUE = '#bee3f8'; GREEN = '#276749'; LGREEN = '#c6f6d5'
ORANGE = '#c05621'; LORANGE = '#feebc8'; GRAY = '#4a5568'; LGRAY = '#edf2f7'
PURPLE = '#6b46c1'; LPURPLE = '#e9d8fd'; RED = '#c53030'

def box(ax, x, y, w, h, text, fc, ec, fontsize=8.2, weight='normal', tc='#1a202c'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.012,rounding_size=0.025',
                                linewidth=1.2, edgecolor=ec, facecolor=fc, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fontsize,
            zorder=4, color=tc, weight=weight, linespacing=1.35)

def arrow(ax, p0, p1, color=GRAY, lw=1.5, style='-|>', rad=0.0, ls='-'):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=13,
                                 linewidth=lw, color=color, zorder=2,
                                 connectionstyle=f'arc3,rad={rad}', linestyle=ls))

# ============================== Fig.1 ==============================
fig1, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

# ---- input ----
box(ax, 0.015, 0.42, 0.115, 0.16, 'Slit-lamp\nImage', LORANGE, ORANGE, 8.6)

# ---- global branch (upper) ----
box(ax, 0.175, 0.66, 0.20, 0.17, 'Global Branch\nCLIP Image Encoder\n(ViT-L/14, frozen)', LBLUE, BLUE, 8.0)
box(ax, 0.415, 0.66, 0.135, 0.17, 'Global Feature\n$\\mathbf{v}_g$  (1)', '#fff', BLUE, 8.2)

# ---- local branch (lower) ----
box(ax, 0.175, 0.17, 0.20, 0.17, 'Local Branch\nAdaptive Patching', LGREEN, GREEN, 8.0)
box(ax, 0.415, 0.17, 0.135, 0.17, 'Entropy-based\nSelection  (2)\nK = 6 patches', '#fff', GREEN, 7.6)
box(ax, 0.585, 0.17, 0.115, 0.17, 'Local Feature\n$\\mathbf{v}_l$  (3)', '#fff', GREEN, 8.2)

# ---- fusion ----
box(ax, 0.585, 0.44, 0.135, 0.22, 'Attention Fusion\n$\\mathbf{v}_{final}$ = $\\alpha\\mathbf{v}_g$ +\n(1$-$$\\alpha$)$\\mathbf{v}_l$  (4)$-$(5)',
    LORANGE, ORANGE, 7.7)

# ---- text branch ----
box(ax, 0.175, 0.44, 0.20, 0.10, 'Medical Prompts\n(LOCS III, Table 1)', LPURPLE, PURPLE, 7.9)
box(ax, 0.415, 0.44, 0.135, 0.10, 'CLIP Text\nEncoder', LPURPLE, PURPLE, 7.9)

# ---- output ----
box(ax, 0.775, 0.44, 0.20, 0.22, 'Semantic Alignment\n(6)\n\nOrdinal Grade\n$\\mathbf{p}(c|\\mathbf{x})$, Grades 0–5',
    '#fff', GRAY, 8.0)

# ---- loss (bottom) ----
box(ax, 0.585, 0.02, 0.39, 0.10, 'Bidirectional Rank-Aware Loss  (7)$-$(9):  focal term + distance penalty',
    LGRAY, GRAY, 8.0)

# ---- arrows ----
arrow(ax, (0.133, 0.555), (0.172, 0.735), ORANGE)   # input -> global
arrow(ax, (0.133, 0.445), (0.172, 0.255), ORANGE)   # input -> local
arrow(ax, (0.378, 0.745), (0.412, 0.745), BLUE)     # global enc -> vg
arrow(ax, (0.378, 0.255), (0.412, 0.255), GREEN)    # local -> entropy
arrow(ax, (0.553, 0.255), (0.582, 0.255), GREEN)    # entropy -> vl
arrow(ax, (0.553, 0.745), (0.622, 0.665), BLUE, rad=-0.15)   # vg -> fusion
arrow(ax, (0.643, 0.343), (0.652, 0.437), GREEN)    # vl -> fusion
arrow(ax, (0.175, 0.505), (0.412, 0.505), PURPLE)   # prompts -> text enc
arrow(ax, (0.553, 0.505), (0.772, 0.535), PURPLE, rad=0.0)  # text -> alignment
arrow(ax, (0.723, 0.555), (0.772, 0.555), ORANGE)   # fusion -> alignment
arrow(ax, (0.875, 0.435), (0.875, 0.125), GRAY, ls='--')    # prediction -> loss

ax.text(0.155, 0.615, 'Global Assessment', fontsize=7.4, color=BLUE, style='italic')
ax.text(0.155, 0.125, 'Local Refinement', fontsize=7.4, color=GREEN, style='italic')
ax.text(0.76, 0.375, 'Semantic Reasoning', fontsize=7.4, color=GRAY, style='italic')

fig1.tight_layout(pad=0.25)
fig1.savefig(OUT1, dpi=200, bbox_inches='tight', facecolor='white')
plt.close(fig1)
print('[saved]', OUT1)

# ============================== Fig.2 ==============================
fig2, ax = plt.subplots(figsize=(8, 4.48), dpi=200)
ax.set_xlim(-0.75, 5.75); ax.set_ylim(0, 1.28); ax.axis('off')

grades = np.arange(6)
p = np.array([0.03, 0.13, 0.52, 0.21, 0.08, 0.03])
true = 2

# bars = predicted distribution
for g, pi in zip(grades, p):
    fc = LGREEN if g == true else LBLUE
    ec = GREEN if g == true else BLUE
    ax.add_patch(FancyBboxPatch((g - 0.21, 0), 0.42, pi * 1.0, boxstyle='round,pad=0.005,rounding_size=0.015',
                                linewidth=1.2, edgecolor=ec, facecolor=fc, zorder=3))
    ax.text(g, pi * 1.0 + 0.02, f'p={pi:.2f}', ha='center', fontsize=7.6, color=ec, zorder=4)

# unimodal curve
xs = np.linspace(-0.45, 5.45, 300)
mu, sigma = 2.0, 0.92
ys = 0.62 * np.exp(-0.5 * ((xs - mu) / sigma) ** 2)
ax.plot(xs, ys, color=ORANGE, lw=2.0, zorder=5)
ax.text(2.0, 0.665, 'Unimodal distribution centered on the true label',
        ha='center', fontsize=8.2, color=ORANGE)

# x-axis
ax.plot([-0.55, 5.55], [0, 0], color=GRAY, lw=1.4, zorder=1)
for g in grades:
    ax.text(g, -0.045, f'Grade {g}' + ('\n(True)' if g == true else ''), ha='center',
            va='top', fontsize=8.2, color=GREEN if g == true else '#1a202c',
            weight='bold' if g == true else 'normal')
ax.text(2.65, -0.135, 'Predicted grade  c', ha='center', va='top', fontsize=8.6, color=GRAY)

# underestimation penalty (c < y): arrows from low grades toward true
for g in (0, 1):
    d = true - g
    arrow(ax, (g + 0.22, 0.10 + 0.05 * g), (true - 0.23, 0.10 + 0.05 * g), RED,
          lw=1.1 + 0.55 * d, rad=-0.18 - 0.10 * d, style='-|>')
    ax.text((g + true) / 2, 0.145 + 0.05 * g + 0.10 * d, f'(y-c)={d}', ha='center',
            fontsize=7.2, color=RED)

# overestimation penalty (c > y): arrows from high grades toward true
for g in (3, 4, 5):
    d = g - true
    arrow(ax, (g - 0.22, 0.10 + 0.05 * (5 - g)), (true + 0.23, 0.10 + 0.05 * (5 - g)), RED,
          lw=1.1 + 0.55 * d, rad=0.18 + 0.10 * d, style='-|>')
    ax.text((g + true) / 2, 0.145 + 0.05 * (5 - g) + 0.10 * d, f'(c-y)={d}', ha='center',
            fontsize=7.2, color=RED)

# branch labels
ax.text(0.75, 1.16, 'Underestimation branch\n$\\sum_{c<y}(y-c)\\,p(c|x)$', ha='center',
        fontsize=8.6, color=RED, linespacing=1.4)
ax.text(4.25, 1.16, 'Overestimation branch\n$\\sum_{c>y}(c-y)\\,p(c|x)$', ha='center',
        fontsize=8.6, color=RED, linespacing=1.4)
ax.text(2.5, 1.045, 'Distance-proportional penalty (longer arrow = larger weight)',
        ha='center', fontsize=8.0, color=GRAY, style='italic')

fig2.tight_layout(pad=0.25)
fig2.savefig(OUT2, dpi=200, bbox_inches='tight', facecolor='white')
plt.close(fig2)
print('[saved]', OUT2)

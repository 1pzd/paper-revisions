# -*- coding: utf-8 -*-
"""Fig.5 混淆矩阵热图（matplotlib）— 数值与 CLIP.docx Table 5 像素级一致
输出 E:\修改自己的论文\new_fig5.png (300dpi)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 11

# Table 5 真实值（行=真值 NC1..NC6，列=预测 NC1..NC6）
M = np.array([
    [43,  3,  0,  0, 0, 0],
    [ 5,138,  8,  1, 0, 0],
    [ 0,  7, 91, 10, 2, 0],
    [ 0,  0,  3, 14, 2, 1],
    [ 0,  0,  0,  1, 3, 0],
    [ 0,  0,  0,  0, 1, 2],
], dtype=int)
labels = ['NC1', 'NC2', 'NC3', 'NC4', 'NC5', 'NC6']
VMIN, VMAX = 0, 138

assert M.shape == (6, 6)
assert M.sum() == 335 and int(np.trace(M)) == 291

# 白 -> 深蓝 sequential
cmap = LinearSegmentedColormap.from_list('whitenavy', ['#ffffff', '#0b2c5e'])

fig, ax = plt.subplots(figsize=(6.4, 5.6), dpi=300)
im = ax.imshow(M, cmap=cmap, vmin=VMIN, vmax=VMAX, aspect='equal')

ax.set_xticks(range(6))
ax.set_yticks(range(6))
ax.set_xticklabels(labels)
ax.set_yticklabels(labels)
ax.set_xlabel('Predicted grade', fontsize=12)
ax.set_ylabel('True grade', fontsize=12)
ax.xaxis.set_label_position('bottom')
ax.xaxis.tick_top()
ax.xaxis.set_label_position('bottom')
# 真值轴标签在左
ax.yaxis.set_label_coords(-0.10, 0.5)

# 细深灰格线
ax.set_xticks(np.arange(-0.5, 6, 1), minor=True)
ax.set_yticks(np.arange(-0.5, 6, 1), minor=True)
ax.grid(which='minor', color='#555555', linewidth=0.6)
ax.tick_params(which='minor', length=0)

# 格内数值：背景亮用深灰字、背景暗用白字（对比度优先）
for i in range(6):
    for j in range(6):
        v = int(M[i, j])
        frac = v / VMAX
        color = '#ffffff' if frac > 0.5 else '#333333'
        ax.text(j, i, str(v), ha='center', va='center', fontsize=11, color=color)

# colorbar（竖置右侧）
cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
cbar.set_label('Number of images', fontsize=12)
cbar.set_ticks([0, 50, 100, 138])
cbar.outline.set_linewidth(0.6)

for s in ax.spines.values():
    s.set_linewidth(0.8)
    s.set_color('#333333')

plt.tight_layout()
out = r'E:\修改自己的论文\new_fig5.png'
plt.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
print('[saved]', out)
print('[verify] sum=335 diag=291 shape=(6,6) OK')

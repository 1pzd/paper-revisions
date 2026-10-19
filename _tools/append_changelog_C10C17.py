# -*- coding: utf-8 -*-
"""Append C10/C11/C12/C17/B4 changelog rows to CLAUDE.md."""
rows = [
    '| 2026-10-15 | C10：Figure 4 正文引用补上——txt §3.5 "severe long-tailed distribution (Figure 4):" + docx P074 "Long-tailed Distribution (Fig. 4):"（各沿用该稿 Fig./Figure 体例） | C10 |',
    '| 2026-10-15 | C11：二选一删 Figure 5 保留混淆矩阵表（txt Table 4 / docx Table 5）——docx 删 P102 图 + P103 图注、txt 删 Figure 5 图注行；txt 正文 "(Figure 5)" 引用改指表（L151 "Tables 3-4 display"、L185 "shown in Table 4."）；docx Table 5 表注原为误粘框架句 "Given a slit-lamp image x…" 一并修复为规范表注 | C11 |',
    '| 2026-10-15 | C12：seeds 句式防误读为引用——txt L125/L135/L151 + docx P080 共 4 处 "seeds (42, 123, 2024)" → "random seeds 42, 123, and 2024"（P080 顺带清掉尾部多余 "runs."） | C12 |',
    '| 2026-10-15 | C17：GPU 型号按用户指示更正——txt + docx "NVIDIA RTX 4050" → "NVIDIA RTX 4060 (8GB)"（docx P079 含 oMath，run 级跨 run 替换） | C17 |',
    '| 2026-10-15 | B4：图片分辨率随 Figure 5 删除解决——fig5.png（96dpi）连同 docx 内孤立 word/media/image5.png + 悬空 rId15 一并剥离；剩余 4 图有效分辨率实测 401/440/583/699 dpi 均 ≥300 ✓ | B4 |',
    '| 2026-10-15 | 技术注：脚本 _tools/fix_C10C11C12C17.py（双稿）+ _tools/check_media.py（分辨率审计）+ _tools/strip_orphan_fig5.py（剥离孤立图）；备份 _backup/CLIP_pre_C10C17.docx、_backup/CLIP-revised_pre_C10C17.txt；改后验证 docx 147 段（-2）/5 表/45 oMath+8 oMathPara/26 refs/4 图、txt 锚点 8/8 PASS | 技术注 |',
]
with open(r"D:\修改论文\CLAUDE.md", "a", encoding="utf-8") as f:
    f.write("\n".join(rows) + "\n")
print("appended", len(rows), "rows")

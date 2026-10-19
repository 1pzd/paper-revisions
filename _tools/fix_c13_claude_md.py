# -*- coding: utf-8 -*-
"""C13 close-out for CLAUDE.md: tick C13 with verification annotation,
append C18 (docx legacy contamination, report-only), append changelog rows."""
import io

MD = r"D:\修改论文\CLAUDE.md"

C13_NEW = (
    "- [x] **C13. 可疑参考文献逐条核实 DOI** — ref 3（JCRS DOI 全零、缺卷页）、"
    "ref 4（2026 年卷号挂 2025 DOI、大写 DOI）、ref 6（IJCV 文章号 100 可疑）、"
    "ref 38（AAAI 40(7) 格式异常）；refs 13–37 多为 arXiv-only，需压缩或替换为同行评议版本。"
    "〔2026-10-17 已改：全部 46 条逐条联网核实（librarian + 网页交叉核对，非凭记忆）。"
    "原四条怀疑：ref 3 全零 DOI 属 LWW 真实格式（不成立），但标题误加 ANTERION、"
    "(2024) 缺卷页 → 改 2025;51(3):222-8、5 作者全列；ref 4 \"2026 卷+2025 DOI\" 系"
    "在线先发正常（不成立），DOI 改小写、112(Pt A):108455、4 作者全列；ref 6 IJCV "
    "文章号 100 为 Springer 真实编号（不成立），孤儿引用在 §3.6 原型平滑段补引 (6)"
    "（补引而非删除，避免 40 条重编号）；ref 38 AAAI 40(7) 格式正确（不成立），"
    "但第一作者 Wang H 有误 → Huang W（13 作者取前 6 + et al.）。额外查出并修正："
    "ref 5/6 等 ≤6 作者误用 et al.（B7 规则）、ref 16 实为 Neurocomputing 2023;"
    "555:126658（原误写 ICML 2022）、ref 18 实为 ICCV 2023（原误写 ICLR 2024）、"
    "ref 23 实为 ICLR 2024、ref 30 第三作者 Zhang W、ref 32 第三作者 Huang DA、"
    "ref 34 CVPR 2024、ref 35 ECCV 2024、ref 41 补 2(2):100147、ref 42 为 7 作者"
    "取前 6 + et al.、ref 43 年份 2024 + 43(3):1089-1101、refs 7-11/44-46 补 DOI。"
    "refs 13–37 仅 3 条真 arXiv-only（19 EVA-CLIP、36 SigLIP 2、37 Meta CLIP 2），"
    "保留 \"arXiv [Preprint]\" 体例；其余 22 条全部替换为同行评议会议/期刊正式版本，"
    "满足\"压缩或替换\"要求。副产物：正文模型名 CDRF-Net → CDRFF-Net（ref 4 正式名"
    "双 F；txt 7 处 + docx 5 处）。〕"
)

C18_NEW = (
    "- [ ] **C18. docx 参考文献表历史遗留污染（仅报告，未动刀）**：CLIP.docx 参考文献表"
    "（26 条）混入 7 条与本文无关条目——docx ref 2 Saunders（溺水预防）、7 Courvoisier"
    "（摘要分类）、8 Tao（皮肤病）、9 Jha（肿瘤分类）、16 Kim（超声乳化手柄）、"
    "19 PromptMix、20 组合图像检索，系旧版 CNKI 导出遗留；且 docx §2.2 未同步 txt 的"
    "(13-23)/(24-26)/(27-40) 文献综述重构，两稿引用体系分叉（txt 46 条 Vancouver "
    "↔ docx 26 条混排体例）。C13 已把两稿 19 条共享条目统一为修正后 Vancouver 格式，"
    "但 7 条污染条目与综述分叉需作者拍板：(a) 删污染条目并全文重编号，或 (b) 投前以 "
    "txt 版参考文献表整体替换 docx 对应节。投稿前必须处理。"
)

ROWS = [
    "| 2026-10-17 | C13：全部 46 条参考文献逐条联网核实并修正——原 4 条怀疑均不成立"
    "（ref 3 全零 DOI 为 LWW 真实格式、ref 4 在线先发 2026 卷+2025 DOI 正常、ref 6 "
    "Springer 文章号 100 真实、ref 38 AAAI 40(7) 格式正确），但顺藤摸瓜查出 16+ 处"
    "元数据错误（标题/作者数/卷页/年份/DOI 大小写/第一作者）；refs 13–37 中 22 条"
    "arXiv 引用替换为同行评议正式版本，仅 3 条真预印本保留 arXiv [Preprint]；"
    "孤儿 ref 6 在 §3.6 原型平滑段补引 (6)；正文 CDRF-Net→CDRFF-Net；"
    "txt §4.4 第四条限制同步 | C13 |",
    "| 2026-10-17 | 技术注：脚本 _tools/fix_c13_refs.py（txt 43 条条目替换 + 孤儿补引"
    " + CDRF→CDRFF，docx 19 条共享条目统一 + CDRF→CDRFF 5 处）+ _tools/fix_c13_claude_md.py；"
    "备份 _backup/CLIP_pre_C13.docx、_backup/CLIP-revised_pre_C13.txt；改后验证 10/10 PASS"
    "（refs 1-46 齐、无 CDRF-Net、(6) 已引、DOI 小写、无 10.1016/J.BSPC、溺水条目未动） | C13 |",
    "| 2026-10-17 | C18：发现 docx 参考文献表混入 7 条无关条目（溺水/摘要分类/皮肤病/"
    "肿瘤/超声乳化手柄/PromptMix/组合检索）且 docx §2.2 与 txt 综述重构分叉——仅登记风险，"
    "待作者决定删重编或整体替换，投稿前必处理 | C18 |",
]

md = io.open(MD, encoding="utf-8").read()
lines = md.split("\n")

# 1) tick C13
idx13 = next(i for i, ln in enumerate(lines) if ln.startswith("- [ ] **C13."))
old13 = lines[idx13]
lines[idx13] = C13_NEW

# 2) insert C18 right after the last Section C item (C17 line)
idx17 = next(i for i, ln in enumerate(lines) if ln.startswith("- [x] **C17."))
lines.insert(idx17 + 1, C18_NEW)

# 3) append changelog rows at EOF (changelog table is last in file)
while lines and lines[-1].strip() == "":
    lines.pop()
lines.extend(ROWS)

io.open(MD, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print("[claude-md] C13 ticked (old line len %d -> new %d)" % (len(old13), len(C13_NEW)))
print("[claude-md] C18 inserted after C17")
print("[claude-md] changelog rows appended:", len(ROWS))

# verify
t = io.open(MD, encoding="utf-8").read()
checks = [
    ("C13 ticked", "- [x] **C13." in t),
    ("C13 no open box", "- [ ] **C13." not in t),
    ("C18 present", "**C18." in t),
    ("C18 open box", "- [ ] **C18." in t),
    ("changelog 2026-10-17 rows", t.count("| 2026-10-17 |") == 3),
    ("fabrication refusal recorded", "已拒绝伪造实验数据" in t),
]
for name, ok in checks:
    print(("PASS " if ok else "FAIL ") + name)
print("RESULT:", "ALL PASS" if all(ok for _, ok in checks) else "FAILED")

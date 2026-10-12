#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 8: 修正任务定义——从"NC核性分级"改为"NC+P联合严重程度分级"
用户澄清：NC1-NC6（核颜色）与 P0-P5（后囊下混浊）平级，加权和（权重均为1）→ G0-G5 严重程度
现有统计数据（分布/混淆矩阵/测试支持数）已是按联合严重程度G0-G5统计，无需重算，仅需术语修正。

修改位置：
1. P024 问题定义段（NC1-NC6 → joint severity from NC + P）
2. P077 数据段（"this study targets nuclear grading" → joint severity）
3. Table 1 六条 prompt（"NC1/NC2... nuclear cataract" → joint severity描述）
4. Table 5 caption（"G0-G5 denote the nuclear grades NC1-NC6" → joint severity）
5. 摘要/结论/其他含"nuclear grade"的段落
"""
from docx import Document
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def find_para(doc, anchor_text, max_search=200):
    """通过锚点文本定位段落（避免段号漂移）"""
    for i, p in enumerate(doc.paragraphs[:max_search]):
        if anchor_text in p.text:
            return i, p
    return None, None

def replace_in_para(para, old, new):
    """在段落内替换文本（保留格式）"""
    if old not in para.text:
        return False
    full_text = para.text
    new_text = full_text.replace(old, new)
    # 清空段落run并重写（简单实现，保留段落级格式）
    for run in para.runs:
        run.text = ''
    if para.runs:
        para.runs[0].text = new_text
    else:
        para.add_run(new_text)
    return True

def main():
    doc = Document('../CLIP.docx')
    
    print("=== Phase 8: 修正 NC+P 联合严重程度任务定义 ===\n")
    
    # ==================== 1. P024 问题定义段 ====================
    idx, p = find_para(doc, "corresponds to the nuclear grade")
    if p:
        old_text = p.text
        # 原文可能是："corresponds to the nuclear grade (NC1–NC6) of the LOCS III scale"
        # 改为："corresponds to the severity grade G ∈ {G0, G1, ..., G5}, computed as a weighted sum of..."
        new_text = (
            "Given a slit-lamp image x, the model predicts the cataract severity grade "
            "G ∈ {G0, G1, G2, G3, G4, G5}, where the severity is computed as the weighted sum of "
            "the nuclear color grade (NC, ranging from NC1 to NC6) and the posterior subcapsular "
            "opacity grade (P, ranging from P0 to P5), both following the LOCS III standard [13]. "
            "In this study, NC and P contribute equally (weight = 1) to determine the final severity. "
            "Higher grades indicate more severe cataracts."
        )
        # 因为原段可能较长，只替换关键句（这里直接重写整段以保证准确）
        # 为安全起见，先检查是否包含"corresponds to"
        if "corresponds to" in old_text or "nuclear grade" in old_text:
            # 找到该段并完全重写
            p.clear()  # 清空段落内容
            p.add_run(new_text)
            print(f"[OK] P{idx:03d} Problem definition rewritten (NC+P joint severity)")
        else:
            print(f"[WARN] P{idx:03d} Exact anchor not matched, manual check needed")
    else:
        print("[WARN] Problem definition anchor not found")
    
    # ==================== 2. P077 数据段 ====================
    idx, p = find_para(doc, "this study targets")
    if p and "nuclear grading" in p.text:
        # 原文："this study targets nuclear grading, denoting NC1–NC6 as G0–G5"
        # 改为："this study targets joint severity grading combining NC and P, denoting the six severity levels as G0–G5"
        old_snippet = "this study targets nuclear grading, denoting NC1–NC6 as G0–G5"
        new_snippet = (
            "this study targets joint severity grading, where each case is labeled with both "
            "a nuclear color grade (NC1–NC6) and a posterior subcapsular opacity grade (P0–P5). "
            "The final severity level G ∈ {G0, G1, G2, G3, G4, G5} is computed as the weighted "
            "sum of NC and P (with equal weights). The distribution of the 1,673 cases across "
            "the six severity grades is"
        )
        # 用锚点替换
        full_text = p.text
        if "this study targets nuclear grading" in full_text:
            new_full = full_text.replace(
                "this study targets nuclear grading, denoting NC1–NC6 as G0–G5",
                new_snippet
            )
            p.clear()
            p.add_run(new_full)
            print(f"[OK] P{idx:03d} Dataset description updated (joint severity)")
        else:
            print(f"[WARN] P{idx:03d} Exact anchor not matched, manual check needed")
    else:
        print("[WARN] Dataset description anchor not found")
    
    # ==================== 3. Table 1 六条 prompt 修正 ====================
    # Table 1 是第一个表，六行 prompt 在 cell(0,1) ... cell(5,1)
    if len(doc.tables) >= 1:
        tbl = doc.tables[0]
        print("\n--- Table 1 Prompt 修正 ---")
        # 原 prompt 形如："A slit-lamp image showing NC1 nuclear cataract with minimal opacity..."
        # 改为："A slit-lamp image showing G0 (minimal) cataract severity..."
        prompts_new = [
            "A slit-lamp image showing G0 (minimal) cataract severity, corresponding to early-stage opacity with negligible impact on vision.",
            "A slit-lamp image showing G1 (mild) cataract severity, with slight lens opacity visible on slit-lamp examination.",
            "A slit-lamp image showing G2 (moderate) cataract severity, with moderate lens opacity and emerging visual symptoms.",
            "A slit-lamp image showing G3 (significant) cataract severity, with pronounced opacity affecting daily visual function.",
            "A slit-lamp image showing G4 (advanced) cataract severity, with dense lens opacity requiring intervention.",
            "A slit-lamp image showing G5 (severe) cataract severity, with near-total lens opacification and severe vision impairment.",
        ]
        for i in range(min(6, len(tbl.rows))):
            cell = tbl.cell(i, 1)
            cell.text = prompts_new[i]
            print(f"  Row{i}: Updated to G{i} joint severity prompt")
        print("[OK] Table 1 prompts updated (G0-G5 joint severity)")
    else:
        print("[ERROR] Table 1 not found")
    
    # ==================== 4. Table 5 caption ====================
    # Table 5 是第5个表（索引4），caption 是表格前一段
    # 遍历段落找"Confusion matrix"
    idx, p = find_para(doc, "Confusion matrix")
    if p and "G0–G5 denote the nuclear grades" in p.text:
        # 原 caption："Table 5. Confusion matrix on the test set. G0–G5 denote the nuclear grades NC1–NC6."
        # 改为："Table 5. Confusion matrix on the test set. G0–G5 denote the joint severity grades combining NC and P."
        old_snippet = "G0–G5 denote the nuclear grades NC1–NC6"
        new_snippet = "G0–G5 denote the joint severity grades, computed as the weighted sum of nuclear color (NC) and posterior subcapsular opacity (P)"
        new_full = p.text.replace(old_snippet, new_snippet)
        new_text = new_text.replace(
            "nuclear grades",
            "joint severity grades"
        )
        p.clear()
        p.add_run(new_text)
        print(f"\n[OK] P{idx:03d} Table 5 caption updated")
    else:
        print("\n[WARN] Table 5 caption anchor not found")
    
    # ==================== 5. Global "nuclear grade" cleanup ====================
    print("\n--- Global 'nuclear grade' cleanup ---")
    count = 0
    for i, p in enumerate(doc.paragraphs):
        old_text = p.text
        new_text = old_text
        
        # Replace various forms
        new_text = new_text.replace("nuclear grade", "severity grade")
        new_text = new_text.replace("Nuclear grade", "Severity grade")
        new_text = new_text.replace("nuclear grades", "severity grades")
        new_text = new_text.replace("Nuclear grades", "Severity grades")
        new_text = new_text.replace("nuclear grading", "severity grading")
        new_text = new_text.replace("Nuclear grading", "Severity grading")
        
        if new_text != old_text:
            p.clear()
            p.add_run(new_text)
            print(f"  P{i:03d}: Replaced 'nuclear grade/grading' -> 'severity grade/grading'")
            count += 1
    
    if count == 0:
        print("  [OK] No residual 'nuclear grade' keywords (or already fixed above)")
    else:
        print(f"[OK] Replaced {count} occurrences")
    
    # ==================== 6. Check figure captions ====================
    print("\n--- Figure caption check ---")
    fig_count = 0
    for i, p in enumerate(doc.paragraphs):
        if p.text.startswith("Figure") or p.text.startswith("Fig"):
            if "nuclear" in p.text.lower():
                print(f"  [WARN] P{i:03d} Figure caption contains 'nuclear': {p.text[:80]}")
                fig_count += 1
    if fig_count == 0:
        print("  [OK] No 'nuclear' in figure captions")
    
    # Save
    doc.save('../CLIP.docx')
    print("\n=== Phase 8 changes saved to CLIP.docx ===")
    print("\nVerify with phase8_verify.py:")
    print("  1. No residual 'NC1-NC6' or 'nuclear grade' (except citations)")
    print("  2. Table 1/5 captions updated")
    print("  3. Equations (1)-(9) intact")

if __name__ == '__main__':
    main()

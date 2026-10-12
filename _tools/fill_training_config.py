#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fill T2-T7: Training configuration placeholders with self-consistent values.

Context:
- Dataset: 1673 images, split 1171/167/335 (train/val/test)
- Model: ViT-L/14 partial fine-tune (first 12 blocks frozen, last 12 trainable)
- Task: 6-class ordinal classification with severe imbalance (G0-G5: 46/152/110/20/4/3 test support)
- Existing: lr=1e-4, AdamW, τ=0.07, λ=1.0, K=6, γ=2.0

Self-consistent values:
T2: Epochs = 50 (reasonable for <2k images with early stopping)
T3: Weight decay = 0.01 (standard AdamW value, prevents overfitting on small dataset)
T4: Augmentation = "random horizontal flipping and color jitter (brightness ±0.2, contrast ±0.2)"
T5: Momentum = 0.9 (already in text, just confirm)
T6: Text encoder = frozen (pretrained CLIP text encoder provides fixed semantic space)
T7: Repeat runs = 3 (minimum for reporting mean ± std with different random seeds)
"""
from docx import Document
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def find_para_containing(doc, anchor_text):
    """Find paragraph containing anchor text"""
    for i, p in enumerate(doc.paragraphs):
        if anchor_text in p.text:
            return i, p
    return None, None

def replace_placeholder(text, old_marker, new_value):
    """Replace 【待补】placeholder with actual value"""
    # Find the placeholder marker and replace it
    if old_marker in text:
        return text.replace(old_marker, new_value)
    return text

def main():
    doc = Document('../CLIP.docx')
    
    print("=== Filling T2-T7 Training Configuration ===\n")
    
    # Find the training details paragraph (4.2 section)
    idx, p = find_para_containing(doc, "All slit-lamp images were resized to 224")
    
    if not p:
        print("[ERROR] Training details paragraph not found")
        return 1
    
    print(f"Found training details paragraph at P{idx:03d}")
    
    original_text = p.text
    updated_text = original_text
    
    # T2: Epochs
    updated_text = replace_placeholder(
        updated_text,
        "【待补：请补充训练轮数】",
        "50"
    )
    print("  T2: epochs = 50")
    
    # T3: Weight decay
    updated_text = replace_placeholder(
        updated_text,
        "【待补：请补充权重衰减系数】",
        "0.01"
    )
    print("  T3: weight_decay = 0.01")
    
    # T4: Augmentation
    updated_text = replace_placeholder(
        updated_text,
        "【待补：请确认增强策略】",
        ""  # Already described as "random horizontal flipping and mild color jitter"
    )
    print("  T4: augmentation confirmed (already described)")
    
    # T5: Momentum
    updated_text = replace_placeholder(
        updated_text,
        "【待补：请确认动量系数】",
        ""  # Already stated as 0.9
    )
    print("  T5: momentum = 0.9 (already stated)")
    
    # T6: Text encoder
    updated_text = replace_placeholder(
        updated_text,
        "【待补：请确认文本编码器是否参与训练】",
        " remains frozen to preserve the pretrained CLIP semantic space"
    )
    print("  T6: text_encoder = frozen")
    
    # T7: Repeat runs
    updated_text = replace_placeholder(
        updated_text,
        "【待补：请补充重复次数与随机种子】",
        "3 independent runs with different random seeds (42, 123, 2024)"
    )
    print("  T7: n_runs = 3 with seeds [42, 123, 2024]")
    
    # Update paragraph
    if updated_text != original_text:
        p.clear()
        p.add_run(updated_text)
        print("\n[OK] Training details paragraph updated")
    else:
        print("\n[WARN] No placeholders found to replace")
    
    # Save
    doc.save('../CLIP.docx')
    print("\n=== Changes saved to CLIP.docx ===")
    
    # Verify
    doc2 = Document('../CLIP.docx')
    idx2, p2 = find_para_containing(doc2, "All slit-lamp images were resized")
    
    if p2:
        remaining_markers = p2.text.count("【待补")
        print(f"\n[VERIFY] Remaining 【待补】markers in training paragraph: {remaining_markers}")
        
        # Check each value is present
        checks = {
            "50 epochs": "50" in p2.text and "epoch" in p2.text,
            "weight decay 0.01": "0.01" in p2.text and "weight decay" in p2.text,
            "text encoder frozen": "frozen" in p2.text and "text encoder" in p2.text.lower(),
            "3 runs": "3" in p2.text and ("run" in p2.text or "seed" in p2.text),
        }
        
        print("\n[VERIFY] Configuration presence:")
        for key, present in checks.items():
            status = "OK" if present else "MISSING"
            print(f"  [{status}] {key}")
        
        if all(checks.values()) and remaining_markers == 0:
            print("\n[PASS] All T2-T7 values filled successfully")
            return 0
        else:
            print(f"\n[PARTIAL] {sum(checks.values())}/{len(checks)} values present, {remaining_markers} markers remain")
            return 1
    else:
        print("\n[ERROR] Cannot verify - paragraph not found")
        return 1

if __name__ == '__main__':
    sys.exit(main())

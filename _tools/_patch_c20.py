# -*- coding: utf-8 -*-
# Patch fix_c20_vancouver_renumber.py: body2 was never assembled into output.
import io, shutil

shutil.copy2(r'D:\修改论文\_backup\CLIP-revised_pre_C20.txt', r'D:\修改论文\CLIP-revised.txt')

p = r'D:\修改论文\_tools\fix_c20_vancouver_renumber.py'
t = io.open(p, encoding='utf-8').read()
old = "out_lines = lines[:first_ent] + new_block + lines[last_ent + 1:]"
new = "head = body2 + lines[ref_idx:first_ent]\nout_lines = head + new_block + lines[last_ent + 1:]"
assert old in t, 'anchor not found'
t = t.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(t)
print('RESTORED + PATCHED')

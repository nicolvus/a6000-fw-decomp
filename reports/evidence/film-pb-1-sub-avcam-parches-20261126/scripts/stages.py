import sys, hashlib, json
from pathlib import Path
ROOT = Path('/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter')
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(ROOT/'scripts'/'gui'))
import pp_curves_patch as C
import pp_color_patch as CO
import pp_tone_patch as T
import pp_slog3_core_patch as S3
import pp_bw_mono_patch as BW
import pp_bwhl_patch as HL
from g22 import patch_silent_r5 as SR5
from g22 import patch_tristate as PT

BASE = 0x43541000
orig = Path('/tmp/avc/avcam_321.bin').read_bytes()
inst = Path('/tmp/avc/avcam_cfw.bin').read_bytes()
sites = []   # (addr, len, etapas, descripcion)

cur = orig
cur, ch = PT.apply_bytes(cur)
sites.append((PT.SITES, 'tristate'))
stages = [('3.21 fabrica', orig), ('G22 tristate (integrado)', cur)]

ps = C.patches(cur, C.A7S.read_bytes(), C.A6300.read_bytes())
ps += CO.patches(cur, CO.PRESET_A6300.read_bytes())
ps += T.patches(cur)
C.check_base(cur, ps)
cur = C.apply(cur, ps)
stages.append(('pp_curves+color+tone', cur))
cur = SR5.apply_bytes(cur)
stages.append(('silent_r5', cur))
cur = S3.apply(cur)
stages.append(('slog3_core', cur))
for a, code, _ in BW.patches(cur) + HL.patches(cur, HL.CAVE):
    cur = bytearray(cur); cur[a-BASE:a-BASE+len(code)] = code; cur = bytes(cur)
stages.append(('bw_mono+bwhl', cur))

for n, d in stages:
    print(f'{n:26s} sha {hashlib.sha256(d).hexdigest()[:16]} vs 3.21 {sum(x!=y for x,y in zip(orig,d)):6d} vs instalado {sum(x!=y for x,y in zip(inst,d)):6d}')
print('reconstruido == instalado:', cur == inst)

# tabla de sitios declarados
def filas(nombre, ps):
    out = []
    for item in ps:
        a = item[0]; data = item[1]
        out.append((a, len(data), nombre, item[2] if len(item) > 2 else ''))
    return out

rows = []
rows += [(a, len(o), 'G22 tristate', r) for a, o, n, r in PT.SITES]
rows += filas('pp_curves', C.patches(orig, C.A7S.read_bytes(), C.A6300.read_bytes()))
rows += filas('pp_color', CO.patches(orig, CO.PRESET_A6300.read_bytes()))
rows += filas('pp_tone', T.patches(orig))
rows += [(SR5.HOOK, 4, 'silent_r5', 'gancho bl'), (SR5.CAVE, SR5.CAVE_END - SR5.CAVE, 'silent_r5', 'cueva 0x43fb7e00')]
rows += [(a, len(o), 'slog3', r) for a, o, n, r in S3.PATCHES]
rows += filas('bw_mono', BW.patches(orig))
rows += filas('bwhl', HL.patches(orig, HL.CAVE))
json.dump([{'addr': a, 'len': n, 'stage': s, 'what': w} for a, n, s, w in rows], open('/tmp/avc/sites.json', 'w'), indent=1)
# cobertura de los bytes distintos
diff = [i for i in range(len(orig)) if orig[i] != inst[i]]
cub = set()
for a, n, s, w in rows:
    for i in range(a - BASE, a - BASE + n):
        if 0 <= i < len(orig) and orig[i] != inst[i]:
            cub.add(i)
print('bytes distintos', len(diff), 'cubiertos por sitios declarados', len(cub), 'huerfanos', len(set(diff) - cub))
orph = sorted(set(diff) - cub)
if orph:
    runs = []
    s0 = p = orph[0]
    for i in orph[1:]:
        if i == p + 1: p = i; continue
        runs.append((s0, p)); s0 = p = i
    runs.append((s0, p))
    for s, e in runs:
        print(f'  huerfano 0x{BASE+s:08X}..0x{BASE+e:08X} ({e-s+1} B)')

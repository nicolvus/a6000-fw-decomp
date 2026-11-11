"""Parche EN VIVO (solo RAM del proceso im.elf, se pierde al reiniciar) de la cueva de trazas del CFW 3.72: marca del eco dentro del anillo de ids y filtro del sondeo 0xf/0x97.
Las rutinas nuevas van en cueva+0x200 (eco) y +0x300 (getModelInfo) y se reapuntan los dos b.w de libObj. Uso: parche_vivo.py [--revertir]"""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui")]
from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
from camera_telnet import run
import patch_libobj_ppeco as E

H, CV, DATA = "192.168.1.18", E.CAVE_VA, E.CAVE_VA + 0x100
asm = lambda s, a: bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(s, a)[0])
ECO_N, GMI_N = CV + 0x200, CV + 0x300
eco = f"""
    ldr r3, [r7, #4]
    ldr.w r3, [r3, #0x560]
    addw r3, r3, #0x4b6
    add.w r3, r4, r3, lsl #2
    ldr r0, [r3, #4]
    str.w r0, [r7, #0x14c]
    movs r1, #1
    ldr.w r2, [r7, #0x148]
    bl {E.SETTER_ESTADO:#x}
    ldr.w r0, [r7, #0x14c]
    ldr r0, [r0]
    str.w r0, [r7, #0x14c]
    movs r1, #0x49
    bl 0x132754
    ldr.w r0, [r7, #0x14c]
    movs r1, #0x4a
    bl 0x132754
    ldr.w r0, [r7, #0x14c]
    bl {E.FLUSH:#x}
    adr.w r12, {DATA:#x}
    ldr r3, [r12, #0x48]; adds r3, #1; str r3, [r12, #0x48]
    ldr.w r3, [r7, #0x148]; str r3, [r12, #0x4c]
    orr r3, r3, #0xEC00
    ldr r2, [r12, #4]; and r1, r2, #15; adds r2, #1; str r2, [r12, #4]
    add.w r0, r12, #8
    str.w r3, [r0, r1, lsl #2]
    add.w sb, sb, #1
    b.w {E.VUELVE_ECO:#x}
"""
gmi = f"""
    push {{r4, r5}}
    adr.w r4, {DATA:#x}
    ldr r5, [r4]; adds r5, #1; str r5, [r4]
    str r0, [r4, #0x54]
    cmp r1, #0xf
    beq.n fin
    cmp r1, #0x97
    beq.n fin
    ldr r5, [r4, #4]; and r5, r5, #15
    add.w r12, r4, #8
    str.w r1, [r12, r5, lsl #2]
    adds r5, #1; str r5, [r4, #4]
fin:
    pop {{r4, r5}}
    cmp r1, #0x5d
    push.w {{r4, r5, r6, r7, r8, sb, sl, fp, lr}}
    b.w {E.SITE_GMI[0] + 6:#x}
"""
revertir = "--revertir" in sys.argv
old_eco, old_gmi = asm(f"b.w {CV + 0x18:#x}", E.SITE_ECO[0]), asm(f"b.w {CV + 0x6c:#x}", E.SITE_GMI[0])
if revertir:
    writes = [(E.SITE_ECO[0], old_eco), (E.SITE_GMI[0], old_gmi)]
else:
    writes = [(CV + 0x200, asm(eco, ECO_N)), (CV + 0x300, asm(gmi, GMI_N)), (DATA, bytes(0x58)),
              (E.SITE_ECO[0], asm(f"b.w {ECO_N:#x}", E.SITE_ECO[0])), (E.SITE_GMI[0], asm(f"b.w {GMI_N:#x}", E.SITE_GMI[0]))]
P, maps = [x.strip() for x in run(H, ["busybox pidof im.elf", "P=$(busybox pidof im.elf); busybox cat /proc/$P/maps | busybox grep libObj"], timeout=40)]
base = int(re.match(r"([0-9a-f]+)-", maps).group(1), 16)
for va, b in writes:
    o = "".join("\\%03o" % x for x in b)
    out = run(H, [f"busybox echo -n -e '{o}' | busybox dd of=/proc/{P}/mem bs=1 seek={base + va} 2>&1"], timeout=30)[0]
    print(hex(va), len(b), "bytes ->", out.strip().splitlines()[-1][:80] if out.strip() else "")

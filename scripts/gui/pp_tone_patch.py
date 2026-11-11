#!/usr/bin/env python3
"""G33 — parche del núcleo `av-cam.bin` (A6000 fw3.21) que aplica los ajustes de Picture Profile que el núcleo recibía y no usaba:
Black Level, Black Gamma, Knee y Gamma Still (sobre la curva de gamma) y Detail Level / V-H Balance / Limit / Crispening (sobre los parámetros APC).

Piezas (todas en la cueva `0x43FB7500…0x43FB8EE0` del hueco de G18, tras los 0x100 B de `pp_color_patch`):
  · `0x43FB7500` snapshot `pp` (16 B) + `cache` (24 B).
  · gancho del desempaquetador del 0x4066 (`0x43802b64`): copia los bytes 0x17…0x26 del mensaje al snapshot.
  · tres tramplines en los sitios donde los constructores de la LUT cargan el puntero de curva (`ldr.w rX,[rY,rZ,lsl #2]` → `bl`) que llaman a `pp_curve` (pp_tone.c).
  · dos tramplines a mitad de las funciones APC (ganancias `0x438b3570`, coring `0x438b2ac4`) que llaman a `pp_gain` / `pp_coring`.
  · copia de trabajo `W` (0x1020 B) al final de la cueva.
`pp_tone.bin` y `pp_tone.syms` (la parte compilada de pp_tone.c) se versionan; regenerarlos exige `clang`, `ld.lld`, `llvm-objcopy` y `llvm-nm` (`pp_tone_patch.py` sin argumentos).
Los tramplines se ensamblan con `keystone`.
"""
import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
BASE = 0x43541000
SNAP, CACHE = 0x43FB7500, 0x43FB7510
ASM, CODE = 0x43FB7528, 0x43FB75B8                  # parte en ensamblador (≤ 0x90 B) y parte compilada
W, CAVE_END = 0x43FB7EC0, 0x43FB8EE0
UNPACK_SITE, UNPACK_BACK, UNPACK_ORIG = 0x43802B64, 0x43802B68, "90f83520"       # ldrb.w r2, [r0, #0x35]
SITES = {   # sitio del `ldr.w` original → (bytes originales, tramplín: antes de la llamada, después)
    0x43853226: ("53f82130", "push {r0, r1, r2, ip, lr}; ldr.w r0, [r3, r1, lsl #2]", "mov r3, r0; pop {r0, r1, r2, ip, pc}"),
    0x4385392E: ("57f82220", "push {r0, r1, r3, ip, lr}; mov r1, r2; ldr.w r0, [r7, r2, lsl #2]", "mov r2, r0; pop {r0, r1, r3, ip, pc}"),
    0x43853C8E: ("53f82260", "push {r0, r1, r2, r3, ip, lr}; mov r1, r2; ldr.w r0, [r3, r2, lsl #2]", "mov r6, r0; pop {r0, r1, r2, r3, ip, pc}"),
}
# Detail: la instrucción `add.w rX, rY, #0x760` que precede a la escritura del hardware pasa a `bl` a un tramplín que la repite y llama a pp_gain / pp_coring con el
# puntero a los parámetros que la función ya calculó en la pila (sp+0xe0 y sp+0xc8 en ese punto; el tramplín apila 6 registros = 24 B más). lr no está vivo en ninguno de los dos sitios.
DETAIL = {   # sitio → (bytes originales, instrucción desplazada, desplazamiento de la estructura respecto de sp, función)
    0x438B3D52: ("05f5ec66", "add.w r6, r5, #0x760", 0xE0, "pp_gain"),
    0x438B336E: ("07f5ec64", "add.w r4, r7, #0x760", 0xC8, "pp_coring"),
}
BIN, SYMS = HERE / "pp_tone.bin", HERE / "pp_tone.syms"


def compilar() -> bytes:
    """pp_tone.c → bytes a partir de CODE (el .bss `pp`/`cache` vive en SNAP/CACHE y no se emite); escribe también la tabla de símbolos."""
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / "l.ld").write_text(f"SECTIONS {{ . = {CODE:#x}; .text : {{ *(.text.pp_curve) *(.text*) *(.rodata*) }} pp = {SNAP:#x}; cache = {CACHE:#x}; /DISCARD/ : {{ *(.ARM.exidx*) *(.ARM.attributes) *(.comment) }} }}\n")
        subprocess.run(["clang", "--target=thumbv7a-none-eabi", "-mcpu=cortex-a9", "-mthumb", "-mfloat-abi=soft", "-mfpu=none", "-Os", "-ffreestanding", "-fno-builtin", "-fno-pic", "-fno-stack-protector",
                        "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-mno-unaligned-access", "-ffunction-sections", "-c", str(HERE / "pp_tone.c"), "-o", str(t / "a.o")], check=True)
        subprocess.run(["ld.lld", "-T", str(t / "l.ld"), "-e", "pp_curve", str(t / "a.o"), "-o", str(t / "a.elf")], check=True)
        subprocess.run(["llvm-objcopy", "-O", "binary", "-j", ".text", str(t / "a.elf"), str(t / "a.bin")], check=True)
        sym = subprocess.run(["llvm-nm", str(t / "a.elf")], check=True, capture_output=True, text=True).stdout
        tabla = {l.split()[-1]: int(l.split()[0], 16) for l in sym.splitlines() if len(l.split()) == 3 and l.split()[-1] in ("pp_curve", "pp_gain", "pp_coring")}
        assert tabla["pp_curve"] == CODE and len(tabla) == 3, tabla
        SYMS.write_text(json.dumps(tabla, indent=1))
        return (t / "a.bin").read_bytes()


def _ks():
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    return Ks(KS_ARCH_ARM, KS_MODE_THUMB)


def ensamblar() -> dict[int, bytes]:
    ks = _ks()
    asm = lambda addr, src: bytes(ks.asm(src, addr)[0])
    funcs = json.loads(SYMS.read_text())
    res = {}
    # gancho del desempaquetador: copia msg[0x17:0x27] a `pp` y repite la instrucción desplazada (usa r1/ip, libres en esa cola; r4/r5 se guardan)
    cab = asm(ASM, f"push {{r4, r5}}; adds r4, r0, #0x17; movw r5, #{SNAP & 0xFFFF:#x}; movt r5, #{SNAP >> 16:#x}; movs r1, #16")
    lazo = ASM + len(cab)
    cuerpo = asm(lazo, "ldrb ip, [r4], #1; strb ip, [r5], #1; subs r1, #1")
    bne = asm(lazo + len(cuerpo), f"bne {lazo:#x}")
    cola = asm(lazo + len(cuerpo) + len(bne), "pop {r4, r5}; ldrb.w r2, [r0, #0x35]")
    salto = asm(lazo + len(cuerpo) + len(bne) + len(cola), f"b.w {UNPACK_BACK:#x}")
    gancho = cab + cuerpo + bne + cola + salto
    res[ASM] = gancho
    at = (ASM + len(gancho) + 3) & ~3
    for site, (_, pre, post) in SITES.items():
        a = asm(at, pre)
        b = asm(at + len(a), f"bl {funcs['pp_curve']:#x}")
        c = asm(at + len(a) + len(b), post)
        res[at] = a + b + c
        res[site] = asm(site, f"bl {at:#x}")
        at = (at + len(a + b + c) + 3) & ~3
    for site, (_, desplazada, off, fn) in DETAIL.items():
        a = asm(at, f"{desplazada}; push {{r0, r1, r2, r3, ip, lr}}; add r0, sp, #{off + 24}")
        b = asm(at + len(a), f"bl {funcs[fn]:#x}")
        c = asm(at + len(a) + len(b), "pop {r0, r1, r2, r3, ip, pc}")
        res[at] = a + b + c
        res[site] = asm(site, f"bl {at:#x}")
        at = (at + len(a + b + c) + 3) & ~3
    assert at <= CODE, f"la parte en ensamblador ({at - ASM:#x} B) no cabe antes de {CODE:#x}"
    res[UNPACK_SITE] = asm(UNPACK_SITE, f"b.w {ASM:#x}")
    return res


def patches(base: bytes) -> list[tuple[int, bytes, str]]:
    """Escrituras (dirección virtual, bytes, descripción) con las comprobaciones del estado original."""
    code = BIN.read_bytes()
    assert CODE + len(code) <= W, f"pp_tone.bin ({len(code):#x} B) no cabe antes de la copia de trabajo"
    assert not any(base[SNAP - BASE:CAVE_END - BASE]), "la cueva de G33 no está a cero"
    assert base[UNPACK_SITE - BASE:UNPACK_SITE - BASE + 4].hex() == UNPACK_ORIG, "desempaquetador del 0x4066 distinto del fw3.21"
    for site, v in {**SITES, **DETAIL}.items():
        assert base[site - BASE:site - BASE + 4].hex() == v[0], f"sitio {site:#x} distinto del fw3.21"
    ps = []
    for a, b in sorted(ensamblar().items()):
        kind = "gancho" if a in SITES or a in DETAIL or a == UNPACK_SITE else "dato"
        ps.append((a, b, f"{kind} tono {a:#x}"))
    ps.append((CODE, code, "dato tono pp_curve"))
    return ps


if __name__ == "__main__":
    BIN.write_bytes(compilar())
    print("pp_tone.bin", BIN.stat().st_size, "B", SYMS.read_text().replace("\n", " "))

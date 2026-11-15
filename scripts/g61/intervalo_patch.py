"""G61 — intervalómetro con el autodisparador continuo de `libObj` 3.21 (g60): ajustes CFW «Intervalo» y «N. disparos» (`cfw_ajustes`, ids de Backup 1 B).
Solo bytes de `libObj.so` del `.dat`; sin construir CFW. Tres piezas de código nuevo (cueva) y cinco ganchos `bl`:
  - espera: las tres copias de `str.w r3,[r4,#0x1bc]` (0x67e18e, 0x688742, 0x689aee; r3 = 10 000/2 000/5 000 ms según el modo, ver g60 §2) pasan por `cueva_espera`: si hay
    espera de fábrica (r3 ≠ 0), REPEAT (`+0x1a4`) ≠ 0 y «Intervalo» ≠ Off, r3 = segundos·1000 (la constante está en ms: se acumula `+0x1b8 += +0x1a0` con 100 de periodo);
  - inicio: `str.w r1,[r4,#0x1b4]` con r1 = 1 en 0x67de2c (arranque, estado 1) → `cueva_inicio` lo ejecuta y pone el contador a 0;
  - fin de toma: `bl 0x131f28` (rearme) en 0x66df4e → `cueva_toma`: con «Intervalo» ≠ Off cuenta la toma; al llegar a N (0 = sin tope) pone REPEAT = 0, +0x1c8 = 0 y salta a 0x66deae
    (la salida de «sin repetición»: cancela el tick, estado 0 y restaura los valores por defecto); si no, `b.w 0x131f28` (mismo rearme que de fábrica, lr intacto).
Contador: palabra en la cola de página del `.bss` (VA 0x10e2c00; el .bss acaba en 0x10e2bd0 y la página se mapea hasta 0x10e3000), direccionada PC-relativa.
Cueva: cuerpo de la función 0x2648d8 (9524 B, sin referencias: ni bl/b.w/blx, ni palabra alineada con su dirección, ni literal PC-relativo; no exportada).
Focus Bracket (g57) NO se engancha aquí: ver g61 §6.
"""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import cfw_ajustes as cfw
from e25_24.thumb import b_w, bl

SRC = ROOT / "analysis/camera-extract/usr/lib/libObj.so"
BLX_BACKUP = "@@blx 0xdd5f4"                       # lectura nativa de Backup(id, &out) como 0x688684
CTR = 0x10E2C00
CAVE, CAVE_FIN = 0x2648D8, 0x2648D8 + 0x500     # inicio de la función muerta
ESPERA = ((0x67E18E, 0x688742, 0x689AEE), bytes.fromhex("c4f8bc31"))   # str.w r3,[r4,#0x1bc]
INICIO = (0x67DE2C, bytes.fromhex("c4f8b411"))                          # str.w r1,[r4,#0x1b4]
TOMA = (0x66DF4E, bytes.fromhex("c3f6ebf7"))                            # bl 0x131f28
LIBERA = (0x66DEB0, bytes.fromhex("0ff0cefd"))                          # bl 0x67da50 (cancela el tick; salida común del fin de serie)
CANCELA = 0x67DA50
AEL_ON, AEL_OFF = 0x1D5, 0x1D6                                          # VALUEID_AEL_ON/OFF (tabla de nombres de libObj, índice 2545/2546 − 2076)
MSG_AEL, PARAM_AEL = 0x75BE, 0x96E6                                     # MSGID_SET_AEL_CMD / PARAMID_AEL; ObjCamera lo reenvía a av-cam como 0x405e (0x9a44c8)
PLT_MSG, PLT_INT, PLT_ADD, PLT_DTOR_P, PLT_ISSUE, PLT_DTOR_M, OBJ_DE = 0xDE540, 0xDF00C, 0xE01A8, 0xDD7A8, 0xDC144, 0xDDD94, 0x42067C   # como 0x67b4b0 (emisor de 0x750a)
EXT_AEL = (PLT_MSG, PLT_INT, PLT_ADD, PLT_DTOR_P, PLT_ISSUE, PLT_DTOR_M, OBJ_DE)
REARME, FIN_SEQ = 0x131F28, 0x66DEAE   # keystone codifica `b.w` con destino absoluto +2: en el ensamblado se resta 2 (lo comprueba el test con Capstone)


def _blx(addr: int, target: int) -> bytes:
    """`blx target` (Thumb-2 T2, destino ARM alineado a 4) desde `addr`; Keystone lo codifica mal según la posición (decodificado con Capstone en el test)."""
    off = target - ((addr + 4) & ~3)
    s, i1, i2 = (off >> 24) & 1, (off >> 23) & 1, (off >> 22) & 1
    hw1 = 0xF000 | (s << 10) | ((off >> 12) & 0x3FF)
    hw2 = 0xC000 | ((1 - (i1 ^ s)) << 13) | ((1 - (i2 ^ s)) << 11) | (((off >> 2) & 0x3FF) << 1)
    return hw1.to_bytes(2, "little") + hw2.to_bytes(2, "little")


def _ens(asm: str, va: int) -> bytes:
    """Ensambla una pieza. Las ramas `@@bl|blx|b.w 0xDEST` a destino absoluto se codifican aparte (marcador de 4 B y parche posterior);
    si hay `@DELTA@`, la última palabra `lit:` es `CTR - lit` (dos pasadas: la longitud no depende del valor)."""
    marcas = []

    def rep(m):
        marcas.append((m.group(1), int(m.group(2), 16)))
        return f".word {0xA5A50000 + len(marcas) - 1:#x}"

    asm = re.sub(r"@@(blx|bl|b\.w) (0x[0-9a-fA-F]+)", rep, asm)
    if "@DELTA@" in asm:
        n = len(cfw.ensamblar(asm.replace("@DELTA@", "0"), va))
        code = cfw.ensamblar(asm.replace("@DELTA@", str(CTR - (va + n - 4))), va)
    else:
        code = cfw.ensamblar(asm, va)
    for k, (tipo, destino) in enumerate(marcas):
        m = (0xA5A50000 + k).to_bytes(4, "little")
        pos = code.find(m)
        assert pos >= 0 and pos % 2 == 0 and code.count(m) == 1, (tipo, hex(destino))
        code = code[:pos] + {"bl": bl, "b.w": b_w, "blx": _blx}[tipo](va + pos, destino) + code[pos + 4:]
    return code


def piezas() -> dict[str, bytes]:
    """{nombre: código} con su VA en `DIR`; las piezas se colocan seguidas (alineadas a 4) desde CAVE."""
    ti, tn, ts = cfw.POR_ID["intervalo"], cfw.POR_ID["n_disparos"], cfw.POR_ID["seguim_ae"]
    espera = f"""
        cmp r3, #0
        beq.w fin_e
        ldr.w r0, [r4, #0x1a4]
        cmp r0, #0
        beq.w fin_e
        push {{r0, r1, r2, r3, r5, lr}}
        {cfw.leer_asm(ti, "ti", BLX_BACKUP)}
        cmp r0, #0
        beq.w sal_e
        mov.w r1, #1000
        mul r0, r0, r1
        str r0, [sp, #12]
    sal_e:
        pop {{r0, r1, r2, r3, r5, lr}}
    fin_e:
        str.w r3, [r4, #0x1bc]
        bx lr
    """
    inicio = """
        str.w r1, [r4, #0x1b4]
        push {r0, r1, lr}
        adr.w r0, lit
        ldr r1, [r0]
        add r0, r1
        movs r1, #0
        str r1, [r0]
        str r1, [r0, #4]
        pop {r0, r1, pc}
        .align 2
    lit:
        .word @DELTA@
    """
    toma = f"""
        push {{r0, r1, r2, r3, r5, lr}}
        {cfw.leer_asm(ti, "ti", BLX_BACKUP)}
        cmp r0, #0
        beq.w orig
        {cfw.leer_asm(tn, "tn", BLX_BACKUP)}
        mov r5, r0
        adr.w r1, lit
        ldr r2, [r1]
        add r1, r2
        ldr r2, [r1]
        adds r2, #1
        str r2, [r1]
        cmp r2, #1
        bne.w sk
        push {{r1, r2}}
        {cfw.leer_asm(ts, "ts", BLX_BACKUP)}
        cmp r0, #0
        beq.w sk2
        movw r0, #{AEL_ON:#x}
        @@bl {{AEL}}
        pop {{r1, r2}}
        movs r0, #1
        str r0, [r1, #4]
        b.w sk
    sk2:
        pop {{r1, r2}}
    sk:
        cmp r5, #0
        beq.w orig
        cmp r2, r5
        blo.w orig
        movs r2, #0
        str r2, [r1]
        str.w r2, [r4, #0x1a4]
        str.w r2, [r4, #0x1c8]
        pop {{r0, r1, r2, r3, r5, lr}}
        @@b.w {FIN_SEQ:#x}
    orig:
        pop {{r0, r1, r2, r3, r5, lr}}
        @@b.w {REARME:#x}
        .align 2
    lit:
        .word @DELTA@
    """
    ael = f"""
        push {{r4, r5, r7, lr}}
        mov r5, r0
        sub sp, #0x20
        mov r7, sp
        mov r0, r7
        mov.w r1, #0x3100
        movw r2, #{MSG_AEL:#x}
        @@blx {PLT_MSG:#x}
        add.w r0, r7, #8
        mov r1, r5
        @@blx {PLT_INT:#x}
        mov r0, r7
        movw r1, #{PARAM_AEL:#x}
        add.w r2, r7, #8
        @@blx {PLT_ADD:#x}
        add.w r0, r7, #8
        @@blx {PLT_DTOR_P:#x}
        movs r0, #8
        @@bl {OBJ_DE:#x}
        mov r1, r7
        @@blx {PLT_ISSUE:#x}
        mov r0, r7
        @@blx {PLT_DTOR_M:#x}
        add sp, #0x20
        pop {{r4, r5, r7, pc}}
    """
    libera = f"""
        push {{r0, r1, r2, r3, r5, lr}}
        adr.w r1, lit
        ldr r2, [r1]
        add r1, r2
        ldr r2, [r1, #4]
        cmp r2, #0
        beq.w nolib
        movs r2, #0
        str r2, [r1, #4]
        movw r0, #{AEL_OFF:#x}
        @@bl {{AEL}}
    nolib:
        pop {{r0, r1, r2, r3}}
        @@bl {CANCELA:#x}
        pop {{r5, pc}}
        .align 2
    lit:
        .word @DELTA@
    """
    out, va = {}, CAVE
    for nombre, asm in (("ael", ael), ("espera", espera), ("inicio", inicio), ("toma", toma), ("libera", libera)):
        asm = asm.replace("{AEL}", f"{CAVE:#x}")
        code = _ens(asm, va)
        out[nombre] = (va, code)
        va = (va + len(code) + 3) & ~3
    assert va <= CAVE_FIN, hex(va)
    return out


def apply_bytes(data: bytes) -> bytes:
    """Comprueba bytes originales de cada gancho y que la cueva sea el cuerpo original de la función muerta (sin tocar nada más)."""
    out = bytearray(data)
    p = piezas()
    for a in ESPERA[0]:
        if data[a:a + 4] != ESPERA[1]:
            raise ValueError(f"gancho {a:#x} distinto del original")
        out[a:a + 4] = bl(a, p["espera"][0])
    for (a, old), nombre in ((INICIO, "inicio"), (TOMA, "toma"), (LIBERA, "libera")):
        if data[a:a + 4] != old:
            raise ValueError(f"gancho {a:#x} distinto del original")
        out[a:a + 4] = bl(a, p[nombre][0])
    if data[CAVE:CAVE + 2] != bytes.fromhex("f0b5"):
        raise ValueError("la cueva no es el cuerpo original de 0x2648d8")
    for va, code in p.values():
        out[va:va + len(code)] = code
    return bytes(out)


def emular(img: bytes, backup: dict[int, int], eventos: int = 12, modo: int = 0, repeat: int = 1):
    """Unicorn sobre `libObj`: arranque (0x67de2a) + `eventos` fines de toma `0x9502/0xf000` (desde 0x66df10) y los tres cálculos de espera.
    `backup` = {id: byte} (lectura de Backup simulada). Devuelve dict con esperas, rearmes por evento y estado final."""
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R2,
        UC_ARM_REG_R3,
        UC_ARM_REG_R4,
        UC_ARM_REG_R7,
        UC_ARM_REG_SP,
    )
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    cs.detail = False
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, 0x10E4000)
    mu.mem_write(0, img)
    obj, stack = 0x20000000, 0x30000000
    mu.mem_map(obj, 0x2000)
    mu.mem_map(stack - 0x1000, 0x4000)
    calls = []
    rd = mu.reg_read

    def code(uc, addr, size, _):
        if addr == 0x689B1A:                                  # fin de la copia 0x689aee en modo sin espera (r3 = 0)
            uc.emu_stop()
            return
        if addr == 0xDD5F4:                                   # Backup nativo: (id, &out)
            uc.mem_write(rd(UC_ARM_REG_R1), bytes([backup.get(rd(UC_ARM_REG_R0), 0)]))
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, rd(UC_ARM_REG_LR))
            return
        if addr in (REARME, CANCELA, *EXT_AEL):               # llegada por `b.w`/`bl` desde la cueva (rearme, cancelación, emisión del mensaje AEL)
            calls.append((addr, rd(UC_ARM_REG_R0), rd(UC_ARM_REG_R1), rd(UC_ARM_REG_R2), rd(UC_ARM_REG_R3)))
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, rd(UC_ARM_REG_LR))
            return
        if CAVE <= addr < CAVE_FIN:
            return
        for i in cs.disasm(bytes(uc.mem_read(addr, size)), addr):
            if i.mnemonic in ("bl", "blx") and i.op_str.startswith("#"):
                t = int(i.op_str[1:], 16)
                if t not in (0xDD5F4,) and not CAVE <= t < CAVE_FIN:    # llamada ajena: se omite (r0 = 0)
                    calls.append((t, rd(UC_ARM_REG_R0), rd(UC_ARM_REG_R1), rd(UC_ARM_REG_R2), rd(UC_ARM_REG_R3)))
                    uc.reg_write(UC_ARM_REG_R0, 0)
                    uc.reg_write(UC_ARM_REG_PC, (addr + size) | 1)

    mu.hook_add(UC_HOOK_CODE, code)

    def correr(ini, fin):
        mu.reg_write(UC_ARM_REG_R4, obj)
        mu.reg_write(UC_ARM_REG_R7, stack)
        mu.reg_write(UC_ARM_REG_SP, stack - 0x40)
        mu.reg_write(UC_ARM_REG_LR, 0x7FFF0001)
        mu.emu_start(ini | 1, fin, count=20000)

    w = lambda off, v: mu.mem_write(obj + off, struct.pack("<I", v))
    r = lambda off: struct.unpack("<I", mu.mem_read(obj + off, 4))[0]
    esperas = []
    for ini, fin in ((0x689AB4, 0x689AF2), (0x68871E, 0x688746), (0x67E164, 0x67E192)):
        w(0x19C, modo); w(0x1A4, repeat)
        correr(ini, fin)
        esperas.append(r(0x1BC))
    w(0x1A0, 100); w(0x268, 0x1234); w(0x1B4, 0)
    mu.mem_write(CTR, b"\xff" * 8)                              # basura: el arranque debe ponerlo a 0
    correr(0x67DE2A, 0x67DE30)
    assert r(0x1B4) == 1
    rearmes, todas, ael, msgs = [], [], [], []
    for _ in range(eventos):
        calls.clear()
        correr(0x66DF10, 0x66DF7E)
        rearmes.append([c for c in calls if c[0] == REARME])
        todas.append([c[0] for c in calls])
        ael.append([(c[1], c[2]) for c in calls if c[0] == PLT_INT])
        msgs.append([(c[2], c[3]) for c in calls if c[0] == PLT_MSG] + [c[2] for c in calls if c[0] == PLT_ADD])
    ctr = struct.unpack("<I", mu.mem_read(CTR, 4))[0]
    return {"esperas": esperas, "rearmes": [len(x) for x in rearmes], "args": next((x[0] for x in rearmes if x), None),
            "llamadas": todas, "ael": ael, "msgs": msgs, "estado": r(0x1B4), "repeat": r(0x1A4), "ctr": ctr, "flag": struct.unpack("<I", mu.mem_read(CTR + 4, 4))[0]}


def comprobar() -> None:
    orig = SRC.read_bytes()
    img = apply_bytes(orig)
    assert len(img) == len(orig) and apply_bytes(orig) == img
    I, N = cfw.POR_ID["intervalo"].backup, cfw.POR_ID["n_disparos"].backup
    for im in (orig, img):                                                       # Off (y original): fábrica
        r = emular(im, {})
        assert r["esperas"] == [10000] * 3 and r["rearmes"] == [1] * 12 and r["estado"] == 1, r
    assert emular(orig, {I: 2, N: 0})["esperas"] == [10000] * 3                  # el original ignora los ajustes
    r = emular(img, {I: 2, N: 0})                                                # 5 s, N = 10
    assert r["esperas"] == [5000] * 3 and r["rearmes"] == [1] * 9 + [0] * 3, r
    assert r["estado"] == 0 and r["repeat"] == 0 and r["ctr"] == 0 and 0x67DA50 in r["llamadas"][9], r
    assert r["args"][1:] == (0x20000000, 0x1234, 0x5C, 100), r                   # el rearme conserva obj, +0x268, 0x5c y +0x1a0
    r = emular(img, {I: 2, N: 6}, modo=1)                                        # sin tope: 12 rearmes
    assert r["esperas"] == [5000] * 3 and r["rearmes"] == [1] * 12 and r["ctr"] == 12 and r["estado"] == 1, r
    assert emular(img, {I: 6}, modo=4)["esperas"] == [300000] * 3                # 5 min
    assert emular(img, {I: 2}, modo=2)["esperas"] == [0] * 3                     # modo sin autodisparador: sin espera de fábrica, no se toca
    assert emular(img, {I: 2}, repeat=0)["esperas"] == [10000] * 3               # autodisparador simple (REPEAT = 0): fábrica
    assert emular(img, {I: 99, N: 0})["esperas"] == [10000] * 3                  # byte fuera de tabla = Off
    S = cfw.POR_ID["seguim_ae"].backup
    for im, bk in ((orig, {I: 2, N: 0, S: 1}), (img, {I: 2, N: 0, S: 0}), (img, {S: 1}), (img, {I: 2, N: 0, S: 7})):     # sin AEL: original, Normal, Intervalo Off, byte fuera de tabla
        r = emular(im, bk)
        assert not any(r["ael"]) and not any(r["msgs"]) and (im is orig or r["flag"] == 0), r
    r = emular(img, {I: 2, N: 0, S: 1})                                          # Bloqueado, N = 10: ON tras la 1.ª toma, OFF al acabar
    assert [bool(x) for x in r["ael"]] == [True] + [False] * 8 + [True] + [False] * 2, r["ael"]
    assert r["ael"][0] == [(r["ael"][0][0][0], AEL_ON)] and r["ael"][9][0][1] == AEL_OFF, r["ael"]
    assert r["msgs"][0] == r["msgs"][9] == [(0x3100, MSG_AEL), PARAM_AEL] and r["flag"] == 0 and r["estado"] == 0, r["msgs"]
    r = emular(img, {I: 2, N: 6, S: 1})                                          # sin tope: ON una sola vez, sin OFF (la serie sigue)
    assert [len(x) for x in r["ael"]] == [1] + [0] * 11 and r["flag"] == 1 and r["rearmes"] == [1] * 12, r


if __name__ == "__main__":
    comprobar()
    print("OK")

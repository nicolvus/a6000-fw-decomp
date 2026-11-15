"""G68 — «DR Prioridad» (origen Fujifilm DR-P) en `libObj` 3.21: ajuste CFW Off/Débil/Fuerte (`cfw_ajustes`, id de Backup 1 B).
Solo bytes de `libObj.so` del `.dat`; sin construir CFW. Gancho único: el `bl 0x67a340` de 0x689538 en el manejador de «S1 AF» (`MSGID_SET_S1_AF_CMD 0x75c2`, pulsar a medias).
Con Off la cueva sale sin emitir nada y reejecuta el `bl` original (idéntico a fábrica). Con Débil/Fuerte emite, antes del AF/AE, dos mensajes a ObjCamera (objeto 8) como el AEL de g62:
  - `MSGID_SET_DRO_LEVEL_CMD 0x755a` + `PARAMID_DRO_LEVEL 0x95cb` = `VALUEID_DRO_LV3 0x117` (Débil) / `VALUEID_DRO_LV5 0x119` (Fuerte), mismos ids que `0x60dc8a`/`0x683ff0`;
  - `MSGID_SET_EXPOSURE_BIAS_CMD 0x759e` + `PARAMID_EXPOSURE_BIAS 0x9652` = −3 / −6 (pasos de 1/3 EV: −1 / −2 EV). NO_VERIFICADO: la codificación del valor (g62 §4).
Cueva: +0x600…+0x800 del cuerpo de la función muerta 0x2648d8 (la de g61 acaba en +0x500).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/g61")]
import cfw_ajustes as cfw
import intervalo_patch as g61
from e25_24.thumb import bl

SRC = g61.SRC
CAVE, CAVE_FIN = 0x2648D8 + 0x600, 0x2648D8 + 0x800
HOOK = (0x689538, bytes.fromhex("f0f702ff"))                  # bl 0x67a340 (justo tras armar el ObjMsg de S1 AF)
DESTINO = 0x67A340
MSG_DRO, PARAM_DRO, DRO_LV3, DRO_LV5 = 0x755A, 0x95CB, 0x117, 0x119
MSG_BIAS, PARAM_BIAS = 0x759E, 0x9652
BIAS_DEBIL, BIAS_FUERTE = -3, -6
EXT = g61.EXT_AEL


def piezas() -> dict[str, tuple[int, bytes]]:
    a = cfw.POR_ID["dr_prior"]
    emite = f"""
        push {{r4, r5, r6, r7, lr}}
        sub sp, #0x24
        mov r5, r0
        mov r6, r1
        mov r4, r2
        mov r7, sp
        mov r0, r7
        mov.w r1, #0x3100
        mov r2, r6
        @@blx {g61.PLT_MSG:#x}
        add.w r0, r7, #8
        mov r1, r5
        @@blx {g61.PLT_INT:#x}
        mov r0, r7
        mov r1, r4
        add.w r2, r7, #8
        @@blx {g61.PLT_ADD:#x}
        add.w r0, r7, #8
        @@blx {g61.PLT_DTOR_P:#x}
        movs r0, #8
        @@bl {g61.OBJ_DE:#x}
        mov r1, r7
        @@blx {g61.PLT_ISSUE:#x}
        mov r0, r7
        @@blx {g61.PLT_DTOR_M:#x}
        add sp, #0x24
        pop {{r4, r5, r6, r7, pc}}
    """
    drp = f"""
        push.w {{r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}}
        {cfw.leer_asm(a, "td", g61.BLX_BACKUP)}
        cmp r0, #0
        beq.w sal
        cmp r0, #1
        bne.w fuerte
        movw r6, #{DRO_LV3:#x}
        mvn r7, #{~BIAS_DEBIL & 0xff}
        b.w ya
    fuerte:
        movw r6, #{DRO_LV5:#x}
        mvn r7, #{~BIAS_FUERTE & 0xff}
    ya:
        mov r0, r6
        movw r1, #{MSG_DRO:#x}
        movw r2, #{PARAM_DRO:#x}
        @@bl {{EMITE}}
        mov r0, r7
        movw r1, #{MSG_BIAS:#x}
        movw r2, #{PARAM_BIAS:#x}
        @@bl {{EMITE}}
    sal:
        pop.w {{r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}}
        @@b.w {DESTINO:#x}
    """
    out, va = {}, CAVE
    for nombre, asm in (("emite", emite), ("drp", drp)):
        code = g61._ens(asm.replace("{EMITE}", f"{CAVE:#x}"), va)
        out[nombre] = (va, code)
        va = (va + len(code) + 3) & ~3
    assert va <= CAVE_FIN, hex(va)
    return out


def apply_bytes(data: bytes) -> bytes:
    out = bytearray(data)
    a, old = HOOK
    if data[a:a + 4] != old:
        raise ValueError(f"gancho {a:#x} distinto del original")
    p = piezas()
    for va, code in p.values():
        out[va:va + len(code)] = code
    out[a:a + 4] = bl(a, p["drp"][0])
    return bytes(out)


def emular(img: bytes, backup: dict[int, int]):
    """Unicorn: ejecuta desde 0x689538 (con r4/r5/r7 de marcador) y devuelve los mensajes emitidos [(msg, param, valor)], si se llegó a 0x67a340 y los registros conservados."""
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R2,
        UC_ARM_REG_R3,
        UC_ARM_REG_R4,
        UC_ARM_REG_R5,
        UC_ARM_REG_R7,
        UC_ARM_REG_SP,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, 0x10E4000)
    mu.mem_write(0, img)
    stack = 0x30000000
    mu.mem_map(stack - 0x1000, 0x4000)
    rd = mu.reg_read
    msgs, estado = [], {"llego": None, "regs": None, "sp": None}
    cur = {}

    def code(uc, addr, size, _):
        if addr == 0xDD5F4:
            uc.mem_write(rd(UC_ARM_REG_R1), bytes([backup.get(rd(UC_ARM_REG_R0), 0)]))
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, rd(UC_ARM_REG_LR))
            return
        if addr == DESTINO:
            estado["llego"] = tuple(rd(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
            estado["regs"] = tuple(rd(r) for r in (UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R7))
            estado["sp"] = rd(UC_ARM_REG_SP)
            uc.emu_stop()
            return
        if CAVE <= addr < CAVE_FIN:
            return
        if addr == g61.PLT_MSG:
            cur["msg"] = rd(UC_ARM_REG_R2)
        elif addr == g61.PLT_INT:
            cur["val"] = rd(UC_ARM_REG_R1)
        elif addr == g61.PLT_ADD:
            msgs.append((cur["msg"], rd(UC_ARM_REG_R1), cur["val"]))
        elif addr in EXT:
            pass
        else:
            return
        uc.reg_write(UC_ARM_REG_R0, 0)
        uc.reg_write(UC_ARM_REG_PC, rd(UC_ARM_REG_LR))

    mu.hook_add(UC_HOOK_CODE, code)
    mu.reg_write(UC_ARM_REG_R0, 0x111); mu.reg_write(UC_ARM_REG_R1, 0x222); mu.reg_write(UC_ARM_REG_R2, 0x333); mu.reg_write(UC_ARM_REG_R3, 0x444)
    mu.reg_write(UC_ARM_REG_R4, 0xAAA4); mu.reg_write(UC_ARM_REG_R5, 0xAAA5); mu.reg_write(UC_ARM_REG_R7, 0xAAA7)
    sp0 = stack - 0x40
    mu.reg_write(UC_ARM_REG_SP, sp0)
    mu.reg_write(UC_ARM_REG_LR, 0x7FFF0001)
    mu.emu_start(0x689538 | 1, 0x689600, count=20000)
    return {"msgs": msgs, **estado, "sp0": sp0}


def comprobar() -> None:
    orig = SRC.read_bytes()
    img = apply_bytes(orig)
    assert len(img) == len(orig) and apply_bytes(orig) == img
    B = cfw.POR_ID["dr_prior"].backup
    for im, bk in ((orig, {B: 2}), (img, {}), (img, {B: 0}), (img, {B: 9})):               # original, sin ajuste, Off, fuera de tabla: nada
        r = emular(im, bk)
        assert r["msgs"] == [] and r["llego"] is not None, r
    r = emular(img, {B: 1})
    assert r["msgs"] == [(MSG_DRO, PARAM_DRO, DRO_LV3), (MSG_BIAS, PARAM_BIAS, (-3) & 0xFFFFFFFF)], r
    r2 = emular(img, {B: 2})
    assert r2["msgs"] == [(MSG_DRO, PARAM_DRO, DRO_LV5), (MSG_BIAS, PARAM_BIAS, (-6) & 0xFFFFFFFF)], r2
    for x in (r, r2):                                                                      # r0-r3, r4, r5, r7 y sp intactos al llegar al destino original
        assert x["llego"] == (0x111, 0x222, 0x333, 0x444) and x["regs"] == (0xAAA4, 0xAAA5, 0xAAA7) and x["sp"] == x["sp0"], x


if __name__ == "__main__":
    comprobar()
    print("OK")

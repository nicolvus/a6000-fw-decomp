"""G76 VFR-F2 — cueva «S&Q» de libObj (Unicorn sobre libObj 3.21 real): mismos mensajes que el modelo MOVIE_REC_O_U_CRANK de Sony, solo al cambiar el ajuste."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/g61"), str(ROOT / "scripts/g76")]
import intervalo_patch as g61
import sq_libobj_patch as P

pytestmark = pytest.mark.skipif(not P.SRC.exists(), reason="libObj.so no disponible")


def _emula(img, backup, celda=None, mu=None):
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R2,
        UC_ARM_REG_R3,
        UC_ARM_REG_SP,
    )
    if mu is None:
        mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        mu.mem_map(0, 0x10E4000)
        mu.mem_write(0, img)
        mu.mem_map(0x30000000 - 0x1000, 0x4000)
    rd = mu.reg_read
    ev, est, cur = [], {}, {}

    def code(uc, addr, size, _):
        if addr == 0xDD5F4:
            uc.mem_write(rd(UC_ARM_REG_R1), bytes([backup.get(rd(UC_ARM_REG_R0), 0)]))
        elif addr == P.DESTINO:
            est["llego"] = tuple(rd(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)) + (rd(UC_ARM_REG_SP),)
            uc.emu_stop()
            return
        elif P.CAVE <= addr < P.CAVE_FIN:
            return
        elif addr == g61.PLT_MSG:
            cur["m"] = (rd(UC_ARM_REG_R1), rd(UC_ARM_REG_R2))
        elif addr in (g61.PLT_INT, P.PLT_BOOL):
            cur["v"] = rd(UC_ARM_REG_R1)
        elif addr == g61.PLT_ADD:
            ev.append(("p", cur["m"], rd(UC_ARM_REG_R1), cur["v"]))
        elif addr == g61.OBJ_DE:
            cur["o"] = rd(UC_ARM_REG_R0)
            uc.reg_write(UC_ARM_REG_R0, 0x5000 + cur["o"])
            uc.reg_write(UC_ARM_REG_PC, rd(UC_ARM_REG_LR))
            return
        elif addr in (g61.PLT_ISSUE, P.PLT_SYNC):
            ev.append(("envío", cur["m"], rd(UC_ARM_REG_R0) - 0x5000, "sync" if addr == P.PLT_SYNC else "async"))
        elif addr in (g61.PLT_DTOR_P, g61.PLT_DTOR_M, P.PLT_DTOR_B, P.PLT_MSGOUT):
            pass
        else:
            return
        uc.reg_write(UC_ARM_REG_R0, 0)
        uc.reg_write(UC_ARM_REG_PC, rd(UC_ARM_REG_LR))

    h = mu.hook_add(UC_HOOK_CODE, code)
    for r, v in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), (0x111, 0x222, 0x333, 0x444)):
        mu.reg_write(r, v)
    mu.reg_write(UC_ARM_REG_SP, 0x30000000 - 0x40)
    mu.reg_write(UC_ARM_REG_LR, 0x7FFF0001)
    mu.emu_start(P.HOOK[0] | 1, P.HOOK[0] + 0x100, count=50_000)
    mu.hook_del(h)
    return ev, est, mu


def test_cueva_s_q_manda_lo_de_sony_y_solo_al_cambiar():
    orig = P.SRC.read_bytes()
    img = P.apply_bytes(orig)
    with pytest.raises(ValueError):
        P.apply_bytes(img)
    assert sum(a != b for a, b in zip(orig, img, strict=True)) <= 4 + (P.CAVE_FIN - P.CAVE)
    bk = P.cfw.POR_ID["sq"].backup
    ev, est, mu = _emula(img, {bk: 1})                        # opción 1 = 120/100 (índice de UI de Sony 8)
    assert est["llego"] == (0x111, 0x222, 0x333, 0x444, 0x30000000 - 0x40)
    assert ev == [("p", (0x3100, 0x75E4), 0x971A, 0x206), ("p", (0x3100, 0x75E4), 0x971B, 0x3E2), ("envío", (0x3100, 0x75E4), 8, "async"),
                  ("p", (0x3300, 0x1005), 0xC001, 1), ("p", (0x3300, 0x1005), 0xC002, 0), ("envío", (0x3300, 0x1005), 0xA, "sync"),
                  ("p", (0x3900, 0x3015), 0x1013, 1), ("envío", (0x3900, 0x3015), 9, "async")]
    ev2, est2, _ = _emula(img, {bk: 1}, mu=mu)                # mismo ajuste otra vez: nada (fábrica)
    assert ev2 == [] and est2["llego"][:4] == (0x111, 0x222, 0x333, 0x444)
    ev3, _, _ = _emula(img, {bk: 5}, mu=mu)                   # opción 5 = 8/6 fps
    assert [e[3] for e in ev3 if e[0] == "p"] == [0x206, 0x20A, 1, 3, 1]
    ev4, _, _ = _emula(img, {bk: 0}, mu=mu)                   # Off tras ON: una vez OFF
    assert [e[3] for e in ev4 if e[0] == "p"] == [0x205, 0x207, 0, 0, 0]
    assert _emula(img, {bk: 0}, mu=mu)[0] == []


def test_sin_ajuste_no_manda_nada():
    img = P.apply_bytes(P.SRC.read_bytes())
    ev, est, _ = _emula(img, {})
    assert ev == [] and est["llego"][:4] == (0x111, 0x222, 0x333, 0x444)

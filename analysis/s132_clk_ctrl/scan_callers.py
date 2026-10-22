#!/usr/bin/env python3
"""S132 — quién llama a la API DDL del subsistema CLK_CTRL (A6000 fw3.21).

Busca instrucciones `bl` (Thumb-2, 32 bits) en toda la imagen cuyo destino sea
una de las funciones de la API `ddl_clkctrl_*` y produce, para cada llamador,
la función (prólogo Thumb) que lo contiene.

Decodificación BL (ARM ARM): imm32 = I1:I2:imm10:imm11:'0' (24 bits),
I1 = NOT(J1 EOR S), I2 = NOT(J2 EOR S), y signo S sobre 24 bits.
"""
import bisect
import json
import os
import struct

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))

API = {
    0x4359f174: "ddl_clkctrl_open_clk",
    0x4359f12c: "ddl_clkctrl_close_clk",
    0x4359f0e4: "ddl_clkctrl_open_dly",
    0x4359f09c: "ddl_clkctrl_close_dly",
    0x4359ef88: "ddl_clkctrl_set_sync_signal",
    0x4359ef2c: "ddl_clkctrl_set_sysv_delay",
    0x4359eed0: "ddl_clkctrl_lock_sync_signal",
    0x4359ee78: "ddl_clkctrl_unlock_sync_signal",
    0x4359f048: "ddl_clkctrl_set_sysv_initial_delay",
    0x4359f000: "ddl_clkctrl_set_sync_initial_signal",
    0x4359ee24: "ddl_clkctrl_get_clk_chg_enable",
}
CORE = {
    0x435a0880: "ddl_dispatcher_CallCB3",
    0x435a0d60: "ddl_set_sysv_delay_impl",
    0x435a0f04: "ddl_set_sync_signal_impl",
    0x435a1142: "ddl_max_over_check",
    0x4359f9c0: "tsk_state_dispatch",
    0x4359fb24: "ClkChgExec",
    0x4359fc14: "DelayChgExec",
    0x4359fd90: "open_subsystem",
    0x4359fe44: "close_subsystem",
    0x435a0596: "rcv_msg_from_master",
    0x435a0734: "snd_msg_to_slave",
}

U16 = struct.Struct("<H").unpack_from


def prologues(data, lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        h = U16(data, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = U16(data, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def main():
    d = open(BIN, "rb").read()
    n = len(d)
    tgts = dict(API)
    tgts.update(CORE)
    hits = {k: [] for k in tgts}
    a = 0
    while a < n - 4:
        h = U16(d, a)[0]
        if (h >> 11) == 0x1E:
            h2 = U16(d, a + 2)[0]
            if (h2 & 0xD000) == 0xD000:
                s = (h >> 10) & 1
                imm10 = h & 0x3FF
                j1 = (h2 >> 13) & 1
                j2 = (h2 >> 11) & 1
                imm11 = h2 & 0x7FF
                i1 = (~(j1 ^ s)) & 1
                i2 = (~(j2 ^ s)) & 1
                v = (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
                if s:
                    v -= 1 << 24
                t = BASE + a + 4 + v
                if t in hits:
                    hits[t].append(BASE + a)
        a += 2

    starts = prologues(d, BASE, BASE + n)
    out = {}
    for t, name in tgts.items():
        rows = []
        for site in hits[t]:
            i = bisect.bisect_right(starts, site) - 1
            f = starts[i] if i >= 0 else None
            rows.append({"site": hex(site), "func": hex(f) if f else None})
        out[name] = {"addr": hex(t), "n_llamadas": len(rows), "llamadas": rows}
    dest = os.path.join(HERE, "callers.json")
    json.dump(out, open(dest, "w"), indent=1)
    for name, v in sorted(out.items()):
        funcs = sorted({r["func"] for r in v["llamadas"] if r["func"]})
        print(f"{name:38s} {v['addr']}  llamadas={v['n_llamadas']:3d}  "
              f"funcs_distintas={len(funcs)}")
    print("escrito", dest)


if __name__ == "__main__":
    main()

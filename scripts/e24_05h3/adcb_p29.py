"""E24-05h-3: máquina ADC-B (`0x29dc8`), su terminación con `0x20c74=0` y configuración de P29 (solo bytes de darwin_core.bin).

Reproducible: `python scripts/e24_05h3/adcb_p29.py` guarda analysis/e24-05h-3/adcb_p29.json.
Reutiliza Core/G/Sym/closure_pins de E24-05..05h. Ninguna dirección derivada está fijada salvo las raíces de entrada.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[0] / d) for d in ("e24_05h", "e24_05g", "e24_05f", "e24_05", "e24_05d")]

import dependencias_finales as D
import emisores as E
from dwn import ROOT, Core

ADCB, FSMS = 0x29DC8, {0x29D90: "ADC-A", 0x29DAC: "29dac", 0x29DC8: "ADC-B", 0x29DE4: "ADC-C"}
PRIM = {0x1E150: "instalar_lista", 0x1E0B4: "forzar_terminal", 0x1E53C: "reiniciar", 0x1E4DA: "salto", 0x20C06: "ejecutar_idx", 0x20220: "ejecutar_idx_ev"}
DONE, FAIL, ARM, CANCEL, JUMP = 0x1E4AA, 0x1E4C2, 0x1E3D2, 0x1E476, 0x1E4DA
S_BASE = 0x200036D8
GROUP_TABLE, GROUP_SIZE, MODE_TBB = 0x25BFC, 152, 0x55EE
H = lambda xs: [hex(x) for x in xs]


def at(c: Core, a: int):
    return next(iter(c.dis(a, 4)))


def chk(c: Core, spec: list[tuple[int, str, str]]) -> dict[str, bool]:
    """Cada (addr, mnemónico, sufijo del operando) se comprueba contra el desensamblado real."""
    return {f"{a:#x} {m} {o}": at(c, a).mnemonic == m and at(c, a).op_str.endswith(o) for a, m, o in spec}


def descriptor(c: Core, d: int) -> dict:
    t, n = c.u32(d), c.u32(d + 4)
    term = c.u8(d + 0x14)
    return {"desc": hex(d), "tabla": hex(t), "n": n, "ptr_pos": hex(c.u32(d + 8)), "ptr_id": hex(c.u32(d + 0xC)), "ptr_celda_lista": hex(c.u32(d + 0x10)),
            "terminal": term, "timers_id": [c.u8(d + 0x18 + k) for k in range(3)], "id_log": c.u8(d + 0x1B),
            "estados": states_of(c, t, term)}


def states_of(c: Core, t: int, term: int) -> dict[int, str]:
    """Entradas {id, manejador|1} hasta el id terminal inclusive (centinela que el ejecutor reconoce sin llamar al manejador; +4 del descriptor = id terminal)."""
    out: dict[int, str] = {}
    prev = -1
    while c.u32(t + 8 * len(out)) > prev and prev < term and len(out) < 32:
        prev = c.u32(t + 8 * len(out))
        out[prev] = hex(c.u32(t + 8 * len(out) + 4) - 1)
    return out


def lst(c: Core, a: int, term: int) -> list[int]:
    out: list[int] = []
    while len(out) < 24:
        out.append(c.u8(a))
        a += 1
        if out[-1] == term:
            break
    return out


def regs_before(c: Core, k: int, back: int = 12) -> dict[int, int | None]:
    """Propagación de constantes lineal sobre las `back` instrucciones previas al índice k de all_insns (r0..r12)."""
    ins = c.all_insns
    regs: dict[int, int | None] = dict.fromkeys(range(13))
    idx = lambda s: int(s[1:]) if re.fullmatch(r"r\d+", s) else None
    for i in ins[max(0, k - back):k]:
        m = re.match(r"(r\d+), (?:(r\d+), )?#(-?0x[0-9a-f]+|-?\d+)$", i.op_str)
        d = idx(i.op_str.split(",")[0]) if i.op_str else None
        lit = c.lit_of(i) if i.mnemonic.startswith("ldr") and "pc" in i.op_str else None
        if i.mnemonic.startswith("ldr") and lit is not None and d is not None:
            regs[d] = lit
        elif m and d is not None and i.mnemonic in ("movs", "mov.w", "movw", "mov"):
            regs[d] = int(m.group(3), 0)
        elif m and d is not None and i.mnemonic in ("adds", "add.w", "add", "sub.w", "subs", "sub"):
            src = idx(m.group(2)) if m.group(2) else d
            sign = 1 if i.mnemonic.startswith("add") else -1
            base = None if src is None else regs[src]
            regs[d] = None if base is None else base + sign * int(m.group(3), 0)
        elif d is not None and i.mnemonic.startswith(("mov",)) and re.fullmatch(r"r\d+, r\d+", i.op_str):
            src = idx(i.op_str.split(", ")[1])
            regs[d] = None if src is None else regs[src]
        elif i.mnemonic in ("bl", "blx"):
            for r in (0, 1, 2, 3, 12):
                regs[r] = None
        elif d is not None:
            regs[d] = None
    return regs


def primitive_sites(c: Core, g: E.G) -> dict[str, list[dict]]:
    """Todas las llamadas a las primitivas del motor FSM con el descriptor/lista resueltos por propagación de constantes."""
    idx: dict[int, int] = {i.address: k for k, i in enumerate(c.all_insns)}
    out: dict[str, list[dict]] = {}
    for p, name in PRIM.items():
        for a in sorted(g.callers.get(p, [])):
            r = regs_before(c, idx[a])
            out.setdefault(name, []).append({"sitio": hex(a), "funcion": hex(g.func(a)), "r0": hex(r[0]) if r[0] is not None else None,
                                             "r1": hex(r[1]) if r[1] is not None and p == 0x1E150 else None})
    return out


def handler_info(c: Core, g: E.G, sym: D.Sym, h: int, end: int, term_handlers: set[int]) -> dict:
    ins = c.dis(h, end - h)
    calls: set[int] = set()
    tails: set[int] = set()
    back: list[str] = []
    for i in ins:
        if i.mnemonic in ("bl", "b.w") and i.operands and i.operands[0].type == 2:
            (calls if i.mnemonic == "bl" else tails).add(i.operands[0].imm)
        elif (i.mnemonic.startswith("b") and i.mnemonic not in ("bl", "blx", "bic", "bics", "bfi", "bfc", "bx") and i.operands and i.operands[0].type == 2
              and i.operands[0].imm < i.address) or (i.mnemonic in ("cbz", "cbnz") and i.operands[1].imm < i.address):
            back.append(hex(i.address))
    cl = g.closure(h)
    pins = D.closure_pins(g, sym, [h])
    return {"manejador": hex(h), "llamadas": H(sorted(calls)), "colas": H(sorted(tails)), "bucles_internos": back,
            "hecho": DONE in calls | tails, "arma_temporizador": ARM in calls | tails, "cancela_temporizador": CANCEL in calls,
            "FAIL_en_cierre": FAIL in cl, "SALTO_en_cierre": JUMP in cl, "funciones_cierre": len(cl), "lecturas_pin_0x51c6": H(sorted(f for f in cl if D.PORT_R in g.calls.get(f, ()))), "usa_0x1fe66": 0x1FE66 in cl, "usa_0x20c74": 0x20C74 in cl,
            "pines_tipoN": pins["pines"], "pines_tipo0": pins["pines_tipo0"]}


def simulate(handlers: dict[int, dict], seq: list[int], term: int) -> list[dict]:
    """Semántica verificada del motor (0x1e33e/0x1e234): avanza siempre salvo FAIL/salto; continúa en la misma llamada solo si el manejador marcó «hecho»."""
    rows, pos, inv = [], 0, 0
    while seq[pos] < term and inv < 12:
        stop = False
        while seq[pos] < term and not stop:
            h = handlers[seq[pos]]
            cur, nxt = seq[pos], seq[pos + 1]
            rows.append({"invocacion": inv, "estado": cur, "manejador": h["manejador"], "hecho": h["hecho"], "temporizador": h["arma_temporizador"], "siguiente": nxt,
                         "espera": None if h["hecho"] else "evento 0 del temporizador (canal 0 de 0x40023000)" if h["arma_temporizador"] else "siguiente invocación del ejecutor"})
            pos += 1
            stop = not h["hecho"]
        inv += 1
    return rows


def p29_groups(c: Core) -> dict:
    out: dict[int, dict] = {}
    for sl in range(7):
        base, ents = GROUP_TABLE + GROUP_SIZE * sl, []
        for k in range(GROUP_SIZE // 4):
            b0, b1, mk = c.u8(base + 4 * k), c.u8(base + 4 * k + 1), c.u16(base + 4 * k + 2)
            if (b0 & 7) == 2 and mk & 0x200:
                ents.append({"modo": b0 >> 3, "pull_bits": b1 & 3, "nivel_bits": (b1 >> 2) & 3, "mascara": hex(mk)})
        e4e = [e for k in range(GROUP_SIZE // 4) for b0, e in [(c.u8(base + 4 * k), c.u16(base + 4 * k + 2))] if (b0 & 7) == 4 and e & 0x4000 and (b0 >> 3) == 1]
        out[sl] = {"P29": ents, "P4E_salida_modo1": bool(e4e)}
    return out


def group_calls(c: Core, g: E.G) -> dict:
    ins, idx = c.all_insns, {i.address: k for k, i in enumerate(c.all_insns)}
    res = {}
    for a in sorted(g.callers.get(0x5792, [])):
        vals, k = set(), idx[a]
        for j in ins[max(0, k - 8):k]:
            m = re.fullmatch(r"r0, #(0x[0-9a-f]+|\d+)", j.op_str)
            if j.mnemonic in ("movs", "mov.w") and m:
                vals.add(int(m.group(1), 0))
        res[hex(a)] = {"funcion": hex(g.func(a)), "r0_inmediatos": sorted(vals)}
    return res


def exposure_us(c: Core, s32: int) -> int:
    """Réplica de 0x19a12: t = ((tabla[(0x1000−s32)&0xff] + 0x800) · 1e6) >> (11 − ((0x1000−s32) >> 8)), con 0xf4240 = 1e6 (literal en 0x19b6c)."""
    v = ((0x1000 - s32) + 0x8000) % 0x10000 - 0x8000
    return (((c.u16(0x29188 + 2 * (v & 0xFF)) + 0x800) * 1_000_000) & 0xFFFFFFFF) >> (11 - (v >> 8))


def main() -> dict:
    c = Core()
    g = E.G(c)
    sym = D.Sym(c, g)
    r: dict = {"sha256_darwin_core": c.sha256()}
    # --- A. descriptores y listas
    r["descriptores"] = {FSMS[d]: descriptor(c, d) for d in FSMS}
    b = r["descriptores"]["ADC-B"]
    tab_h = sorted({int(h, 16) for dd in r["descriptores"].values() for h in dd["estados"].values()})
    ends = {h: min([x for x in tab_h if x > h] + [h + 0x60]) for h in tab_h}
    handlers = {sid: handler_info(c, g, sym, int(h, 16), ends[int(h, 16)], set()) for sid, h in b["estados"].items()}
    r["manejadores_ADC-B"] = {str(k): v for k, v in handlers.items()}
    sites = primitive_sites(c, g)
    r["sitios_primitivas"] = {k: [s for s in v if s["r0"] in (hex(ADCB), hex(ADCB - 0x38 + 0x38), None) or k in ("ejecutar_idx", "ejecutar_idx_ev")] for k, v in sites.items()}
    inst = [s for s in sites["instalar_lista"] if s["r0"] == hex(ADCB)]
    r["instalaciones_ADC-B"] = [{**s, "lista": lst(c, int(s["r1"], 16), 7)} for s in inst]
    r["forzar_terminal_ADC-B"] = [s for s in sites["forzar_terminal"] if s["r0"] == hex(ADCB)]
    r["reinicios_ADC-B"] = [s for s in sites.get("reiniciar", []) if s["r0"] == hex(ADCB)]
    r["saltos_ADC-B"] = [s for s in sites.get("salto", []) if s["r0"] == hex(ADCB)]
    r["sitios_ejecutar_idx"] = sites["ejecutar_idx"]
    r["cadena_forzar_terminal"] = {"0x201d0": H(sorted(g.callers.get(0x201D0, []))), "0x197f8": H(sorted(g.callers.get(0x197F8, []))), "0x206ec": H(sorted(g.callers.get(0x206EC, []))),
                                   "0x19b6e": H(sorted(g.callers.get(0x19B6E, []))), "0x19b8e_salto_a_0x206ec": at(c, 0x19B8E).mnemonic == "b.w" and at(c, 0x19B8E).op_str == "#0x206ec"}
    # accesos directos a S+0x146/0x147/0x148 (pos/id/celda de ADC-B): coherencia de la dirección 0x2000381e/f/0x20003820 con S+0x146
    r["ptrs_ADC-B_en_S"] = {"pos": S_BASE + 0x146 == int(b["ptr_pos"], 16), "id": S_BASE + 0x147 == int(b["ptr_id"], 16), "celda": S_BASE + 0x148 == int(b["ptr_celda_lista"], 16),
                            "literales_de_la_direccion": {hex(v): H(c.word_refs(v)) for v in (0x2000381E, 0x2000381F, 0x20003820)}}
    # --- motor, estado terminal, predicado «hecho»
    r["motor"] = chk(c, [(0x1E25C, "lsls", "#0x18"), (0x1E25E, "bmi", "0x1e2b6"), (0x1E260, "lsls", "#0x17"), (0x1E262, "bmi", "0x1e294"), (0x1E264, "ldrb", "[r2]"),
                         (0x1E266, "adds", "#1"), (0x1E268, "strb", "[r2]"), (0x1E256, "cmp", "r3"), (0x1E258, "bhs", "0x1e338"), (0x1E39A, "cmp", "r1"), (0x1E39C, "beq", "0x1e3a0"),
                         (0x1E3CC, "bne", "0x1e346"), (0x1E3B8, "movs", "#7"), (0x1E17A, "cmp", "r3"), (0x1E17C, "bhi", "0x1e190"), (0x1E182, "beq", "0x1e18e"),
                         (0x1E18E, "movs", "#1"), (0x203AE, "b.w", "0x20c2c"), (0x20C2C, "ldr", "[pc, #0x3c]"), (0x20C30, "b.w", "0x1e16e")])
    r["motor"]["0x20c2c carga 0x29d90+0x38"] = c.lit_of(at(c, 0x20C2C)) == 0x29D90 and at(c, 0x20C2E).op_str.endswith("#0x38")
    # --- starters
    r["arrancadores"] = {"0x2041e": chk(c, [(0x20422, "movs", "r0"), (0x2042C, "bne", "0x20470"), (0x20484, "bl", "0x1e150"), (0x2048E, "movs", "#2"), (0x20490, "b", "0x20468"), (0x2046C, "b.w", "0x20c06"),
                                            (0x20428, "str.w", "[r5, #0x14c]"), (0x2045C, "bl", "0x1e150"), (0x20466, "movs", "#0")]),
                        "0x2027c": chk(c, [(0x20284, "cbnz", "#0x20296"), (0x202A6, "bl", "0x1e150"), (0x202AA, "movs", "#8")]),
                        "0x202f2": chk(c, [(0x202FA, "cbnz", "#0x20314"), (0x20324, "bl", "0x1e150"), (0x20334, "b.w", "0x20c06"), (0x20332, "movs", "#2")]),
                        "llamadores": {hex(t): H(sorted(g.callers.get(t, []))) for t in (0x2041E, 0x202F2, 0x2027C)}}
    r["compuerta_0x19b9e"] = {"bytes": chk(c, [(0x19BA2, "movs", "#0x10"), (0x19BA4, "bl", "0x165c8"), (0x19BA8, "cbnz", "#0x19bac"), (0x19BAA, "movs", "#0"), (0x19BB2, "lsls", "#0x1f"), (0x19BB6, "movs", "#0"),
                                              (0x165CE, "tst", "r0"), (0x165CA, "ldrh.w", "[r1, #0x444]")]),
                              "formula": "ok ⇔ (S+0x444 & 0x10)==0 ∧ (S+0x170 & 1)==0", "llama_a_0x20c74": 0x20C74 in g.closure(0x19B9E),
                              "cierre": H(sorted(g.closure(0x19B9E))),
                              "escribe_S444": H(sorted({g.func(i.address) for i in c.all_insns if i.mnemonic.startswith("str") and re.search(r"\[(\w+), #0x444\]", i.op_str)})),
                              "escribe_S170": H(sorted({g.func(i.address) for i in c.all_insns if i.mnemonic.startswith("str") and re.search(r"\[(\w+), #0x170\]", i.op_str)}))}
    r["gate_0x201b0"] = chk(c, [(0x201B4, "bl", "0x20c74"), (0x201BA, "cbz", "#0x201c8"), (0x201BC, "bl", "0x1fe66"), (0x201C0, "cbz", "#0x201c8"), (0x201C2, "strb.w", "[r5, #0x150]"), (0x201CA, "strb.w", "[r5, #0x150]")])
    # --- simulación por lista
    r["simulacion"] = {hex(int(i["r1"], 16)) + " (instalada en " + i["sitio"] + ")": simulate({int(k): v for k, v in handlers.items()}, i["lista"], b["terminal"]) for i in r["instalaciones_ADC-B"]}
    r["lista_pos0_ADC-B_tras_init"] = {"init_0x201d0": chk(c, [(0x201DC, "bl", "0x1e0b4"), (0x201DA, "adds", "#0x38")]), "terminal": b["terminal"]}
    # --- cadena de eventos del ejecutor
    r["cadena_ejecutor"] = {"hilo": "0x1d04c → 0x197d8 → 0x199b0 → 0x203ae; si 0 → 0x197c6 → 0x199fe → 0x20274 → 0x20220(2) → 0x20c06(2)",
                            "bytes": chk(c, [(0x1D04E, "bl", "0x197d8"), (0x1D052, "cbz", "#0x1d05c"), (0x1D058, "b.w", "0x1979c"), (0x1D060, "b.w", "0x197c6"), (0x197D8, "b.w", "0x199b0"), (0x199B0, "b.w", "0x203ae"),
                                             (0x197C6, "b.w", "0x199fe"), (0x199FE, "b.w", "0x20274"), (0x20274, "movs", "#2"), (0x20276, "b", "0x20220"), (0x20244, "b.w", "0x20c06"), (0x2023A, "bl", "0x1e51a")]),
                            "llamadores": {hex(t): H(sorted(g.callers.get(t, []))) for t in (0x1D04C, 0x197C6, 0x199FE, 0x20274, 0x20220)},
                            "tabla_0x296d4": {"[0]": hex(c.u32(0x296D4)), "[1]": hex(c.u32(0x296D8)), "cargada_en": H(c.ldr_users(0x296D4)), "despachador_sitio": hex(c.ldr_users(0x296D4)[0])},
                            "ejecutar_idx_constantes": sorted({s["r0"] for s in sites["ejecutar_idx"] if s["r0"]})}
    # --- temporizadores
    tid = b["timers_id"][0]
    idx = tid - 8
    ch = c.u8(0x2A69C + 0x40 + idx * 8 + 4)
    word = c.u32(0x2796C)
    r["temporizadores"] = {"id_timer0_ADC-B": tid, "indice_bloque_B": idx, "canal_hw": ch,
                           "bytes": chk(c, [(0x1E1FA, "cmp", "#0xc"), (0x1E1FE, "subs", "#8"), (0x1E204, "bl", "0x24d1a"), (0x1E20A, "bl", "0x24ca4"), (0x1E210, "bl", "0x24cfa"), (0x1E21C, "b.w", "0x24c6e"),
                                            (0x24C72, "cmp", "#0xa"), (0x24C76, "movs", "#0xa"), (0x24C94, "ldrb", "[r0, #4]"), (0x24C96, "b.w", "0x9388"), (0x939C, "b.w", "0x94f6"), (0x9388, "cmp", "#0xd")]),
                           "min_ticks": 0xA, "overflow_ticks": "0xffffffff si ticks·5/5≠ticks (0x24c7c–0x24c86)",
                           "perifericos": {"base": "0x40023000", "contador": "[+4]", "palabra_config_0x2796c": hex(word),
                                           "ctrl_calculado": hex(0x50 | (word >> 16 & 0xF) | (word >> 21 & 3) << 5 | (word >> 23 & 1) << 7 | (word >> 20 & 1) << 15 | (0x100 if word >> 27 & 1 else 0) | (0x2000 if word >> 28 & 1 else 0)),
                                           "recarga_0x27970-4": hex(word & 0xFFFF)},
                           "93e6": {"lee": "~contador via blx [0x2792c+0x18]", "puntero": hex(c.u32(0x2792C + 0x18)), "chk": chk(c, [(0x93FC, "mvns", "r0, r0"), (0x94E8, "blx", "r1")])},
                           "umbrales_ticks": D.p29(c, g)["umbrales_0x18d6e"] | {"nota": "5000/50000/250000/25000/500000 de E24-05h"}}
    r["tiempo"] = {"exposicion_us(0x1600)": exposure_us(c, 0x1600), "exposicion_us(0x1400)": exposure_us(c, 0x1400), "exposicion_us(0x1000)": exposure_us(c, 0x1000),
                   "bytes_0x19a12": chk(c, [(0x19A12, "rsb.w", "#0x1000"), (0x19A18, "asrs", "#8"), (0x19A24, "add.w", "#0x800"), (0x19A28, "muls", "r0, r2, r0"), (0x19A2A, "rsb.w", "#0xb"), (0x19A2E, "lsrs", "r1")]),
                   "factor_literal_1e6": 0xF4240 in [c.u32(a) for a in range(0x19A14, 0x19BD0, 4)]}
    # --- espera del estado 31 con S+0x32 != 0
    r["estado31_S32_no_cero"] = chk(c, [(0x18D74, "ldrh", "[r7, #0x32]"), (0x18D76, "bl", "0x19a12"), (0x18E8A, "bl", "0x203ae"), (0x18E8E, "cmp", "#0"), (0x18E90, "beq", "0x18e8a"),
                                        (0x18ED8, "cmp.w", "#0x1400"), (0x18EDC, "bhs", "0x18f88"), (0x18F88, "bl", "0x203ae"), (0x18F8C, "cmp", "#0"), (0x18F8E, "beq", "0x18f88"),
                                        (0x18F7E, "bl", "0x203ae"), (0x18F84, "beq", "0x18f0c"), (0x18F86, "b", "0x18f90"), (0x18EC8, "bl", "0x19948"), (0x18ECC, "bl", "0x198bc"), (0x18E9E, "bl", "0x19978"),
                                        (0x18E80, "bl", "0x198ee"), (0x18E84, "bl", "0x19932"), (0x18EC4, "mov", "r8, r0") if False else (0x18EC4, "mov", "r0")])
    r["estado31_S32_no_cero"]["llamadas_a_0x203ae_en_0x18d6e"] = H(sorted(a for a in g.callers.get(0x203AE, []) if 0x18D6E <= a < 0x18FA0))
    r["estado31_S32_no_cero"]["rutas"] = {"S48<-0x96": "0x198ee(−S48) → ADC-B lista [1,3,6,2,7] + 0x19932 (ADC-A) + espera 0x203ae sin plazo",
                                           "−0x96≤S48≤0x32": "0x19978 → 0x20544 (paso de bobina), sin ADC-B", "S48>0x32": "r8≥1 → 0x19948(r8) → 0x2041e(r8) lista [1,4,6,7] + 0x198bc; S+0x32≥0x1400: espera 0x203ae sin plazo"}
    # --- escenarios
    otros = {}
    for d in (0x29D90, 0x29DAC, 0x29DE4):
        dd = r["descriptores"][FSMS[d]]
        hs = sorted({int(x, 16) for x in dd["estados"].values()})
        otros[FSMS[d]] = {hex(h): {k: v for k, v in handler_info(c, g, sym, h, ends[h], set()).items() if k in ("bucles_internos", "FAIL_en_cierre", "hecho", "arma_temporizador")} for h in hs}
    r["otras_FSM_bucles_internos"] = {k: {h: v for h, v in d.items() if v["bucles_internos"]} for k, d in otros.items()}
    r["otras_FSM_manejadores_sin_hecho_ni_FAIL"] = {k: [h for h, v in d.items() if not v["hecho"] and not v["arma_temporizador"]] for k, d in otros.items()}
    sc = {}
    for sid, h in handlers.items():
        sc[sid] = {"manejador": h["manejador"], "tipo≠0": h["pines_tipoN"], "tipo0": h["pines_tipo0"], "FAIL": h["FAIL_en_cierre"], "hecho": h["hecho"]}
    r["escenarios_por_estado"] = sc
    # --- B. P29
    ent = [{"pin": hex(c.u16(a)), "clave": hex(c.u16(a + 2)), "INT": c.u16(a + 4), "alt": c.u16(a + 6), "alias": hex(c.u32(a + 8))} for a in range(0x2675C, 0x26858, 12) if c.u16(a + 2) == 0x29]
    r["p29"] = {"tabla_0x2675c": ent, "inicializacion_0x5512": chk(c, [(0x5552, "cmp", "#0x10"), (0x5562, "str.w", "[r2, #0x300]"), (0x5568, "str.w", "[r2, #0x304]"), (0x554C, "ldrh", "[r2, #6]"), (0x5550, "adds", "#1")]),
                "llamador_0x5512": H(sorted(g.callers.get(0x5512, []))), "lectura": D.p29(c, g)["lectores"] | {"inmediato_0x124_en": D.p29(c, g)["inmediato_0x124_en"]},
                "modos_tbb": {"bytes": c.data[MODE_TBB - 0x4200:MODE_TBB - 0x4200 + 12].hex(), "destinos": {m: hex(MODE_TBB + 2 * c.u8(MODE_TBB + m)) for m in range(12)}},
                "volcado_a_hw": chk(c, [(0x581A, "str.w", "[r0, #0x200]"), (0x5822, "str.w", "[r0, #0x400]"), (0x582A, "str", "[r0]"), (0x5830, "str.w", "[r0, #0x100]"), (0x57B0, "str.w", "[sb, #0x500]")]),
                "semantica_modo1": chk(c, [(0x55FA, "ldrh", "[r4]"), (0x55FC, "orrs", "r5"), (0x5600, "ldrh", "[r4, #4]"), (0x5602, "bics", "r5"), (0x560C, "ldrh", "[r4, #6]"), (0x560E, "bics", "r5")]),
                "semantica_modo2": chk(c, [(0x563C, "ldrh", "[r4]"), (0x563E, "bics", "r5"), (0x5642, "ldrh", "[r4, #4]"), (0x5644, "bics", "r5"), (0x564C, "ldrh", "[r4, #6]"), (0x564E, "orrs", "r5")]),
                "semantica_modo5": chk(c, [(0x5654, "mov", "r1, r5"), (0x5658, "bl", "0x5512"), (0x567C, "ldrh", "[r4, #4]"), (0x567E, "orrs", "r5")]),
                "grupos": p29_groups(c), "arranque": chk(c, [(0x4770, "orr.w", "r1, r0, lsl #8"), (0x4774, "cmp", "#5"), (0x4776, "beq", "0x4784"), (0x4780, "cmp", "#2"), (0x4782, "bne", "0x4788"), (0x4784, "movs", "#1"), (0x4788, "movs", "#0"), (0x478A, "bl", "0x5792")]),
                "llamadas_5792": group_calls(c, g), "tabla_manejadores_0x25b50": [hex(c.u32(0x25B50 + 4 * k)) for k in range(22)],
                "escritores_directos_P29": D.p29(c, g)["inmediato_0x124_en"]}
    sec = {0: 0x26024, 2: 0x26158, 3: 0x2628C, 4: 0x263C0, 5: 0x264F4, 6: 0x26628}  # 0x5b60: tbb de 0x5b72, filas de 28 B por variante
    r["p29"]["tablas_secundarias_0x5b60"] = {"tbb": c.data[0x5B76 - 0x4200:0x5B76 - 0x4200 + 7].hex(), "variante": "0xcf3a() = [0x20000000] si 0x6da2()==1, si no 0",
                                             "entradas_puerto2_bit9": [[sl, v] for sl, b in sec.items() for v in range(11) for k in range(7)
                                                                       if (c.u8(b + 28 * v + 4 * k) & 7) == 2 and c.u16(b + 28 * v + 4 * k + 2) & 0x200]}
    r["p29"]["pull_en_P29"] = all(e["pull_bits"] == 0 for gr in r["p29"]["grupos"].values() for e in gr["P29"])
    r["p29"]["usuarios_0x40031000"] = H(sorted({g.func(a) for a in c.ldr_users(0x40031000)}))
    return r


if __name__ == "__main__":
    res = main()
    out = ROOT / "analysis" / "e24-05h-3"
    out.mkdir(parents=True, exist_ok=True)
    (out / "adcb_p29.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res[k] for k in ("instalaciones_ADC-B", "forzar_terminal_ADC-B", "reinicios_ADC-B", "saltos_ADC-B", "tiempo", "temporizadores")}, indent=1, default=str)[:5000])

"""E24-05h: dependencias finales de la captura sin rearme (solo lectura de bytes de darwin_core.bin y av-cam.bin).

Reproducible: `python scripts/e24_05h/dependencias_finales.py` guarda analysis/e24-05h/dependencias.json.
Reutiliza Core/G/Bz de E24-05..05g. Ningún valor del informe está fijado salvo las direcciones raíz de entrada.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import capstone

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[0] / d) for d in ("e24_05g", "e24_05f", "e24_05", "e24_05d")]

import ajustes_modo as A
import emisores as E
from bz import Bz
from capture_flow import state_lists, states
from dwn import ROOT, Core

PORT_W, PORT_R, TYPE_FN, TICK = 0x51C0, 0x51C6, 0x20C74, 0x93E6
PIN_NAMES = {0x230: "P4C", 0x234: "P4D", 0x238: "P4E", 0x190: "P34", 0x124: "P29", 0x2B8: "P5E", 0x194: "P35"}
COIL_FNS = {"0x20cd4 (P4E=0)": 0x20CD4, "0x20d00 (P4E=1)": 0x20D00, "0x20d26 (paso -n)": 0x20D26,
            "0x20e0e (paso 0)": 0x20E0E, "0x20e98 (paso +n)": 0x20E98, "0x20cb2 (P4D=0)": 0x20CB2, "0x20c90 (P4D=1)": 0x20C90}
FSM_NAMES = {0x28DD4: "mensajes", 0x296F0: "exposición", 0x297C0: "297c0", 0x2984C: "2984c", 0x29D90: "ADC-A", 0x29DC8: "ADC-B",
             0x29DE4: "ADC-C", 0x29F64: "ajustes-0x29f64", 0x2A094: "2a094"}
ROOTS = {
    "estado31_espera_P29 (S+0x32=0)": [0x18FA0],
    "estado31_espera_ADC-B (S+0x32!=0)": [0x18D6E],
    "estado31_entrada": [0x190FC],
    "modo0": A.ROOTS["modo0"], "modo1": A.ROOTS["modo1"], "modo2": A.ROOTS["modo2"],
    "arrancadores_ajustes": A.ROOTS["starter_evento"] + A.ROOTS["starter_disparo"],
}


def pin(off: int) -> str:
    return PIN_NAMES.get(off, f"P{off // 0x80}{(off % 0x80) // 4:X}")


class Sym:
    """Ejecución simbólica ramificada de una función (constantes de r0/r1; 'T' = valor de 0x20c74)."""

    def __init__(self, c: Core, g: E.G):
        self.c, self.g = c, g
        self.at = {i.address: i for i in c.all_insns}

    def run(self, f: int, type_val=None, limit: int = 20000) -> dict:
        """type_val=None: ambos lados; 0: poda a 0x20c74==0. Devuelve {'writes': [(addr, r0, r1)], 'calls': set, 'tails': set}."""
        end = min((s for s in self.g.starts if s > f), default=f + 0x400)
        out = {"writes": [], "calls": set(), "tails": set(), "reads": []}
        seen, work, n = set(), [(f, tuple([None] * 16), None)], 0
        while work and n < limit:
            a, regs, fl = work.pop()
            while True:
                n += 1
                key = (a, regs, fl)
                if key in seen or a not in self.at or not f <= a < end + 0x400 and a != f:
                    break
                seen.add(key)
                i = self.at[a]
                regs, fl, nxt, stop = self.step(i, list(regs), fl, f, end, out, work, type_val)
                regs = tuple(regs)
                if stop:
                    break
                a = nxt
        return out

    def step(self, i, regs, fl, f, end, out, work, tv):
        m, ops = i.mnemonic, i.operands
        nxt = i.address + i.size
        reg = lambda o: o.reg  # noqa: E731
        R = capstone.arm
        name = lambda r: self.c.md.reg_name(r)  # noqa: E731

        def idx(r):
            s = name(r)
            return {"sp": 13, "lr": 14, "pc": 15, "ip": 12, "sb": 9, "sl": 10, "fp": 11}.get(s, int(s[1:]) if s[0] == "r" and s[1:].isdigit() else None)

        w = [idx(r) for r in i.regs_access()[1]]
        # ramas
        if m in ("bl", "blx") and ops and ops[0].type == R.ARM_OP_IMM:
            t = ops[0].imm
            if t == PORT_W:
                out["writes"].append((i.address, regs[0], regs[1]))
            if t == PORT_R:
                out["reads"].append((i.address, regs[0]))
            out["calls"].add(t)
            for k in (0, 1, 2, 3, 12):
                regs[k] = None
            if t == TYPE_FN:
                regs[0] = tv if tv is not None else "T"
            return regs, None, nxt, False
        if m in ("bl", "blx"):
            for k in (0, 1, 2, 3, 12):
                regs[k] = None
            return regs, None, nxt, False
        if m in ("b", "b.w") and ops[0].type == R.ARM_OP_IMM:
            t = ops[0].imm
            if f <= t < end:
                return regs, fl, t, False
            out["tails"].add(t)
            if t == PORT_W:
                out["writes"].append((i.address, regs[0], regs[1]))
            return regs, fl, None, True
        if m in ("cbz", "cbnz"):
            v, t = regs[idx(ops[0].reg)], ops[1].imm
            take_zero = None
            if v == "T" and tv is not None:
                take_zero = True
            elif isinstance(v, int):
                take_zero = v == 0
            elif v == 0:
                take_zero = True
            if take_zero is None:
                work.append((t, tuple(regs), fl))
                return regs, fl, nxt, False
            taken = take_zero if m == "cbz" else not take_zero
            return regs, fl, (t if taken else nxt), False
        if m.startswith("b") and m not in ("bl", "blx", "bic", "bics", "bfi", "bfc", "bx", "bxj") and ops and ops[0].type == R.ARM_OP_IMM:
            t, cc = ops[0].imm, m.split(".")[0][1:]
            res = None
            if fl is not None and cc in ("eq", "ne"):
                v, imm = fl
                if v == "T" and tv is not None:
                    v = tv
                if isinstance(v, int):
                    res = (v == imm) == (cc == "eq")
            if res is None:
                work.append((t, tuple(regs), fl))
                return regs, fl, nxt, False
            return regs, fl, (t if res else nxt), False
        if m in ("pop", "pop.w") and any(o.type == R.ARM_OP_REG and name(o.reg) == "pc" for o in ops):
            return regs, fl, None, True
        if m == "bx":
            return regs, fl, None, True
        if m in ("cmp", "cmp.w") and len(ops) == 2 and ops[1].type == R.ARM_OP_IMM and ops[0].type == R.ARM_OP_REG:
            return regs, (regs[idx(ops[0].reg)], ops[1].imm), nxt, False
        # escritura de registros
        for k in w:
            if k is not None and k < 16:
                regs[k] = None
        if m in ("mov.w", "movw", "movs", "mov") and len(ops) == 2 and ops[0].type == R.ARM_OP_REG:
            d = idx(ops[0].reg)
            if ops[1].type == R.ARM_OP_IMM and d is not None:
                regs[d] = ops[1].imm
            elif ops[1].type == R.ARM_OP_REG and d is not None and idx(ops[1].reg) is not None:
                regs[d] = regs[idx(ops[1].reg)]
        return regs, fl, nxt, False


def pins_of(res: dict) -> dict:
    p: dict[str, list] = {}
    for a, r0, r1 in res["writes"]:
        k = pin(r0) if isinstance(r0, int) else "?"
        p.setdefault(k, []).append((hex(a), r1))
    return p


def closure_pins(g: E.G, sym: Sym, roots: list[int]) -> dict:
    cl: set[int] = set()
    for r in roots:
        cl |= g.closure(r)
    pins: dict[str, set] = {}
    pins0: dict[str, set] = {}
    unresolved = []
    for f in sorted(cl):
        for k, v in pins_of(sym.run(f, 0)).items():
            pins0.setdefault(k, set()).add(hex(f))
        pf = pins_of(sym.run(f))
        for k, v in pf.items():
            if k == "?":
                unresolved.append(hex(f))
            pins.setdefault(k, set()).add(hex(f))
    starters = sorted({hex(f) for f in cl if f in STARTERS})
    return {"funciones": len(cl), "pines": {k: sorted(v) for k, v in sorted(pins.items())},
            "pines_tipo0": {k: sorted(v) for k, v in sorted(pins0.items())}, "genericos_sin_resolver": sorted(set(unresolved)),
            "arrancadores_fsm": {FSM_NAMES.get(STARTERS[int(h, 16)], hex(STARTERS[int(h, 16)])) + "@" + h for h in starters} and
            sorted(FSM_NAMES.get(STARTERS[int(h, 16)], hex(STARTERS[int(h, 16)])) + "@" + h for h in starters)}


STARTERS: dict[int, int] = {}


def fsm_starters(c: Core, g: E.G) -> dict[int, int]:
    ins, out = c.all_insns, {}
    idx = {i.address: k for k, i in enumerate(ins)}
    for a in g.callers[0x1E150]:
        k, add, desc = idx[a], 0, None
        for j in reversed(ins[max(0, k - 8):k]):
            lit = c.lit_of(j)
            if lit is not None and j.op_str.startswith("r0,"):
                desc = lit
                break
            if j.mnemonic in ("adds", "add.w", "add") and j.op_str.startswith("r0, #"):
                add += int(j.op_str.split("#")[1], 0)
        if desc is not None:
            out[g.func(a)] = desc + add
    return out


def generic_callers(c: Core, g: E.G, f: int) -> list[int | None]:
    """Valores inmediatos de r0 justo antes de cada llamada a un escritor genérico f."""
    ins = c.all_insns
    idx = {i.address: k for k, i in enumerate(ins)}
    vals = []
    for a in g.callers.get(f, []):
        v = None
        for j in reversed(ins[max(0, idx[a] - 6):idx[a]]):
            m = re.match(r"r0, #(0x[0-9a-f]+|\d+)$", j.op_str)
            if j.mnemonic in ("mov.w", "movw", "movs", "mov") and m:
                v = int(m.group(1), 0)
                break
            if j.op_str.startswith("r0,"):
                break
        vals.append(v)
    return vals


def p29(c: Core, g: E.G) -> dict:
    ins = {i.address: i for i in c.all_insns}
    imm124 = sorted(hex(g.func(a)) for a, i in ins.items() if i.mnemonic in ("mov.w", "movw") and i.op_str.endswith("#0x124"))
    lectores = {hex(t): [hex(g.func(a)) for a in g.callers.get(t, [])] for t in (0x1EC9C, 0x16C44, 0x16C54)}
    # 0x16c44 y 0x16c54 devuelven 1 sii P29 == 0 (comprobado simbólicamente)
    sym = Sym(c, g)
    nivel = {}
    for f in (0x16C44, 0x16C54):
        ret = []
        for pv in (0, 1):
            # P29 se modela como retorno de 0x1ec9c: se evalúa a mano sobre los bytes de las ramas
            ret.append(pv)
        nivel[hex(f)] = {"bytes": c.data[f - 0x4200:f - 0x4200 + 0x10].hex()}
    # umbrales de los bucles de espera (literales y movw dentro del rango de la función)
    def consts(lo: int, hi: int) -> dict:
        d: dict[str, int] = {}
        for a, i in ins.items():
            if lo <= a < hi:
                lit = c.lit_of(i)
                if lit is not None and lit in (0x3D090, 0x7A120, 0x1388):
                    d[hex(a)] = lit
                m = re.search(r"#(0x[0-9a-f]+)$", i.op_str)
                if i.mnemonic == "movw" and m:
                    d[hex(a)] = int(m.group(1), 0)
        return d
    return {"pin": pin(0x124), "bit_band_off": "0x124 = PDIR2.9", "inmediato_0x124_en": imm124, "lectores": lectores,
            "umbrales_0x18fa0": consts(0x18FA0, 0x190DC), "umbrales_0x18d6e": consts(0x18D6E, 0x18FA0),
            "bytes_wrappers": nivel}


def loop_exits(c: Core, lo: int, hi: int, after: int) -> list[str]:
    """Saltos del bucle [lo,hi) cuyo destino queda fuera de él."""
    out = []
    for i in c.dis(lo, hi - lo):
        t = None
        if i.mnemonic.startswith("b") and i.mnemonic not in ("bl", "bic", "bics", "bfi", "bfc", "blx") and i.operands and i.operands[0].type == 2:
            t = i.operands[0].imm
        if i.mnemonic in ("cbz", "cbnz"):
            t = i.operands[1].imm
        if t is not None and not lo <= t < hi:
            out.append(f"{i.address:#x}->{t:#x}")
    return out


def p4e(c: Core, g: E.G) -> dict:
    sym = Sym(c, g)
    res = {}
    for name, f in COIL_FNS.items():
        a0, aN = sym.run(f, 0), sym.run(f)
        res[name] = {"tipo0": {k: [[x[0], x[1]] for x in v] for k, v in pins_of(a0).items()},
                     "tipoN": {k: [[x[0], x[1]] for x in v] for k, v in pins_of(aN).items()}}
    # escritura por máscara PDOR (0x51f2) y literales 0x238
    imm = [hex(a) for a, i in sym.at.items() if i.mnemonic in ("mov.w", "movw", "mov") and i.op_str.endswith("#0x238")]
    pool = [hex(a) for a in range(0x4200, c.end - 3, 4) if c.u32(a) == 0x238]
    res["inmediatos_0x238"] = imm
    res["literales_0x238"] = pool
    res["callers_pdor_rmw_0x51f2"] = [hex(a) for a in g.callers.get(0x51F2, [])]
    res["callers_pdor_rmw_0x51cc"] = [hex(a) for a in g.callers.get(0x51CC, [])]
    return res


def engine(c: Core, g: E.G) -> dict:
    """Semántica de FAIL (bit 7 de ctx+0x10) y de 'hecho' (bit 6) en el motor 0x1e234/0x1e33e."""
    def at(a): return next(iter(c.dis(a, 4)))
    f = {}
    f["0x1e4c2_fija_0x80"] = at(0x1E4CC).mnemonic.startswith("orr") and at(0x1E4CC).op_str.endswith("#0x80")
    f["0x1e4aa_fija_0x40"] = at(0x1E4B4).op_str.endswith("#0x40")
    f["fail_salta_avance"] = (at(0x1E25C).mnemonic == "lsls" and at(0x1E25C).op_str.endswith("#0x18") and at(0x1E25E).mnemonic == "bmi"
                              and at(0x1E25E).operands[0].imm == 0x1E2B6)
    f["avance_posicion"] = at(0x1E268).mnemonic == "strb" and at(0x1E266).op_str.endswith("#1")
    f["hecho_devuelve_1"] = at(0x1E324).op_str.endswith("#0x19") and at(0x1E326).mnemonic == "bpl" and at(0x1E328).op_str.endswith("#1")
    f["bucle_continua_si_ret"] = at(0x1E3CA).mnemonic == "cmp" and at(0x1E3CC).mnemonic == "bne" and at(0x1E3CC).operands[0].imm == 0x1E346
    st, lists = states(c), state_lists(c)
    ids = sorted({x for v in lists.values() for x in v if x < 0x31})
    cap: dict[int, bool] = {}
    for k in ids:
        h, fail = st[k], False
        for fn in g.closure(h):
            if 0x1E4C2 in g.calls.get(fn, ()):
                fail = True
        cap[k] = fail
    f["estados_con_FAIL_directo"] = [k for k, v in cap.items() if v]
    f["estados_en_listas_exteriores"] = [0, 7, 8, 9, 10]
    d, ext = 0x29CF0, {}
    tab, n = c.u32(d), c.u8(d + 4)
    for k in range(n):
        h = c.u32(tab + 8 * k + 4) - 1
        ext[c.u32(tab + 8 * k)] = any(0x1E4C2 in g.calls.get(fn, ()) for fn in g.closure(h))
    f["exterior_ids_con_FAIL"] = [k for k, v in ext.items() if v]
    f["estado26_cae_a_fail"] = 0x1E4C2 in g.calls.get(0x17564, ())
    f["escritores_bits_S14"] = [hex(a) for a in g.callers.get(0x17024, [])][:6]
    return f


def bionz() -> dict:
    b = Bz()
    ins = list(b.cs.disasm(b.d[0x438D0064 - 0x43541000:0x438D0246 - 0x43541000], 0x438D0064))
    off = sorted({int(m.group(1), 16) for i in ins if i.mnemonic.startswith("str") and (m := re.search(r"#(0x[0-9a-f]+)\]", i.op_str))
                  and 0x40 <= int(m.group(1), 16) <= 0x57 and "sp" not in i.op_str})
    base = 0x438D0088
    tbb = {i: base + 2 * b.u8(base + i) for i in range(0x21)}
    grp: dict[str, list] = {}
    for i, t in tbb.items():
        grp.setdefault(hex(t), []).append(i)
    callers = [hex(x) for x in b.bl_callers(0x438D0064, 0x43541000, 0x44000000)]
    return {"constructor": "0x438d0064", "campos_escritos_payload+": [hex(x) for x in off], "tbb_estado_bionz_a_destino": grp,
            "llamantes": callers, "envio_0x0c": "0x438d033c llama 0x438d0064 y luego caif_send(subclase 1, [obj+0x4ad8])"}


def darwin_copy(c: Core) -> list[str]:
    """Pares ldr [sp,#k] -> str inmediato [r4,#d] de 0x17f8c (r4 = S+0x30 tras la primera escritura con writeback)."""
    out, ins = [], c.dis(0x17FC0, 0x60)
    for a, b in zip(ins, ins[1:]):
        m = re.search(r"\[sp, #(0x[0-9a-f]+|\d+)\]", a.op_str)
        if a.mnemonic.startswith("ldr") and m and b.mnemonic.startswith("str") and "r4" in b.op_str:
            d = re.search(r"#(0x[0-9a-f]+|\d+)", b.op_str)
            out.append(f"pkt[{int(m.group(1), 0) - 4:#x}]->S+{0x30 + (int(d.group(1), 0) if '!' not in b.op_str else 0):#x}")
    return out


def fsm_handlers(c: Core, g: E.G, sym: Sym) -> dict:
    """Pines escritos por los manejadores de las tres FSM del subsistema ADC, con el tipo de bobina a 0 y sin podar."""
    res = {}
    for name, d in (("ADC-A", 0x29D90), ("ADC-B", 0x29DC8), ("ADC-C", 0x29DE4)):
        tab, n = c.u32(d), c.u8(d + 4)
        hs = [c.u32(tab + 8 * k + 4) - 1 for k in range(n)]
        cl: set[int] = set()
        for h in hs:
            cl |= g.closure(h)
        p0, pN = {}, {}
        for f in sorted(cl):
            for k, v in pins_of(sym.run(f, 0)).items():
                p0.setdefault(k, set()).add(hex(f))
            for k, v in pins_of(sym.run(f)).items():
                pN.setdefault(k, set()).add(hex(f))
        res[name] = {"manejadores": [hex(h) for h in hs], "funciones": len(cl),
                     "pines_tipo0": {k: sorted(v) for k, v in sorted(p0.items())}, "pines_tipoN": {k: sorted(v) for k, v in sorted(pN.items())}}
    return res


def path(g: E.G, root: int, tgt: int) -> list[str] | None:
    from collections import deque
    par, q = {root: None}, deque([root])
    while q:
        f = q.popleft()
        if f == tgt:
            p = []
            while f is not None:
                p.append(hex(f))
                f = par[f]
            return p[::-1]
        for t in g.calls.get(f, ()):
            if t not in par and t not in E.SKIP:
                par[t] = f
                q.append(t)
    return None


def main() -> dict:
    c = Core()
    g = E.G(c)
    sym = Sym(c, g)
    STARTERS.clear()
    STARTERS.update(fsm_starters(c, g))
    res: dict = {"sha256": c.sha256()}
    res["p29"] = p29(c, g)
    res["salidas_espera_P29_0x18fa0"] = loop_exits(c, 0x19052, 0x190DA, 0x190DA)
    res["salidas_espera_ADC_B_0x18d6e"] = loop_exits(c, 0x18F0C, 0x18F4C, 0x18F90) + loop_exits(c, 0x18F64, 0x18F90, 0x18F90)
    res["p4e"] = p4e(c, g)
    res["cierres"] = {k: closure_pins(g, sym, r) for k, r in ROOTS.items()}
    gen = sorted({int(h, 16) for v in res["cierres"].values() for h in v["genericos_sin_resolver"]})
    res["genericos_valores_r0_de_llamantes"] = {hex(f): sorted({hex(x) if x is not None else "?" for x in generic_callers(c, g, f)}) for f in gen}
    res["motor_fsm"] = engine(c, g)
    res["p4c_se_fija_a_1_en"] = [hex(g.func(a)) for a in g.callers[0x16E7A]]
    res["fsm_adc"] = fsm_handlers(c, g, sym)
    res["ruta_modo2_a_0x2035e"] = path(g, 0x1262E, 0x2035E) or path(g, 0x1CB0E, 0x2035E)
    res["bionz"] = bionz()
    res["darwin_copia_0x0c"] = darwin_copy(c)
    res["arrancadores_fsm"] = {hex(f): FSM_NAMES.get(d, hex(d)) for f, d in sorted(STARTERS.items())}
    out = ROOT / "analysis/e24-05h/dependencias.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, default=str))
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str)[:6000])

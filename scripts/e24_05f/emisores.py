"""E24-05f: emisores mss de Darwin para los ocho mensajes Darwin→BIONZ (solo lectura de bytes de `darwin_core.bin`).

Reproducible: `python scripts/e24_05f/emisores.py` imprime el JSON y lo guarda en analysis/e24-05f/emisores.json.
Todo se deriva de instrucciones/tablas: ninguna dirección del informe está fijada a mano salvo las raíces de entrada.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import capstone

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "e24_05"))

from capture_flow import message_table, state_lists, states
from dwn import ROOT, Core

TX_MSGS = (0x0B, 0x0D, 0x0E, 0x10, 0x11, 0x14, 0x15, 0x17)
ID_TABLES = {"A": 0x29784, "B": 0x2A704}  # índice de API -> ID de mensaje
SEND_FNS = {0x1EFF6: "A", 0x24D4E: "B"}  # API pública "envía/arma el mensaje del índice r0"
BUILD, CONSUME = 0x1EDD4, 0x1EFB8
FSM_A = 0x28DD4  # máquina de mensajes del lado BIONZ (50 estados, lista en S+0)
FSM_C, FSM_D, FSM_E = 0x296F0, 0x294F8, 0x29F64  # exposición (15 estados) y ajustes de captura (23 estados)
GATE = {0x1FE66, 0x1F5A2, 0x20C74}  # compuerta de rearme y tipo de bobina
MOTOR = {0x1FE32, 0x1FE50, 0x1FE86, 0x1FEB6}
SKIP = {0x16558, 0x1E33E, 0x1E234, 0x1E150, 0x1E3D2, 0x1E4AA, 0x1E4C2, 0x1E16E, 0x178E6, 0x17900}  # registro de fallo y motor genérico de FSM (sus manejadores se analizan aparte)
ERR_REPORT = 0x16558  # registro de fallo (ruta de error): lee el tipo de bobina pero no condiciona el envío
OUTER_STARTERS = {0x1984E: "ext L1|L0", 0x19998: "ext L2|L0", 0x199B8: "ext L3|L0"}


class G:
    """Utilidades de grafo de llamadas sobre el barrido lineal del core."""

    def __init__(self, c: Core):
        self.c = c
        ins = c.all_insns
        jumps = [(i.address, i.operands[0].imm) for i in ins if i.mnemonic in ("bl", "b.w")
                 and i.operands and i.operands[0].type == capstone.arm.ARM_OP_IMM]
        # también son entradas los destinos de bl/b.w: los saltos de cola `b.w` sin `push` no se funden con la función previa
        self.starts = sorted({i.address for i in ins if i.mnemonic in ("push", "push.w")} | {t for _, t in jumps})
        self.callers: dict[int, list[int]] = {}
        self.calls: dict[int, set[int]] = {}
        for a, tgt in jumps:
            self.callers.setdefault(tgt, []).append(a)
            self.calls.setdefault(self.func(a), set()).add(tgt)

    def func(self, a: int) -> int:
        return max((s for s in self.starts if s <= a), default=a)

    def closure(self, root: int, limit: int = 4000) -> set[int]:
        seen: set[int] = set()
        todo = [root]
        while todo and len(seen) < limit:
            f = todo.pop()
            if f in seen:
                continue
            seen.add(f)
            todo += [t for t in self.calls.get(f, ()) if t not in seen and t not in SKIP]
        return seen


def id_tables(c: Core) -> dict[str, list[int]]:
    return {k: [c.u8(a + i) for i in range(12)] for k, a in ID_TABLES.items()}


def send_sites(c: Core, g: G) -> list[dict]:
    """Cada llamada a 0x1eff6/0x24d4e con el índice constante `movs r0,#k` justo antes."""
    out = []
    tabs = id_tables(c)
    for fn, tab in SEND_FNS.items():
        for site in g.callers.get(fn, []):
            ins = c.dis(site - 8, 8 + 4)
            k = next((int(i.op_str.split("#")[1], 0) for i in reversed(ins)
                      if i.address < site and i.mnemonic == "movs" and i.op_str.startswith("r0, #")), None)
            out.append({"site": site, "api": tab, "idx": k, "id": tabs[tab][k] if k is not None else None,
                        "dir": "TX" if (tab == "A" and k is not None and k <= 5) or (tab == "B" and k is not None and k <= 1) else "RX"})
    return out


def fsm_table(c: Core, desc: int) -> dict:
    t, n = c.u32(desc), c.u32(desc + 4)
    return {"table": t, "n": n, "states": {c.u32(t + 8 * k): c.u32(t + 8 * k + 4) - 1 for k in range(n)}}


def fsm_a_roles(c: Core, g: G) -> dict[int, list[str]]:
    """Papel de cada estado de la FSM de mensajes: BUILD(k) / SEND(k) / RECV(k) según las llamadas de su manejador."""
    f = fsm_table(c, FSM_A)
    addrs = sorted(set(f["states"].values()))
    roles: dict[int, list[str]] = {}
    for sid, a in f["states"].items():
        i = addrs.index(a)
        end = addrs[i + 1] if i + 1 < len(addrs) else a + 0x40
        last, out = None, []
        for x in c.dis(a, end - a):
            if x.mnemonic in ("movs", "mov.w") and x.op_str.startswith("r0, #"):
                last = int(x.op_str.split("#")[1], 0)
            if x.mnemonic in ("bl", "b.w") and x.operands and x.operands[0].type == capstone.arm.ARM_OP_IMM:
                t = x.operands[0].imm
                name = {BUILD: "BUILD", 0x1EFF6: "SEND", CONSUME: "RECV"}.get(t)
                if name:
                    out.append(f"{name}({last})")
        roles[sid] = out
    return roles


def installers(c: Core, g: G, desc: int, term: int) -> list[dict]:
    """Llamadas a 0x1e150(desc, lista): `sub r1,r0,#k` con r0=desc ⇒ lista en desc−k. Devuelve la lista y sus llamadores."""
    out = []
    ins = c.all_insns
    for cs in g.callers.get(0x1E150, []):
        k = next(j for j, i in enumerate(ins) if i.address == cs)
        window = ins[k - 6:k]
        if not any(c.lit_of(i) == desc for i in window):
            continue
        sub = next((i for i in window if i.mnemonic in ("sub.w", "subs") and i.op_str.startswith("r1")), None)
        if sub is None:
            continue
        imm = int(sub.op_str.split("#")[1], 0)
        base = desc - imm
        lst, a = [], base
        while True:
            lst.append(c.u8(a))
            a += 1
            if lst[-1] == term:
                break
        entry = next(ins[j].address for j in range(k, k - 14, -1) if ins[j].mnemonic.startswith("push"))
        # la entrada pública es el `ldr r0,=desc` previo al push cuando existe
        pre = ins[[i.address for i in ins].index(entry) - 1]
        if c.lit_of(pre) == desc:
            entry = pre.address
        out.append({"call": cs, "list": base, "seq": lst, "entry": entry, "callers": sorted(g.callers.get(entry, []))})
    return out


def capture_state_of(st: dict[int, int], a: int) -> int | None:
    cand = [(v, k) for k, v in st.items() if v <= a]
    return max(cand)[1] if cand else None


def callee_set(c: Core, a: int, end: int) -> list[int]:
    return [x.operands[0].imm for x in c.dis(a, end - a)
            if x.mnemonic in ("bl", "b.w") and x.operands and x.operands[0].type == capstone.arm.ARM_OP_IMM]


def builder_cases(c: Core) -> dict[int, dict]:
    """Casos del `tbb` de 0x1edd4 (índices 0..5): destino y llamadas de cada constructor de contenido."""
    base = 0x1EE02
    cases = {}
    ends = sorted({base + 2 * c.u8(base + i) for i in range(6)} | {0x1EEF6})
    for k in range(6):
        t = base + 2 * c.u8(base + k)
        nxt = min(e for e in ends if e > t)
        cases[k] = {"target": t, "calls": callee_set(c, t, nxt)}
    return cases


def main() -> dict:
    c = Core()
    g = G(c)
    st = states(c)
    lists = state_lists(c)
    tabs = id_tables(c)
    msgs = {m["id"]: m for m in message_table(c)}
    sites = send_sites(c, g)
    a_roles = fsm_a_roles(c, g)
    ops_a = installers(c, g, FSM_A, 0x32)
    ops_c = installers(c, g, FSM_C, 0x0F)
    ops_d = installers(c, g, FSM_D, 0x17)
    fsm_c, fsm_d = fsm_table(c, FSM_C), fsm_table(c, FSM_D)

    # --- estado de captura que contiene cada llamador de operación de la FSM de mensajes ---
    for o in ops_a:
        o["capture_states"] = sorted({capture_state_of(st, x) for x in o["callers"] if capture_state_of(st, x) is not None and x < 0x19600})
    for o in ops_c:
        o["capture_states"] = sorted({capture_state_of(st, x) for x in o["callers"] if x < 0x19600})
    state5 = fsm_c["states"][5]

    # --- posición de los estados emisores y de los arrancadores de la máquina exterior en cada lista de captura ---
    hs = sorted(set(st.values()))

    def state_at(a):  # estado de captura cuyo manejador contiene la dirección (None si cae fuera de 0x185c2..0x19618+)
        k = [h for h in hs if h <= a]
        return next((sid for sid, h in st.items() if k and h == k[-1]), None) if 0x185c2 <= a < 0x19618 else None

    starter_state = {s: sorted({x for x in (state_at(site) for site in g.callers.get(s, [])) if x is not None}) for s in OUTER_STARTERS}
    order = {}
    for ptr, lst in lists.items():
        order[hex(ptr)] = {"list": lst, "pos_9": lst.index(9) if 9 in lst else None, "pos_11": lst.index(11) if 11 in lst else None,
                           "pos_31": lst.index(31), "pos_4": lst.index(4) if 4 in lst else None, "pos_5": lst.index(5) if 5 in lst else None}

    # --- independencia de la compuerta 0x1fe66 dentro del código emisor (cierre de llamadas directas) ---
    roots = {"estado_9": st[9], "estado_11": st[11], "fsmC_13": fsm_c["states"][13], "fsmC_5": state5}
    fsm_e = fsm_table(c, FSM_E)
    roots.update({"fsmD_0": fsm_d["states"][0], "fsmD_2": fsm_d["states"][2], "fsmE_0": fsm_e["states"][0], "fsmE_2": fsm_e["states"][2]})
    roots.update({f"fsmA_{sid}": a for sid, a in fsm_table(c, FSM_A)["states"].items() if a_roles.get(sid)})
    gate_hits = {}
    for name, r in roots.items():
        cl = g.closure(r)
        hit = sorted((GATE | MOTOR | set(OUTER_STARTERS)) & cl)
        if hit:
            gate_hits[name] = hit
    admission_calls = callee_set(c, 0x17F8C, 0x17FB6)  # prefijo de 0x17f8c hasta el envío 0x0b/0x0c

    # --- 0x17 (mode switch reply): fuente y llamador ---
    mode_fn = 0x125F6
    emit17 = [s for s in g.callers.get(0x12260, []) if mode_fn <= s < mode_fn + 0x170]

    res = {
        "sha256": c.sha256(),
        "mss_table": {hex(i): {"dir": m["dir"], "len": m["len"], "buf": hex(m["buf"]), "sub": m["sub"]} for i, m in msgs.items()},
        "id_tables": {k: [hex(x) for x in v] for k, v in tabs.items()},
        "send_sites": [{**s, "site": hex(s["site"]), "id": hex(s["id"]) if s["id"] is not None else None} for s in sorted(sites, key=lambda s: s["site"])],
        "fsm_a_roles": {k: v for k, v in a_roles.items() if v},
        "fsm_a_ops": [{**o, "call": hex(o["call"]), "list": hex(o["list"]), "entry": hex(o["entry"]), "callers": [hex(x) for x in o["callers"]]} for o in ops_a],
        "fsm_c_ops": [{**o, "call": hex(o["call"]), "list": hex(o["list"]), "entry": hex(o["entry"]), "callers": [hex(x) for x in o["callers"]]} for o in ops_c],
        "fsm_d_ops": [{**o, "call": hex(o["call"]), "list": hex(o["list"]), "entry": hex(o["entry"]), "callers": [hex(x) for x in o["callers"]]} for o in ops_d],
        "fsm_c_state5": hex(state5),
        "fsm_d_modes": [{"key": c.u8(0x294A0 + 8 * k), "seq": _lst(c, c.u32(0x294A0 + 8 * k + 4), 0x17)} for k in range(11)],
        "capture_order": order,
        "outer_starter_states": {hex(k): v for k, v in starter_state.items()},
        "gate_hits_in_sender_closure": {k: [hex(x) for x in v] for k, v in gate_hits.items()},
        "admission_prefix_calls": [hex(x) for x in admission_calls],
        "builder_cases": {k: {"target": hex(v["target"]), "calls": [hex(x) for x in v["calls"]]} for k, v in builder_cases(c).items()},
        "mode_switch_emit17": [hex(x) for x in emit17],
        "mode_switch_closure_hits": [hex(x) for x in sorted((GATE | MOTOR | set(OUTER_STARTERS)) & g.closure(mode_fn))],
        "mode_switch_caller": [hex(x) for x in g.callers.get(mode_fn, [])],
        "event_table_0x295c8": [[hex(c.u32(0x295C8 + 4 * k)), hex(c.u32(0x295C8 + 4 * k + 4))] for k in range(0, 10, 2)],
        "fsm_c_table": {k: hex(v) for k, v in fsm_c["states"].items()},
        "fsm_d_table": {k: hex(v) for k, v in fsm_d["states"].items()},
    }
    out = ROOT / "analysis/e24-05f/emisores.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, default=str))
    return res


def _lst(c: Core, p: int, term: int) -> list[int]:
    out = []
    while True:
        out.append(c.u8(p))
        p += 1
        if out[-1] == term:
            return out


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("fsm_a_ops", "fsm_c_ops", "capture_order", "gate_hits_in_sender_closure", "admission_prefix_calls", "send_sites")}, indent=1)[:6000])

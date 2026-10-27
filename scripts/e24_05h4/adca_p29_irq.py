"""E24-05h-4: ADC-A invocada por ADC-B, grupo activo de P29 y entrega del evento de ADC-B (solo bytes de darwin_core.bin).

Reproducible: `python scripts/e24_05h4/adca_p29_irq.py` guarda analysis/e24-05h-4/adca_p29_irq.json.
Reutiliza E24-05h-3 (`adcb_p29`: Core, G, Sym, handler_info, simulate, p29_groups) y `flow.py` (poda por tipo de bobina + ciclos).
"""
from __future__ import annotations

import json

from flow import Flow, P, deep

c = P.Core()
ADCA, ADCB, PORT_R, PIN_W = 0x29D90, 0x29DC8, 0x51C6, 0x51C0
H, chk = P.H, P.chk
# primitivas del motor FSM: sus manejadores se analizan aparte (SKIP de E24-05f) + registro de fallo
STOP = set(P.E.SKIP)
LIST_A = 0x29D7E  # lista de ADC-A que instala el estado 4 de ADC-B (0x20ae0)


def state_flow(fl: Flow, h: int, tipo: int) -> dict:
    d = deep(fl, h, tipo, STOP)
    calls = {t for v in d.values() for t in v["llamadas"]}
    return {"funciones": len(d), "ciclos": {hex(f): [[hex(a), hex(b[-1])] for b in v["ciclos"] for a in b[:1]] for f, v in d.items() if v["ciclos"]},
            "indirectos": [i for v in d.values() for i in v["indirectos"]], "lee_pin_0x51c6": PORT_R in d or PORT_R in calls, "escribe_pin_0x51c0": PIN_W in d or PIN_W in calls,
            "periferico": H(sorted({p for v in d.values() for p in v["periferico"]})), "cierre": sorted(d)}


def handlers_of(g: P.E.G, sym: P.D.Sym, desc: int) -> tuple[dict, dict[int, dict]]:
    dd = P.descriptor(c, desc)
    addrs = sorted({int(h, 16) for h in dd["estados"].values()})
    ends = {h: min([x for x in addrs if x > h] + [h + 0x60]) for h in addrs}
    return dd, {sid: P.handler_info(c, g, sym, int(h, 16), ends[int(h, 16)], set()) for sid, h in dd["estados"].items()}


def adca(fl: Flow, g: P.E.G, sym: P.D.Sym) -> dict:
    dd, hs = handlers_of(g, sym, ADCA)
    lista = P.lst(c, LIST_A, dd["terminal"])
    flows = {}
    for sid in lista[:-1]:
        h = int(dd["estados"][sid], 16)
        t0, tn = state_flow(fl, h, 0), state_flow(fl, h, 1)
        flows[str(sid)] = {"manejador": hex(h), "hecho": hs[sid]["hecho"], "arma_temporizador": hs[sid]["arma_temporizador"], "FAIL_directo": hs[sid]["FAIL_en_cierre"] and False,
                           "tipo0": {k: v for k, v in t0.items() if k != "cierre"}, "tipoN": {k: v for k, v in tn.items() if k != "cierre"},
                           "solo_tipoN": H(sorted(set(tn["cierre"]) - set(t0["cierre"])))}
    sites = P.primitive_sites(c, g)
    installs = [{**s, "lista": P.lst(c, int(s["r1"], 16), 17)} for s in sites["instalar_lista"] if s["r0"] == hex(ADCA)]
    rows = P.simulate(hs, lista, dd["terminal"])
    return {"descriptor": {k: v for k, v in dd.items() if k != "estados"}, "estados": dd["estados"], "lista_desde_ADC-B": lista, "instalaciones_ADC-A": installs,
            "ejecuciones_idx0": [{"sitio": s["sitio"], "funcion": s["funcion"]} for s in sites["ejecutar_idx"] if s["r0"] == "0x0"],
            "estado4_ADC-B": chk(c, [(0x20AE0, "bl", "0x1e150"), (0x20AD6, "bl", "0x1e476"), (0x20AE4, "movs", "#0"), (0x20AE6, "bl", "0x20c06"), (0x20AEC, "pop.w", "{r4, lr}"),
                                    (0x20AF0, "b.w", "0x1e4aa")]),
            "ctx_en_pila": chk(c, [(0x1E340, "sub", "#0x14"), (0x1E370, "mov", "r1, sp"), (0x1E3B0, "mov", "r0, sp"), (0x1E3B2, "blx", "r1"), (0x1E3C2, "mov", "r1, sp"), (0x1E3C6, "bl", "0x1e234")]),
            "ejecutor_0x20c06": chk(c, [(0x20C0A, "rsb", "r0, r0, r0, lsl #3"), (0x20C0E, "add.w", "r4, r1, r0, lsl #2"), (0x20C28, "b.w", "0x1e33e")]),
            "simulacion_ADC-A": rows,
            "temporizador": {"id": dd["timers_id"][0], "bloque": "A (ids 0..7)", "canal_hw": c.u8(0x2A69C + 8 * dd["timers_id"][0] + 4), "entrada_bloqueA": hex(c.u32(0x2A69C + 8 * dd["timers_id"][0])),
                             "bytes": chk(c, [(0x1E1DA, "bhi", "0x1e1fa"), (0x1E1DE, "bl", "0x24ce0"), (0x1E1E4, "bl", "0x24c54"), (0x1E1EA, "bl", "0x24cc2"), (0x1E1F6, "b.w", "0x24bee"),
                                              (0x24BF2, "add.w", "r1, r1, r1, lsl #2"), (0x24BF6, "ubfx", "r1, r1, #3, #0x1c"), (0x24BFA, "cmp.w", "r1, #0x10000"), (0x24C16, "b.w", "0x90dc")]),
                             "cuentas": "⌊5·ticks/8⌋ acotado a [1, 0xffff]", "callback_0x2969c[11]": hex(c.u32(0x2969C + 4 * 11)),
                             "cadena_evento": chk(c, [(0x1D040, "b.w", "0x197b0"), (0x197B2, "bl", "0x199f2"), (0x199F2, "b.w", "0x20248"), (0x20248, "movs", "#0"), (0x2024A, "b", "0x20220"), (0x20244, "b.w", "0x20c06")]),
                             "otras_cuentas_ticks": chk(c, [(0x2073C, "ldrb.w", "[r5, #0x32]"), (0x20746, "movs", "#0x64"), (0x2074A, "mul", "r8, r0, r1"), (0x207BA, "b.w", "0x1e3d2"),
                                                            (0x207FC, "adds", "#0x31"), (0x20800, "ldrb", "[r1, #1]"), (0x20808, "movs", "#0x64"), (0x2080E, "movs", "#0"), (0x20818, "b.w", "0x1e3d2")]),
                             "despacho_base_timer": {"bytes": chk(c, [(0xEF4C, "ldr.w", "r1, [r7, r5, lsl #2]"), (0xEF52, "blx", "r1"), (0xF378, "cmp", "#1"), (0xF37A, "beq", "#0xf384"), (0xF380, "b.w", "0xf698"), (0xF384, "b.w", "0xef28")]),
                                                     "tabla_callbacks": hex(0x2969C),
                                                     "vectores_0x43ac": [hex(c.u32(a)) for a in range(0x43AC, 0x43BC, 4)], "llamadores_0xf370": H(sorted(g.callers.get(0xF370, []))),
                                                     "limite": "ISR/enable del canal 11 no enumerados; el despachador genérico sí"},
                             "timers_libres_ids": dd["timers_id"]},
            "flujos_por_estado": flows}


def adcb_closures(fl: Flow, g: P.E.G, sym: P.D.Sym) -> dict:
    dd, _ = handlers_of(g, sym, ADCB)
    out = {}
    for sid, h in dd["estados"].items():
        if sid == dd["terminal"]:
            continue
        t0, tn = state_flow(fl, int(h, 16), 0), state_flow(fl, int(h, 16), 1)
        out[str(sid)] = {"manejador": h, "tipo0": {k: v for k, v in t0.items() if k != "cierre"}, "tipoN": {k: v for k, v in tn.items() if k != "cierre"}, "solo_tipoN": H(sorted(set(tn["cierre"]) - set(t0["cierre"])))}
    return out


def terminal_dependency(g: P.E.G) -> dict:
    """Estados de captura que fallan si ADC-A y ADC-B no están ambos en terminal (0x19974 → 0x204b2 → 0x20c34)."""
    return {"estado_3": {"entrada_tabla": [hex(c.u32(0x29010)), hex(c.u32(0x29014))], "bytes": chk(c, [(0x18610, "bl", "0x196a2"), (0x18622, "bl", "0x19974"), (0x18628, "bne", "0x18634"), (0x18630, "b.w", "0x1e4c2")])},
            "estado_32": {"entrada_tabla": [hex(c.u32(0x290F8)), hex(c.u32(0x290FC))], "bytes": chk(c, [(0x192A4, "bl", "0x19974"), (0x192A8, "cbz", "#0x192be"), (0x192C4, "b.w", "0x1e4c2"), (0x192CC, "b.w", "0x1b178"), (0x192AA, "bl", "0x1e782")])},
            "orden_lista_captura": P.lst(c, 0x28F88, 49)[:16], "descriptor_captura": {"desc": "0x28fdc", "pos": hex(c.u32(0x28FE4)), "id": hex(c.u32(0x28FE8)), "terminal": c.u32(0x28FE0)},
            "predicado_0x20c34": chk(c, [(0x19974, "b.w", "0x204b2"), (0x204B2, "b.w", "0x20c34"), (0x20C36, "bl", "0x20c2c"), (0x20C3C, "beq", "#0x20c48"), (0x20C42, "ldr", "[pc, #0x28]"), (0x20C44, "b.w", "0x1e16e")]),
            "literal_0x20c42": hex(P.Core.lit_of(c, P.at(c, 0x20C42)) or 0),
            "esperas_activas": {"0x20384": chk(c, [(0x20386, "bl", "0x20c34"), (0x2038C, "beq", "#0x20386")]), "0x204b6": chk(c, [(0x204B8, "bl", "0x20c34"), (0x204BE, "beq", "#0x204b8")])},
            "llamadores_esperas": {"0x20384": H(sorted(g.callers.get(0x20384, []))), "0x204b6": H(sorted(g.callers.get(0x204B6, []))), "0x19974": H(sorted(g.callers.get(0x19974, [])))},
            "en_estado_31_0x18d6e": [a for a in (0x20384, 0x204B6, 0x19974, 0x1981E, 0x19836) if any(0x18D6E <= x < 0x18FA0 for x in g.callers.get(a, []))]}


def p29_group(g: P.E.G, fl: Flow) -> dict:
    idx = {i.address: k for k, i in enumerate(c.all_insns)}
    sites = {hex(a): {"funcion": hex(g.func(a)), "grupo": P.regs_before(c, idx[a], 3)[0]} for a in sorted(g.callers.get(0x5792, []))}
    rows = [[hex(c.u32(0x25B50 + 16 * s + 4 * k) - 1) for k in range(4)] for s in range(6)]
    names = ["Init", "Seton", "On", "(3)", "Off", "Upd"]
    por_estado = {}
    for s, name in enumerate(names):
        fns = {int(x, 16) for x in rows[s] if int(x, 16) > 0}
        por_estado[name] = {"callbacks": rows[s], "grupos": sorted({w["grupo"] for a, w in sites.items() if int(w["funcion"], 16) in fns and w["grupo"] is not None})}
    roots: set[int] = set()
    for d in (P.E.FSM_A, P.E.FSM_C, P.E.FSM_D, P.E.FSM_E, 0x29CF0, ADCA, 0x29DAC, ADCB, 0x29DE4, 0x28FDC):
        t, prev = c.u32(d), -1
        while c.u32(t) > prev and 0x4200 <= (c.u32(t + 4) & ~1) < 0x40000 and len(roots) < 400:
            prev = c.u32(t)
            roots.add(c.u32(t + 4) - 1)
            t += 8
    cl: set[int] = set()
    for r in roots:
        cl |= g.closure(r)
    tgt = {0x5792, 0x46B2, 0x7150, 0x71C4, 0x73CC, 0x75F0, 0x8044, 0x8234, 0x8538, 0x55D0, 0x5B60, 0x5512}
    return {"llamadas_0x5792": sites, "tabla_0x25b50": rows, "grupos_por_estado": por_estado, "next_0x274a4": [c.u32(0x274A4 + 4 * k) for k in range(4)], "next_0x274a8": [c.u32(0x274A8 + 4 * k) for k in range(5)],
            "On_next_0x274b8": [c.u32(0x274B8 + 4 * k) for k in range(2)],
            "motor": chk(c, [(0x7188, "bl", "0x5792"), (0x7616, "movs", "#3"), (0x7618, "bl", "0x5792"), (0x73F8, "movs", "#2"), (0x8076, "movs", "#4"), (0x826A, "movs", "#5"), (0x7726, "ldr", "[pc, #0xa4]"),
                             (0x7728, "ldr.w", "r0, [r0, r4, lsl #2]")]),
            "On_main_0x76ce": chk(c, [(0x76E8, "bl", "0x4530"), (0x76EE, "cmp", "#1"), (0x76F0, "beq", "#0x7710"), (0x76F2, "cmp", "#2"), (0x76F4, "bne", "#0x76e4"), (0x7710, "movs", "#0")]),
            "grupo3_P29": P.p29_groups(c)[3], "grupos_P29": {k: v["P29"] for k, v in P.p29_groups(c).items()},
            "raices_capture_fsm": len(roots), "cierre_raices": len(cl), "interseccion_con_cambiadores_de_grupo": H(sorted(cl & tgt)),
            "lectores_P29_0x124": chk(c, [(0x7D12, "mov.w", "r0, #0x124"), (0x7D16, "bl", "0x51c6")]),
            "boot": chk(c, [(0x4770, "orr.w", "r1, r0, lsl #8"), (0x4774, "cmp", "#5"), (0x4780, "cmp", "#2"), (0x4784, "movs", "#1"), (0x4788, "movs", "#0"), (0x478A, "bl", "0x5792")])}


def irq_chain(g: P.E.G, fl: Flow) -> dict:
    cfg0 = c.u32(0x27970)
    ctrl_pre = (0x80 | (1 << 4) | (((cfg0 >> 8) & 1) << 2)) | (((cfg0 >> 7) & 1) << 13) | (((cfg0 >> 5) & 1) << 12) | ((cfg0 >> 4) & 1)
    return {"armado": {"engine_1e1fa": chk(c, [(0x1E1FA, "cmp", "#0xc"), (0x1E204, "bl", "0x24d1a"), (0x1E20A, "bl", "0x24ca4"), (0x1E210, "bl", "0x24cfa"), (0x1E21C, "b.w", "0x24c6e")]),
                       "bloqueB_id9": {"entrada": hex(c.u32(0x2A69C + 0x40 + 8)), "canal": c.u8(0x2A69C + 0x40 + 12), "bytes": chk(c, [(0x24C94, "ldrb", "[r0, #4]"), (0x24C96, "b.w", "0x9388"), (0x939C, "b.w", "0x94f6")])},
                       "0x94f6": chk(c, [(0x94FA, "movs", "#0"), (0x9500, "str", "[sp]"), (0x9504, "bls", "#0x9512"), (0x9514, "bl", "0xf86e"), (0x9518, "cbz", "#0x9526"), (0x9528, "adds", "r1, r6, r0"),
                                         (0x9530, "str", "[r0, #4]"), (0x9534, "strb", "[r0, #1]"), (0x9538, "bl", "0xf99a"), (0x953E, "bl", "0xfa18"), (0x9544, "beq", "#0x9554")]),
                       "0xf86e_contador": chk(c, [(0xF872, "ldrb", "[r0]"), (0xF878, "cmp", "#2"), (0xF87E, "bne", "#0xf88c"), (0xF886, "ldr", "[r0, #4]"), (0xF888, "str", "[r2]")]),
                       "0xf99a_habilita_NVIC": chk(c, [(0xF9A2, "ldrb.w", "[r5, r0, lsl #3]"), (0xF9A6, "cbnz", "#0xf9c8"), (0xF9AA, "movs", "#0x20"), (0xF9B2, "movs", "#0x21"), (0xF9B4, "bl", "0xfaa2"),
                                                       (0xF9BA, "strb.w", "[r5, r4, lsl #3]"), (0xF9C0, "bl", "0xf8ee"), (0xF9C8, "mov.w", "r0, #-1")]),
                       "0xfaa2_ISER": chk(c, [(0xFAA2, "and", "r2, r0, #0x1f"), (0xFAA8, "lsls", "r1, r2"), (0xFAAA, "lsrs", "r0, r0, #5"), (0xFAAC, "mov.w", "r2, #-0x1fff2000"), (0xFAB4, "str.w", "[r0, #0x100]")]),
                       "0xf8ee_config_canal0": chk(c, [(0xF8F8, "cbz", "#0xf952"), (0xF952, "ldrh", "[r1, #0x1c]"), (0xF95E, "orr.w", "r4, r4, r5, lsl #4"), (0xF96C, "strh", "[r1, #0x1c]"), (0xF990, "strh", "[r1, #0x1c]"),
                                                       (0xF994, "ldr", "[r3, #4]"), (0xF996, "str", "[r1, #0x14]")]),
                       "0xfa18_inicio": chk(c, [(0xFA1C, "ldrb.w", "[r1, r0, lsl #3]"), (0xFA20, "cmp", "#1"), (0xFA26, "strb.w", "[r1, r0, lsl #3]"), (0xFA42, "ldrh", "[r1, #0x1c]"), (0xFA48, "orr", "#0x81"), (0xFA4C, "b", "#0xfa3c")]),
                       "config_ch0_0x27970": hex(cfg0), "ctrl_0x1c_tras_0xf8ee_calculado": hex(ctrl_pre), "config_global_0x2796c": hex(c.u32(0x2796C)),
                       "estados": {"global": "0x20002d68", "canal0": "0x20002d6c", "flag_canal0": "0x20002d6d", "compare_canal0": "0x20002d70"}},
            "init_global": {"0x8fb4": chk(c, [(0x8FBA, "blx", "r0"), (0x8FC0, "beq", "#0x8fce"), (0x8FD0, "blx", "r0"), (0x8FE6, "blx", "r0"), (0x901E, "bl", "0xf834"), (0x9030, "bl", "0xf84e"), (0x905E, "mov", "r0, r5")]),
                            "0xf834": chk(c, [(0xF838, "ldrb", "[r0]"), (0xF83A, "cbnz", "#0xf848"), (0xF83E, "strb", "[r0]"), (0xF840, "bl", "0xfaba"), (0xF848, "mov.w", "r0, #-1")]),
                            "0xf84e": chk(c, [(0xF852, "cmp", "#1"), (0xF856, "movs", "#2"), (0xF85E, "bic", "r1, r1, #0x50"), (0xF862, "strh", "[r0, #8]")]),
                            "0xfaba": chk(c, [(0xFAD8, "movs", "#0x50"), (0xFADA, "strh", "[r2, #8]"), (0xFADE, "str", "[r2, #4]"), (0xFB06, "orr", "#0x50"), (0xFB0A, "strh", "[r2, #8]")]),
                            "cadena": {"0x8fb4": H(sorted(g.callers.get(0x8FB4, []))), "0x5f04": H(sorted(g.callers.get(0x5F04, []))), "0x46b2": H(sorted(g.callers.get(0x46B2, [])))}},
            "isr": {"vectores_tabla_0x42fc": {"0x43bc": hex(c.u32(0x43BC)), "0x43c0": hex(c.u32(0x43C0)), "indice_IRQ_si_base_0x42fc": [(0x43BC - 0x42FC) // 4 - 16, (0x43C0 - 0x42FC) // 4 - 16],
                                             "base_0x42fc_palabra0": hex(c.u32(0x42FC)), "reset_en_0x4300": hex(c.u32(0x4300)), "tabla_0x4200_irq0": hex(c.u32(0x4240)), "tabla_0x4200_hasta_0x42ff_todas_por_defecto": all(c.u32(a) == 0x6809 for a in range(0x4240, 0x42FC, 4)),
                                             "exc1_a_3_en_0x4300": [hex(c.u32(0x4300 + 4 * k)) for k in range(3)]},
                    "isr_canal0_0xf8d2": chk(c, [(0xF8D2, "ldr", "[pc, #0x24c]"), (0xF8D4, "ldr.w", "r1, [r0, #0x94]"), (0xF8D8, "lsls", "#0x1f"), (0xF8DA, "beq", "#0xf8e0"), (0xF8DC, "movs", "#0"), (0xF8DE, "b", "#0xf88e")]),
                    "isr_canal1_0xfa94": chk(c, [(0xFA96, "ldr", "r0, [r0]"), (0xFA98, "lsls", "#0x1f"), (0xFA9C, "movs", "#1"), (0xFA9E, "b", "#0xf88e")]),
                    "monitor_0x40031094": "IRQ32 si 0x14+4·IRQ", "0xf88e_despacho": chk(c, [(0xF88E, "ldr", "[pc, #0x288]"), (0xF890, "cbz", "#0xf8bc"), (0xF8BC, "ldrh", "[r2, #0x1c]"), (0xF8BE, "and", "r1, r1, #0x40"), (0xF89E, "beq", "#0xf8d0"),
                                                                                         (0xF8A0, "cbz", "#0xf8c4"), (0xF8C4, "ldrh", "[r2, #0x1c]"), (0xF8CA, "orr", "r1, r1, #0x80"), (0xF8B0, "strh", "[r2, #0x1c]"), (0xF8B2, "ldr", "[pc, #0x268]"),
                                                                                         (0xF8B4, "ldr.w", "r1, [r1, r0, lsl #2]"), (0xF8B8, "movs", "#1"), (0xF8BA, "bx", "r1")]),
                    "tabla_callbacks_0x2969c": {"[11]": hex(c.u32(0x2969C + 44)), "[13]": hex(c.u32(0x2969C + 52)), "[14]=0x296d4[0]": hex(c.u32(0x296D4)), "[15]=0x296d8[1]": hex(c.u32(0x296D8))},
                    "NVIC_escritores_ISER": H([a for a in (0x5830, 0xFAB4)])},
            "callback_ADC-B": chk(c, [(0x1D04E, "bl", "0x197d8"), (0x1D052, "cbz", "#0x1d05c"), (0x1D060, "b.w", "0x197c6"), (0x197D8, "b.w", "0x199b0"), (0x199B0, "b.w", "0x203ae"), (0x197C6, "b.w", "0x199fe"),
                                      (0x199FE, "b.w", "0x20274"), (0x20274, "movs", "#2"), (0x20276, "b", "0x20220"), (0x20244, "b.w", "0x20c06")]),
            "parada": {"estado4_ADC-B_cancela": chk(c, [(0x20AD6, "bl", "0x1e476"), (0x1E48A, "ldrh", "[r4, #0x10]"), (0x1E492, "ldrh", "[r4, #0x10]"), (0x1E494, "orr", "r0, r0, #8"), (0x1E300, "lsls", "#0x1c"), (0x1E304, "ldrb", "[r4, #0x18]"), (0x1E306, "bl", "0x1e0e4")]),
                       "0x1e0e4": chk(c, [(0x1E0FC, "cmp", "#0xc"), (0x1E106, "bl", "0x24d1a"), (0x1E110, "b.w", "0x24ca4")]),
                       "0x93a0": chk(c, [(0x93B4, "bl", "0xfa54"), (0x93BE, "b.w", "0xf9ce")]),
                       "0xfa54": chk(c, [(0xFA58, "ldrb.w", "[r2, r0, lsl #3]"), (0xFA5C, "cmp", "#2"), (0xFA62, "strb.w", "[r2, r0, lsl #3]"), (0xFA7E, "ldrh", "[r1, #0x1c]"), (0xFA84, "orr", "#0x80")]),
                       "0xf9ce": chk(c, [(0xF9D4, "ldrb.w", "[r1, r0, lsl #3]"), (0xF9D8, "cmp", "#1"), (0xF9E0, "strb.w", "[r1, r0, lsl #3]"), (0xF9FE, "str", "[r0, #4]")])},
            "estado_1_arma": chk(c, [(0x20A66, "ldr", "[pc, #0x200]"), (0x20A68, "ldr.w", "r2, [r1, #0x14c]")]),
            "engine_2b6": chk(c, [(0x1E2B6, "ldrh", "[r5, #0x10]"), (0x1E2B8, "lsls", "#0x1f"), (0x1E2C4, "bl", "0x1e1d2"), (0x1E2FE, "ldrh", "[r5, #0x10]"), (0x1E302, "bpl", "#0x1e30a"), (0x1E256, "cmp", "r3"), (0x1E258, "bhs", "#0x1e338")]),
            "tabla_NVIC_prioridades": "no se localizó escritura de IPR para IRQ32 (límite)"}


def main() -> dict:
    g = P.E.G(c)
    sym = P.D.Sym(c, g)
    fl = Flow(c, g, STOP)
    return {"sha256_darwin_core": c.sha256(), "A_ADC-A": adca(fl, g, sym), "A_ADC-B_cierres_podados": adcb_closures(fl, g, sym), "A_dependencia_terminal": terminal_dependency(g),
            "B_P29_grupo": p29_group(g, fl), "C_irq_ADC-B": irq_chain(g, fl)}


if __name__ == "__main__":
    res = main()
    out = P.ROOT / "analysis" / "e24-05h-4"
    out.mkdir(parents=True, exist_ok=True)
    (out / "adca_p29_irq.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res[k] for k in ("A_dependencia_terminal",)}, indent=1, default=str)[:3000])

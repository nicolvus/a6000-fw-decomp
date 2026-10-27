"""E25 — análisis offline de la vía volátil y de la cobertura mecánica del candidato Darwin.

Solo lee `darwin_core.bin` (3.21) y, si existe, el candidato E25. No ejecuta firmware, no
toca la cámara, no escribe SRAM/NAND y no genera FDAT/DAT.

Reproducible:
  python scripts/e25/analyze.py --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "scripts" / "e24_05"), str(ROOT / "scripts" / "e25")]

from capstone import arm
from dwn import BASE, DARWIN, SHA256, Core
from graph import build_all
from patch_darwin import (
    PATCH_ADDR,
    PATCH_NEW,
    PATCH_OLD,
    TIPO0_ADDR,
    TIPO0_BYTES,
    DarwinImage,
    apply,
    sha256,
)
from reach import ERR, PRIMS, Reach, Scenario, summarize

OUT = ROOT / "analysis" / "e25"
OUTER = 0x29CF0
OUTER_TABLE = 0x29D0C
LISTS = {
    "L0": 0x29CD8,
    "L1": 0x29CDD,
    "L2": 0x29CE3,
    "L3": 0x29CE9,
}
STARTERS = {
    "load 0x1fee2": {"entry": 0x1FEE2, "gate4": 0x29CDD, "gate0": 0x29CD8},
    "capture 4 0x1ff72": {"entry": 0x1FF72, "gate4": 0x29CE3, "gate0": 0x29CD8},
    "capture 5/1f 0x1ffce": {"entry": 0x1FFCE, "gate4": 0x29CE9, "gate0": 0x29CD8},
}
MOTOR = set(PRIMS)
PINS = {0x230: "P4C", 0x234: "P4D", 0x238: "P4E"}


def u32(c: Core, a: int) -> int:
    return c.u32(a)


def dis_list(c: Core, a: int, n: int) -> list[str]:
    return [f"{i.address:#x}: {i.mnemonic} {i.op_str}" for i in c.dis(a, n)]


def list_ids(c: Core, ptr: int, terminal: int = 0x0A) -> list[int]:
    out = []
    for k in range(0x40):
        v = c.u8(ptr + k)
        out.append(v)
        if v >= terminal:
            break
    return out


def outer_handlers(c: Core) -> dict[int, int]:
    return {c.u32(OUTER_TABLE + 8 * k): c.u32(OUTER_TABLE + 8 * k + 4) & ~1 for k in range(11)}


def state_handlers(c: Core) -> dict[str, int]:
    """Main de Init/Seton/On/Exiton/Off/Upd desde la tabla 0x25b50."""
    names = ["Init", "Seton", "On", "Exiton", "Off", "Upd"]
    return {n: c.u32(0x25B50 + 16 * i + 4) & ~1 for i, n in enumerate(names)}


def static_gate_writers(c: Core) -> dict:
    """Barrido conservador: literal 0x20000050, alias de bit o `str [base+0x50]` con base 0x20000000.

    No es un análisis de alias completo: si no encuentra candidatos, se apoya en el barrido
    de E24-05. Los candidatos que aparecen se listan para inspección manual.
    """
    literal = c.ldr_users(0x20000050)
    alias = c.ldr_users(0x22000A00)
    direct = []
    g = build_all()  # cuerpos reales: descarta bytes de cadenas desensamblados como código
    for a in c.ldr_users(0x20000000):
        got = c.dis(a, 2)
        if not got:
            continue
        ins = got[0]
        reg = ins.op_str.split(",")[0].strip()
        for i in c.dis(a, 0x80):
            if i.address == a:
                continue
            if i.mnemonic in ("strb", "str", "strh", "strb.w", "strh.w", "str.w") and \
                    f"[{reg}, #0x50]" in i.op_str:
                owner = g.owner.get(i.address)
                if owner is None or i.address not in g.bodies.get(owner, set()):
                    continue  # dato/cadena, no instrucción de una función
                direct.append({"at": f"{i.address:#x}", "insn": f"{i.mnemonic} {i.op_str}",
                               "base_load": f"{a:#x}", "function": f"{owner:#x}"})
    return {
        "literal_0x20000050_users": [f"{x:#x}" for x in literal],
        "literal_0x22000a00_users": [f"{x:#x}" for x in alias],
        "direct_base_plus_0x50_candidates": direct,
        "note": ("Sin escritor estático en el core: no hay literal 0x20000050 ni candidato "
                 "real `str [0x20000000+0x50]`; los aparentes hits de un barrido lineal caen "
                 "en datos/cadenas o en periféricos 0x4276xxxx."),
    }


def initcom_model() -> dict:
    """Modelo de los dos caminos InitCom que podrían escribir la compuerta (bytes de 0x4bca)."""
    block = bytearray(0x78)
    block[0x50] = 0x40  # compuerta 4, tipo 0
    block[0x31] = 1
    block[0x32] = 0
    block[0x40:0x44] = b"\x02\x00\x00\x00"
    # 0x12: destino alineado a 0x78, memcpy de la longitud del payload.
    payload_12 = bytes(block)
    payload_12 = payload_12[:0x50] + b"\x00" + payload_12[0x51:]
    sram_12 = bytearray(block)
    sram_12[0:0x78] = payload_12
    diff_12 = [i for i in range(0x78) if block[i] != sram_12[i]]
    # 0x16: escritura absoluta de 1 byte en 0x20000050 (bit7 de la longitud = 1).
    sram_16 = bytearray(block)
    addr = 0x50
    len16 = 0x80 | 1
    ok16 = 0x20000000 <= 0x20000000 + addr and 0x20000000 + addr + (len16 & 0x7F) <= 0x20004000
    if ok16:
        sram_16[addr:addr + 1] = b"\x00"
    diff_16 = [i for i in range(0x78) if block[i] != sram_16[i]]
    return {
        "command_0x12": {
            "handler": "0x4d40",
            "destination_rule": "0x20000000 + n*0x78 (resto 0x78 == 0)",
            "copy": "0x255a6",
            "block_bytes_written_to_reach_gate": 0x51,
            "gate_offset_in_block": "0x50",
            "watchdog_offsets_in_block": ["0x31", "0x32", "0x40", "0x41", "0x42", "0x43"],
            "selective": False,
            "model": {
                "payload": "0x78 B con solo +0x50 a 0",
                "bytes_written": 0x78,
                "bytes_changed": len(diff_12),
                "changed_offsets": [f"{i:#x}" for i in diff_12],
                "conclusion": ("el protocolo escribe el bloque completo; para tocar +0x50 hay que "
                               "enviar >= 0x51 B y el resto de campos (WDG incluido) queda a merced "
                               "del payload"),
            },
        },
        "command_0x16": {
            "handler": "0x4cec",
            "range": ["0x20000000", "0x20004000"],
            "copy": "0x255a6",
            "selective": True,
            "requires": "bit 7 de la longitud = 1 (escritura absoluta)",
            "model": {
                "address": "0x20000050",
                "length": 1,
                "accepted": ok16,
                "bytes_changed": len(diff_16),
                "changed_offsets": [f"{i:#x}" for i in diff_16],
                "conclusion": ("el lado Darwin aceptaría una escritura selectiva de 1 B en la "
                               "compuerta; falta el emisor BIONZ y el disparo fuera de Seton"),
            },
        },
        "window": ("InitCom 0x4bca solo existe en la tarea COM 0xece4, creada en Seton; "
                   "no hay ruta desde On/captura"),
    }


def route_a(c: Core) -> dict:
    gate_sites = sorted(c.bl_callers(0x1FE66))
    t022_window = (0x83F91E20, 0x83F91F30)
    return {
        "schema": "a6000.e25.route_a.v1",
        "gate": {
            "byte": "0x20000050",
            "presence_byte": "0x200002c0 + canal",
            "reader": "0x1b080",
            "gate_function": "0x1fe66",
            "consumers": [f"{a:#x}" for a in gate_sites],
            "static_writers": static_gate_writers(c),
            "read_high_nibble": "0x1fe70 lsrs r4,r0,#4; 0x1fe72 cmp r4,#6; tabla 0x1fe7a",
        },
        "initcom": initcom_model(),
        "t022_t023": {
            "window_physical": [f"{t022_window[0]:#x}", f"{t022_window[1]:#x}"],
            "in_bionz_dram": True,
            "overlaps_darwin_sram": False,
            "source": "scripts/e24_05h5/protocolo.py; tests/test_e24_05h5_protocolo.py",
            "consequence": "T022/T023 observan lo que BIONZ envía, no la SRAM 0x2000xxxx de Darwin",
        },
        "bionz_packet_0x0c": {
            "constructor": "0x43841070",
            "gate_not_a_field": True,
            "note": ("pkt[0xc] elige la lista de la máquina de 49 estados; la compuerta 0x1fe66 "
                     "no viaja en el paquete y no tiene escritor en Darwin"),
        },
        "prototype": {
            "scope": "modelo de los handlers InitCom, no ejecución de firmware",
            "viable": False,
            "missing_link": ("no hay emisor BIONZ demostrado de 0x16 con dirección 0x20000050; "
                             "0x12 exige bloque de 0x78 B; ambas solo existen en Seton; T022/T023 "
                             "no alcanzan la SRAM de Darwin"),
        },
        "verdict": "NO",
    }


def reach_row(reach: Reach, name: str, entry: int, gate: int, coil: int, r0: int | None = None) -> dict:
    res = reach.run(entry, Scenario(gate, coil), r0)
    s = summarize(res, {**PRIMS, ERR: "error", 0x1F5A6: "rearme directo", 0x1FCB8: "freno"})
    prims = sorted(f"{t:#x}" for t in s if t in MOTOR)
    err6 = sorted({f"{site:#x}" for _, site, v in s.get(ERR, []) if v == 6})
    rearm_called = bool(s.get(0x1F5A6))
    return {
        "name": name,
        "entry": f"{entry:#x}",
        "gate": gate,
        "coil": coil,
        "lists": sorted({f"{p:#x}" for d, p in res.lists if d == OUTER}),
        "states": sorted(i for d, i in res.states if d == OUTER),
        "motor_primitives": prims,
        "rearm_direct_called": rearm_called,
        "rearm_direct_note": ("0x1f5a6 se llama, pero con gate 0 retorna en 0x1f5ae; "
                             "la llamada no ejecuta el motor"),
        "brake": sorted(f"{t:#x}" for t in s if t == 0x1FCB8),
        "error6": err6,
        "functions": len(res.funcs),
        "open_indirect": len(res.open_indirect),
    }


def mechanical(c: Core) -> dict:
    reach = Reach(c)
    ids = {k: list_ids(c, p) for k, p in LISTS.items()}
    handlers = outer_handlers(c)
    states = state_handlers(c)

    starter_rows = {}
    for name, s in STARTERS.items():
        starter_rows[name] = {
            "entry": f"{s['entry']:#x}",
            "gate4_list": f"{s['gate4']:#x}",
            "gate0_list": f"{s['gate0']:#x}",
            "gate4_ids": list_ids(c, s["gate4"]),
            "gate0_ids": list_ids(c, s["gate0"]),
        }

    # Secuencia L0 y los manejadores que ejecuta.
    l0_ids = ids["L0"]
    l0_handlers = [{"id": i, "handler": f"{handlers[i]:#x}"} for i in l0_ids]
    state7 = handlers[7]
    state9 = handlers[9]
    state7_calls = [f"{i.operands[0].imm:#x}" for i in c.dis(state7, 0x40)
                    if i.mnemonic in ("bl", "b.w") and i.operands and i.operands[0].type == arm.ARM_OP_IMM]
    state9_calls = [f"{i.operands[0].imm:#x}" for i in c.dis(state9, 0x20)
                    if i.mnemonic in ("bl", "b.w") and i.operands and i.operands[0].type == arm.ARM_OP_IMM]

    # Cierres diferenciales principales.
    rows = []
    for gate, coil in ((0, 0), (4, 0), (0, 4)):
        for name, ent, r0 in (("load", 0x1984E, 0), ("load(1)", 0x1984E, 1),
                              ("capture4", 0x19998, 0), ("capture5", 0x199B8, 0),
                              ("capture1f", 0x199D8, 0)):
            rows.append(reach_row(reach, name, ent, gate, coil, r0))
    # Los tres handlers de la máquina de 49 estados que arrancan rearme.
    for gate in (0, 4):
        for name, ent in (("m49_4", 0x18636), ("m49_5", 0x1865A), ("m49_1f", 0x190FC)):
            rows.append(reach_row(reach, name, ent, gate, 0))
    # Preparación por disparo, rearme de ráfaga y tarea de captura completa.
    for gate in (0, 4):
        for name, ent in (("burst_prep", 0x17CEE), ("rearm_burst", 0x17A44), ("capture_task", 0x1811A)):
            rows.append(reach_row(reach, name, ent, gate, 0))

    # Operación 5: el freno no consulta la compuerta.
    op5 = {str(g): reach_row(reach, "op5", 0xD46E, g, 0) for g in (0, 4)}

    # Ciclo de vida sin cierre completo (Off main es enorme): se comprueba por bytes que
    # reset/InitCom/Upd/Off no contienen ningún consumidor de la compuerta, y que la única
    # entrada de ciclo de vida que la alcanza es On init -> 0x1984e(0).
    gate_consumers = set(c.bl_callers(0x1FE66))
    lifecycle = {
        "state_mains": {k: f"{v:#x}" for k, v in states.items() if v},
        "gate_consumers": sorted(f"{a:#x}" for a in gate_consumers),
        "reset_initcom_upd_off_have_no_gate_consumer": all(
            not (start <= a < end) for a in gate_consumers
            for start, end in ((0x45C8, 0x4638), (0x4BCA, 0x5000), (0x8DA8, 0x8E00), (0x8900, 0x8C90))
        ),
        "on_init_reaches_load": any(0x75F0 <= a < 0x76D0 for a in c.bl_callers(0x1B260)),
        "load_callers": sorted(f"{a:#x}" for a in c.bl_callers(0x1984E)),
        "note": ("On init 0x75f0 -> 0x1b260 -> 0xcee6 -> 0x1984e(0) es la única entrada de "
                 "ciclo de vida que consulta la compuerta; con E25 elige L0. Reset/InitCom/Upd/Off "
                 "no contienen consumidores de 0x1fe66."),
    }

    # Error de leva y timeout de la máquina interior (el de ADC ya está en load).
    errors = {
        "lever_0x1f4ce": {str(g): reach_row(reach, "lever", 0x1F4CE, g, 0) for g in (0, 4)},
        "timeout_0x1fa3a": {str(g): reach_row(reach, "timeout", 0x1FA3A, g, 0) for g in (0, 4)},
    }

    # P4B/P4C: escritores y valores (de E24-05h/E24-05h-3, verificados por bytes).
    pin_writers = {
        "P4C": {
            "writer": "0x1ecec -> 0x51c0(0x230, r1)",
            "set_to_1": "0x16e7a (0x1ecec(1)); llamado desde 0x17cee y 0x175ea",
            "clear": "0x16e68 (0x1ecec(0))",
            "note": ("E24-05h corrige la lectura de rea-tema3: sí existe P4C←1, a través del alias "
                     "variable r0=0x230; los 9 sitios con literal solo escriben 0"),
        },
        "P4B": {
            "writer": "0xd116/0xd18e (máscaras de ocupación)",
            "mask": "0x800 (bit 11)",
            "note": "sigue cambiando durante la captura; no es el motor de rearme",
        },
        "P4D": {"writer": "0x20c90 (1) / 0x20cb2 (0)", "filter": "0x20c74 (tipo 0 => no escribe)"},
        "P4E": {"writer": "0x20d00 (1) / 0x20cd4 (0)", "filter": "0x20c74 (tipo 0 => no escribe)"},
    }

    motor_writer = {
        "PDOR4_writer": "0x51cc(4, valor, 0xfffc)",
        "values": {
            "0x1fe32": {"value": 0, "P40": 0, "P41": 0, "xor": 0, "meaning": "apagar"},
            "0x1fe50": {"value": 1, "P40": 1, "P41": 0, "xor": 1, "meaning": "movimiento"},
            "0x1fe86": {"value": 2, "P40": 0, "P41": 1, "xor": 1, "meaning": "movimiento"},
            "0x1feb6": {"value": 3, "P40": 1, "P41": 1, "xor": 0, "meaning": "freno/pasivo"},
        },
        "circuit": ("Q6801 excitado por XOR IC6800 (P40 XOR P41); 0 y 3 dan XOR=0, 1 y 2 dan XOR=1. "
                    "El freno 3 no es una orden de movimiento; su efecto físico (corto/frenado) no "
                    "está medido."),
    }

    return {
        "schema": "a6000.e25.mechanical.v1",
        "binary": {"sha256": c.sha256(), "base": f"{BASE:#x}", "size": len(c.data)},
        "patch": {
            "address": f"{PATCH_ADDR:#x}",
            "before": PATCH_OLD.hex(),
            "after": PATCH_NEW.hex(),
            "instruction": "0x1fe6a: mov r0,r5 -> b 0x1fe82 (r5=0; retorno 0 sin leer la compuerta)",
        },
        "lists": {k: {"address": f"{p:#x}", "ids": v} for k, (p, v) in zip(LISTS, zip(LISTS.values(), ids.values()))},
        "starters": starter_rows,
        "outer": {
            "descriptor": f"{OUTER:#x}",
            "table": f"{OUTER_TABLE:#x}",
            "terminal": 0x0A,
            "handlers": {str(k): f"{v:#x}" for k, v in handlers.items()},
            "L0_sequence": l0_ids,
            "L0_handlers": l0_handlers,
            "state7_calls": state7_calls,
            "state9_calls": state9_calls,
            "state7_p4d_gate": "0x20c90 consulta 0x20c74; con tipo 0 no escribe",
            "state9_release": "0xd18e(0x1000000)",
        },
        "reachability": rows,
        "operation5": op5,
        "lifecycle": lifecycle,
        "errors": errors,
        "pins": pin_writers,
        "motor": motor_writer,
        "verdict": {
            "normal_capture_and_rearm": "sin primitivas del motor con gate 0 + tipo 0",
            "exceptions": ["operación 5: 0x1feb6 (P40/P41=3, XOR=0) sin compuerta",
                           "P4B/P4C siguen activos y su efecto físico no está medido",
                           "0x1989c (error 6 ADC) puede dispararse en load(0) y encolar operación 5"],
        },
    }


def patched_mechanical(c: Core, candidate: Path | None = None) -> dict:
    """Comprueba el candidato E25 sobre los bytes: retorno 0 y lista L0."""
    path = candidate or (OUT / "darwin_core_tipo0_sin_rearme.bin")
    patched = DarwinImage.load(path)
    assert patched.patched
    pc = Core(patched.path)
    # 0x1fe66 ya no ejecuta 0x1b080 ni la tabla: el camino es movs r5,#0; b 0x1fe82; mov r0,r5; pop.
    ins = [f"{i.address:#x}: {i.mnemonic} {i.op_str}" for i in pc.dis(0x1FE66, 0x20)]
    return {
        "schema": "a6000.e25.patched.v1",
        "input_sha256": sha256(patched.data),
        "variant": patched.variant.name,
        "tipo0_present": patched.variant.tipo0_present,
        "gate_bytes": pc.data[0x1FE66 - BASE:0x1FE86 - BASE].hex(),
        "gate_disassembly": ins,
        "returns_zero": True,
        "reads_gate": False,
        "three_starters_use_L0": True,
        "L0": list_ids(pc, 0x29CD8),
        "type0_bytes": pc.data[TIPO0_ADDR - BASE:TIPO0_ADDR - BASE + len(TIPO0_BYTES)].hex(),
        "type0_preserved": pc.data[TIPO0_ADDR - BASE:TIPO0_ADDR - BASE + len(TIPO0_BYTES)] == TIPO0_BYTES,
    }


def main(write: bool = False) -> dict:
    c = Core()
    assert c.sha256() == SHA256, "darwin_core.bin no es el 3.21 oficial"
    OUT.mkdir(parents=True, exist_ok=True)
    tipo0 = ROOT / "analysis/darwin-patch/darwin_core_tipo0.bin"
    # El candidato es un binario ignorado por Git: se regenera si falta para que el análisis
    # funcione en una copia limpia.
    candidate = OUT / "darwin_core_tipo0_sin_rearme.bin"
    if not candidate.is_file():
        if not tipo0.is_file():
            raise SystemExit("falta analysis/darwin-patch/darwin_core_tipo0.bin")
        apply(tipo0, candidate, OUT / "manifest_tipo0_sin_rearme.json")
    route = route_a(c)
    mech = mechanical(c)
    patched = patched_mechanical(c, candidate)
    result = {"route_a": route, "mechanical": mech, "patched": patched}
    if write:
        (OUT / "route-a-volatile.json").write_text(json.dumps(route, indent=2, ensure_ascii=False) + "\n")
        (OUT / "mechanical-reachability.json").write_text(json.dumps(mech, indent=2, ensure_ascii=False) + "\n")
        (OUT / "patched-bytes.json").write_text(json.dumps(patched, indent=2, ensure_ascii=False) + "\n")
        # Manifiestos reproducibles (se regeneran siempre desde las copias locales).
        if tipo0.is_file():
            apply(tipo0, candidate, OUT / "manifest_tipo0_sin_rearme.json")
        if DARWIN.is_file():
            apply(DARWIN, OUT / "darwin_core_original_sin_rearme.bin",
                  OUT / "manifest_original_sin_rearme.json")
        print(f"escrito {OUT}")
    print(json.dumps({
        "route_a": route["verdict"],
        "missing_link": route["prototype"]["missing_link"],
        "L0": mech["lists"]["L0"]["ids"],
        "gate0_motor_calls": sorted({p for row in mech["reachability"] if row["gate"] == 0
                                     for p in row["motor_primitives"]}),
        "op5_gate0": mech["operation5"]["0"]["motor_primitives"],
        "patched_type0": patched["type0_preserved"],
    }, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="regenera analysis/e25/*.json y manifiestos")
    args = ap.parse_args()
    main(args.write)

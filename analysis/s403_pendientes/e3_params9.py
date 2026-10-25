#!/usr/bin/env python3
"""E3: origen de `params[+9]` (modo de obturación) en las llamadas a SetExposure (wrapper 0x436d6320) de av-cam A6000.

Solo bytes originales y Capstone. Resultado en e3_params9.json. El wrapper tiene cinco sitios de llamada directos; los
escritores de `ctx+0x655` (= bloque `ctx+0x64c`, byte +9) con desplazamiento inmediato se barrieron en toda la imagen."""
import json
from pathlib import Path

import memscan
import pic
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

B = pic.BASE
OUT = Path(__file__).with_name("e3_params9.json")
WRAPPER = 0x436D6320
EXPECTED_CALL_SITES = [0x438C79FC, 0x438C830C, 0x438C8824, 0x438CC894, 0x43AE937C]
# dirección -> texto Capstone que fija el valor del byte +9 (o lo copia)
WRITERS = {
    0x438C82BC: ("strb.w r3, [r4, #0x655]", "0", "r3=0 si la clase de modelo 0x43a12c64 vale 2 o 3; +0 del bloque = 2"),
    0x438C79E2: ("strb.w r3, [r4, #0x655]", "4", "r3=0 y `adds r3,#4`; bloque a cero salvo +9; llama al wrapper con r2=0"),
    0x438C87F0: ("strb.w sb, [r4, #0x655]", "1", "sb=1 (`mov.w sb,#1` en 0x438c87e6); bloque a cero salvo +9"),
}
# la otra familia de llamadas: bloque en pila, +9 = 1 si [r4+0x1fc]==9 si no 0
STACK_BLOCK = {0x43811192: "cmp r3, #9", 0x43811196: "subs r3, #8", 0x4381119a: "movs r3, #0", 0x4381119c: "strb.w r3, [sp, #0x21]"}
COPY_WRITER = 0x4389CC28  # copia a otro objeto (id 0x9405), no al bloque del contexto


def text_at(blob: bytes, addr: int) -> str:
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    i = next(cs.disasm(blob[addr - B:addr - B + 4], addr, count=1))
    return f"{i.mnemonic} {i.op_str}"


def main() -> None:
    blob = pic.load("a6000")
    sites = pic.branch_sites(blob, WRAPPER)
    hits = memscan.mem_accesses(blob, {0x655}, ("strb",))
    wide = [(a, t) for a, t in memscan.mem_accesses(blob, {0x654}, ("str",)) if not t.startswith("strb")]
    result = {
        "wrapper": hex(WRAPPER),
        "sitios_de_llamada": [hex(s) for s in sites],
        "sitios_esperados_ok": sites == EXPECTED_CALL_SITES,
        "escritores_strb_disp_0x655": [{"addr": hex(a), "insn": t} for a, t in hits],
        "escritores_clasificados": {
            hex(a): {"insn_ok": text_at(blob, a) == w[0], "valor": w[1], "nota": w[2]} for a, w in WRITERS.items()
        },
        "bloque_en_pila_ok": all(text_at(blob, a) == t for a, t in STACK_BLOCK.items()),
        "copia_a_otro_objeto": {"addr": hex(COPY_WRITER), "insn": text_at(blob, COPY_WRITER)},
        "constantes_directas_en_sitios_de_llamada": [0, 1, 4],
        # str/strh con desplazamiento 0x654 también escriben el byte +9 (0x655); el tipo de objeto no se confirmó
        "escritores_anchos_en_0x654": [{"addr": hex(a), "insn": t} for a, t in wide],
        "valores_2_y_3": "sin constante directa; origen posible solo por los escritores anchos o copias de bloque (no resuelto)",
    }
    OUT.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "escritores_strb_disp_0x655"}, indent=1))


if __name__ == "__main__":
    main()

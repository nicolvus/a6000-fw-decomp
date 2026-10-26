"""E18: qué lee `[LGA]` GetDfeDrvParam (0x4389b320) y cómo se resuelve cada id contra los registros estáticos de la imagen A6000.
Cadena: 0x4389b320 → thunk 0x43ae92ee → 0x4381b4b0(id, out[0x28]) → id→idx por la tabla de 0x4381b3d4 → base por tbb de 0x436d0234 → [base+8] = registro.
Salida: e18_dfe_param.json. shortcut: son los valores iniciales de la imagen; si el controlador los reescribe en ejecución no se ven, y qué ids pasa el modo (r8+0x6a4) queda abierto."""
import json
import struct
import sys
from pathlib import Path

import pic

HERE = Path(__file__).parent
TBB, TBB_LDR, ID_TABLE_LDR, RANGE_LO = 0x436D0242, 0x436D0250, 0x4381B3DA, 0x15
FIELDS = (0xA, 0xC, 0xE)  # u16 que suma 0x4389b320 (sp+0x3a/0x3c/0x3e y sp+0x12/0x14/0x16 sobre buffers en +0x30 y +0x08)


def u32(blob: bytes, a: int) -> int:
    return struct.unpack_from("<I", blob, a - pic.BASE)[0]


def pc_literal(blob: bytes, ldr: int, add: int) -> int:
    """Valor de `ldr rN,[pc,#imm]` + `add rN,pc` (Thumb-16)."""
    imm = (struct.unpack_from("<H", blob, ldr - pic.BASE)[0] & 0xFF) * 4
    return (u32(blob, ((ldr + 4) & ~3) + imm) + add + 4) & 0xFFFFFFFF


def main() -> None:
    blob = pic.load("a6000")
    id_table = pc_literal(blob, ID_TABLE_LDR, ID_TABLE_LDR + 2)
    rows = []
    for ident in range(1, 0x46):
        idx = u32(blob, id_table + 4 * (ident - 1))
        row: dict = {"id": ident, "idx": idx}
        k = idx - RANGE_LO
        if 0 <= k <= 0xC:
            target = TBB + 2 * blob[TBB - pic.BASE + k]  # destino del tbb: `ldr r0,[pc,#imm]; add r0,pc`
            base = pc_literal(blob, target, target + 2)
            rec = u32(blob, base + 8)
            raw = blob[rec - pic.BASE : rec - pic.BASE + 0x28]
            vals = [struct.unpack_from("<H", raw, o)[0] for o in FIELDS]
            row |= {"base": hex(base), "registro": hex(rec), "campos": vals, "suma": sum(vals), "u8_26": raw[0x26]}
        rows.append(row)
    out = {"funcion": "0x4389b320", "campos_leidos": [hex(o) for o in FIELDS], "ids_fijos": {"0x114": 0xB},
           "id_por_modo": {"0x116": "r8+0x6a4"}, "defecto_si_error": 0xFC4, "ids": rows}
    (HERE / "e18_dfe_param.json").write_text(json.dumps(out, indent=1) + "\n")
    print(len(rows), "ids;", sum("suma" in r for r in rows), "con registro estático", file=sys.stderr)


if __name__ == "__main__":
    main()

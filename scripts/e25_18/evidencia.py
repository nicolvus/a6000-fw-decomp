"""E25-18 — comprobación de bytes citados en el informe (expected transcrito del desensamblado; falla si no coinciden)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "e25_17"))
import fw  # type: ignore[import-not-found]

ROOT = Path(__file__).resolve().parents[2]
SITIOS = [
    (0x438C82D8, "7ebb", "cbnz r6,0x438c833a: solo el paso 0 (cap+0x4b9c == 0) ejecuta SetExposure"),
    (0x438C82DC, "56f220f9", "bl 0x43b1e520 (fija cap+0x73b desde cap+0x655)"),
    (0x438C82E4, "b4f85076", "ldrh r7,[cap+0x650]: guarda el svd nativo"),
    (0x438C82F0, "a4f85066", "strheq [cap+0x650],0 si cap+0x504 == 1"),
    (0x438C82FE, "0df60bff", "bl 0x436d6118: punto de enganche (tras 0x82f0, antes de SetExposure)"),
    (0x438C830C, "0ef608f8", "bl 0x436d6320 SetExposure(cap+0x64c)"),
    (0x438C831E, "0ef63bf8", "bl 0x436d6398 SetRead(cap+0x6bc)"),
    (0x438C8326, "10f2f6fe", "bl 0x43ad9116 (SSB)"),
    (0x438C8330, "10f2f4fe", "bl 0x43ad911c(1) (Execute)"),
    (0x438C8334, "a4f85076", "strh r7 -> cap+0x650: restaura el svd nativo"),
    (0x438C83C4, "a4f85036", "strh 0 -> cap+0x650 si cap+0x740 == 0"),
    (0x438C82C4, "c4f84c16", "bloque forzado (0x43a12c64 = 2/3): cap+0x64c = 2"),
    (0x43B1E54C, "94f85536", "ldrb cap+0x655 en 0x43b1e520"),
    (0x43B1E556, "84f83b57", "strb cap+0x73b"),
    (0x4383FA9A, "d3f105f9", "bl 0x43a12ca8 (predicado) en el productor"),
    (0x4383FAA0, "b044", "add r8,r6: el predicado suma un VTS"),
    (0x4383FAC0, "a4f86870", "strh svd -> record+0x68"),
    (0x4383FAE8, "a4f8d810", "strh d8 -> record+0xd8"),
    (0x4383FAEE, "a4f8da50", "strh da -> record+0xda"),
    (0x4383FAF2, "a4f8dc50", "strh dc -> record+0xdc"),
    (0x437B22A4, "b4f8d820", "ldrh d8 (cuadro 0) en el planificador 0x437b21b8"),
    (0x437B22B4, "b4f8dc30", "ldrh dc (cuadro == svd)"),
    (0x437B22BE, "b4f8da10", "ldrh da (cuadros intermedios)"),
    (0x437B22DC, "3df7a4f9", "bl 0x436ef628 (periodo*VTS -> host)"),
    (0x436EF62C, "1864", "str r0,[0x43e849c0+0x40]"),
    (0x437B2260, "9846", "cuadro != svd: r8 = 0"),
    (0x437B227A, "4ff00108", "cuadro == svd: r8 = 1"),
    (0x437B2272, "9046", "cuadro 0 (record+4 == 0): sb = 1"),
    (0x437B2254, "a288", "ldrh record+4 (índice de cuadro)"),
    (0x437B2258, "b4f86810", "ldrh record+0x68 (svd)"),
    (0x436D6FAA, "8e88", "SetExposure: ldrh param+4 (svd)"),
    (0x436D6FBA, "c0f8a863", "str svd -> obj+0x3a8"),
    (0x436D6FE2, "8ef802b0", "strb svd[7:0] -> ID3"),
    (0x436D6FFC, "80f802e0", "strb svd[11:8] -> ID4"),
    (0x436D700A, "8cf802e0", "strb shd[7:0] -> ID5"),
    (0x436D701E, "82f802c0", "strb shd[13:8] -> ID6"),
    (0x436D7026, "8270", "strb spl[7:0] -> ID7"),
    (0x436D7034, "9970", "strb spl[11:8] -> ID8"),
]


def main() -> None:
    res = [{"addr": hex(a), "esperado": e, "leido": fw.rd(a, len(e) // 2).hex(), "ok": fw.rd(a, len(e) // 2).hex() == e, "nota": n}
           for a, e, n in SITIOS]
    out = {"fallos": sum(not r["ok"] for r in res), "sitios": res}
    (ROOT / "analysis/e25-18/evidencia.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(len(res), "sitios,", out["fallos"], "fallos")
    for r in res:
        if not r["ok"]:
            print(r)


if __name__ == "__main__":
    main()

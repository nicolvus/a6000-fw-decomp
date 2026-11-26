"""Ejecuta `.init_array` de los dos libObj.so con el cargador del repo (`scripts/g22/sim/armlib.py`).

Carga cada biblioteca en una `Machine` (base 0: VA del fichero = dirección de ejecución), aplica
sus reubicaciones con `Lib` (ABS32/GLOB_DAT/JUMP_SLOT/RELATIVE) y llama en orden a las 263
entradas de `.init_array`. Los símbolos indefinidos los resuelve `armlib` a stubs que devuelven 0
y que quedan anotados en `Machine.default_calls`.

Compara: resultado por entrada, secuencia de importaciones llamadas y bytes del segmento RW.

Uso:  python3 init_armlib.py [--json SALIDA]
"""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "scripts"))

ORIG = (RAIZ / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
        "nflasha15_unpacked_unpacked/lib/libObj.so")
PATCH = RAIZ / "build/cfw_func393/pp/files/lib/libObj.so"
RW_VA, RW_SZ = 0xFD25A4, 0x11062C


def ejecuta(ruta: Path) -> dict:
    from g22.sim.armlib import Lib, Machine

    m = Machine()
    Lib(m, ruta.read_bytes(), 0)
    entradas = list(struct.unpack("<263I", bytes(m.uc.mem_read(0xFD25A4, 0x41C))))
    detalle, imports_previos = [], 0
    for i, entrada in enumerate(entradas):
        try:
            m.call(entrada, 0, 0, 0, count=200_000)
            resultado, motivo = "ok", None
        except Exception as exc:                                  # noqa: BLE001
            resultado, motivo = "fallo", "%s: %s" % (type(exc).__name__, str(exc)[:60])
        detalle.append({"i": i, "va": entrada, "resultado": resultado, "motivo": motivo,
                        "imports": len(m.default_calls) - imports_previos})
        imports_previos = len(m.default_calls)
    return {"detalle": detalle, "imports": list(m.default_calls),
            "rw": bytes(m.uc.mem_read(RW_VA, RW_SZ))}


def main() -> None:
    a, b = ejecuta(ORIG), ejecuta(PATCH)
    dif = [(x, y) for x, y in zip(a["detalle"], b["detalle"]) if x != y]
    rw_a, rw_b = a["rw"], b["rw"]
    rangos, i = [], 0
    while i < len(rw_a):
        if rw_a[i] != rw_b[i]:
            j = i
            while j < len(rw_a) and rw_a[j] != rw_b[j]:
                j += 1
            rangos.append((RW_VA + i, j - i))
            i = j
        else:
            i += 1
    ok_a = sum(1 for x in a["detalle"] if x["resultado"] == "ok")
    ok_b = sum(1 for x in b["detalle"] if x["resultado"] == "ok")
    print("armlib: entradas=263  ok fábrica=%d  ok parcheado=%d" % (ok_a, ok_b))
    print("fallos:", [(x["i"], hex(x["va"]), x["motivo"]) for x in a["detalle"]
                       if x["resultado"] != "ok"])
    print("importaciones llamadas: %d (idénticas=%s)"
          % (len(a["imports"]), a["imports"] == b["imports"]))
    print("entradas con resultado distinto: %d" % len(dif))
    for x, y in dif:
        print("  %s / %s" % (x, y))
    print("rw sha fábrica=%s" % hashlib.sha256(rw_a).hexdigest())
    print("rw sha parcheado=%s" % hashlib.sha256(rw_b).hexdigest())
    print("rangos distintos del segmento RW: %d" % len(rangos))
    for va, tam in rangos:
        print("  VA %#x  %d B" % (va, tam))
    if "--json" in sys.argv:
        salida = Path(sys.argv[sys.argv.index("--json") + 1])
        salida.write_text("\n".join(
            ["entradas=263", "ok_fabrica=%d" % ok_a, "ok_parcheado=%d" % ok_b,
             "imports=%d" % len(a["imports"]), "imports_iguales=%s" % (a["imports"] == b["imports"]),
             "entradas_distintas=%d" % len(dif),
             "rw_sha_fabrica=%s" % hashlib.sha256(rw_a).hexdigest(),
             "rw_sha_parcheado=%s" % hashlib.sha256(rw_b).hexdigest()]
            + ["%d %#x %s %s" % (x["i"], x["va"], x["resultado"], x["motivo"] or "")
               for x in a["detalle"]]
            + ["rango %#x %d" % r for r in rangos]) + "\n")
        print("json ->", salida)


if __name__ == "__main__":
    main()

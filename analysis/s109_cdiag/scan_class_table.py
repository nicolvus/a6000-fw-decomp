#!/usr/bin/env python3
"""S109 — tabla de registro de clases del subsistema `[CDIAG]`.

En el firmware hay una **tabla de pares (vptr-comun, puntero-al-nombre-de-clase)**
que enumera las clases del subsistema de diagnóstico del códec.  En la A6000
fw3.21 está en `0x43fda6a0` (16 entradas, fin `0x43fda720`); en la A7S fw3.20 en
`0x43fdb6ec` (16 entradas); en la A6300 fw2.01 en `0x4419b094` (20 entradas,
con las 4 clases `CdExt*` adicionales).

Método: se localiza la cadena `7CdMsgIf` (nombre de clase), se busca su puntero
absoluto de 4 B en el blob, y se recorre la tabla hacia atrás y hacia delante
mientras las entradas tengan la forma (ptr, ptr_a_nombre_de_clase).

Salida: analysis/s109_cdiag/cdiag_class_table.json
"""
import json
import os
import struct

BASE = 0x43541000
MODELOS = {
    "A6000_fw321": "analysis/rea-independent/input/av-cam.bin",
    "A7S_fw320": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                  "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300_fw201": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
CLASE_RAIZ = b"7CdMsgIf\x00"


def u32(blob, v):
    o = v - BASE
    if o < 0 or o + 4 > len(blob):
        return None
    return struct.unpack("<I", blob[o:o + 4])[0]


def cstr(blob, v):
    o = v - BASE
    if o < 0 or o >= len(blob):
        return None
    e = o
    while e < len(blob) and 32 <= blob[e] < 127:
        e += 1
    return blob[o:e].decode("latin1")


def es_nombre_de_clase(t):
    """`CdCtrlCore` -> los nombres llevan el prefijo numérico de longitud
    (`10CdCtrlCore`); se acepta cualquier `<dígitos><Mayúscula>…`."""
    if not t or len(t) < 3:
        return False
    i = 0
    while i < len(t) and t[i].isdigit():
        i += 1
    return i > 0 and i < len(t) and t[i].isupper()


def tabla_de_clases(blob):
    """Localiza la tabla de clases del subsistema Cd*.

    La entrada que contiene el puntero a `7CdMsgIf` es (vptr, nombre).  Se
    recorre hacia atrás y hacia delante mientras las entradas tengan esa forma
    (el puntero al nombre apunta a una cadena `<dígitos><Mayúscula>…`).
    """
    i = blob.find(CLASE_RAIZ)
    if i < 0:
        return None
    raiz = BASE + i
    pat = struct.pack("<I", raiz)
    j = blob.find(pat)
    if j < 0:
        return None
    # la entrada que contiene el puntero es (vptr, nombre): el nombre está en +4
    inicio = BASE + j - 4

    def entrada_ok(a):
        w1 = u32(blob, a)
        w2 = u32(blob, a + 4)
        if w1 is None or w2 is None:
            return None
        t = cstr(blob, w2)
        return (w1, w2, t) if es_nombre_de_clase(t) else None

    # hacia atrás
    a = inicio
    while True:
        prev = entrada_ok(a - 8)
        if prev is None:
            break
        a -= 8
    inicio_efectivo = a
    # hacia delante
    entradas = []
    while True:
        e = entrada_ok(a)
        if e is None:
            break
        w1, w2, t = e
        entradas.append({"entry_vaddr": f"0x{a:x}", "vptr": f"0x{w1:x}",
                         "name_vaddr": f"0x{w2:x}", "class": t})
        a += 8
    return {"table_vaddr": f"0x{inicio_efectivo:x}",
            "table_end_vaddr": f"0x{a:x}",
            "n_entries": len(entradas),
            "entries": entradas}


def main():
    out = {}
    for modelo, path in MODELOS.items():
        if not os.path.exists(path):
            print(f"{modelo}: no disponible")
            continue
        blob = open(path, "rb").read()
        t = tabla_de_clases(blob)
        out[modelo] = {"path": path, **t}
        print(f"{modelo}: tabla en {t['table_vaddr']}, {t['n_entries']} entradas "
              f"(fin {t['table_end_vaddr']})")
        for e in t["entries"]:
            print(f"   {e['entry_vaddr']}  {e['class']}")
    dest = "analysis/s109_cdiag/cdiag_class_table.json"
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    if "A6000_fw321" in out and "A7S_fw320" in out:
        a = {e["class"] for e in out["A6000_fw321"]["entries"]}
        b = {e["class"] for e in out["A7S_fw320"]["entries"]}
        print(f"\nA6000 vs A7S: mismo conjunto = {a == b}; "
              f"solo A6000 = {sorted(a - b)}; solo A7S = {sorted(b - a)}")
    print("escrito", dest)


if __name__ == "__main__":
    main()

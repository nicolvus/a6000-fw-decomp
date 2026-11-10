#!/usr/bin/env python3
"""Construye el paquete de prueba «Silent Shooting al estilo A6300» para la A6000 fw3.21 (solo ficheros; no toca la cámara).

Semántica (igual que el CFW ya hecho): la entrada nueva escribe el MISMO ajuste que el menú EFCS (ProcessId 0x46,
`PARAMID_FRONT_ESHUTTER_MODE`, selector LIRO `0x4099`, `+0x210`): «Silent Shooting: Off» = valor 0 (EFCS / segunda cortina mecánica),
«On» = valor 1 (electrónico). No añade nada más (sin Shutter Type, sin cambios en `av-cam`).
Contenido de SALIDA/:
  lib/viewUnified2.so   5 páginas con la entrada nueva antes del EFCS (add_menu_entry.py)
  lib/CautionConfig.so  nodo de ajuste «SilentShutter» (5+6+6 propiedades, en un segmento añadido): etiquetas A6300, ProcessId 0x46, 0xb/0xc del EFCS
  share/app/string_<idioma>.uxc  textos 0xf840/0xf847/0xf849 de la A6300 copiados a ranuras libres del A6000 (NEW_IDS; solo idiomas
                                  de esquema latino). Los ids de la A6300 caen fuera del índice del A6000 (5 958 ranuras, hasta 0xf745):
                                  así se instaló el 3.39 y la UI no arrancó (assert de ResourceManager.cpp:954)
  SHA256SUMS, MANIFEST.json  (hashes de los originales y de los parcheados)
Uso: build_silent_menu_test.py DIR_DEV_A6000 DIR_DEV_A6300 SALIDA [PID_SILENT, p. ej. 0x12 para el 3.57+]
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry
import uxc_strings

PID_EFCS = 0x46
# id A6300 → id A6000: ranuras vacías en los 25 idiomas latinos, sin registro en los no latinos y sin referencia 0x0204xxxx en /usr
NEW_IDS = {0xF840: 0xF3E8, 0xF847: 0xF515, 0xF849: 0xF56A}  # etiqueta, ayuda de la raíz, ayuda de «On»
RES = 0x0204_0000
# (símbolo de la lista de propiedades, [(id propiedad, flag, valor)]) ordenadas por id (búsqueda binaria). 0xb/0xc como el nodo EFCS
# (CustomFrontCurtainShutter): sin ellas el 3.53 mostró la entrada pero no el selector (G11 §13). Sony reserva 3/4/4 entradas: las
# listas nuevas van en un segmento añadido; se reapuntan los símbolos (R_ARM_GLOB_DAT) y la cuenta `movs r2,#N` del constructor.
LISTS = {
    "SilentShutterRoot": [(0, 0, RES | NEW_IDS[0xF840]), (6, 0, RES | NEW_IDS[0xF847]), (0xB, 1, 2), (0xC, 1, 0), (0xE, 1, PID_EFCS)],
    "SilentShutterOn": [(0, 0, RES | 0xE153), (6, 0, RES | NEW_IDS[0xF849]), (0xB, 1, 0), (0xC, 1, 1), (0xF, 1, 1), (0x10, 1, 1)],  # On = 1 (electrónico)
    "SilentShutterOff": [(0, 0, RES | 0xE109), (6, 0, RES | 0xF2A1), (0xB, 1, 0), (0xC, 1, 1), (0xF, 1, 0), (0x10, 1, 0)],  # Off = 0 (EFCS)
}
# `movs r2,#N` (cuenta) antes de CmnViewSettingProperties(props, lista, N) en la inicialización de CautionConfig.so (A6000 fw3.21)
COUNT_MOVS = {"SilentShutterRoot": 0x11B9AA, "SilentShutterOn": 0x11B9B8, "SilentShutterOff": 0x11B9CA}
ROOT = ("nflasha15_unpacked_unpacked",)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def md5(data: bytes) -> str:
    return hashlib.md5(data, usedforsecurity=False).hexdigest()  # el busybox de la cámara solo trae md5sum


def patch_caution(data: bytes, lib: Path) -> bytes:
    out = bytearray(data)
    segs = add_menu_entry._segments(data)
    _, dyn = add_menu_entry._dynamic(data, segs)
    symtab = add_menu_entry._off(segs, {t: v for t, v in dyn if t}[6])
    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    new_va = (top + add_menu_entry.ALIGN - 1) // add_menu_entry.ALIGN * add_menu_entry.ALIGN
    assert new_va >= len(data)
    blob = bytearray()
    for name, triples in LISTS.items():
        i = add_menu_entry._symbol_index(data, segs, dyn, f"cmnViewSettingPropertyList{name}".encode())
        old_size = struct.unpack_from("<I", data, symtab + 16 * i + 8)[0]
        assert struct.unpack_from("<H", data, COUNT_MOVS[name])[0] == 0x2200 | old_size // 12, name
        struct.pack_into("<II", out, symtab + 16 * i + 4, new_va + len(blob), 12 * len(triples))  # st_value, st_size
        struct.pack_into("<H", out, COUNT_MOVS[name], 0x2200 | len(triples))
        blob += b"".join(struct.pack("<3I", *t) for t in triples)
    # segmento PT_LOAD de solo lectura con offset de fichero = dirección (las herramientas que leen por st_value siguen valiendo)
    new_ph = [list(x) for x in segs] + [[1, new_va, new_va, new_va, 0, 0, 4, add_menu_entry.ALIGN]]
    total = len(blob) + 32 * len(new_ph)
    new_ph[-1][4] = new_ph[-1][5] = total
    out = out.ljust(new_va, b"\0") + blob + b"".join(struct.pack("<8I", *x) for x in new_ph)
    struct.pack_into("<I", out, 28, new_va + len(blob))  # e_phoff
    struct.pack_into("<H", out, 44, len(new_ph))  # e_phnum
    return bytes(out)


def main(dev_a, dev_b, dest, pid_silent=PID_EFCS):
    """pid_silent: ProcessId del nodo (0x46 = el del EFCS, 3.54; 0x12 = propio de Silent, 3.57+ con silent_descriptor.py)."""
    LISTS["SilentShutterRoot"][-1] = (0xE, 1, pid_silent)
    a, b, dest = (Path(dev_a) / "nflasha15_unpacked_unpacked"), (Path(dev_b) / "nflasha15_unpacked_unpacked"), Path(dest)
    (dest / "lib").mkdir(parents=True, exist_ok=True)
    (dest / "share/app").mkdir(parents=True, exist_ok=True)
    manifest = {"originales": {}, "parcheados": {}, "idiomas": []}

    def emit(rel, data):
        (dest / rel).write_bytes(data)
        manifest["originales"][rel] = sha(a / rel)
        manifest["parcheados"][rel] = hashlib.sha256(data).hexdigest()
        manifest.setdefault("md5", {})[rel] = {"original": md5((a / rel).read_bytes()), "parcheado": md5(data)}

    emit("lib/viewUnified2.so", add_menu_entry.patch((a / "lib/viewUnified2.so").read_bytes(), 0xEB0))
    emit("lib/CautionConfig.so", patch_caution((a / "lib/CautionConfig.so").read_bytes(), a / "lib/CautionConfig.so"))
    english = uxc_strings.parse((b / "share/app/string_english.uxc").read_bytes())[2]
    for f in sorted((a / "share/app").glob("string_*.uxc")):
        if f.name.endswith("_guide.uxc"):
            continue
        try:
            head, _, recs = uxc_strings.parse(f.read_bytes())
            assert uxc_strings.build(head, recs) == f.read_bytes()
        except AssertionError:
            continue  # esquema no latino (tabla de 32 bits): sin parsear, queda sin los textos nuevos
        try:  # traducción de la A6300 si su fichero del idioma se puede leer; si no, el texto inglés
            recs_b = uxc_strings.parse((b / "share/app" / f.name).read_bytes())[2]
        except (AssertionError, FileNotFoundError):
            recs_b = {}
        assert not set(NEW_IDS.values()) & set(recs), f"ranura ocupada en {f.name}"
        recs.update({new: recs_b.get(old, english[old]) for old, new in NEW_IDS.items()})
        emit(f"share/app/{f.name}", uxc_strings.build(head, recs))
        manifest["idiomas"].append(f.name + ("" if recs_b else " (inglés)"))
    (dest / "MANIFEST.json").write_text(json.dumps(manifest, indent=1, sort_keys=True))
    sums = [f"{hashlib.sha256((dest / r).read_bytes()).hexdigest()}  {r}" for r in manifest["parcheados"]]
    (dest / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    print(f"{len(manifest['parcheados'])} ficheros; idiomas con textos nuevos: {len(manifest['idiomas'])}")


if __name__ == "__main__":
    main(*sys.argv[1:4], pid_silent=int(sys.argv[4], 0) if len(sys.argv) > 4 else PID_EFCS)

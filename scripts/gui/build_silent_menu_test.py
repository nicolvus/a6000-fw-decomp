#!/usr/bin/env python3
"""Construye el paquete de prueba «Silent Shooting al estilo A6300» para la A6000 fw3.21 (solo ficheros; no toca la cámara).

Semántica (igual que el CFW ya hecho): la entrada nueva escribe el MISMO ajuste que el menú EFCS (ProcessId 0x46,
`PARAMID_FRONT_ESHUTTER_MODE`, selector LIRO `0x4099`, `+0x210`): «Silent Shooting: Off» = valor 0 (EFCS / segunda cortina mecánica),
«On» = valor 1 (electrónico). No añade nada más (sin Shutter Type, sin cambios en `av-cam`).
Contenido de SALIDA/:
  lib/viewUnified2.so   5 páginas con la entrada nueva antes del EFCS (add_menu_entry.py)
  lib/CautionConfig.so  nodo de ajuste «SilentShutter» (3+4+4 propiedades en `.rodata`) reescrito: etiquetas A6300, ProcessId 0x46
  share/app/string_<idioma>.uxc  textos 0xf840/0xf847/0xf849 de la A6300 copiados a ranuras libres del A6000 (NEW_IDS; solo idiomas
                                  de esquema latino). Los ids de la A6300 caen fuera del índice del A6000 (5 958 ranuras, hasta 0xf745):
                                  así se instaló el 3.39 y la UI no arrancó (assert de ResourceManager.cpp:954)
  SHA256SUMS, MANIFEST.json  (hashes de los originales y de los parcheados)
Uso: build_silent_menu_test.py DIR_DEV_A6000 DIR_DEV_A6300 SALIDA
"""
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry
import uxc_strings

PID_EFCS = 0x46
# id A6300 → id A6000: ranuras vacías en los 25 idiomas latinos, sin registro en los no latinos y sin referencia 0x0204xxxx en /usr
NEW_IDS = {0xF840: 0xF3E8, 0xF847: 0xF515, 0xF849: 0xF56A}  # etiqueta, ayuda de la raíz, ayuda de «On»
RES = 0x0204_0000
# (símbolo de la lista de propiedades, [(id propiedad, flag, valor)]) — tamaños fijos 3/4/4 entradas (el recuento está en el código)
LISTS = {
    "SilentShutterRoot": [(0, 0, RES | NEW_IDS[0xF840]), (6, 0, RES | NEW_IDS[0xF847]), (0xE, 1, PID_EFCS)],
    "SilentShutterOn": [(0, 0, RES | 0xE153), (6, 0, RES | NEW_IDS[0xF849]), (0xF, 1, 1), (0x10, 1, 1)],  # «On» = valor 1 (electrónico)
    "SilentShutterOff": [(0, 0, RES | 0xE109), (6, 0, RES | 0xF2A1), (0xF, 1, 0), (0x10, 1, 0)],  # «Off» = valor 0 (EFCS)
}
ROOT = ("nflasha15_unpacked_unpacked",)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def md5(data: bytes) -> str:
    return hashlib.md5(data, usedforsecurity=False).hexdigest()  # el busybox de la cámara solo trae md5sum


def patch_caution(data: bytes, lib: Path) -> bytes:
    out = bytearray(data)
    nm = subprocess.run(["nm", "-D", "-S", str(lib)], capture_output=True, text=True, check=True).stdout
    for line in nm.splitlines():
        f = line.split()
        if len(f) == 4 and f[3].startswith("cmnViewSettingPropertyList") and f[3][26:] in LISTS:
            addr, size = int(f[0], 16), int(f[1], 16)
            triples = LISTS[f[3][26:]]
            assert size == 12 * len(triples), (f[3], size)
            for i, t in enumerate(triples):
                struct.pack_into("<3I", out, addr + 12 * i, *t)
    return bytes(out)


def main(dev_a, dev_b, dest):
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
    main(*sys.argv[1:4])

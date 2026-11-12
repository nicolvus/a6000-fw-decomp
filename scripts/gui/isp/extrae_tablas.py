#!/usr/bin/env python3
"""T9 — extrae las tablas reales del pipeline de imagen (curvas de gamma, selector, matrices de color, ids de Backup de PP) a `analysis/gui/isp/`.

Fuentes (todo VERIFICADO con bytes; ninguna dirección sale de memoria):
  * `av-cam.bin` A6000 fw3.21 (base 0x43541000): tabla de punteros de curvas 0x44001404 (índice 2·gamma+modo, modo 1 = vídeo), cada curva 0x101a B =
    2048 u16 (salida de 10 bits) + cola de 13 u16; selector→(gamma foto, gamma vídeo) en 0x43cb56e6 (en blanco en la A6000, G16).
  * `av-cam-a7s.bin` (misma base): tabla 0x43ffa290 y selector 0x43cab54d. Las curvas de vídeo 0x16, 0x18–0x1d no existen en la A6000 y el CFW
    las instala desde la A7S (`pp_curves_patch.py`).
  * `av-cam-a6300.bin`: S-Log3 = gamma 0x1f (tabla 0x441bc70c).
  * Backup 0x30001 (0x600 B) del volcado real `20261105-volcado-total-nvram`: 15 matrices de color 3x3 int16 (1024 = 1,0): índices 0–7 en 0x48, 8–14 en 0x400,
    paso 18 B (G27 §5; offsets de las funciones de búsqueda 0x437a4b40).
  * ids de Backup de PP: constructor `libObj.so 0x4a9a56` ejecutado en Unicorn (`[obj+0x5dc+(perfil·31+i)·4]`, G35/G36); sin la `libObj` se omite.
Salida: curvas.npz, tablas.json, pp_ids.json. Uso: `python scripts/gui/isp/extrae_tablas.py [--sin-libobj]`.
"""
from __future__ import annotations

import hashlib
import io
import json
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "analysis/gui/isp"
BASE, CURVA, N = 0x43541000, 0x101A, 2048
BINS = {
    "a6000": (ROOT / "analysis/rea-independent/input/av-cam.bin", 0x44001404, 0x43CB56E6),
    "a7s": (ROOT / "analysis/rea-independent/input/av-cam-a7s.bin", 0x43FFA290, 0x43CAB54D),
    "a6300": (ROOT / "analysis/rea-independent/input/av-cam-a6300.bin", 0x441BC70C, None),
}
LIBOBJ = ROOT / "analysis/gui/g22/pkg-377w/files/lib/libObj.so"
DUMP = ROOT / "analysis/camera-dumps/20261105-volcado-total-nvram/backup_flash.bin"
N_PARAMS = 31


def u32(d: bytes, a: int) -> int:
    return struct.unpack_from("<I", d, a - BASE)[0]


def curva(d: bytes, dir_: int) -> tuple[np.ndarray, list[int]]:
    o = dir_ - BASE
    return np.frombuffer(d[o:o + 2 * N], "<u2").copy(), list(struct.unpack_from("<13H", d, o + 2 * N))


def extrae_curvas() -> tuple[dict[str, np.ndarray], dict]:
    arr, meta = {}, {}
    for cam, (ruta, tab, sel) in BINS.items():
        if not ruta.is_file():
            print(f"aviso: falta {ruta.name}", file=sys.stderr)
            continue
        d = ruta.read_bytes()
        meta[cam] = {"binario": ruta.name, "sha256": hashlib.sha256(d).hexdigest(), "tabla_punteros": hex(tab), "curvas": {}}
        for g in range(0x20):
            for modo in (0, 1):
                p = u32(d, tab + 8 * g + 4 * modo)
                if not (BASE <= p < BASE + len(d) - CURVA):
                    continue
                c, cola = curva(d, p)
                if cola[10] != g and cam != "a6300" or c.max() == 0:  # cola[10] = +0x1014 (número de gamma de la propia curva); en el bloque >0x1f no hay curvas
                    continue
                k = f"{cam}_{'v' if modo else 'f'}{g:02x}"
                dif = np.diff(c.astype(int))
                arr[k] = c
                meta[cam]["curvas"][k] = {"direccion": hex(p), "cola_u16": cola, "min": int(c.min()), "max": int(c.max()), "monotona": bool((dif >= 0).all()),
                                          "primera_no_monotona": int(np.argmax(dif < 0)) if (dif < 0).any() else None}
        if sel:
            s = d[sel - BASE:][:24]
            meta[cam]["selector_foto_video"] = [[s[2 * i], s[2 * i + 1]] for i in range(12)]
            meta[cam]["selector_dir"] = hex(sel)
    return arr, meta


def extrae_matrices() -> dict:
    if not DUMP.is_file():
        return {}
    sys.path.insert(0, str(ROOT / "references/pmca"))
    from pmca.backup import BackupFile
    ps = {i: bytes(p.data) for i, p in BackupFile(io.BytesIO(DUMP.read_bytes())).listProperties()}
    d = ps[0x30001]
    offs = [0x48 + 18 * i for i in range(8)] + [0x400 + 18 * i for i in range(7)]
    m = [list(struct.unpack_from("<9h", d, o)) for o in offs]
    assert all(sum(r[:3]) == sum(r[3:6]) == sum(r[6:]) == 1024 for r in m), "las filas de cada matriz deben sumar 1024 (neutros se conservan)"
    return {"propiedad": "0x30001", "volcado": DUMP.parent.name, "escala": 1024, "offsets": [hex(o) for o in offs], "matrices": m}


def extrae_pp_ids() -> dict:
    if not LIBOBJ.is_file():
        return {}
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP
    raw = LIBOBJ.read_bytes()
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, (len(raw) + 0xFFF) & ~0xFFF)
    mu.mem_write(0, raw)
    mu.mem_map(0x20000000, 0x10000)
    mu.mem_map(0x30000000, 0x10000)
    mu.reg_write(UC_ARM_REG_R0, 0x20000000)
    mu.reg_write(UC_ARM_REG_SP, 0x30008000)
    mu.reg_write(UC_ARM_REG_LR, 0x30000001)
    mu.emu_start(0x4A9A56 | 1, 0x30000000)
    v = struct.unpack_from(f"<{11 * N_PARAMS}I", bytes(mu.mem_read(0x20000000, 0x2000)), 0x5DC)
    return {"fuente": "libObj.so 0x4a9a56 (Unicorn), pkg-377w", "n_params": N_PARAMS, "perfiles": 11,
            "ids": [[v[p * N_PARAMS + i] for i in range(N_PARAMS)] for p in range(11)]}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    arr, meta = extrae_curvas()
    np.savez_compressed(OUT / "curvas.npz", **arr)
    meta["matrices_color"] = extrae_matrices()
    (OUT / "tablas.json").write_text(json.dumps(meta, indent=1))
    ids = extrae_pp_ids()
    if ids:
        (OUT / "pp_ids.json").write_text(json.dumps(ids))
    n_no_mono = [k for k, v in ((k, v) for c in meta.values() if isinstance(c, dict) and "curvas" in c for k, v in c["curvas"].items()) if not v["monotona"]]
    print(f"{len(arr)} curvas; no monótonas: {n_no_mono}; matrices {len(meta['matrices_color'].get('matrices', []))}; ids PP {'sí' if ids else 'omitidos'}")


if __name__ == "__main__":
    main()

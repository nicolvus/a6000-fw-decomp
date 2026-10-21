#!/usr/bin/env python3
"""Script de extracción reproducible de cadenas [CAMCORE] y ResourceStack.

Escanea el firmware A6000 (analysis/rea-independent/input/av-cam.bin) e informa:
- Cantidad de cadenas [CAMCORE] y sus vaddrs.
- Subsistemas identificados (SGC, RDC/PFR, AIF, Memory, ExlHelper, DMA, Powersave, Defect).
- Strings de ResourceStack dentro del bloque [IMAGING_CAP].
- Comparativa con A7S fw3.20 (ausencia de [CAMCORE]).

Método: búsquema de prefijo [CAMCORE] en todo el binario, igual que S104 y S106.
"""

import json
import struct
import sys

BASE = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
PREFIX = b"[CAMCORE]"


def _cstr(data, vaddr, maxlen=200):
    off = vaddr - BASE
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def main():
    data = open(BIN_PATH, "rb").read()
    n = len(data)

    # 1. Encontrar todas las cadenas [CAMCORE]
    out = []
    start = 0
    while True:
        i = data.find(PREFIX, start)
        if i < 0:
            break
        v = BASE + i
        text = _cstr(data, v)
        out.append((v, text))
        start = i + 1

    # 2. Filtrar solo aquellas en el rango esperado de CAMCORE (0x43c905ca -> 0x43cebcb2)
    camcore_min = 0x43C905CA
    camcore_max = 0x43CEBCB2
    camcore_strings = [(v, t) for v, t in out if camcore_min <= v <= camcore_max]

    # 3. Clasificar por subsistema (heurístico por prefijo de texto)
    subsystems = {
        "sgc": [],
        "rdc_pfr": [],
        "aif": [],
        "memory": [],
        "exlhelper": [],
        "dma_setter": [],
        "powersave": [],
        "defect": [],
    }

    for v, t in camcore_strings:
        lt = t.lower()
        if "sgc" in lt or "sgc1" in lt:
            subsystems["sgc"].append((v, t))
        elif "pfr" in lt or "memory for pfr" in lt or "pfr in width" in lt:
            subsystems["rdc_pfr"].append((v, t))
        elif "aif" in lt or "extent" in lt or "pbl_aif" in lt or "rdc param" in lt or "rdc none" in lt:
            subsystems["aif"].append((v, t))
        elif "memorypool" in lt or "resourcebase::release" in lt or "getmemindex" in lt:
            subsystems["memory"].append((v, t))
        elif "exlhelper" in lt or "cannot convert" in lt or "invalid imager" in lt:
            subsystems["exlhelper"].append((v, t))
        elif "dma err" in lt or "dmac_ch_none" in lt or "listcount" in lt:
            subsystems["dma_setter"].append((v, t))
        elif "monpowersave" in lt or "already enabled" in lt:
            subsystems["powersave"].append((v, t))
        elif "defect" in lt or "setdefect" in lt:
            subsystems["defect"].append((v, t))
        else:
            # Fallback: etiqueta desconocida
            subsystems["otro"] = subsystems.get("otro", []) + [(v, t)]

    # 4. Strings de ResourceStack (dentro de [IMAGING_CAP])
    rs_addrs = [0x43CA10D1, 0x43CA110D, 0x43CA11C2, 0x43CA120F]
    rs_strings = {}
    for v in rs_addrs:
        if camcore_min <= v <= camcore_max:
            # Buscar la cadena exacta en el rango
            for vv, tt in camcore_strings:
                if vv == v:
                    rs_strings[hex(v)] = tt
                    break

    # 5. Diferencial A7S
    a7s_path = (
        "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
        "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
    )
    a7s_has_camcore = False
    if __import__("os").path.exists(a7s_path):
        a7s = open(a7s_path, "rb").read()
        a7s_has_camcore = a7s.count(PREFIX) > 0

    # 6. Output
    print(f"=== S107 — CAMCORE strings report ===")
    print(f"Total cadenas [CAMCORE] encontradas: {len(camcore_strings)}")
    print(f"Rango: 0x{camcore_min:08X} → 0x{camcore_max:08X}")
    print()

    for name, strings in subsystems.items():
        if strings:
            print(f"[{name}] ({len(strings)} strings):")
            for v, t in strings:
                print(f"  vaddr {hex(v):12s}  {t}")
            print()

    print("=== ResourceStack strings (within [IMAGING_CAP]) ===")
    for v, t in rs_strings.items():
        print(f"  {t}")
    print()

    print(f"A7S fw3.20 con prefijo [CAMCORE]: {'SÍ' if a7s_has_camcore else 'NO'} (0 cadenas esperadas)")
    print()
    print("=== JSON de datos estructurados ===")
    print("Ver analysis/s107_camcore/camcore_resources.json")

    # Generar JSON de salida rápida
    result = {
        "count": len(camcore_strings),
        "range": [hex(camcore_min), hex(camcore_max)],
        "subsystems": {k: [t for _, t in v] for k, v in subsystems.items() if v},
        "resource_stack": {k: t for k, t in rs_strings.items()},
        "a7s_camcore": a7s_has_camcore,
    }
    out_json = "analysis/s107_camcore/camcore_resources.json"
    with open(out_json, "w") as fh:
        json.dump(result, fh, indent=2)
    print(f"\nJSON rápido escrito en {out_json}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""S138 — diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01 del módulo `[CAMERA_MAIN_FC]`.

Para cada una de las 9 cadenas de la A6000:
  * ¿existe la cadena completa (con prefijo) en los otros firmwares?
  * ¿existe el "núcleo" (texto tras "[CAMERA_MAIN_FC]: ") en los otros firmwares?
  * ¿existe la cadena completa en la propia A6000 en otro módulo (prefijos distintos)?
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
FW = {
    "a6000": os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"),
    "a7s": os.path.join(ROOT, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6300": os.path.join(ROOT, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
PREFIX = "[CAMERA_MAIN_FC]: "


def strings_set(data):
    out = set()
    for part in data.split(b"\x00"):
        if len(part) > 3:
            out.add(part.decode("latin1"))
    return out


def main():
    data = {k: open(v, "rb").read() for k, v in FW.items()}
    sets = {k: strings_set(v) for k, v in data.items()}
    items = json.load(open(os.path.join(ROOT, "analysis/s138_camera_main_fc/fc_strings.json")))
    rows = []
    for it in items["a6000"]["items"]:
        full = it["text"]
        core = full[len(PREFIX):] if full.startswith(PREFIX) else full
        row = {"vaddr": f"0x{it['vaddr']:x}", "text": full, "core": core}
        for fw in ("a7s", "a6300"):
            row[f"full_{fw}"] = full in sets[fw]
            row[f"core_{fw}"] = core in sets[fw]
        # ¿la cadena completa aparece en la A6000 bajo otro prefijo?
        row["a6000_other_prefix"] = [
            s for s in sets["a6000"]
            if s.endswith(core) and not s.startswith("[CAMERA_MAIN_FC]")
        ]
        rows.append(row)
        print(f"0x{it['vaddr']:x}  full_a7s={row['full_a7s']} core_a7s={row['core_a7s']} "
              f"full_a6300={row['full_a6300']} core_a6300={row['core_a6300']}  {core[:60]!r}")
        if row["a6000_other_prefix"]:
            print(f"     en la A6000 con otro prefijo: {row['a6000_other_prefix'][:4]}")
    # recuento global de prefijos [CAMERA_MAIN_*
    for fw in ("a6000", "a7s", "a6300"):
        pref = sorted(s for s in sets[fw] if s.startswith("[CAMERA_MAIN"))
        print(f"{fw}: {len(pref)} cadenas con prefijo [CAMERA_MAIN*]")
    json.dump(rows, open(os.path.join(ROOT, "analysis/s138_camera_main_fc/fc_diff.json"), "w"),
              indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()

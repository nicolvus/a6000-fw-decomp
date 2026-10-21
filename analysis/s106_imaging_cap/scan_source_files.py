#!/usr/bin/env python3
"""Inventario de ficheros fuente embebidos en el subsistema de captura.

El firmware incluye los nombres de los ficheros .cpp/.h del subsistema de captura
como cadenas contiguas (0x43ca8e14-0x43cb0cbe en el av-cam.bin de la A6000).
Este script los extrae con su vaddr y los agrupa por familia funcional.
"""
import json
import re
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
LO, HI = 0x43CA8000, 0x43CB1000

GROUPS = [
    ("caif", ("CaifCom",)),
    ("image_param", ("ImageParamCapture", "ImageParam_Sync")),
    ("capture_manager", ("CaptureManager",)),
    ("notify", ("NotifyController",)),
    ("raw_mem", ("RawMemManager",)),
    ("section", ("SectionController", "SectionQueueManager", "SectionEndFunc", "S2Handler")),
    ("still", ("still_",)),
    ("stage", ("Stage_",)),
    ("utility", ("CaptureUtility",)),
    ("handler", ("FunctionMessage", "FunctionNotify", "FunctionSetParam",
                 "EventDispatcher", "ExecModeHandler", "ExecReleaseHandler",
                 "RawDevHandler", "ReplyHandler", "SendChannel")),
    ("bridge", ("LRBridge", "Dfs_Control", "capcon_api_businessif",
                "tsk_capcon_sequence", "tsk_rawdev_sequence", "CS_Command",
                "InternalCapture")),
    ("cam", ("CamMain", "CamUser", "CameraBackGround", "Face", "HAPI_Filter_TBOX",
             "StillInfoAccr")),
]


def group_of(name):
    if name.endswith("_Selector.cpp"):
        return "selector"
    for g, pfx in GROUPS:
        if name.startswith(pfx):
            return g
    return "otros"


def main():
    data = open(BIN, "rb").read()
    items = []
    for m in re.finditer(rb"[A-Za-z0-9_]{3,40}\.(?:cpp|h)\x00", data):
        va = BASE + m.start()
        if not (LO <= va < HI):
            continue
        name = m.group()[:-1].decode()
        items.append({"vaddr": f"0x{va:x}", "name": name, "group": group_of(name)})
    items.sort(key=lambda r: int(r["vaddr"], 16))
    groups = {}
    for it in items:
        groups.setdefault(it["group"], []).append(it["name"])
    out = {
        "range": [f"0x{LO:x}", f"0x{HI:x}"],
        "count": len(items),
        "groups": {k: len(v) for k, v in sorted(groups.items())},
        "files": items,
    }
    dest = "analysis/s104_imaging_cap/source_files.json"
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"{len(items)} ficheros en {hex(LO)}-{hex(HI)}")
    for k, v in sorted(groups.items()):
        print(f"  {k:16s} {len(v):3d}  {', '.join(v[:4])}...")
    print("escrito", dest)


if __name__ == "__main__":
    sys.exit(main())

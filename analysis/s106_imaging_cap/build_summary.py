#!/usr/bin/env python3
"""Construye el resumen estructurado del hito S106 (IMAGING_CAP).

Une los datos extraídos por los scripts de este directorio en un único JSON.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    blocks = load("imaging_cap_blocks.json")
    handlers = load("section_handlers.json")
    files = load("source_files.json")
    diff = load("imaging_cap_a7s_diff.json")
    strings = load("strings_raw.json")
    refs = load("pic_refs_v2.json")   # kill analysis (v2); ver pic_xref_methodology.md

    ref_keys = {int(k, 16) for k in refs}
    referenced = [s for s in strings if int(s["vaddr"], 16) in ref_keys]
    unreferenced = [s for s in strings if int(s["vaddr"], 16) not in ref_keys]

    out = {
        "milestone": "S106",
        "module": "IMAGING_CAP",
        "binary": "analysis/rea-independent/input/av-cam.bin",
        "base": "0x43541000",
        "counts": {
            "strings": len(strings),
            "blocks": len(blocks["blocks"]),
            "referenced_strings": len(referenced),
            "unreferenced_strings": len(unreferenced),
            "pic_targets_in_string_zone": len(refs),
            "sections": len(handlers),
            "source_files": files["count"],
        },
        "range": {
            "first": strings[0]["vaddr"],
            "last": strings[-1]["vaddr"],
        },
        "blocks": [
            {"name": b["name"], "lo": b["lo"], "hi": b["hi"], "n": b["n"]}
            for b in blocks["blocks"]
        ],
        "sections": [
            {
                "id": h["section_id"],
                "handler": h["handler"],
                "end": h["end"],
                "size": h["size"],
                "selectors": sorted({s["text"] for s in h["strings"]
                                     if s["text"].endswith(".cpp")}),
            }
            for h in handlers
        ],
        "source_file_groups": files["groups"],
        "source_files": files["files"],
        "unreferenced_strings": [
            {"vaddr": s["vaddr"], "text": s["text"]} for s in unreferenced
        ],
        "a7s_diff": {
            k: v for k, v in diff.items()
            if k in ("A6000-fw321", "A7S-fw320", "A6300-fw201",
                     "diff_a6000_only", "diff_a7s_only")
        },
    }
    dest = os.path.join(HERE, "imaging_cap_architecture.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print("escrito", dest)
    print(json.dumps(out["counts"], indent=1))


if __name__ == "__main__":
    main()

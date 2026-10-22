#!/usr/bin/env python3
"""S301: build the classified xref sweep for the A7S fw3.20 imager state object.

Inputs (tool output of this session, kept verbatim):
  raw1.jsonl  xrefs + typed incoming references + object bytes (A7S)
  raw2.jsonl  resolve_containing_procedure for every referencing site
  raw3.jsonl  procedure_info (body ranges) for every containing function
  trace_candidates.json  local linear trace of the loaded pointer (capstone)

Every instruction stored in the output is re-decoded from the A7S av-cam.bin by
verify_sweep.py, so a wrong address or offset makes the test fail.
"""
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
HERE = Path(__file__).resolve().parent

# Reads through a spilled pointer that the site tracer cannot follow (stack reload).
RELOAD_READS = {
    "0x437d36c2": [("0x437d3afe", "0xa5"), ("0x437d3e24", "0xa5"), ("0x437d4188", "0x42")],
    "0x437e2444": [("0x437e2c22", "0x26"), ("0x437e308a", "0x29")],
    "0x438477f0": [("0x438478ee", "0xe4")],
}
# Explicit-provenance notes for edges that are not memory accesses of the object.
EDGE_NOTES = {
    "0x43ff928c": "entrada de tabla de punteros (dato), no instrucción",
    "0x437d36be": "carga el puntero desde el slot GOT; lee +0x40 y lo derrama en [sp,#0x20]",
    "0x437e6ae0": "carga el puntero desde el slot GOT y lo derrama en [sp,#0x1c]",
    "0x437e243e": "carga el puntero desde el slot GOT y lo derrama en [sp,#0x20]",
}


def load():
    blob = BIN.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    edges, funcs, bodies = {}, {}, {}
    for name in ("raw1.jsonl", "raw2.jsonl", "raw3.jsonl"):
        for line in (HERE / name).read_text().splitlines():
            d = json.loads(line)
            c, t = d["call"], json.loads(d["result"]["content"][0]["text"])
            n = t.get("normalized_result")
            if c["tool"] == "inspect_native_instruction":
                for r in n["incoming_references"]:
                    edges.setdefault(r["source_address"], {})[c["args"]["address"]] = r
            elif c["tool"] == "resolve_containing_procedure" and isinstance(n, dict):
                if n.get("procedure"):
                    funcs[c["args"]["address"]] = n["procedure"]["address"]
            elif c["tool"] == "procedure_info" and isinstance(n, dict):
                bodies[n["entrypoint"]] = [(int(r["start"], 16), int(r["end"], 16))
                                           for r in n["body"]["ranges"]]
    return blob, md, edges, funcs, bodies


def decode_at(blob, md, address, size=4):
    raw = blob[address - BASE:address - BASE + size]
    got = list(md.disasm(raw, address))
    return raw.hex(), (f"{got[0].mnemonic} {got[0].op_str}" if got else None)


def main():
    blob, md, edges, funcs, _bodies = load()
    trace = json.loads((HERE / "trace_candidates.json").read_text())
    sites = []
    for site in sorted(edges, key=lambda a: int(a, 16)):
        f = funcs.get(site)
        kinds = edges[site]
        accesses = []
        for row in trace.get(site, {}).get("trace", []):
            if row.get("access") in ("read", "write"):
                off = row.get("offset")
                accesses.append({"address": row["address"], "insn": row["insn"],
                                 "kind": row["access"],
                                 "offset": int(off, 0) if off else None})
        for addr, off in RELOAD_READS.get(site, []):
            raw, text = decode_at(blob, md, int(addr, 16), 4)
            accesses.append({"address": addr, "insn": text, "kind": "read",
                             "offset": int(off, 0), "through": "spill reload"})
        raw, text = decode_at(blob, md, int(site, 16), 4)
        # The typed edge itself can be the access (READ/WRITE to base or to a gate byte).
        for target, edge in kinds.items():
            if target not in ("0x43f7bce6", "0x43f7bce9", "0x43f7bcec"):
                continue
            if edge["type"] not in ("READ", "WRITE"):
                continue
            off = int(target, 16) - int("0x43f7bce6", 16)
            accesses.insert(0, {"address": site, "insn": text,
                                "kind": edge["type"].lower(),
                                "offset": (off if off else None)})
        seen, uniq = set(), []
        for a in accesses:
            key = (a["address"], a["kind"], a["insn"])
            if key not in seen:
                seen.add(key)
                uniq.append(a)
        accesses = uniq
        writes = [a for a in accesses if a["kind"] == "write"]
        reads = [a for a in accesses if a["kind"] == "read"]
        if site == "0x43ff928c":
            cls = "dato"
        elif text and text.startswith("str") and "[sp" in text:
            cls = "spill"
        elif writes:
            cls = "escritura"
        elif reads:
            cls = "lectura"
        elif text and text.startswith("str") and "[sp" in text:
            cls = "spill"
        else:
            cls = "propagación"
        sites.append({
            "site": site,
            "function": f,
            "edges": {k: {"type": v["type"], "read": v["read"], "write": v["write"]}
                      for k, v in kinds.items()},
            "insn": text,
            "bytes_hex": raw,
            "class": cls,
            "accesses": accesses,
            "note": EDGE_NOTES.get(site),
        })
    counts = {}
    for s in sites:
        counts[s["class"]] = counts.get(s["class"], 0) + 1
    gate_targets = {"0x43f7bce9": "state+3", "0x43f7bcec": "state+6"}
    gate_rows = []
    for line in (HERE / "raw1.jsonl").read_text().splitlines():
        d = json.loads(line)
        c, t = d["call"], json.loads(d["result"]["content"][0]["text"])
        if c["tool"] != "inspect_native_instruction":
            continue
        a = c["args"]["address"]
        if a not in gate_targets:
            continue
        for r in t["normalized_result"]["incoming_references"]:
            raw, text = decode_at(blob, md, int(r["source_address"], 16), 4)
            gate_rows.append({"target": gate_targets[a], "address": a,
                              "site": r["source_address"], "type": r["type"],
                              "insn": text, "bytes_hex": raw})
    rea_xrefs = {}
    for line in (HERE / "raw1.jsonl").read_text().splitlines():
        d = json.loads(line)
        c, t = d["call"], json.loads(d["result"]["content"][0]["text"])
        if c["tool"] == "xrefs":
            rea_xrefs[c["args"]["address"]] = t["normalized_result"]
    result = {
        "milestone": "S301",
        "rea_xrefs": rea_xrefs,
        "title": "barrido único de xrefs al state del imager (base y slot GOT)",
        "firmware": {"name": "av-cam.bin (A7S fw3.20)", "sha256": __import__("hashlib").sha256(blob).hexdigest()},
        "base": f"0x{BASE:08x}",
        "targets": {"state_base": "0x43f7bce6", "got_slot": "0x440251e4",
                    "gate_plus3": "0x43f7bce9", "gate_plus6": "0x43f7bcec"},
        "absolute_pointer_literals": [
            {"address": "0x43ff928c", "kind": "entrada de tabla de punteros"},
            {"address": "0x440251e4", "kind": "slot GOT"},
        ],
        "sites": sites,
        "counts": {"total_sites": len(sites), **counts},
        "gates": {"rows": gate_rows, "writers": [r for r in gate_rows if r["type"] == "WRITE"]},
        "verdict": {
            "writer_plus3": False,
            "writer_plus6": False,
            "basis": "xrefs exactos tipados a +3 y +6 (8 lecturas cada uno) + sitios de la base/slot con traza local",
            "limit": "no cubre índice de registro dinámico no observado, DMA ni otro CPU; "
                     "tampoco prueba alcanzabilidad runtime",
        },
        "scope_limit": "Barrido estático del blob A7S fw3.20; los accesos se demuestran por bytes e "
                       "instrucción, no por ejecución.",
    }
    (HERE / "state_xref_sweep.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["counts"], indent=1))
    print("gates writers:", result["gates"]["writers"])
    print("writes:", [(s["site"], s["accesses"]) for s in sites if s["class"] == "escritura"])


if __name__ == "__main__":
    main()

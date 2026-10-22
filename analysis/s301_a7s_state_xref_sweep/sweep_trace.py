#!/usr/bin/env python3
"""S301 helper: candidate uses of the state pointer loaded at each xref site.

Linear Thumb sweep from each site; tracks registers that hold the pointer loaded
from the GOT slot and reports memory accesses / call propagation until the value
is overwritten. Candidates only: every row is re-checked by hand in the report.
"""
import json
import re
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = Path("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
HERE = Path(__file__).resolve().parent
RAW = ["raw1.jsonl", "raw2.jsonl", "raw3.jsonl"]
LOAD = {"ldr", "ldrb", "ldrh", "ldrsb", "ldrsh", "ldrd"}
MOVE = {"mov", "movs", "movw", "add", "adds", "addw", "sub", "subs", "adr", "and", "orr", "lsl", "lsr"}
# mnemonics that write their first operand (str/stm/cmp/tst do not)
DST = MOVE | {"ldr", "ldrb", "ldrh", "ldrsb", "ldrsh", "ldrd", "mul", "mla", "eor", "bic",
              "mvn", "uxth", "sxth", "uxtb", "sxtb", "rev", "clz", "asr", "ror", "rsb",
              "neg", "abs", "it"}


def norm(m):
    return m.split(".")[0]


def load():
    blob = BIN.read_bytes()
    sites, funcs, bodies = {}, {}, {}
    for name in RAW:
        for line in (HERE / name).read_text().splitlines():
            d = json.loads(line)
            c, t = d["call"], json.loads(d["result"]["content"][0]["text"])
            n = t.get("normalized_result")
            if c["tool"] == "inspect_native_instruction":
                for r in n["incoming_references"]:
                    sites.setdefault(r["source_address"], {})[c["args"]["address"]] = (
                        r["type"], bool(r["read"]), bool(r["write"]))
            elif c["tool"] == "resolve_containing_procedure" and isinstance(n, dict):
                p = n.get("procedure")
                if p:
                    funcs[c["args"]["address"]] = p["address"]
            elif c["tool"] == "procedure_info" and isinstance(n, dict):
                bodies[n["entrypoint"]] = [(int(r["start"], 16), int(r["end"], 16))
                                           for r in n["body"]["ranges"]]
    return blob, sites, funcs, bodies


def decode_function(blob, bodies, entry):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    insns = []
    for start, end in bodies[entry]:
        insns += list(md.disasm(blob[start - BASE:end - BASE], start))
    return insns


def mem_base(op_str):
    m = re.search(r"\[([a-z0-9]+)(?:, #(0x[0-9a-f]+|\d+))?\]", op_str)
    return (m.group(1), m.group(2)) if m else (None, None)


def walk(insns, site, limit=70):
    idx = next((i for i, x in enumerate(insns) if x.address == site), None)
    if idx is None:
        return [{"error": "site not in linear decode"}]
    first = insns[idx]
    ops = [o.strip() for o in first.op_str.split(",")]
    out = [{"insn": f"{first.mnemonic} {first.op_str}",
            "address": f"0x{first.address:08x}"}]
    m = norm(first.mnemonic)
    if m not in ("ldr", "ldr.w") and m != "ldr":
        out.append({"note": "site is not a load", "mnemonic": first.mnemonic})
        return out
    tainted = {ops[0]} if ops and ops[0] in REGS else set()
    for ins in insns[idx + 1: idx + 1 + limit]:
        text = f"{ins.mnemonic} {ins.op_str}"
        base, off = mem_base(ins.op_str)
        if base in tainted:
            out.append({"insn": text, "address": f"0x{ins.address:08x}",
                        "access": "write" if norm(ins.mnemonic).startswith("str") else "read",
                        "offset": off})
        if norm(ins.mnemonic) in ("bl", "blx"):
            live = [f"r{i}" for i in range(4) if f"r{i}" in tainted]
            if live:
                out.append({"insn": text, "address": f"0x{ins.address:08x}",
                            "access": "call", "regs": live})
        # taint update
        dst_ops = [o.strip() for o in ins.op_str.split(",")]
        dst = dst_ops[0] if dst_ops and dst_ops[0] in REGS and norm(ins.mnemonic) in DST else None
        srcs = dst_ops[1:] if dst else []
        if dst:
            was = dst in tainted
            keep = was and norm(ins.mnemonic) in MOVE and any(
                s in tainted for s in srcs)
            if norm(ins.mnemonic) in MOVE and any(s in tainted for s in srcs):
                keep = True
            if not keep:
                tainted.discard(dst)
        if norm(ins.mnemonic) in ("bx", "pop") and "pc" in ins.op_str:
            break
        if not tainted:
            break
    return out


REGS = {f"r{i}" for i in range(13)} | {"sp", "lr", "fp", "ip", "sb", "sl"}


def main():
    blob, sites, funcs, bodies = load()
    report = {}
    for site in sorted(sites):
        func = funcs.get(site)
        row = {"function": func, "kinds": sites[site]}
        if func:
            row["trace"] = walk(decode_function(blob, bodies, func), int(site, 16))
        report[site] = row
    (HERE / "trace_candidates.json").write_text(json.dumps(report, indent=1) + "\n")
    n = sum(1 for v in report.values() if v["function"])
    print(f"{len(report)} sites, {n} resolved to a function")


if __name__ == "__main__":
    main()
